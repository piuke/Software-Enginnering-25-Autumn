"""
Custom Exceptions - 自定义异常类
定义系统中使用的各种异常
"""

from typing import Optional


def _get_i18n():
    """延迟导入 i18n 以避免循环依赖"""
    try:
        from config.i18n import get_i18n
        return get_i18n()
    except ImportError:
        return None


class AnimeShopException(Exception):
    """基础异常类"""
    pass


# ============ 用户相关异常 ============

class UserException(AnimeShopException):
    """用户相关异常基类"""
    pass


class ValidationError(UserException):
    """数据验证失败异常"""
    pass


class InvalidUsernameError(ValidationError):
    """无效的用户名"""
    def __init__(self, username: str = None):
        self.username = username
        i18n = _get_i18n()
        if i18n:
            message = i18n.t('user.invalid_username', username=username or '')
        else:
            message = f"无效的用户名: {username}" if username else "用户名格式不正确"
        super().__init__(message)


class InvalidEmailError(ValidationError):
    """无效的邮箱"""
    def __init__(self, email: str = None):
        self.email = email
        i18n = _get_i18n()
        if i18n:
            message = i18n.t('user.invalid_email', email=email or '')
        else:
            message = f"无效的邮箱: {email}" if email else "邮箱格式不正确"
        super().__init__(message)


class InvalidPasswordError(ValidationError):
    """无效的密码"""
    def __init__(self, reason: str = None):
        self.reason = reason
        i18n = _get_i18n()
        if i18n:
            message = i18n.t('user.invalid_password', reason=reason or '')
        else:
            message = f"密码不符合要求: {reason}" if reason else "密码格式不正确"
        super().__init__(message)


class UserAlreadyExistsError(UserException):
    """用户已存在"""
    def __init__(self, username: str = None, email: str = None):
        self.username = username
        self.email = email
        i18n = _get_i18n()
        if i18n:
            message = i18n.t('user.user_already_exists', username=username or '', email=email or '')
        else:
            if username and email:
                message = f"用户名 '{username}' 或邮箱 '{email}' 已被注册"
            elif username:
                message = f"用户名 '{username}' 已被注册"
            elif email:
                message = f"邮箱 '{email}' 已被注册"
            else:
                message = "用户已存在"
        super().__init__(message)


class UserNotFoundError(UserException):
    """用户不存在"""
    def __init__(self, identifier: str = None):
        self.identifier = identifier
        i18n = _get_i18n()
        if i18n:
            message = i18n.t('user.user_not_found', identifier=identifier or '')
        else:
            message = f"用户不存在: {identifier}" if identifier else "用户不存在"
        super().__init__(message)


class AuthenticationError(UserException):
    """认证失败"""
    def __init__(self, message: Optional[str] = None):
        i18n = _get_i18n()
        if message is None:
            if i18n:
                message = i18n.t('user.authentication_failed')
            else:
                message = "用户名或密码错误"
        super().__init__(message)


# ============ 商品相关异常 ============

class ProductException(AnimeShopException):
    """商品相关异常基类"""
    pass


class ProductNotFoundError(ProductException):
    """商品不存在"""
    def __init__(self, product_id: int = None):
        self.product_id = product_id
        i18n = _get_i18n()
        if i18n:
            message = i18n.t('product.product_not_found', product_id=product_id or '')
        else:
            message = f"商品不存在: {product_id}" if product_id else "商品不存在"
        super().__init__(message)


class InsufficientStockError(ProductException):
    """库存不足"""
    def __init__(self, product_name: str = None, available: int = 0, requested: int = 0):
        self.product_name = product_name
        self.available = available
        self.requested = requested
        i18n = _get_i18n()
        if i18n:
            message = i18n.t('product.insufficient_stock', 
                           product_name=product_name or '', 
                           available=available, 
                           requested=requested)
        else:
            message = f"商品 '{product_name}' 库存不足 (可用: {available}, 需要: {requested})"
        super().__init__(message)


# ============ 订单相关异常 ============

class OrderException(AnimeShopException):
    """订单相关异常基类"""
    pass


class OrderNotFoundError(OrderException):
    """订单不存在"""
    def __init__(self, order_id: int = None):
        self.order_id = order_id
        i18n = _get_i18n()
        if i18n:
            message = i18n.t('order.order_not_found', order_id=order_id or '')
        else:
            message = f"订单不存在: {order_id}" if order_id else "订单不存在"
        super().__init__(message)


class InvalidOrderStatusError(OrderException):
    """无效的订单状态操作"""
    def __init__(self, current_status: str, target_status: str):
        self.current_status = current_status
        self.target_status = target_status
        i18n = _get_i18n()
        if i18n:
            message = i18n.t('order.invalid_order_status', 
                           current_status=current_status, 
                           target_status=target_status)
        else:
            message = f"无法从 '{current_status}' 状态变更到 '{target_status}' 状态"
        super().__init__(message)


# ============ 权限相关异常 ============

class PermissionException(AnimeShopException):
    """权限相关异常基类"""
    pass


class PermissionDeniedError(PermissionException):
    """权限不足"""
    def __init__(self, action: str = None):
        self.action = action
        i18n = _get_i18n()
        if i18n:
            message = i18n.t('permission.permission_denied', action=action or '')
        else:
            message = f"权限不足: {action}" if action else "权限不足"
        super().__init__(message)


class NotSellerError(PermissionException):
    """非卖家用户"""
    def __init__(self):
        i18n = _get_i18n()
        if i18n:
            message = i18n.t('permission.not_seller')
        else:
            message = "该操作仅卖家用户可执行"
        super().__init__(message)


# ============ 数据库相关异常 ============

class DatabaseException(AnimeShopException):
    """数据库相关异常基类"""
    pass


class DatabaseConnectionError(DatabaseException):
    """数据库连接失败"""
    def __init__(self, reason: str = None):
        i18n = _get_i18n()
        if i18n:
            message = i18n.t('system.database_error', reason=reason or '')
        else:
            message = f"数据库连接失败: {reason}" if reason else "数据库连接失败"
        super().__init__(message)
