"""
Admin model - 管理员模型
管理员权限和操作
"""

from typing import Optional, List
from datetime import datetime


class Admin:
    """
    管理员类
    
    Attributes:
        admin_id (int): 管理员ID
        username (str): 用户名
        password (str): 密码
        email (str): 邮箱
        role (str): 角色(super_admin/admin/moderator)
        permissions (List[str]): 权限列表
        created_at (datetime): 创建时间
    """
    
    def __init__(self, username: str, password: str, email: str, 
                 role: str = "admin"):
        """
        初始化管理员对象
        
        Args:
            username: 用户名
            password: 密码
            email: 邮箱
            role: 角色
        """
        self.admin_id: Optional[int] = None
        self.username: str = username
        self.password: str = password
        self.email: str = email
        self.role: str = role
        self.permissions: List[str] = self._get_default_permissions(role)
        self.created_at: datetime = datetime.now()
    
    def _get_default_permissions(self, role: str) -> List[str]:
        """
        根据角色获取默认权限
        
        Args:
            role: 角色
            
        Returns:
            List[str]: 权限列表
        """
        permissions_map = {
            'super_admin': ['all'],
            'admin': ['review_reports', 'remove_products', 'ban_users', 
                     'manage_categories'],
            'moderator': ['review_reports', 'remove_products']
        }
        return permissions_map.get(role, [])
    
    def review_report(self, report_id: int, approved: bool, 
                     result: str) -> bool:
        """
        审核举报
        
        Args:
            report_id: 举报ID
            approved: 是否通过
            result: 审核结果
            
        Returns:
            bool: 审核是否成功
        """
        # TODO: 实现审核举报逻辑
        pass
    
    def remove_product(self, product_id: int, reason: str) -> bool:
        """
        下架商品
        
        Args:
            product_id: 商品ID
            reason: 下架原因
            
        Returns:
            bool: 下架是否成功
        """
        # TODO: 实现下架商品逻辑
        pass
    
    def ban_user(self, user_id: int, duration_days: int, reason: str) -> bool:
        """
        封禁用户
        
        Args:
            user_id: 用户ID
            duration_days: 封禁天数
            reason: 封禁原因
            
        Returns:
            bool: 封禁是否成功
        """
        # TODO: 实现封禁用户逻辑
        pass
    
    def unban_user(self, user_id: int) -> bool:
        """
        解封用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 解封是否成功
        """
        # TODO: 实现解封用户逻辑
        pass
    
    def get_pending_reports(self) -> List[dict]:
        """
        获取待审核的举报列表
        
        Returns:
            List[dict]: 举报列表
        """
        # TODO: 实现获取待审核举报逻辑
        pass
    
    def has_permission(self, permission: str) -> bool:
        """
        检查是否有指定权限
        
        Args:
            permission: 权限名称
            
        Returns:
            bool: 是否有权限
        """
        return 'all' in self.permissions or permission in self.permissions
    
    def to_dict(self) -> dict:
        """
        将管理员对象转换为字典
        
        Returns:
            dict: 管理员信息字典
        """
        return {
            'admin_id': self.admin_id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'permissions': self.permissions,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self) -> str:
        """管理员对象的字符串表示"""
        return f"<Admin(id={self.admin_id}, username='{self.username}', role='{self.role}')>"
