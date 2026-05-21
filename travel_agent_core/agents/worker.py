from typing import List, Any
import asyncio
import time
from .base import BaseAgent
from core.message import Message, Bid, AgentResponse
from core.visualizer import visualizer
from .data_transformers import AttractionTransformer, HotelTransformer, FoodTransformer, TransportTransformer


class WorkerAgent(BaseAgent):
    """
    具备特定 API 调用能力的工人智能体
    capabilities: 该工人能执行的动作列表，如 ["get_weather", "search_poi"]
    api_handler: 封装了实际 API 调用的对象（如 WeatherAPI(), AmapAPI()）
    """

    def __init__(self, agent_id: str, capabilities: List[str], api_handler: Any):
        super().__init__(agent_id)
        self.capabilities = capabilities
        self.api = api_handler
        self.is_busy = False      # 简单状态标识，防止同时执行多个任务

    async def handle_message(self, msg: Message):
        if msg.type == "cfp":
            await self._handle_cfp(msg)
        elif msg.type == "award" and msg.recipient == self.agent_id:
            await self._execute_task(msg)

    async def _handle_cfp(self, msg: Message):
        """收到招标公告，若能力匹配且空闲，则提交投标书"""
        required_skill = msg.metadata.get("skill")
        if required_skill in self.capabilities and not self.is_busy:
            # 构造投标书
            bid = Bid(
                agent_id=self.agent_id,
                task_id=msg.metadata["task_id"],
                cost=0.0,              # 可扩展为根据任务复杂度计算
                capabilities=self.capabilities
            )
            bid_msg = Message(
                type="bid",
                recipient=msg.sender,    # 发回给管理者
                content=bid,
                metadata={"task_id": msg.metadata["task_id"]}
            )
            await self.send_message(bid_msg)
            print(f"[{self.agent_id}] 投标：技能 {required_skill}，任务 {msg.metadata['task_id']}")

    async def _execute_task(self, msg: Message):
        """中标后执行具体任务，调用 API 并返回结果"""
        self.is_busy = True
        task_data = msg.content          # 包含 action 和 params
        action = task_data["action"]
        params = task_data["params"]
        task_id = msg.metadata["task_id"]

        print(f"[{self.agent_id}] 开始执行任务：{action}，参数：{params}")
        
        start_time = time.time()
        
        # [新增] 记录任务开始事件
        visualizer.record_event("task_started", {
            "agent_id": self.agent_id,
            "task_id": task_id,
            "sub_id": msg.metadata.get("sub_id"),
            "action": action,
            "params": params
        })

        try:
            # ---- 动态调用对应的 API 方法 ----
            func = getattr(self.api, action, None)
            if not func:
                raise ValueError(f"未找到 API 方法: {action}")

            # 调用 API（支持同步方法，需在线程池中执行）
            raw_result = await asyncio.to_thread(func, **params)
            
            # ✅ 根据 action 类型转换数据为标准格式
            response = self._transform_result(action, params, raw_result, task_id)
            
            # 添加处理时间
            processing_time = int((time.time() - start_time) * 1000)
            response.metadata["processing_time_ms"] = processing_time
            
        except Exception as e:
            error_msg = f"任务执行失败: {str(e)}"
            print(f"[{self.agent_id}] {error_msg}")
            
            # ✅ 创建失败响应
            response = AgentResponse.failed(
                task_id=task_id,
                error_message=error_msg,
                source="api_error"
            )
            response.metadata["processing_time_ms"] = int((time.time() - start_time) * 1000)
            
            # [新增] 记录任务失败事件
            visualizer.record_event("task_failed", {
                "agent_id": self.agent_id,
                "task_id": task_id,
                "error": str(e)
            })

        # ✅ 构造结果消息，使用标准化响应格式
        reply = Message(
            type="task_result",
            recipient=msg.sender,
            content=response.to_dict(),  # 转换为字典格式
            metadata={"task_id": task_id, "sub_id": msg.metadata.get("sub_id")}
        )
        await self.send_message(reply)

        self.is_busy = False
        print(f"[{self.agent_id}] 任务 {task_id} 执行完毕，状态: {response.status}")
    
    def _transform_result(self, action: str, params: dict, raw_result: Any, task_id: str) -> AgentResponse:
        """
        根据 action 类型将原始 API 结果转换为标准格式
        
        Args:
            action: API 动作名称
            params: 请求参数
            raw_result: API 原始返回
            task_id: 任务ID
            
        Returns:
            AgentResponse 标准化响应
        """
        # 检查是否有错误
        if isinstance(raw_result, dict) and "error" in raw_result:
            return AgentResponse.failed(
                task_id=task_id,
                error_message=raw_result["error"],
                source="api_error"
            )
        
        # 根据不同的 action 进行数据转换
        if action == "search_poi":
            return self._transform_poi_search(params, raw_result, task_id)
        elif action == "get_route":
            return self._transform_route(params, raw_result, task_id)
        elif action == "get_current_weather" or action == "get_forecast_weather":
            return self._transform_weather(raw_result, task_id)
        else:
            # 默认：直接包装原始结果
            return AgentResponse.success(
                task_id=task_id,
                items=[raw_result] if not isinstance(raw_result, list) else raw_result,
                source="unknown_api"
            )
    
    def _transform_poi_search(self, params: dict, raw_result: Any, task_id: str) -> AgentResponse:
        """转换 POI 搜索结果（景点/酒店/美食）"""
        pois = raw_result.get("pois", []) if isinstance(raw_result, dict) else []
        
        if not pois:
            return AgentResponse.failed(
                task_id=task_id,
                error_message="未找到任何POI数据",
                source="amap_api"
            )
        
        # 根据关键词判断类型
        keywords = params.get("keywords", "").lower()
        
        if "酒店" in keywords or "住宿" in keywords:
            # 酒店转换
            budget = params.get("budget_per_night")
            budget_float = float(budget) if budget is not None else None
            transformed, over_budget_count = HotelTransformer.transform_list(
                pois, budget_per_night=budget_float, max_count=3
            )
            
            metadata = {
                "source": "amap_api",
                "total_found": len(pois),
                "returned_count": len(transformed)
            }
            
            if over_budget_count > 0:
                metadata["over_budget"] = True
                metadata["over_budget_count"] = over_budget_count
                return AgentResponse.partial(
                    task_id=task_id,
                    items=transformed,
                    error_message=f"{over_budget_count}家酒店超出预算限制",
                    **metadata
                )
            else:
                return AgentResponse.success(task_id=task_id, items=transformed, **metadata)
        
        elif "美食" in keywords or "餐厅" in keywords or "餐饮" in keywords:
            # 美食转换
            budget = params.get("budget_per_person")
            budget_float = float(budget) if budget is not None else None
            meal_type = params.get("meal_type", "lunch")
            transformed, over_budget_count = FoodTransformer.transform_list(
                pois, budget_per_person=budget_float, meal_type=meal_type, max_count=4
            )
            
            metadata = {
                "source": "amap_api",
                "total_found": len(pois),
                "returned_count": len(transformed)
            }
            
            if over_budget_count > 0:
                metadata["over_budget"] = True
                metadata["over_budget_count"] = over_budget_count
                return AgentResponse.partial(
                    task_id=task_id,
                    items=transformed,
                    error_message=f"{over_budget_count}家餐厅超出预算限制",
                    **metadata
                )
            else:
                return AgentResponse.success(task_id=task_id, items=transformed, **metadata)
        
        else:
            # 默认作为景点处理
            preferences = params.get("preferences", [])
            dislikes = params.get("dislikes", [])
            transformed = AttractionTransformer.transform_list(
                pois, preferences=preferences, dislikes=dislikes, max_count=5
            )
            
            return AgentResponse.success(
                task_id=task_id,
                items=transformed,
                source="amap_api",
                total_found=len(pois),
                returned_count=len(transformed)
            )
    
    def _transform_route(self, params: dict, raw_result: Any, task_id: str) -> AgentResponse:
        """转换路线数据"""
        if not raw_result or isinstance(raw_result, dict) and "error" in raw_result:
            return AgentResponse.failed(
                task_id=task_id,
                error_message="路线规划失败",
                source="amap_api"
            )
        
        origin_name = params.get("origin", "起点")
        destination_name = params.get("destination", "终点")
        
        transformed = TransportTransformer.transform_route(
            raw_result, origin_name, destination_name
        )
        
        return AgentResponse.success(
            task_id=task_id,
            items=[transformed],
            source="amap_api"
        )
    
    def _transform_weather(self, raw_result: Any, task_id: str) -> AgentResponse:
        """转换天气数据"""
        if not raw_result or isinstance(raw_result, dict) and "error" in raw_result:
            return AgentResponse.failed(
                task_id=task_id,
                error_message="天气查询失败",
                source="amap_api"
            )
        
        # 天气数据保持原有结构，但包装为标准格式
        return AgentResponse.success(
            task_id=task_id,
            items=[raw_result] if not isinstance(raw_result, list) else raw_result,
            source="amap_api"
        )