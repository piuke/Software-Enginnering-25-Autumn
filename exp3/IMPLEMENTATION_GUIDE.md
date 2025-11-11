# 🚀 代码实现路线图

## 📚 第一步: 阅读代码 (建议顺序)

### 1️⃣ 基础层 (15分钟) - 最先阅读

```
config/settings.py          → 系统配置,了解有哪些常量
utils/validators.py         → 数据验证方法
utils/helpers.py           → 工具函数(密码加密等)
```

**要点:**
- 看看有哪些配置项可用
- 了解验证和加密方法的使用方式

---

### 2️⃣ 数据层 (30分钟) - 理解数据结构

```
database/db_manager.py     → 重点看 init_database() 和基础CRUD方法
```

**要点:**
- 11张表的结构
- 主键、外键关系
- `execute_query()`, `execute_insert()` 等方法的使用

```
models/user.py             → 用户基类
models/seller.py           → 卖家类(注意继承关系)
models/product.py          → 商品类(注意枚举类型)
models/order.py            → 订单类
models/auction.py          → 拍卖类
models/message.py          → 消息类
models/report.py           → 举报类
models/admin.py            → 管理员类
```

**阅读技巧:**
- 先看 `__init__()` - 了解对象有哪些属性
- 再看方法签名 - 了解每个方法的输入输出
- 看 `to_dict()` - 了解对象如何序列化

---

### 3️⃣ 业务层 (40分钟) - 理解业务逻辑

```
services/user_service.py      → 最重要! 用户注册登录等
services/product_service.py   → 商品发布搜索等
services/order_service.py     → 订单流程
services/auction_service.py   → 拍卖功能
services/message_service.py   → 消息功能
services/report_service.py    → 举报功能
```

**要点:**
- 每个方法都有详细的 docstring
- TODO 注释给出了实现提示
- 参数和返回值都有类型注解

---

### 4️⃣ 表现层 (15分钟) - 理解用户交互

```
main.py                      → 程序入口和菜单系统
```

**要点:**
- `AnimeShoppingMall` 类如何初始化各个服务
- 菜单系统如何组织
- 如何调用服务层方法

---

## 🎯 第二步: 开始实现 (按优先级)

### 阶段 1: 用户系统 ⭐⭐⭐ (最优先,约150行)

**为什么先做这个?**
- 所有功能都依赖用户系统
- 没有用户就无法测试其他功能
- 相对简单,容易建立信心

#### 1.1 实现用户注册 (约50行)

**文件**: `services/user_service.py`

**方法**: `register()`

**实现步骤:**
```python
def register(self, username: str, password: str, email: str,
            is_seller: bool = False, shop_name: str = None) -> Optional[int]:
    # 1. 导入工具
    from utils.validators import Validator
    from utils.helpers import Helper
    
    # 2. 验证输入
    if not Validator.validate_username(username):
        return None
    if not Validator.validate_email(email):
        return None
    is_valid, error = Validator.validate_password(password)
    if not is_valid:
        return None
    
    # 3. 检查是否存在
    existing = self.db.execute_query(
        "SELECT user_id FROM users WHERE username = ? OR email = ?",
        (username, email)
    )
    if existing:
        return None
    
    # 4. 加密密码
    hashed_pwd = Helper.hash_password(password)
    
    # 5. 插入用户表
    user_id = self.db.execute_insert(
        "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
        (username, hashed_pwd, email)
    )
    
    # 6. 如果是卖家,插入卖家表
    if is_seller and shop_name:
        self.db.execute_insert(
            "INSERT INTO sellers (user_id, shop_name) VALUES (?, ?)",
            (user_id, shop_name)
        )
    
    return user_id
```

**测试方法:**
修改 `main.py` 的 `register_menu()`:
```python
def register_menu(self):
    print("\n--- 用户注册 ---")
    username = input("用户名: ").strip()
    password = input("密码: ").strip()
    email = input("邮箱: ").strip()
    is_seller = input("是否注册为卖家? (y/n): ").strip().lower() == 'y'
    shop_name = None
    if is_seller:
        shop_name = input("店铺名称: ").strip()
    
    user_id = self.user_service.register(username, password, email, is_seller, shop_name)
    if user_id:
        print(f"✅ 注册成功! 用户ID: {user_id}")
    else:
        print("❌ 注册失败,请检查输入")
```

---

#### 1.2 实现用户登录 (约40行)

**方法**: `login()`

**实现步骤:**
```python
def login(self, username: str, password: str) -> Optional[Dict]:
    from utils.helpers import Helper
    
    # 1. 查询用户
    users = self.db.execute_query(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )
    
    if not users:
        return None
    
    user = users[0]
    
    # 2. 验证密码
    if not Helper.verify_password(password, user['password']):
        return None
    
    # 3. 检查是否是卖家
    sellers = self.db.execute_query(
        "SELECT * FROM sellers WHERE user_id = ?",
        (user['user_id'],)
    )
    
    # 4. 返回用户信息
    return {
        'user_id': user['user_id'],
        'username': user['username'],
        'email': user['email'],
        'is_verified': user['is_verified'],
        'is_seller': len(sellers) > 0,
        'seller_id': sellers[0]['seller_id'] if sellers else None
    }
```

**测试:**
```python
def login_menu(self):
    print("\n--- 用户登录 ---")
    username = input("用户名: ").strip()
    password = input("密码: ").strip()
    
    user_info = self.user_service.login(username, password)
    if user_info:
        self.current_user = user_info
        print(f"✅ 登录成功! 欢迎, {user_info['username']}")
    else:
        print("❌ 用户名或密码错误")
```

---

#### 1.3 实现获取用户信息 (约20行)

**方法**: `get_user_by_id()`

```python
def get_user_by_id(self, user_id: int) -> Optional[User]:
    from models.user import User
    
    users = self.db.execute_query(
        "SELECT * FROM users WHERE user_id = ?",
        (user_id,)
    )
    
    if not users:
        return None
    
    user_data = users[0]
    user = User(user_data['username'], '', user_data['email'])
    user.user_id = user_data['user_id']
    user.is_verified = user_data['is_verified']
    
    return user
```

---

### 阶段 2: 商品系统 ⭐⭐⭐ (第二优先,约200行)

#### 2.1 实现商品发布 (约60行)

**文件**: `services/product_service.py`

**方法**: `create_product()`

```python
def create_product(self, seller_id: int, product_data: dict) -> Optional[int]:
    from utils.validators import Validator
    
    # 1. 验证卖家存在
    sellers = self.db.execute_query(
        "SELECT seller_id FROM sellers WHERE seller_id = ?",
        (seller_id,)
    )
    if not sellers:
        return None
    
    # 2. 验证必填字段
    required = ['title', 'description', 'price', 'category']
    for field in required:
        if field not in product_data:
            return None
    
    # 3. 验证价格
    if not Validator.validate_price(product_data['price']):
        return None
    
    # 4. 插入商品
    product_id = self.db.execute_insert(
        """INSERT INTO products (seller_id, title, description, price, category, stock)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (seller_id, product_data['title'], product_data['description'],
         product_data['price'], product_data['category'],
         product_data.get('stock', 1))
    )
    
    return product_id
```

---

#### 2.2 实现商品搜索 (约70行)

**方法**: `search_products()`

```python
def search_products(self, keyword: str = None, category: str = None,
                   min_price: float = None, max_price: float = None,
                   limit: int = 20, offset: int = 0) -> List[Dict]:
    
    # 构建查询
    query = "SELECT * FROM products WHERE status = 'available'"
    params = []
    
    if keyword:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f"%{keyword}%", f"%{keyword}%"])
    
    if category:
        query += " AND category = ?"
        params.append(category)
    
    if min_price:
        query += " AND price >= ?"
        params.append(min_price)
    
    if max_price:
        query += " AND price <= ?"
        params.append(max_price)
    
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    return self.db.execute_query(query, tuple(params))
```

---

#### 2.3 实现商品浏览 (约40行)

**方法**: `get_product_by_id()`, `get_products_by_category()`

```python
def get_product_by_id(self, product_id: int) -> Optional[Product]:
    products = self.db.execute_query(
        "SELECT * FROM products WHERE product_id = ?",
        (product_id,)
    )
    
    if not products:
        return None
    
    # 增加浏览次数
    self.db.execute_update(
        "UPDATE products SET view_count = view_count + 1 WHERE product_id = ?",
        (product_id,)
    )
    
    # 返回商品对象
    from models.product import Product
    p_data = products[0]
    product = Product(p_data['seller_id'], p_data['title'],
                     p_data['description'], p_data['price'],
                     p_data['category'], p_data['stock'])
    product.product_id = p_data['product_id']
    
    return product
```

---

### 阶段 3: 订单系统 ⭐⭐ (第三优先,约150行)

#### 3.1 实现创建订单 (约70行)

**文件**: `services/order_service.py`

**方法**: `create_order()`

```python
def create_order(self, buyer_id: int, product_id: int, quantity: int,
                shipping_address: str) -> Optional[int]:
    
    # 1. 获取商品信息
    products = self.db.execute_query(
        "SELECT * FROM products WHERE product_id = ? AND status = 'available'",
        (product_id,)
    )
    
    if not products:
        return None
    
    product = products[0]
    
    # 2. 检查库存
    if product['stock'] < quantity:
        return None
    
    # 3. 计算总价
    total_price = product['price'] * quantity
    
    # 4. 创建订单
    order_id = self.db.execute_insert(
        """INSERT INTO orders (buyer_id, seller_id, product_id, quantity, 
           total_price, shipping_address, status)
           VALUES (?, ?, ?, ?, ?, ?, 'pending')""",
        (buyer_id, product['seller_id'], product_id, quantity,
         total_price, shipping_address)
    )
    
    # 5. 减少库存
    new_stock = product['stock'] - quantity
    self.db.execute_update(
        "UPDATE products SET stock = ? WHERE product_id = ?",
        (new_stock, product_id)
    )
    
    # 6. 如果库存为0,更新状态
    if new_stock == 0:
        self.db.execute_update(
            "UPDATE products SET status = 'sold_out' WHERE product_id = ?",
            (product_id,)
        )
    
    return order_id
```

---

## 📊 实现进度跟踪

### 核心功能清单

| 功能 | 优先级 | 预计行数 | 状态 |
|------|--------|---------|------|
| **用户注册** | ⭐⭐⭐ | 50 | ⬜ 待实现 |
| **用户登录** | ⭐⭐⭐ | 40 | ⬜ 待实现 |
| **获取用户信息** | ⭐⭐⭐ | 20 | ⬜ 待实现 |
| **商品发布** | ⭐⭐⭐ | 60 | ⬜ 待实现 |
| **商品搜索** | ⭐⭐⭐ | 70 | ⬜ 待实现 |
| **商品详情** | ⭐⭐ | 40 | ⬜ 待实现 |
| **创建订单** | ⭐⭐ | 70 | ⬜ 待实现 |
| **支付订单** | ⭐⭐ | 40 | ⬜ 待实现 |
| **发货** | ⭐⭐ | 30 | ⬜ 待实现 |
| **确认收货** | ⭐⭐ | 30 | ⬜ 待实现 |
| **商品收藏** | ⭐ | 30 | ⬜ 待实现 |
| **创建拍卖** | ⭐ | 50 | ⬜ 待实现 |
| **出价** | ⭐ | 60 | ⬜ 待实现 |
| **发送消息** | ⭐ | 40 | ⬜ 待实现 |
| **提交举报** | ⭐ | 40 | ⬜ 待实现 |

---

## 🎯 本周目标建议

### Day 1-2: 用户系统
- ✅ 实现用户注册
- ✅ 实现用户登录
- ✅ 测试注册登录流程

### Day 3-4: 商品系统
- ✅ 实现商品发布
- ✅ 实现商品搜索和浏览
- ✅ 测试商品功能

### Day 5-6: 订单系统
- ✅ 实现订单创建
- ✅ 实现订单支付流程
- ✅ 测试订单功能

### Day 7: 完善和测试
- ✅ 代码风格检查 (Pylint)
- ✅ 功能测试
- ✅ 文档更新

---

## 💡 实现技巧

### 1. 使用已有的工具类

```python
# ✅ 好的做法
from utils.validators import Validator
from utils.helpers import Helper

if not Validator.validate_email(email):
    return None

hashed_pwd = Helper.hash_password(password)
```

### 2. 使用数据库管理器的方法

```python
# ✅ 好的做法
user_id = self.db.execute_insert(
    "INSERT INTO users (...) VALUES (...)",
    (param1, param2)
)

users = self.db.execute_query(
    "SELECT * FROM users WHERE username = ?",
    (username,)
)
```

### 3. 注意错误处理

```python
# ✅ 好的做法
def some_method(self):
    # 验证输入
    if not valid_input:
        return None
    
    # 检查是否存在
    if not exists:
        return None
    
    # 执行操作
    result = self.db.execute_insert(...)
    
    # 检查结果
    if not result:
        return None
    
    return result
```

### 4. 逐步测试

```python
# 每实现一个功能,立即在 main.py 中测试
# 不要等到全部实现完才测试
```

---

## 🚀 开始实现

### 推荐从这里开始:

1. **打开** `services/user_service.py`
2. **找到** `register()` 方法
3. **参考** `IMPLEMENTATION_EXAMPLE.py` 中的示例
4. **开始编码!**

需要帮助时随时问我! 🎉
