"""
User model - 用户模型
负责管理用户基本信息和认证功能
"""

from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(Enum):
    """用户角色枚举"""
    USER = "user"              # 普通用户
    ADMIN = "admin"            # 管理员
    SUPERADMIN = "superadmin"  # 超级管理员


class User:
    """
    用户基类
    
    Attributes:
        user_id (int): 用户ID
        username (str): 用户名
        password (str): 密码(实际应用中应该加密存储)
        email (str): 邮箱
        role (UserRole): 用户角色
        is_verified (bool): 是否已实名认证
        profile (dict): 用户资料(兴趣、社交属性等)
        following (List[int]): 关注的用户ID列表
        followers (List[int]): 粉丝的用户ID列表
        created_at (datetime): 创建时间
    """
    
    def __init__(self, username: str, password: str, email: str, role: str = 'user'):
        """
        初始化用户对象
        
        Args:
            username: 用户名
            password: 密码
            email: 邮箱
            role: 用户角色 (user/admin/superadmin)
        """
        self.user_id: Optional[int] = None
        self.username: str = username
        self.password: str = password
        self.email: str = email
        self.role: str = role
        self.is_verified: bool = False
        self.profile: dict = {}
        self.following: List[int] = []
        self.followers: List[int] = []
        self.created_at: datetime = datetime.now()
        self.updated_at: datetime = datetime.now()
    
    def is_admin(self) -> bool:
        """
        检查是否是管理员
        
        Returns:
            bool: 是否是管理员或超级管理员
        """
        return self.role in ['admin', 'superadmin']
    
    def is_superadmin(self) -> bool:
        """
        检查是否是超级管理员
        
        Returns:
            bool: 是否是超级管理员
        """
        return self.role == 'superadmin'
    
    def login(self, password: str) -> bool:
        """
        用户登录验证
        
        Args:
            password: 输入的密码
            
        Returns:
            bool: 登录是否成功
        """
        # TODO: 实现登录逻辑,验证密码
        pass
    
    def update_profile(self, profile_data: dict) -> bool:
        """
        更新用户资料
        
        Args:
            profile_data: 包含用户资料的字典
            
        Returns:
            bool: 更新是否成功
        """
        # TODO: 实现用户资料更新逻辑
        pass
    
    def verify_identity(self, verification_data: dict) -> bool:
        """
        实名认证
        
        Args:
            verification_data: 认证信息
            
        Returns:
            bool: 认证是否成功
        """
        # TODO: 实现实名认证逻辑
        pass
    
    def follow_user(self, target_user_id: int) -> bool:
        """
        关注其他用户
        
        Args:
            target_user_id: 目标用户ID
            
        Returns:
            bool: 关注是否成功
        """
        # TODO: 实现关注逻辑
        pass
    
    def unfollow_user(self, target_user_id: int) -> bool:
        """
        取消关注
        
        Args:
            target_user_id: 目标用户ID
            
        Returns:
            bool: 取消关注是否成功
        """
        # TODO: 实现取消关注逻辑
        pass
    
    def send_message(self, receiver_id: int, content: str, 
                    message_type: str = 'text') -> bool:
        """
        发送消息
        
        Args:
            receiver_id: 接收者ID
            content: 消息内容
            message_type: 消息类型(text/voice/image/emoji)
            
        Returns:
            bool: 发送是否成功
        """
        # TODO: 实现发送消息逻辑
        pass
    
    def to_dict(self) -> dict:
        """
        将用户对象转换为字典
        
        Returns:
            dict: 用户信息字典
        """
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_verified': self.is_verified,
            'profile': self.profile,
            'following_count': len(self.following),
            'followers_count': len(self.followers),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self) -> str:
        """用户对象的字符串表示"""
        return f"<User(id={self.user_id}, username='{self.username}')>"
