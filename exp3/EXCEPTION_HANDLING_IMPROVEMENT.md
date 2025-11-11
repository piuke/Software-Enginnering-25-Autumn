# 异常处理改进说明

## 改进概述

将 `user_service.py` 中的错误处理方式从返回 `None` 改为抛出异常（raise exception）。

## 改进的好处

### 1. **明确的错误类型**
```python
# 之前: 所有错误都返回 None，无法区分具体原因
if not user_id:
    print("注册失败")  # 不知道是用户名错误还是邮箱错误

# 现在: 不同错误抛出不同异常
try:
    user_id = user_service.register(...)
except InvalidUsernameError as e:
    print(f"用户名格式错误: {e}")
except InvalidEmailError as e:
    print(f"邮箱格式错误: {e}")
except UserAlreadyExistsError as e:
    print(f"用户已存在: {e}")
```

### 2. **强制错误处理**
```python
# 之前: 容易忘记检查 None
user_id = user_service.register(...)
# 忘记检查就继续使用 user_id，可能导致后续错误

# 现在: 必须用 try-except 捕获，否则程序会崩溃
try:
    user_id = user_service.register(...)
    # 只有成功才会执行这里
except Exception as e:
    # 强制处理错误
    print(f"错误: {e}")
```

### 3. **详细的错误信息**
```python
# 之前
print("注册失败")

# 现在
InvalidUsernameError: 无效的用户名: ab
InvalidEmailError: 无效的邮箱: invalid-email
InvalidPasswordError: 密码不符合要求: 密码至少6个字符
UserAlreadyExistsError: 用户名 'test_user' 或邮箱 'test@example.com' 已被注册
```

### 4. **完整的堆栈跟踪**
异常会自动提供调用栈信息，便于调试。

## 创建的异常类

### 用户相关异常
- `InvalidUsernameError` - 无效的用户名
- `InvalidEmailError` - 无效的邮箱
- `InvalidPasswordError` - 无效的密码
- `UserAlreadyExistsError` - 用户已存在
- `UserNotFoundError` - 用户不存在
- `AuthenticationError` - 认证失败（密码错误）

### 其他异常（已定义，待使用）
- `ProductNotFoundError` - 商品不存在
- `InsufficientStockError` - 库存不足
- `OrderNotFoundError` - 订单不存在
- `InvalidOrderStatusError` - 无效的订单状态操作
- `PermissionDeniedError` - 权限不足
- `NotSellerError` - 非卖家用户
- `DatabaseConnectionError` - 数据库连接失败

## 修改的文件

### 1. 新增文件
- `utils/exceptions.py` - 定义所有自定义异常类

### 2. 修改文件
- `services/user_service.py` - 使用异常替代返回 None
- `main.py` - 添加异常捕获和处理

## 使用示例

### 注册
```python
try:
    user_id = user_service.register(
        username='testuser',
        password='password123',
        email='test@example.com',
        is_seller=False
    )
    print(f"✓ 注册成功! 用户ID: {user_id}")
except InvalidUsernameError as e:
    print(f"✗ 用户名格式错误: {e}")
except InvalidEmailError as e:
    print(f"✗ 邮箱格式错误: {e}")
except InvalidPasswordError as e:
    print(f"✗ 密码不符合要求: {e}")
except UserAlreadyExistsError as e:
    print(f"✗ 用户已存在: {e}")
except Exception as e:
    print(f"✗ 未知错误: {e}")
```

### 登录
```python
try:
    user = user_service.login(username='testuser', password='password123')
    print(f"✓ 登录成功! 欢迎 {user['username']}")
except UserNotFoundError as e:
    print(f"✗ 用户不存在: {e}")
except AuthenticationError as e:
    print(f"✗ 密码错误: {e}")
except Exception as e:
    print(f"✗ 登录失败: {e}")
```

## 测试结果

所有测试均通过 ✅

1. ✓ 无效用户名检测
2. ✓ 无效邮箱检测
3. ✓ 密码太短检测
4. ✓ 重复注册拦截
5. ✓ 用户不存在检测
6. ✓ 错误密码拦截
7. ✓ 正常注册和登录流程

## 后续建议

1. 在其他 service 层也使用异常处理（`product_service.py`, `order_service.py` 等）
2. 在 API 层可以统一捕获异常并返回合适的 HTTP 状态码
3. 可以添加日志记录，记录所有异常
4. 考虑添加国际化支持，让错误消息支持多语言
