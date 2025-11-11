"""
实现示例: 用户注册功能
这是一个完整的实现示例,展示如何实现用户注册
"""

from typing import Optional
from utils.validators import Validator
from utils.helpers import Helper

def register_example(db_manager, username: str, password: str, email: str,
                    is_seller: bool = False, shop_name: str = None) -> Optional[int]:
    """
    用户注册的完整实现示例
    
    这个示例展示了如何:
    1. 验证输入数据
    2. 检查用户是否已存在
    3. 加密密码
    4. 插入数据库
    5. 处理卖家注册
    """
    
    # Step 1: 验证输入数据
    if not Validator.validate_username(username):
        print("用户名格式错误(3-20个字符,字母数字下划线)")
        return None
    
    if not Validator.validate_email(email):
        print("邮箱格式错误")
        return None
    
    is_valid, error_msg = Validator.validate_password(password)
    if not is_valid:
        print(f"密码格式错误: {error_msg}")
        return None
    
    if is_seller and not shop_name:
        print("卖家必须提供店铺名称")
        return None
    
    # Step 2: 检查用户名和邮箱是否已存在
    existing_user = db_manager.execute_query(
        "SELECT user_id FROM users WHERE username = ? OR email = ?",
        (username, email)
    )
    
    if existing_user:
        print("用户名或邮箱已存在")
        return None
    
    # Step 3: 加密密码
    hashed_password = Helper.hash_password(password)
    
    # Step 4: 插入用户表
    user_id = db_manager.execute_insert(
        """INSERT INTO users (username, password, email, is_verified, profile)
           VALUES (?, ?, ?, 0, '{}')""",
        (username, hashed_password, email)
    )
    
    if not user_id:
        print("用户注册失败")
        return None
    
    # Step 5: 如果是卖家,插入卖家表
    if is_seller:
        seller_id = db_manager.execute_insert(
            """INSERT INTO sellers (user_id, shop_name, rating, total_sales)
               VALUES (?, ?, 5.0, 0)""",
            (user_id, shop_name)
        )
        
        if not seller_id:
            print("卖家信息保存失败")
            return None
    
    print(f"注册成功! 用户ID: {user_id}")
    return user_id


# 使用示例:
# from database import DatabaseManager
# db = DatabaseManager()
# user_id = register_example(db, "testuser", "password123", "test@example.com")
