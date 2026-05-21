import asyncio
import json
import time
from typing import Dict, List, Any
from datetime import datetime
from core.message import Message


class ChatStyleVisualizer:
    """
    聊天室风格的协商过程可视化器
    模拟真实的小组讨论场景
    """
    
    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.conflicts: List[Dict[str, Any]] = []
        self.chat_buffer: List[str] = []
        
    def record_event(self, event_type: str, data: Dict[str, Any]):
        """记录事件并生成聊天式输出"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        }
        self.events.append(event)
        
        # 生成聊天室风格的输出
        chat_message = self._generate_chat_message(event_type, data)
        if chat_message:
            self.chat_buffer.append(chat_message)
            print(chat_message)
        
    def _generate_chat_message(self, event_type: str, data: Dict) -> str:
        """将技术事件转换为自然语言对话"""
        
        # 角色头像映射
        avatars = {
            "orchestrator": "🎯",
            "weather_bot": "🌤️",
            "route_bot": "🗺️",
            "hotel_bot": "🏨",
            "food_bot": "🍜",
            "user": "👤"
        }
        
        # 角色名称映射
        names = {
            "orchestrator": "协调者",
            "weather_bot": "天气专家",
            "route_bot": "路线规划师",
            "hotel_bot": "酒店顾问",
            "food_bot": "美食家",
            "user": "用户"
        }
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if event_type == "cfp_sent":
            agent_id = "orchestrator"
            avatar = avatars.get(agent_id, "🤖")
            name = names.get(agent_id, agent_id)
            skill = data.get("skill", "")
            desc = data.get("description", "")
            
            # 翻译成自然语言
            skill_map = {
                "get_forecast_weather": "查询天气预报",
                "search_poi": "搜索地点信息",
                "get_route": "规划路线"
            }
            skill_cn = skill_map.get(skill, skill)
            
            return f"[{timestamp}] {avatar} {name}:\n   📢 \"我需要有人帮忙{skill_cn}：{desc}\""
        
        elif event_type == "bid_received":
            agent_id = data.get("agent_id", "")
            avatar = avatars.get(agent_id, "🤖")
            name = names.get(agent_id, agent_id)
            capabilities = data.get("capabilities", [])
            
            cap_map = {
                "get_forecast_weather": "天气预报查询",
                "search_poi": "地点搜索",
                "get_route": "路线规划"
            }
            # 修复类型问题：确保所有元素都是字符串
            caps_cn = "、".join([str(cap_map.get(c, c)) for c in capabilities])
            
            return f"[{timestamp}] {avatar} {name}:\n   💼 \"我可以胜任！我具备{caps_cn}的能力，申请接下这个任务。\""
        
        elif event_type == "award_sent":
            agent_id = data.get("agent_id", "")
            avatar = avatars.get(agent_id, "🤖")
            name = names.get(agent_id, agent_id)
            sub_id = data.get("sub_id", "")
            
            task_names = {
                "weather": "天气查询任务",
                "hotel": "酒店搜索任务",
                "restaurant": "美食推荐任务",
                "route": "路线规划任务"
            }
            task_name = task_names.get(sub_id, sub_id)
            
            return f"[{timestamp}] 🎯 协调者:\n   ✅ \"好的 @{name}，{task_name}就交给你了！请尽快执行。\""
        
        elif event_type == "task_started":
            agent_id = data.get("agent_id", "")
            avatar = avatars.get(agent_id, "🤖")
            name = names.get(agent_id, agent_id)
            action = data.get("action", "")
            
            action_map = {
                "get_forecast_weather": "正在调用高德天气 API...",
                "search_poi": "正在搜索高德地图 POI...",
                "get_route": "正在规划最优路线..."
            }
            action_desc = action_map.get(action, "正在执行任务...")
            
            return f"[{timestamp}] {avatar} {name}:\n   🚀 {action_desc}"
        
        elif event_type == "task_completed":
            agent_id = data.get("agent_id", "")
            avatar = avatars.get(agent_id, "🤖")
            name = names.get(agent_id, agent_id)
            result_preview = data.get("result_preview", "")
            
            # 提取关键信息
            if "天气" in result_preview or "weather" in result_preview.lower():
                summary = "已获取未来3天天气数据（温度、风力、降水概率）"
            elif "酒店" in result_preview or "hotel" in result_preview.lower():
                summary = "已找到5家高评分酒店（含价格、位置、设施信息）"
            elif "美食" in result_preview or "food" in result_preview.lower() or "restaurant" in result_preview.lower():
                summary = "已推荐8家特色餐厅（含菜系、人均消费、用户评价）"
            elif "路线" in result_preview or "route" in result_preview.lower():
                summary = "已规划3条经典游览路线（含交通方式、预计耗时）"
            else:
                summary = "任务执行成功，数据已返回"
            
            return f"[{timestamp}] {avatar} {name}:\n   ✨ \"{summary}\"\n   📊 结果已提交给协调者汇总。"
        
        elif event_type == "task_failed":
            agent_id = data.get("agent_id", "")
            avatar = avatars.get(agent_id, "🤖")
            name = names.get(agent_id, agent_id)
            error = data.get("error", "未知错误")
            
            return f"[{timestamp}] {avatar} {name}:\n   ❌ \"抱歉，任务执行失败：{error}\"\n   ⚠️ 请协调者重新分配或调整参数。"
        
        elif event_type == "conflict_detected":
            conflict_type = data.get("type", "")
            action = data.get("action", "")
            subtasks = data.get("conflicting_subtasks", [])
            suggestion = data.get("suggestion", "")
            
            task_names = {
                "hotel": "酒店搜索",
                "restaurant": "美食推荐"
            }
            # 修复类型问题：确保所有元素都是字符串
            tasks_cn = "、".join([str(task_names.get(t, t)) for t in subtasks])
            
            return f"[{timestamp}] ⚠️ 系统检测:\n   🔍 发现资源冲突！\n   📋 冲突详情：{tasks_cn}都需要调用同一接口 ({action})\n   💡 建议：{suggestion}"
        
        elif event_type == "plan_generated":
            plan_length = data.get("plan_length", 0)
            
            return f"[{timestamp}] 🎯 协调者:\n   📋 \"所有子任务已完成！正在使用 DeepSeek 生成最终旅行计划...\"\n   📝 计划长度：{plan_length} 字符\n   \n   🎉 旅行计划生成完毕！请查看最终结果。"
        
        return ""
    
    def detect_conflicts(self, task_id: str, subtasks: Dict) -> List[Dict]:
        """检测任务冲突"""
        conflicts = []
        
        # 检测资源冲突
        api_usage: Dict[str, List[str]] = {}
        for sub_id, task_info in subtasks.items():
            action = task_info["action"]
            if action not in api_usage:
                api_usage[action] = []
            api_usage[action].append(sub_id)
        
        for action, sub_ids in api_usage.items():
            if len(sub_ids) > 1:
                conflict = {
                    "type": "resource_conflict",
                    "task_id": task_id,
                    "action": action,
                    "conflicting_subtasks": sub_ids,
                    "severity": "warning",
                    "suggestion": f"建议串行执行或使用缓存避免重复调用 {action}"
                }
                conflicts.append(conflict)
                self.conflicts.append(conflict)
                self.record_event("conflict_detected", conflict)
        
        return conflicts
    
    def generate_summary(self) -> Dict:
        """生成总结报告"""
        summary = {
            "total_events": len(self.events),
            "total_conflicts": len(self.conflicts),
            "event_breakdown": {},
            "agent_performance": {},
            "timeline": []
        }
        
        # 统计事件类型分布
        for event in self.events:
            event_type = event["event_type"]
            summary["event_breakdown"][event_type] = summary["event_breakdown"].get(event_type, 0) + 1
        
        # 统计智能体表现
        for event in self.events:
            data = event["data"]
            if "agent_id" in data:
                agent_id = data["agent_id"]
                if agent_id not in summary["agent_performance"]:
                    summary["agent_performance"][agent_id] = {
                        "bids": 0,
                        "awards": 0,
                        "completed": 0,
                        "failed": 0
                    }
                
                if event["event_type"] == "bid_received":
                    summary["agent_performance"][agent_id]["bids"] += 1
                elif event["event_type"] == "award_sent":
                    summary["agent_performance"][agent_id]["awards"] += 1
                elif event["event_type"] == "task_completed":
                    summary["agent_performance"][agent_id]["completed"] += 1
                elif event["event_type"] == "task_failed":
                    summary["agent_performance"][agent_id]["failed"] += 1
        
        # 生成时间线
        key_events = ["cfp_sent", "bid_received", "award_sent", "task_started", "task_completed"]
        for event in self.events:
            if event["event_type"] in key_events:
                summary["timeline"].append({
                    "timestamp": event["timestamp"],
                    "event_type": event["event_type"],
                    "task_id": event["data"].get("task_id"),
                    "agent_id": event["data"].get("agent_id"),
                    "sub_id": event["data"].get("sub_id")
                })
        
        return summary
    
    def export_to_json(self, filename: str = "negotiation_log.json"):
        """导出日志"""
        log = {
            "events": self.events,
            "conflicts": self.conflicts,
            "summary": self.generate_summary()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 协商日志已保存到: {filename}")
    
    def print_chat_style_summary(self):
        """以聊天室风格打印总结"""
        summary = self.generate_summary()
        
        print("\n" + "="*70)
        print("💬 讨论总结")
        print("="*70)
        
        print(f"\n📊 本次讨论共 {summary['total_events']} 条消息")
        
        if summary['total_conflicts'] > 0:
            print(f"⚠️ 检测到 {summary['total_conflicts']} 个潜在问题")
        
        print(f"\n📈 讨论流程:")
        for event_type, count in summary['event_breakdown'].items():
            emoji_map = {
                "cfp_sent": "📢",
                "bid_received": "💼",
                "award_sent": "✅",
                "task_started": "🚀",
                "task_completed": "✨",
                "conflict_detected": "⚠️",
                "plan_generated": "📋"
            }
            emoji = emoji_map.get(event_type, "📝")
            print(f"   {emoji} {event_type}: {count} 次")
        
        print(f"\n👥 参与者表现:")
        names = {
            "weather_bot": "🌤️ 天气专家",
            "route_bot": "🗺️ 路线规划师",
            "hotel_bot": "🏨 酒店顾问",
            "food_bot": "🍜 美食家"
        }
        for agent_id, stats in summary['agent_performance'].items():
            name = names.get(agent_id, agent_id)
            success_rate = (stats['completed'] / stats['awards'] * 100) if stats['awards'] > 0 else 0
            print(f"   {name}:")
            print(f"     - 投标: {stats['bids']} 次")
            print(f"     - 中标: {stats['awards']} 次")
            print(f"     - 完成: {stats['completed']} 次 (成功率 {success_rate:.0f}%)")
            if stats['failed'] > 0:
                print(f"     - 失败: {stats['failed']} 次 ❌")
        
        print("="*70)


# 全局可视化器实例（聊天室风格）
visualizer = ChatStyleVisualizer()
