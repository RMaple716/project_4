from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class TaskStatus:
    """任务状态常量"""
    PENDING = "pending"         # 待处理
    ANNOUNCED = "announced"     # 已广播招标
    AWARDED = "awarded"         # 已签约
    COMPLETED = "completed"     # 已完成
    FAILED = "failed"           # 失败


@dataclass
class Message:
    """
    智能体间传递的消息信封。
    - type: 消息类型，如 "cfp", "bid", "award", "task_result", "final_plan" 等
    - sender: 发送者 agent_id
    - recipient: 接收者 agent_id，None 表示广播
    - content: 消息体，可以是字符串、字典等任意类型
    - metadata: 附加信息，如 task_id, sub_id, skill 等
    """
    type: str
    sender: Optional[str] = None
    recipient: Optional[str] = None
    content: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Bid:
    """
    投标书。
    - agent_id: 投标智能体的 ID
    - task_id: 所投任务的 ID
    - cost: 执行代价（可自定义，如金钱、时间等）
    - capabilities: 该智能体拥有的能力列表
    """
    agent_id: str
    task_id: str
    cost: float = 0.0
    capabilities: List[str] = field(default_factory=list)


@dataclass
class AgentResponse:
    """
    智能体统一响应格式（符合多智能体通信数据格式规范 v1.0）
    
    示例：
    {
        "task_id": "subtask_001",
        "status": "success",
        "data": {
            "items": [...]
        },
        "metadata": {
            "processing_time_ms": 150,
            "source": "amap_api",
            "is_mock": false,
            "over_budget": false
        },
        "error_message": null
    }
    """
    task_id: str
    status: str = "success"  # success / failed / partial
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        """转换为字典格式，用于消息传输"""
        return {
            "task_id": self.task_id,
            "status": self.status,
            "data": self.data,
            "metadata": self.metadata,
            "error_message": self.error_message
        }
    
    @classmethod
    def success(cls, task_id: str, items: List[Dict], **metadata_kwargs) -> 'AgentResponse':
        """快速创建成功响应"""
        metadata = {
            "processing_time_ms": 0,
            "source": "unknown",
            "is_mock": False,
            "over_budget": False
        }
        metadata.update(metadata_kwargs)
        return cls(
            task_id=task_id,
            status="success",
            data={"items": items},
            metadata=metadata
        )
    
    @classmethod
    def failed(cls, task_id: str, error_message: str, **metadata_kwargs) -> 'AgentResponse':
        """快速创建失败响应"""
        metadata = {
            "processing_time_ms": 0,
            "source": "unknown"
        }
        metadata.update(metadata_kwargs)
        return cls(
            task_id=task_id,
            status="failed",
            error_message=error_message,
            metadata=metadata
        )
    
    @classmethod
    def partial(cls, task_id: str, items: List[Dict], error_message: str = "", **metadata_kwargs) -> 'AgentResponse':
        """快速创建部分成功响应（如预算超标时）"""
        metadata = {
            "processing_time_ms": 0,
            "source": "unknown",
            "over_budget": True
        }
        metadata.update(metadata_kwargs)
        return cls(
            task_id=task_id,
            status="partial",
            data={"items": items},
            error_message=error_message if error_message else "部分结果超出预算限制",
            metadata=metadata
        )
