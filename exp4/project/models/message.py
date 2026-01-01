"""
Message model - 消息模型
管理用户间的通讯
"""

from typing import Optional
from datetime import datetime
from enum import Enum


class MessageType(Enum):
    """消息类型枚举"""
    TEXT = "text"        # 文字
    VOICE = "voice"      # 语音
    IMAGE = "image"      # 图片
    EMOJI = "emoji"      # 表情包


class MessageStatus(Enum):
    """消息状态枚举"""
    SENT = "sent"            # 已发送
    DELIVERED = "delivered"  # 已送达
    READ = "read"            # 已读


class Message:
    """
    消息类
    
    Attributes:
        msg_id (int): 消息ID
        sender_id (int): 发送者ID
        receiver_id (int): 接收者ID
        content (str): 消息内容
        msg_type (MessageType): 消息类型
        status (MessageStatus): 消息状态
        created_at (datetime): 创建时间
        read_at (datetime): 阅读时间
    """
    
    def __init__(self, sender_id: int, receiver_id: int, content: str,
                 msg_type: str = "text"):
        """
        初始化消息对象
        
        Args:
            sender_id: 发送者ID
            receiver_id: 接收者ID
            content: 消息内容
            msg_type: 消息类型
        """
        self.msg_id: Optional[int] = None
        self.sender_id: int = sender_id
        self.receiver_id: int = receiver_id
        self.content: str = content
        self.msg_type: MessageType = MessageType(msg_type)
        self.status: MessageStatus = MessageStatus.SENT
        self.created_at: datetime = datetime.now()
        self.read_at: Optional[datetime] = None
    
    def send(self) -> bool:
        """
        发送消息
        
        Returns:
            bool: 发送是否成功
        """
        # TODO: 实现发送消息逻辑
        pass
    
    def mark_as_delivered(self) -> bool:
        """
        标记为已送达
        
        Returns:
            bool: 标记是否成功
        """
        # TODO: 实现标记送达逻辑
        pass
    
    def mark_as_read(self) -> bool:
        """
        标记为已读
        
        Returns:
            bool: 标记是否成功
        """
        # TODO: 实现标记已读逻辑
        pass
    
    def delete(self) -> bool:
        """
        删除消息
        
        Returns:
            bool: 删除是否成功
        """
        # TODO: 实现删除消息逻辑
        pass
    
    def to_dict(self) -> dict:
        """
        将消息对象转换为字典
        
        Returns:
            dict: 消息信息字典
        """
        return {
            'msg_id': self.msg_id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'content': self.content,
            'msg_type': self.msg_type.value,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'read_at': self.read_at.isoformat() if self.read_at else None
        }
    
    def __repr__(self) -> str:
        """消息对象的字符串表示"""
        return f"<Message(id={self.msg_id}, from={self.sender_id}, to={self.receiver_id})>"
