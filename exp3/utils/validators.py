"""
Validators - 数据验证工具
提供各种数据验证功能
"""

import re
from typing import Optional, Tuple


class Validator:
    """数据验证类"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        验证邮箱格式
        
        Args:
            email: 邮箱地址
            
        Returns:
            bool: 是否有效
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """
        验证用户名格式
        
        Args:
            username: 用户名
            
        Returns:
            bool: 是否有效
        """
        # 用户名: 3-20个字符,字母数字下划线
        pattern = r'^[a-zA-Z0-9_]{3,20}$'
        return bool(re.match(pattern, username))
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, Optional[str]]:
        """
        验证密码强度
        
        Args:
            password: 密码
            
        Returns:
            Tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        if len(password) < 6:
            return False, "密码至少6个字符"
        if len(password) > 20:
            return False, "密码最多20个字符"
        # 可以添加更多密码复杂度要求
        return True, None
    
    @staticmethod
    def validate_price(price: float) -> bool:
        """
        验证价格
        
        Args:
            price: 价格
            
        Returns:
            bool: 是否有效
        """
        return price > 0
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        验证手机号码
        
        Args:
            phone: 手机号码
            
        Returns:
            bool: 是否有效
        """
        pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(pattern, phone))
