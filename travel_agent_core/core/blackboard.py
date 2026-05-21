import asyncio
from typing import Any, Dict, Optional


class Blackboard:
    """共享黑板，多个智能体可以读写共享数据"""

    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._lock = asyncio.Lock()   # 保证并发安全

    async def write(self, key: str, value: Any):
        """写入数据"""
        async with self._lock:
            self._data[key] = value

    async def read(self, key: str) -> Optional[Any]:
        """读取数据"""
        async with self._lock:
            return self._data.get(key)

    async def update(self, key: str, updater_func):
        """原子更新：读取-修改-写回"""
        async with self._lock:
            old_val = self._data.get(key)
            new_val = updater_func(old_val)
            self._data[key] = new_val
            return new_val

    async def delete(self, key: str):
        async with self._lock:
            self._data.pop(key, None)