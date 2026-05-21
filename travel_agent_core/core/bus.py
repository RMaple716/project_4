from __future__ import annotations
import asyncio
from typing import Dict, Optional, Set
from .message import Message
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agents.base import BaseAgent   

class MessageBus:
    """
    消息总线，负责在智能体之间路由消息。
    提供点对点（指定 recipient）和主题广播（通过 metadata 中的 topic 或 type）两种模式。
    """

    def __init__(self):
        # 已注册的智能体：agent_id -> agent_instance (需要有 mailbox 属性)
        self.agents: Dict[str, 'BaseAgent'] = {}
        # 主题订阅：topic -> {agent_id, ...}
        self.subscriptions: Dict[str, Set[str]] = {}

    def register_agent(self, agent: 'BaseAgent'):
        """
        注册一个智能体到总线。
        agent 必须实现以下接口：
          - agent.mailbox: asyncio.Queue   (用于接收消息)
          - agent.agent_id: str            (唯一标识)
        """
        self.agents[agent.agent_id] = agent
        print(f"[MessageBus] 注册智能体: {agent.agent_id}")

    def subscribe(self, agent_id: str, topic: str):
        """订阅某个主题，当该主题的消息广播时，此智能体会收到"""
        if topic not in self.subscriptions:
            self.subscriptions[topic] = set()
        self.subscriptions[topic].add(agent_id)

    def unsubscribe(self, agent_id: str, topic: str):
        """取消订阅"""
        if topic in self.subscriptions:
            self.subscriptions[topic].discard(agent_id)

    async def route_message(self, msg: Message):
        """
        根据消息的目标地址路由消息：
        1. 如果指定了 recipient，则点对点投递到该智能体的信箱。
        2. 如果 recipient 为 None，则视为广播：
           - 优先检查 metadata 中是否有 "topic"，广播给该主题的所有订阅者。
           - 若无 topic，则广播给所有已注册的智能体（慎用）。
        """
        if msg.recipient:
            # 点对点模式
            target = self.agents.get(msg.recipient)
            if target:
                await target.mailbox.put(msg)
            else:
                print(f"[MessageBus] 警告: 接收者 {msg.recipient} 未注册")
        else:
            # 广播模式：先尝试主题广播
            topic = msg.metadata.get("topic")
            if topic and topic in self.subscriptions:
                recipients = self.subscriptions[topic]
            else:
                # 无主题则发送给所有智能体（谨慎使用，避免泛滥）
                recipients = set(self.agents.keys())
                print(f"[MessageBus] 无指定主题，广播给所有 {len(recipients)} 个智能体")

            for agent_id in recipients:
                agent = self.agents.get(agent_id)
                if agent:
                    await agent.mailbox.put(msg)