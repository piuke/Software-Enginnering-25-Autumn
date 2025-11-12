# API 使用指南

## DatabaseManager API

```python
from database.db_manager import DatabaseManager

db = DatabaseManager("anime_mall.db")

# 查询（SELECT）
users = db.execute_query("SELECT * FROM users WHERE role = ?", ("admin",))

# 插入（INSERT）
user_id = db.execute_insert(
    "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
    ("alice", "hashed_pwd", "alice@example.com")
)

# 更新（UPDATE）
affected = db.execute_update(
    "UPDATE users SET email = ? WHERE user_id = ?",
    ("new@email.com", 1)
)

# 删除（DELETE）
affected = db.execute_delete("DELETE FROM users WHERE user_id = ?", (5,))
```

## ProductService API

```python
from services.product_service import ProductService

product_service = ProductService(db)

# 创建商品
product_id = product_service.create_product(
    seller_id=1,
    product_data={
        'title': '初音未来手办',
        'description': '正版授权',
        'price': 299.99,
        'category': 'VOCALOID',
        'stock': 10
    }
)

# 更新商品
product_service.update_product(
    product_id=123,
    product_data={'price': 199.99, 'stock': 5}
)

# 删除商品（卖家）
product_service.delete_product(product_id=123, seller_id=1, is_admin=False)

# 删除商品（管理员）
product_service.delete_product(product_id=123, is_admin=True)
```

## AdminService API

详见 `ADMIN_SYSTEM_GUIDE.md`

## 数据格式

### product_data 格式
```python
product_data = {
    'title': str,              # 必填
    'description': str,         # 必填
    'price': float,            # 必填
    'category': str,           # 必填
    'images': str,             # 可选，JSON字符串 '["url1", "url2"]'
    'stock': int,              # 可选，默认1
    'status': str,             # 可选，默认'available'
    'auctionable': bool        # 可选，默认False
}
```
