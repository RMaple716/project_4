import asyncio
import uuid
import json
import os
import openai
from typing import Optional, Dict, List, Any
from .base import BaseAgent
from core.message import Message, Bid, TaskStatus
from core.visualizer import ChatStyleVisualizer

# 创建全局可视化器实例
visualizer = ChatStyleVisualizer()


class OrchestratorAgent(BaseAgent):
    """
    旅游规划调度经理（LLM 增强版）
    使用 DeepSeek 解析用户意图、动态生成子任务，并汇总最终旅行计划。
    """

    def __init__(self, agent_id: str = "orchestrator"):
        super().__init__(agent_id)
        self.pending_tasks: Dict[str, dict] = {}
        self.bids: Dict[str, List[Bid]] = {}
        self.negotiation_results: Dict[str, dict] = {}  # [新增] 存储协商结果
        
        # 延迟加载 DeepSeek API Key（在实例化时检查，而不是模块加载时）
        deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")
        if not deepseek_key:
            print("[WARNING] DEEPSEEK_API_KEY 未设置，将使用默认配置")
            deepseek_key = "sk-placeholder-key"  # 占位符，实际使用时会失败
        
        # 初始化 DeepSeek 客户端
        self.deepseek_client = openai.OpenAI(
            api_key=deepseek_key,
            base_url="https://api.deepseek.com/v1"
        )

    async def handle_message(self, msg: Message) -> None:
        """处理接收到的消息（实现抽象方法）"""
        if msg.type == "user_request":
            await self._decompose_and_announce(msg)
        elif msg.type == "bid":
            await self._collect_bid(msg)
        elif msg.type == "task_result":
            await self._handle_task_result(msg)

    async def _decompose_and_announce(self, msg: Message):
        """使用 DeepSeek 解析用户自然语言请求，动态生成子任务并招标"""
        user_input = msg.content

        # ---------- 1. 调用 DeepSeek 提取意图 ----------
        try:
            prompt = f"""
你是一个旅行规划助手。从用户输入中提取目的地城市、游玩天数、兴趣标签。
兴趣标签可选：天气、美食、酒店、路线、景点、购物等。
请直接返回一个 JSON，格式严格如下：
{{"city": "城市名", "days": 天数, "interests": ["标签1", "标签2"]}}
用户输入：{user_input}
"""
            response = self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=200
            )
            raw = response.choices[0].message.content
            if raw is None:
                raise ValueError("DeepSeek 返回内容为空")
            raw = raw.strip()
            # 有时模型会返回代码块，去掉可能的 ```json ... ```
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
            plan_info = json.loads(raw)
        except Exception as e:
            print(f"[{self.agent_id}] DeepSeek 解析失败，使用默认值: {e}")
            plan_info = {"city": "北京", "days": 3, "interests": ["天气", "美食", "酒店", "路线"]}

        city = plan_info.get("city", "北京")
        days = plan_info.get("days", 3)
        interests = plan_info.get("interests", [])

        # ---------- 2. 根据兴趣动态生成子任务 ----------
        subtasks = {}
        
        # 天气查询（默认总是添加）
        if "天气" in interests or not subtasks:
            subtasks["weather"] = {
                "action": "get_forecast_weather",
                "params": {"location": city, "days": days},
                "description": f"查询 {city} 未来{days}天天气"
            }
        
        # 景点/古迹搜索
        attraction_keywords = ["景点", "古迹", "博物馆", "公园", "旅游", "观光", "历史", "文化"]
        if any(keyword in interests for keyword in attraction_keywords):
            subtasks["attraction"] = {
                "action": "search_poi",
                "params": {"keywords": "旅游景点", "city": city},
                "description": f"搜索 {city} 热门景点和古迹"
            }
        
        # 酒店搜索
        if "酒店" in interests or "住宿" in interests:
            subtasks["hotel"] = {
                "action": "search_poi",
                "params": {"keywords": "酒店", "city": city},
                "description": f"搜索 {city} 周边酒店"
            }
        
        # 美食搜索
        food_keywords = ["美食", "餐厅", "餐饮", "小吃", "特色菜"]
        if any(keyword in interests for keyword in food_keywords):
            subtasks["restaurant"] = {
                "action": "search_poi",
                "params": {"keywords": "美食", "city": city},
                "description": f"搜索 {city} 特色美食"
            }
        
        # 路线规划
        if "路线" in interests or "交通" in interests:
            subtasks["route"] = {
                "action": "get_route",
                "params": {
                    "origin": f"{city}市中心",
                    "destination": f"{city}热门景点",
                    "city": city
                },
                "description": f"规划 {city} 市内经典路线"
            }
        
        # 如果没有任何匹配，至少查询天气和景点
        if len(subtasks) <= 1 and "weather" in subtasks:
            subtasks["attraction"] = {
                "action": "search_poi",
                "params": {"keywords": "旅游景点", "city": city},
                "description": f"搜索 {city} 热门景点"
            }

        # ---------- 3. 广播招标 ----------
        task_id = str(uuid.uuid4())[:8]
        requirement_id = f"req_{task_id}"  # [新增] 生成需求ID
        
        self.pending_tasks[task_id] = {
            "subtasks": subtasks,
            "reply_to": msg.sender,
            "results": {},  # 改为字典，key 为 sub_id
            "total": len(subtasks),
            "requirement_id": requirement_id,  # [新增] 保存需求ID
            "city_name": city,  # [新增] 保存城市名
            "travel_days": days  # [新增] 保存天数
        }
        self.bids[task_id] = []

        # [新增] 初始化协商结果存储
        from datetime import datetime
        self.negotiation_results[task_id] = {
            "task_id": task_id,
            "requirement_id": requirement_id,
            "city_name": city,
            "travel_days": days,
            "agent_results": {},
            "timestamp": datetime.now().isoformat()
        }

        print(f"[{self.agent_id}] 任务 {task_id} 解析结果：城市={city}, 兴趣={interests}, 子任务数={len(subtasks)}")
        
        # [新增] 检测冲突
        visualizer.detect_conflicts(task_id, subtasks)

        for sub_id, task_info in subtasks.items():
            cfp_msg = Message(
                type="cfp",
                content=task_info,
                metadata={
                    "task_id": task_id,
                    "sub_id": sub_id,
                    "skill": task_info["action"]
                }
            )
            await self.send_message(cfp_msg)
            
            # [新增] 记录招标事件
            visualizer.record_event("cfp_sent", {
                "task_id": task_id,
                "sub_id": sub_id,
                "skill": task_info["action"],
                "description": task_info["description"]
            })

    async def _collect_bid(self, msg: Message):
        """收集投标书，并在收齐后评标"""
        bid: Bid = msg.content
        task_id = msg.metadata["task_id"]
        if task_id not in self.pending_tasks:
            return

        self.bids[task_id].append(bid)
        print(f"[{self.agent_id}] 收到 {bid.agent_id} 的投标，任务 {task_id} ({len(self.bids[task_id])}/{self.pending_tasks[task_id]['total']})")
        
        # [新增] 记录投标事件
        visualizer.record_event("bid_received", {
            "agent_id": bid.agent_id,
            "task_id": task_id,
            "capabilities": bid.capabilities,
            "cost": bid.cost
        })

        if len(self.bids[task_id]) >= self.pending_tasks[task_id]["total"]:
            await self._evaluate_and_award(task_id)

    async def _evaluate_and_award(self, task_id: str):
        """评标并签约（先到先得，能力匹配）"""
        task_info = self.pending_tasks[task_id]
        subtasks = task_info["subtasks"]
        bids = self.bids[task_id]

        skill_bids: Dict[str, Bid] = {}
        for bid in bids:
            for cap in bid.capabilities:
                if cap not in skill_bids:
                    skill_bids[cap] = bid

        for sub_id, task_data in subtasks.items():
            required_skill = task_data["action"]
            winner = skill_bids.get(required_skill)
            if winner:
                award_msg = Message(
                    type="award",
                    recipient=winner.agent_id,
                    content=task_data,
                    metadata={"task_id": task_id, "sub_id": sub_id}
                )
                await self.send_message(award_msg)
                print(f"[{self.agent_id}] 子任务 {sub_id} 签约给 {winner.agent_id}")
                
                # [新增] 记录签约事件
                visualizer.record_event("award_sent", {
                    "agent_id": winner.agent_id,
                    "task_id": task_id,
                    "sub_id": sub_id,
                    "skill": required_skill
                })
            else:
                print(f"[{self.agent_id}] 警告：子任务 {sub_id} 无匹配投标者")

    async def _handle_task_result(self, msg: Message):
        """收集子任务结果，全部完成后用 DeepSeek 汇总生成最终旅行计划"""
        task_id = msg.metadata["task_id"]
        sub_id = msg.metadata.get("sub_id")
        task_info = self.pending_tasks.get(task_id)
        if not task_info:
            return

        # ✅ 解析标准化响应格式
        result_data = msg.content
        if isinstance(result_data, dict):
            # 新格式：AgentResponse.to_dict()
            status = result_data.get("status", "success")
            items = result_data.get("data", {}).get("items", [])
            metadata = result_data.get("metadata", {})
            error_message = result_data.get("error_message")
            
            # 存储结构化结果
            task_info["results"][sub_id] = {
                "status": status,
                "items": items,
                "metadata": metadata,
                "error_message": error_message
            }
            
            # [新增] 保存协商结果（符合多智能体通信数据格式规范）
            if task_id not in self.negotiation_results:
                self.negotiation_results[task_id] = {
                    "task_id": task_id,
                    "requirement_id": task_info.get("requirement_id", ""),
                    "city_name": "",
                    "travel_days": 0,
                    "agent_results": {},
                    "timestamp": ""
                }
            
            self.negotiation_results[task_id]["agent_results"][sub_id] = {
                "task_id": f"{task_id}_{sub_id}",
                "status": status,
                "data": {
                    "items": items
                },
                "metadata": metadata,
                "error_message": error_message
            }
        else:
            # 旧格式：直接字符串（向后兼容）
            task_info["results"][sub_id] = {
                "status": "success",
                "items": [{"raw": str(result_data)}],
                "metadata": {},
                "error_message": None
            }
        
        completed_count = sum(1 for r in task_info["results"].values() if r["status"] in ["success", "partial"])
        print(f"[{self.agent_id}] 任务进度: {completed_count}/{task_info['total']}")
        
        # [新增] 记录任务完成事件
        visualizer.record_event("task_completed", {
            "task_id": task_id,
            "sub_id": sub_id,
            "agent_id": msg.sender,  # ← 添加 agent_id 用于统计
            "result_preview": str(result_data)[:100]
        })

        if completed_count >= task_info["total"]:
            # ✅ 按时间槽组织每日行程
            organized_plan = self._organize_by_time_slots(task_info["results"])
            
            # ---------- 用 DeepSeek 汇总 ----------
            raw_results = json.dumps(organized_plan, ensure_ascii=False, indent=2)
            prompt = f"""
你是一个专业的旅行规划师。下面是结构化的旅行数据（包含景点、酒店、美食、路线等），
请根据这些数据生成一份人性化、易读的 1-3 日旅行计划。

数据结构说明：
- 每个景点有 visit_time_slot 字段（morning/afternoon/evening）表示建议游览时段
- 请按时段组织行程，避免时间冲突

原始数据：
{raw_results}

要求：
1. 语言亲切，包含具体建议
2. 以"亲爱的旅行者，这是为你定制的行程："开头
3. 按天、按时段（上午/下午/晚上）组织内容
4. 标注预算超标的提醒（如果有）
"""
            try:
                response = self.deepseek_client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=800
                )
                content = response.choices[0].message.content
                if content is None:
                    raise ValueError("DeepSeek 返回内容为空")
                final_plan = content.strip()
            except Exception as e:
                print(f"[{self.agent_id}] DeepSeek 汇总失败: {e}")
                final_plan = "以下是原始数据，请查阅：\n" + raw_results

            reply = Message(
                type="final_plan",
                recipient=task_info["reply_to"],
                content=final_plan,
                metadata={"task_id": task_id}
            )
            await self.send_message(reply)
            
            # [新增] 记录计划生成事件并输出总结
            visualizer.record_event("plan_generated", {
                "task_id": task_id,
                "plan_length": len(final_plan)
            })
            
            # [新增] 以聊天室风格打印总结
            visualizer.print_chat_style_summary()
            
            # [新增] 导出协商结果（符合多智能体通信数据格式规范）
            self._export_negotiation_results(task_id)
            
            # [新增] 导出日志
            visualizer.export_to_json()

            del self.pending_tasks[task_id]
            del self.bids[task_id]
    
    def _export_negotiation_results(self, task_id: str):
        """
        导出协商结果，符合多智能体通信数据格式规范
        输出文件：negotiation_result.json
        """
        if task_id not in self.negotiation_results:
            print(f"[WARNING] 未找到任务 {task_id} 的协商结果")
            return
        
        result = self.negotiation_results[task_id]
        
        # 构建符合规范的输出格式
        output = {
            "code": 200,
            "msg": "多智能体协商完成",
            "data": {
                "task_id": result["task_id"],
                "requirement_id": result.get("requirement_id", ""),
                "city_name": result.get("city_name", ""),
                "travel_days": result.get("travel_days", 0),
                "agent_results": result["agent_results"],
                "summary": {
                    "total_agents": len(result["agent_results"]),
                    "successful_agents": sum(
                        1 for r in result["agent_results"].values() 
                        if r["status"] == "success"
                    ),
                    "failed_agents": sum(
                        1 for r in result["agent_results"].values() 
                        if r["status"] == "failed"
                    )
                },
                "timestamp": result.get("timestamp", "")
            }
        }
        
        # 保存到文件
        filename = "negotiation_result.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 协商结果已保存到: {filename}")
        print(f"📊 参与智能体: {output['data']['summary']['total_agents']} 个")
        print(f"✅ 成功: {output['data']['summary']['successful_agents']} 个")
        print(f"❌ 失败: {output['data']['summary']['failed_agents']} 个")
        
        # 同时在控制台输出简要信息
        print("\n" + "="*70)
        print("🤖 多智能体协商结果概览")
        print("="*70)
        
        for sub_id, agent_result in result["agent_results"].items():
            status_icon = "✅" if agent_result["status"] == "success" else "❌"
            items_count = len(agent_result["data"]["items"])
            print(f"\n{status_icon} 子任务: {sub_id}")
            print(f"   状态: {agent_result['status']}")
            print(f"   返回数据项数: {items_count}")
            
            # 显示前2条数据的简要信息
            if items_count > 0:
                print(f"   数据预览:")
                for i, item in enumerate(agent_result["data"]["items"][:2]):
                    if isinstance(item, dict):
                        name = item.get("name", item.get("location", "未知"))
                        print(f"     {i+1}. {name}")
        
        print("="*70)
    
    def _organize_by_time_slots(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        按时间槽组织行程数据
        
        Args:
            results: 各子任务的结果字典 {sub_id: {status, items, metadata, error_message}}
            
        Returns:
            按天和时间槽组织的行程结构
        """
        organized = {
            "daily_schedule": [],
            "summary": {
                "total_attractions": 0,
                "total_hotels": 0,
                "total_restaurants": 0,
                "over_budget_items": []
            }
        }
        
        # 按类型分组
        attractions = []
        hotels = []
        restaurants = []
        routes = []
        weather = []
        
        for sub_id, result in results.items():
            if result["status"] == "failed":
                continue
            
            items = result.get("items", [])
            metadata = result.get("metadata", {})
            
            # 检查是否预算超标
            if metadata.get("over_budget"):
                organized["summary"]["over_budget_items"].append({
                    "sub_id": sub_id,
                    "count": metadata.get("over_budget_count", 0)
                })
            
            # 根据 sub_id 判断类型
            if sub_id == "weather":
                weather.extend(items)
            elif sub_id == "hotel":
                hotels.extend(items)
                organized["summary"]["total_hotels"] += len(items)
            elif sub_id == "restaurant":
                restaurants.extend(items)
                organized["summary"]["total_restaurants"] += len(items)
            elif sub_id == "route":
                routes.extend(items)
            else:
                # 默认为景点
                attractions.extend(items)
                organized["summary"]["total_attractions"] += len(items)
        
        # 按时间槽组织景点
        time_slots = {"morning": [], "afternoon": [], "evening": []}
        for att in attractions:
            slot = att.get("visit_time_slot", "morning")
            if slot in time_slots:
                time_slots[slot].append(att)
        
        # 构建每日行程（简化版：假设所有景点在一天内）
        day_plan = {
            "day_index": 1,
            "schedule": []
        }
        
        # 上午行程
        if time_slots["morning"]:
            day_plan["schedule"].append({
                "time_slot": "morning",
                "time_range": "09:00-12:00",
                "type": "attraction",
                "items": time_slots["morning"]
            })
        
        # 午餐
        if restaurants:
            day_plan["schedule"].append({
                "time_slot": "lunch",
                "time_range": "12:00-13:30",
                "type": "meal",
                "items": restaurants[:1]  # 只取第一个餐厅
            })
        
        # 下午行程
        if time_slots["afternoon"]:
            day_plan["schedule"].append({
                "time_slot": "afternoon",
                "time_range": "14:00-17:00",
                "type": "attraction",
                "items": time_slots["afternoon"]
            })
        
        # 晚餐
        if len(restaurants) > 1:
            day_plan["schedule"].append({
                "time_slot": "dinner",
                "time_range": "18:00-19:30",
                "type": "meal",
                "items": restaurants[1:2]
            })
        
        # 晚上行程
        if time_slots["evening"]:
            day_plan["schedule"].append({
                "time_slot": "evening",
                "time_range": "20:00-21:30",
                "type": "attraction",
                "items": time_slots["evening"]
            })
        
        # 住宿信息
        if hotels:
            day_plan["accommodation"] = hotels[0]
        
        # 路线信息
        if routes:
            day_plan["routes"] = routes
        
        # 天气信息
        if weather:
            day_plan["weather"] = weather[0]
        
        organized["daily_schedule"].append(day_plan)
        
        return organized