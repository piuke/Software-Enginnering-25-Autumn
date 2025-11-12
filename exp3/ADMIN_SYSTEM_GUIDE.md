# 管理员系统使用指南

## 用户角色

| 角色 | 权限 |
|------|------|
| `user` | 普通用户 |
| `admin` | 下架商品、封禁用户、审核举报 |
| `superadmin` | 所有权限 + 设置用户角色 |

**默认超级管理员**：用户名 `superadmin`，密码 `admin123`（首次运行自动创建）

## API 使用

### 初始化
```python
from database.db_manager import DatabaseManager
from services.admin_service import AdminService

db = DatabaseManager()
admin_service = AdminService(db)
```

### 管理员操作

```python
# 下架商品
admin_service.remove_product(admin_id=1, product_id=123, reason="违规")

# 封禁用户（30天）
admin_service.ban_user(admin_id=1, user_id=456, duration_days=30, reason="违规")

# 解封用户
admin_service.unban_user(admin_id=1, user_id=456)

# 审核举报
admin_service.review_report(admin_id=1, report_id=10, approved=True, result="已处理")

# 查看统计
stats = admin_service.get_statistics(admin_id=1)

# 设置角色（超级管理员专用）
admin_service.set_user_role(admin_id=1, user_id=100, new_role='admin')
```

### 商品删除

```python
from services.product_service import ProductService
product_service = ProductService(db)

# 卖家删除（只能删除自己的）
product_service.delete_product(product_id=123, seller_id=5, is_admin=False)

# 管理员删除（可删除任何商品）
product_service.delete_product(product_id=123, is_admin=True)
```

### 角色检查

```python
from models.user import User

user = User(username="alice", password="pwd", email="a@b.com", role="admin")

if user.is_admin():      # admin 或 superadmin
    print("管理员")
    
if user.is_superadmin(): # 仅 superadmin
    print("超级管理员")
```
