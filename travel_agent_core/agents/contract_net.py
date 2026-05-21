# agents/contract_net.py - 新建：严格的合同网协议实现

import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class CNPMessage:
    """合同网协议消息"""
    
    def __init__(self, msg_type: str, sender: str, receiver: str, 
                 content: Dict[str, Any], timestamp: Optional[float] = None):
        self.msg_type = msg_type  # CFP/BID/AWARD/REJECT/INFORM
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.timestamp = timestamp or time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.msg_type,
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content,
            "timestamp": self.timestamp,
            "time_str": datetime.fromtimestamp(self.timestamp).strftime("%H:%M:%S")
        }


class NegotiationRecord:
    """协商记录"""
    
    def __init__(self, task_id: str, initiator: str):
        self.task_id = task_id
        self.initiator = initiator
        self.messages: List[CNPMessage] = []
        self.start_time = time.time()
        self.end_time = None
        self.status = "ongoing"  # ongoing/completed/failed
    
    def add_message(self, msg: CNPMessage):
        self.messages.append(msg)
    
    def complete(self, status: str = "completed"):
        self.end_time = time.time()
        self.status = status
    
    def get_summary(self) -> Dict[str, Any]:
        duration = (self.end_time or time.time()) - self.start_time
        return {
            "task_id": self.task_id,
            "initiator": self.initiator,
            "status": self.status,
            "duration_seconds": round(duration, 2),
            "message_count": len(self.messages),
            "messages": [msg.to_dict() for msg in self.messages]
        }


class ContractNetProtocol:
    """
    严格的合同网协议（Contract Net Protocol）实现
    
    协议流程：
    1. CFP (Call For Proposal) - 招标
    2. BID (Proposal) - 投标（可多轮）
    3. EVALUATE - 评标
    4. AWARD/REJECT - 中标/拒绝
    5. INFORM - 执行结果通知
    """
    
    def __init__(self):
        self.negotiations: Dict[str, NegotiationRecord] = {}
        self.active_bids: Dict[str, List[Dict]] = {}  # task_id -> bids
    
    def create_negotiation(self, task_id: str, initiator: str) -> NegotiationRecord:
        """创建新的协商记录"""
        record = NegotiationRecord(task_id, initiator)
        self.negotiations[task_id] = record
        self.active_bids[task_id] = []
        return record
    
    def send_cfp(self, task_id: str, initiator: str, 
                 participants: List[str], task_info: Dict[str, Any]) -> List[CNPMessage]:
        """
        阶段1: 发送招标书（CFP）
        
        参数：
            task_id: 任务ID
            initiator: 发起者
            participants: 参与者列表
            task_info: 任务信息
        
        返回：CFP消息列表
        """
        if task_id not in self.negotiations:
            self.create_negotiation(task_id, initiator)
        
        cfp_messages = []
        for participant in participants:
            msg = CNPMessage(
                msg_type="CFP",
                sender=initiator,
                receiver=participant,
                content={
                    "task_id": task_id,
                    "task_description": task_info.get("description", ""),
                    "requirements": task_info.get("requirements", {}),
                    "deadline": task_info.get("deadline"),
                    "constraints": task_info.get("constraints", {})
                }
            )
            self.negotiations[task_id].add_message(msg)
            cfp_messages.append(msg)
        
        print(f"\n📢 [{task_id}] {initiator} 向 {len(participants)} 个智能体发送招标书(CFP)")
        print(f"   任务描述: {task_info.get('description', 'N/A')}")
        
        return cfp_messages
    
    def submit_bid(self, task_id: str, bidder: str, 
                   bid_info: Dict[str, Any]) -> CNPMessage:
        """
        阶段2: 提交投标书（BID）
        
        参数：
            task_id: 任务ID
            bidder: 投标者
            bid_info: 投标信息（包含能力、成本、时间等）
        
        返回：BID消息
        """
        if task_id not in self.negotiations:
            raise ValueError(f"任务 {task_id} 不存在")
        
        bid = {
            "bidder": bidder,
            "capability_score": bid_info.get("capability_score", 0),
            "estimated_cost": bid_info.get("estimated_cost", 0),
            "estimated_time": bid_info.get("estimated_time", 0),
            "confidence": bid_info.get("confidence", 0.5),
            "rationale": bid_info.get("rationale", ""),
            "timestamp": time.time()
        }
        
        # 添加到活跃投标列表
        self.active_bids[task_id].append(bid)
        
        msg = CNPMessage(
            msg_type="BID",
            sender=bidder,
            receiver=self.negotiations[task_id].initiator,
            content=bid
        )
        
        self.negotiations[task_id].add_message(msg)
        
        print(f"   📝 {bidder} 提交投标书")
        print(f"      能力评分: {bid['capability_score']:.2f}")
        print(f"      预计耗时: {bid['estimated_time']}秒")
        print(f"      置信度: {bid['confidence']:.2f}")
        if bid['rationale']:
            print(f"      理由: {bid['rationale']}")
        
        return msg
    
    def evaluate_bids(self, task_id: str) -> Dict[str, Any]:
        """
        阶段3: 评标
        
        评估标准：
        - 能力评分（权重40%）
        - 置信度（权重30%）
        - 时间成本（权重20%）
        - 经济成本（权重10%）
        
        返回：中标者信息和排名
        """
        if task_id not in self.active_bids:
            return {"error": "没有投标"}
        
        bids = self.active_bids[task_id]
        
        if not bids:
            return {"error": "没有收到投标"}
        
        # 计算综合得分
        scored_bids = []
        for bid in bids:
            # 归一化时间成本（时间越短得分越高）
            max_time = max([b["estimated_time"] for b in bids]) or 1
            time_score = 1 - (bid["estimated_time"] / max_time)
            
            # 归一化经济成本
            max_cost = max([b["estimated_cost"] for b in bids]) or 1
            cost_score = 1 - (bid["estimated_cost"] / max_cost)
            
            # 综合得分
            total_score = (
                bid["capability_score"] * 0.4 +
                bid["confidence"] * 0.3 +
                time_score * 0.2 +
                cost_score * 0.1
            )
            
            scored_bids.append({
                **bid,
                "total_score": total_score,
                "time_score": time_score,
                "cost_score": cost_score
            })
        
        # 按总分排序
        scored_bids.sort(key=lambda x: x["total_score"], reverse=True)
        
        winner = scored_bids[0]
        
        print(f"\n🏆 [{task_id}] 评标结果:")
        for i, bid in enumerate(scored_bids, 1):
            marker = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
            print(f"   {marker} #{i} {bid['bidder']}: 总分{bid['total_score']:.2f} "
                  f"(能力:{bid['capability_score']:.2f}, 置信:{bid['confidence']:.2f})")
        
        return {
            "winner": winner,
            "ranked_bids": scored_bids,
            "total_bidders": len(bids)
        }
    
    def award_contract(self, task_id: str, winner: str) -> CNPMessage:
        """
        阶段4a: 授予合同（AWARD）
        """
        msg = CNPMessage(
            msg_type="AWARD",
            sender=self.negotiations[task_id].initiator,
            receiver=winner,
            content={"task_id": task_id, "message": "恭喜中标！请开始执行任务"}
        )
        
        self.negotiations[task_id].add_message(msg)
        print(f"\n✅ [{task_id}] 合同授予: {winner}")
        
        return msg
    
    def reject_bids(self, task_id: str, rejected_bidders: List[str]) -> List[CNPMessage]:
        """
        阶段4b: 拒绝投标（REJECT）
        """
        messages = []
        for bidder in rejected_bidders:
            msg = CNPMessage(
                msg_type="REJECT",
                sender=self.negotiations[task_id].initiator,
                receiver=bidder,
                content={"task_id": task_id, "message": "感谢参与，本次未中标"}
            )
            self.negotiations[task_id].add_message(msg)
            messages.append(msg)
        
        if rejected_bidders:
            print(f"   ❌ 拒绝投标: {', '.join(rejected_bidders)}")
        
        return messages
    
    def inform_result(self, task_id: str, executor: str, 
                      result: Dict[str, Any]) -> CNPMessage:
        """
        阶段5: 通知执行结果（INFORM）
        """
        msg = CNPMessage(
            msg_type="INFORM",
            sender=executor,
            receiver=self.negotiations[task_id].initiator,
            content={
                "task_id": task_id,
                "status": result.get("status", "completed"),
                "result": result.get("data", {}),
                "execution_time": result.get("execution_time", 0)
            }
        )
        
        self.negotiations[task_id].add_message(msg)
        self.negotiations[task_id].complete("completed")
        
        print(f"\n📨 [{task_id}] {executor} 汇报执行结果")
        print(f"   状态: {result.get('status', 'N/A')}")
        
        return msg
    
    def get_negotiation_visualization(self, task_id: str) -> str:
        """
        生成协商过程的可视化文本
        
        返回：ASCII艺术风格的协商流程图
        """
        if task_id not in self.negotiations:
            return "任务不存在"
        
        record = self.negotiations[task_id]
        summary = record.get_summary()
        
        lines = []
        lines.append("\n" + "="*70)
        lines.append(f"📊 协商过程可视化 - 任务 {task_id}")
        lines.append("="*70)
        lines.append(f"发起者: {record.initiator}")
        lines.append(f"状态: {record.status}")
        lines.append(f"耗时: {summary['duration_seconds']}秒")
        lines.append(f"消息数: {summary['message_count']}")
        lines.append("")
        
        # 绘制时间线
        lines.append("时间线:")
        lines.append("─" * 70)
        
        for msg in record.messages:
            icon = {
                "CFP": "📢",
                "BID": "📝",
                "AWARD": "✅",
                "REJECT": "❌",
                "INFORM": "📨"
            }.get(msg.msg_type, "•")
            
            time_str = msg.to_dict()["time_str"]
            arrow = "→" if msg.msg_type in ["CFP", "AWARD", "REJECT"] else "←"
            
            lines.append(f"  [{time_str}] {icon} {msg.sender} {arrow} {msg.receiver}")
            
            if msg.msg_type == "BID":
                content = msg.content
                lines.append(f"         能力:{content.get('capability_score', 0):.2f} "
                           f"置信:{content.get('confidence', 0):.2f}")
        
        lines.append("─" * 70)
        
        # 统计信息
        bid_count = sum(1 for m in record.messages if m.msg_type == "BID")
        lines.append(f"\n统计:")
        lines.append(f"  • 招标次数: 1")
        lines.append(f"  • 投标数量: {bid_count}")
        lines.append(f"  • 中标者: {self._get_winner(task_id)}")
        
        return "\n".join(lines)
    
    def _get_winner(self, task_id: str) -> str:
        """获取中标者"""
        for msg in reversed(self.negotiations[task_id].messages):
            if msg.msg_type == "AWARD":
                return msg.receiver
        return "未知"
    
    def export_negotiation_log(self, task_id: str) -> Dict[str, Any]:
        """导出完整的协商日志（供前端调用）"""
        if task_id not in self.negotiations:
            return {"error": "任务不存在"}
        
        return {
            "task_id": task_id,
            "negotiation": self.negotiations[task_id].get_summary(),
            "visualization": self.get_negotiation_visualization(task_id)
        }


# 测试
if __name__ == "__main__":
    cnp = ContractNetProtocol()
    
    # 模拟完整协商过程
    task_id = "route_planning_001"
    
    # 1. CFP
    cnp.send_cfp(
        task_id=task_id,
        initiator="orchestrator",
        participants=["route_bot", "weather_bot", "hotel_bot"],
        task_info={
            "description": "规划从天安门到故宫的路线",
            "requirements": {"origin": "天安门", "destination": "故宫"},
            "deadline": 10
        }
    )
    
    # 2. BID（多个智能体投标）
    cnp.submit_bid(task_id, "route_bot", {
        "capability_score": 0.95,
        "estimated_cost": 0,
        "estimated_time": 2,
        "confidence": 0.98,
        "rationale": "我是专业的路线规划智能体"
    })
    
    cnp.submit_bid(task_id, "weather_bot", {
        "capability_score": 0.3,
        "estimated_cost": 0,
        "estimated_time": 1,
        "confidence": 0.2,
        "rationale": "我只能提供天气信息"
    })
    
    # 3. EVALUATE & AWARD
    evaluation = cnp.evaluate_bids(task_id)
    winner = evaluation["winner"]["bidder"]
    cnp.award_contract(task_id, winner)
    
    # 4. INFORM
    cnp.inform_result(task_id, winner, {
        "status": "success",
        "data": {"distance": "1.5km", "duration": "8min"},
        "execution_time": 1.5
    })
    
    # 5. 可视化
    print(cnp.get_negotiation_visualization(task_id))
