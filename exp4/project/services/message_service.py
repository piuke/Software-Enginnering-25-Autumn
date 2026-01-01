"""
Message Service - 消息服务层
处理消息相关的业务逻辑
"""

from typing import Optional, List, Dict
from models.message import Message, MessageType
from utils.exceptions import UserNotFoundError, PermissionDeniedError
from config.settings import MESSAGE_CONFIG
from config.i18n import t
from utils.helpers import Helper
from datetime import datetime


class MessageService:
    """
    消息服务类
    提供消息发送、接收、查看等功能
    """
    
    def __init__(self, db_manager):
        """
        初始化消息服务
        
        Args:
            db_manager: 数据库管理器实例
        """
        self.db = db_manager
    
    def send_message(self, sender_id: int, receiver_id: int, 
                    content: str, msg_type: str = "text") -> Optional[int]:
        """
        发送消息
        
        Args:
            sender_id: 发送者ID
            receiver_id: 接收者ID
            content: 消息内容
            msg_type: 消息类型(text/voice/image/emoji)
            
        Returns:
            Optional[int]: 成功返回消息ID,失败返回None
        """
        # 1. 验证用户是否存在
        users = self.db.execute_query(
            "SELECT user_id FROM users WHERE user_id IN (?, ?)",
            (sender_id, receiver_id)
        )
        if len(users) != 2:
            # 判断哪个用户不存在
            existing_ids = {u['user_id'] for u in users}
            if sender_id not in existing_ids:
                raise UserNotFoundError(str(sender_id))
            if receiver_id not in existing_ids:
                raise UserNotFoundError(str(receiver_id))
            return None

        # 2. 校验消息类型与内容长度
        supported = set(MESSAGE_CONFIG.get('supported_types', ['text']))
        if msg_type not in supported:
            raise ValueError(t('message.unsupported_type', type=msg_type))

        max_len = int(MESSAGE_CONFIG.get('max_content_length', 1000))
        if content is None:
            content = ''
        content = content.strip()
        if not content:
            raise ValueError(t('message.empty_content'))
        if len(content) > max_len:
            raise ValueError(t('message.too_long', max=max_len))

        # 3. 保存到数据库
        query = (
            "INSERT INTO messages (sender_id, receiver_id, content, msg_type, status) "
            "VALUES (?, ?, ?, ?, 'sent')"
        )
        msg_id = self.db.execute_insert(query, (sender_id, receiver_id, content, msg_type))
        return msg_id
    
    def get_message_by_id(self, msg_id: int) -> Optional[Message]:
        """
        根据ID获取消息
        
        Args:
            msg_id: 消息ID
            
        Returns:
            Optional[Message]: 消息对象
        """
        rows = self.db.execute_query(
            "SELECT * FROM messages WHERE msg_id = ?",
            (msg_id,)
        )
        if not rows:
            return None
        row = rows[0]
        msg = Message(row['sender_id'], row['receiver_id'], row['content'], row['msg_type'])
        msg.msg_id = row['msg_id']
        # created_at 格式化
        created = row.get('created_at')
        if isinstance(created, str):
            try:
                msg.created_at = Helper.parse_datetime(created)
            except Exception:
                pass
        # 状态
        try:
            from models.message import MessageStatus
            msg.status = MessageStatus(row['status'])
        except Exception:
            pass
        # read_at
        read_at = row.get('read_at')
        if read_at:
            try:
                msg.read_at = Helper.parse_datetime(read_at) if isinstance(read_at, str) else read_at
            except Exception:
                pass
        return msg
    
    def get_conversation(self, user_id1: int, user_id2: int,
                        limit: int = 50, offset: int = 0) -> List[Dict]:
        """
        获取两个用户之间的对话记录
        
        Args:
            user_id1: 用户1的ID
            user_id2: 用户2的ID
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            List[Dict]: 消息列表
        """
        query = (
            "SELECT * FROM messages "
            "WHERE (sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?) "
            "ORDER BY created_at ASC LIMIT ? OFFSET ?"
        )
        rows = self.db.execute_query(query, (user_id1, user_id2, user_id2, user_id1, limit, offset))
        return rows
    
    def get_user_messages(self, user_id: int, limit: int = 20) -> List[Dict]:
        """
        获取用户的所有消息(最近联系人)
        
        Args:
            user_id: 用户ID
            limit: 返回数量限制
            
        Returns:
            List[Dict]: 消息列表
        """
        # 拉取用户相关的较多消息后在内存中按对方用户聚合，取每个会话的最新一条
        rows = self.db.execute_query(
            "SELECT * FROM messages WHERE sender_id=? OR receiver_id=? ORDER BY created_at DESC LIMIT 1000",
            (user_id, user_id)
        )
        latest_by_peer: Dict[int, Dict] = {}
        for row in rows:
            peer = row['receiver_id'] if row['sender_id'] == user_id else row['sender_id']
            if peer not in latest_by_peer:
                latest_by_peer[peer] = row
            if len(latest_by_peer) >= limit:
                break
        # 返回按时间降序
        result = sorted(latest_by_peer.values(), key=lambda r: r['created_at'], reverse=True)
        return result[:limit]
    
    def mark_as_read(self, msg_id: int, user_id: int) -> bool:
        """
        标记消息为已读
        
        Args:
            msg_id: 消息ID
            user_id: 用户ID(验证权限)
            
        Returns:
            bool: 标记是否成功
        """
        # 只允许接收者标记为已读
        affected = self.db.execute_update(
            "UPDATE messages SET status='read', read_at=CURRENT_TIMESTAMP WHERE msg_id=? AND receiver_id=?",
            (msg_id, user_id)
        )
        return affected > 0
    
    def mark_conversation_as_read(self, user_id: int, 
                                  other_user_id: int) -> bool:
        """
        标记与某用户的所有对话为已读
        
        Args:
            user_id: 当前用户ID
            other_user_id: 对方用户ID
            
        Returns:
            bool: 标记是否成功
        """
        affected = self.db.execute_update(
            "UPDATE messages SET status='read', read_at=CURRENT_TIMESTAMP "
            "WHERE receiver_id=? AND sender_id=? AND status <> 'read'",
            (user_id, other_user_id)
        )
        return affected > 0
    
    def delete_message(self, msg_id: int, user_id: int) -> bool:
        """
        删除消息
        
        Args:
            msg_id: 消息ID
            user_id: 用户ID(验证权限)
            
        Returns:
            bool: 删除是否成功
        """
        # 允许发送者或接收者删除
        affected = self.db.execute_delete(
            "DELETE FROM messages WHERE msg_id=? AND (sender_id=? OR receiver_id=?)",
            (msg_id, user_id, user_id)
        )
        return affected > 0
    
    def get_unread_count(self, user_id: int) -> int:
        """
        获取用户的未读消息数量
        
        Args:
            user_id: 用户ID
            
        Returns:
            int: 未读消息数量
        """
        rows = self.db.execute_query(
            "SELECT COUNT(*) AS cnt FROM messages WHERE receiver_id=? AND status <> 'read'",
            (user_id,)
        )
        return int(rows[0]['cnt']) if rows else 0
    
    def search_messages(self, user_id: int, keyword: str, 
                       limit: int = 20) -> List[Dict]:
        """
        搜索消息
        
        Args:
            user_id: 用户ID
            keyword: 搜索关键词
            limit: 返回数量限制
            
        Returns:
            List[Dict]: 消息列表
        """
        keyword = (keyword or '').strip()
        if not keyword:
            return []
        rows = self.db.execute_query(
            "SELECT * FROM messages WHERE (sender_id=? OR receiver_id=?) AND content LIKE ? "
            "ORDER BY created_at DESC LIMIT ?",
            (user_id, user_id, f"%{keyword}%", limit)
        )
        return rows
