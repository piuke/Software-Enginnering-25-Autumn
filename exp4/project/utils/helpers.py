"""
Helpers - 辅助工具函数
提供各种辅助功能
"""

import hashlib
import json
from datetime import datetime
from typing import Any, Dict


class Helper:
    """辅助工具类"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        对密码进行哈希加密
        
        Args:
            password: 明文密码
            
        Returns:
            str: 加密后的密码
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        验证密码
        
        Args:
            password: 明文密码
            hashed_password: 加密后的密码
            
        Returns:
            bool: 密码是否匹配
        """
        return Helper.hash_password(password) == hashed_password
    
    @staticmethod
    def format_datetime(dt: datetime) -> str:
        """
        格式化日期时间
        
        Args:
            dt: 日期时间对象
            
        Returns:
            str: 格式化后的字符串
        """
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def parse_datetime(dt_str: str) -> datetime:
        """
        解析日期时间字符串
        
        Args:
            dt_str: 日期时间字符串
            
        Returns:
            datetime: 日期时间对象
        """
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def dict_to_json(data: Dict) -> str:
        """
        字典转JSON字符串
        
        Args:
            data: 字典数据
            
        Returns:
            str: JSON字符串
        """
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    @staticmethod
    def json_to_dict(json_str: str) -> Dict:
        """
        JSON字符串转字典
        
        Args:
            json_str: JSON字符串
            
        Returns:
            Dict: 字典数据
        """
        return json.loads(json_str)
    
    @staticmethod
    def format_price(price: float) -> str:
        """
        格式化价格显示
        
        Args:
            price: 价格
            
        Returns:
            str: 格式化后的价格字符串
        """
        return f"¥{price:.2f}"
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """
        清理用户输入
        
        Args:
            text: 输入文本
            
        Returns:
            str: 清理后的文本
        """
        # 移除前后空白
        text = text.strip()
        # 可以添加更多清理规则
        return text
