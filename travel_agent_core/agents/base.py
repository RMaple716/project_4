import asyncio
from abc import ABC, abstractmethod
from typing import Optional

# 假设 core.message 中定义了 Message
from core.message import Message


class BaseAgent(ABC):
    """所有智能体的抽象基类，自带消息循环"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.mailbox: asyncio.Queue = asyncio.Queue()
        self.bus = None          # 消息总线，由外部注入
        self._running = False
        self._task: Optional[asyncio.Task] = None

    def set_bus(self, bus):
        """注入消息总线（需在启动前调用）"""
        self.bus = bus

    async def start(self):
        """启动智能体的消息处理循环"""
        if not self.bus:
            raise RuntimeError(f"Agent {self.agent_id}: 消息总线未设置，请先调用 set_bus()")
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        print(f"[{self.agent_id}] 已启动")

    async def stop(self):
        """优雅停止智能体"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        print(f"[{self.agent_id}] 已停止")

    async def _run_loop(self):
        """不断从信箱中取出消息并处理"""
        while self._running:
            try:
                # 使用 wait_for 避免永久阻塞，便于检查 _running 标志
                msg = await asyncio.wait_for(self.mailbox.get(), timeout=0.5)
                await self.handle_message(msg)
                self.mailbox.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"[{self.agent_id}] 处理消息时出错: {e}")

    async def send_message(self, msg: Message):
        """通过总线发送一条消息"""
        msg.sender = self.agent_id
        assert self.bus is not None
        await self.bus.route_message(msg)

    @abstractmethod
    async def handle_message(self, msg: Message):
        """处理接收到的消息，子类必须实现"""
        ...