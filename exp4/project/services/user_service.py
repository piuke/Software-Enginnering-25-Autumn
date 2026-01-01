"""
User Service - 用户服务层
处理用户相关的业务逻辑
"""

from typing import Optional, List, Dict
from models.user import User
from utils.exceptions import (
    InvalidUsernameError,
    InvalidEmailError,
    InvalidPasswordError,
    UserAlreadyExistsError,
    UserNotFoundError,
    AuthenticationError
)


class UserService:
    """
    用户服务类
    提供用户注册、登录、认证、社交等功能
    """
    
    def __init__(self, db_manager):
        """
        初始化用户服务
        
        Args:
            db_manager: 数据库管理器实例
        """
        self.db = db_manager
    
    def register(self, username: str, password: str, email: str,
                is_seller: bool = False, shop_name: str = None) -> int:
        """
        用户注册
        
        Args:
            username: 用户名
            password: 密码
            email: 邮箱
            is_seller: 是否注册为卖家
            shop_name: 店铺名称(卖家必填)
            
        Returns:
            int: 成功返回用户ID
            
        Raises:
            InvalidUsernameError: 用户名格式不正确
            InvalidEmailError: 邮箱格式不正确
            InvalidPasswordError: 密码不符合要求
            UserAlreadyExistsError: 用户名或邮箱已被注册
        """
        from utils.validators import Validator
        from utils.helpers import Helper
        
        # 验证用户名
        if not Validator.validate_username(username):
            raise InvalidUsernameError(username)
        
        # 验证邮箱
        if not Validator.validate_email(email):
            raise InvalidEmailError(email)
        
        # 验证密码
        is_valid_pwd, err = Validator.validate_password(password)
        if not is_valid_pwd:
            raise InvalidPasswordError(err)
        
        # 检查用户是否已存在
        existing_user = self.db.execute_query(
            "SELECT user_id FROM users WHERE username=? OR email=?",
            (username, email)
        )
        if existing_user:
            raise UserAlreadyExistsError(username, email)
        
        # encrypt password
        pwd = Helper.hash_password(password)
        
        # 设置用户角色和店铺信息
        role = 'seller' if is_seller else 'user'
        if is_seller and shop_name:
            user_id = self.db.execute_insert(
                "INSERT INTO users (username, email, password, role, shop_name) VALUES (?, ?, ?, ?, ?)",
                (username, email, pwd, role, shop_name)
            )
        else:
            user_id = self.db.execute_insert(
                "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                (username, email, pwd, role)
            )

        return user_id

    def login(self, username: str, password: str) -> Dict:
        """
        用户登录
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            Dict: 成功返回用户信息
            
        Raises:
            UserNotFoundError: 用户不存在
            AuthenticationError: 密码错误
        """
        # 查询用户
        users = self.db.execute_query(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )
        if not users:
            raise UserNotFoundError(username)
        
        user = users[0]  # execute_query 返回列表，取第一个元素

        # 验证密码
        from utils.helpers import Helper
        from config.i18n import t
        if not Helper.verify_password(password, user['password']):
            raise AuthenticationError(t('user.password_wrong'))

        return user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        根据ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[User]: 用户对象
        """
        from models.user import User

        users = self.db.execute_query(
            "SELECT * FROM users WHERE user_id=?",
            (user_id,)
        )
        if not users:
            return None

        user_data = users[0]
        return User(user_data['username'], user_data['password'], user_data['email'])

    def update_profile(self, user_id: int, profile_data: dict) -> bool:
        """
        更新用户资料
        
        Args:
            user_id: 用户ID
            profile_data: 资料数据
            
        Returns:
            bool: 更新是否成功
        """
        # TODO: 实现更新资料逻辑
        pass
    
    def verify_identity(self, user_id: int, 
                       verification_data: dict) -> bool:
        """
        实名认证
        
        Args:
            user_id: 用户ID
            verification_data: 认证信息
            
        Returns:
            bool: 认证是否成功
        """
        # TODO: 实现实名认证逻辑
        pass
    
    def follow_user(self, user_id: int, target_user_id: int) -> bool:
        """
        关注用户
        
        Args:
            user_id: 当前用户ID
            target_user_id: 目标用户ID
            
        Returns:
            bool: 关注是否成功
        """
        # TODO: 实现关注逻辑
        pass
    
    def unfollow_user(self, user_id: int, target_user_id: int) -> bool:
        """
        取消关注
        
        Args:
            user_id: 当前用户ID
            target_user_id: 目标用户ID
            
        Returns:
            bool: 取消关注是否成功
        """
        # TODO: 实现取消关注逻辑
        pass
    
    def get_followers(self, user_id: int) -> List[Dict]:
        """
        获取粉丝列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[Dict]: 粉丝列表
        """
        # TODO: 实现获取粉丝列表逻辑
        pass
    
    def get_following(self, user_id: int) -> List[Dict]:
        """
        获取关注列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[Dict]: 关注列表
        """
        # TODO: 实现获取关注列表逻辑
        pass
    
    def search_users(self, keyword: str, limit: int = 20) -> List[Dict]:
        """
        搜索用户
        
        Args:
            keyword: 搜索关键词
            limit: 返回数量限制
            
        Returns:
            List[Dict]: 用户列表
        """
        # TODO: 实现搜索用户逻辑
        pass
