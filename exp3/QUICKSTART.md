# 快速开始

## 项目结构

```
exp3/
├── main.py           # 主程序
├── models/           # 数据模型 (User, Product, Order, etc.)
├── services/         # 业务逻辑 (UserService, ProductService, etc.)
├── database/         # 数据库管理
└── utils/            # 工具函数
```

## 运行

```bash
cd exp3
python main.py
```

## 数据库

使用 SQLite，文件：`anime_mall.db`（自动创建）
默认超级管理员：`superadmin` / `admin123`

## 核心模块

**Models**: User, Seller, Product, Order, Auction, Message, Report, Admin

**Services**: UserService, ProductService, OrderService, AuctionService, MessageService, ReportService, AdminService

## 实现建议

找 `# TODO:` 注释实现具体逻辑：

1. **用户系统**: register() → login() → get_user_by_id()
2. **商品系统**: create_product() → search_products() → get_product_by_id()
3. **订单系统**: create_order() → pay_order() → get_orders_by_buyer()
4. **管理系统**: 参考 `ADMIN_SYSTEM_GUIDE.md`

## API 示例

参考 `IMPLEMENTATION_GUIDE.md` 查看详细用法

````

## 运行方式

### 方式1: 直接运行 (推荐)

```bash
cd c:\Users\uke-x\Documents\se\exp3
python main.py
```

### 方式2: 作为模块运行

```bash
cd c:\Users\uke-x\Documents\se
python -m exp3.main
```

## 代码统计

- **总代码行数**: 2961 行
- **Python文件数**: 27 个
- **接口方法数**: 60+ 个

## 核心类说明

### 数据模型层 (models/)

| 类名 | 文件 | 说明 |
|------|------|------|
| User | user.py | 用户基类 |
| Seller | seller.py | 卖家类(继承User) |
| Product | product.py | 商品类 |
| Order | order.py | 订单类 |
| Auction | auction.py | 拍卖类 |
| Message | message.py | 消息类 |
| Report | report.py | 举报类 |
| Admin | admin.py | 管理员类 |

### 业务服务层 (services/)

| 服务类 | 文件 | 功能 |
|--------|------|------|
| UserService | user_service.py | 用户注册、登录、认证 |
| ProductService | product_service.py | 商品发布、搜索、收藏 |
| OrderService | order_service.py | 订单创建、支付、发货 |
| AuctionService | auction_service.py | 拍卖创建、竞价 |
| MessageService | message_service.py | 消息通讯 |
| ReportService | report_service.py | 举报审核 |

## 数据库设计

系统使用 SQLite 数据库,包含11张核心表:

1. users - 用户表
2. sellers - 卖家表
3. products - 商品表
4. orders - 订单表
5. auctions - 拍卖表
6. bid_history - 出价历史
7. messages - 消息表
8. reports - 举报表
9. admins - 管理员表
10. follows - 关注关系
11. favorites - 收藏关系

数据库文件会自动创建在项目根目录: `anime_mall.db`

## 如何开始实现功能

所有需要实现的方法都标记了 `# TODO:` 注释。

### 实现示例

找到任意一个 TODO 标记的方法,例如 `services/user_service.py` 中的 `register()`:

```python
def register(self, username: str, password: str, email: str,
            is_seller: bool = False, shop_name: str = None) -> Optional[int]:
    """
    用户注册
    ...
    """
    # TODO: 实现注册逻辑
    # 1. 验证用户名和邮箱是否已存在
    # 2. 密码加密
    # 3. 创建User或Seller对象
    # 4. 保存到数据库
    pass
```

实现步骤:
1. 根据TODO提示编写具体逻辑
2. 使用 `self.db` 操作数据库
3. 使用 `utils/validators.py` 进行数据验证
4. 使用 `utils/helpers.py` 进行密码加密等操作

## 推荐实现顺序

### 阶段1: 用户系统 ⭐⭐⭐
1. `UserService.register()` - 用户注册
2. `UserService.login()` - 用户登录  
3. `UserService.get_user_by_id()` - 获取用户信息

### 阶段2: 商品系统 ⭐⭐⭐
1. `ProductService.create_product()` - 发布商品
2. `ProductService.get_product_by_id()` - 获取商品
3. `ProductService.search_products()` - 搜索商品

### 阶段3: 订单系统 ⭐⭐
1. `OrderService.create_order()` - 创建订单
2. `OrderService.pay_order()` - 支付订单
3. `OrderService.get_orders_by_buyer()` - 查看订单

### 阶段4: 拍卖系统 ⭐
1. `AuctionService.create_auction()` - 创建拍卖
2. `AuctionService.place_bid()` - 出价
3. `AuctionService.end_auction()` - 结束拍卖

## 代码规范

本项目遵循 Python PEP 8 代码规范:

- 类名: `PascalCase`
- 函数/变量: `snake_case`
- 常量: `UPPER_CASE`
- 每行不超过100字符
- 使用类型注解
- 完整的 docstring

### 检查代码风格

```bash
# 安装 pylint
pip install pylint

# 检查代码
pylint models/ services/ database/ utils/ config/ main.py

# 评分应该在 8.0 以上
```

## 测试建议

### 手动测试
运行 `main.py`,通过命令行界面测试各个功能

### 单元测试
可以创建 `tests/` 目录,编写单元测试:

```python
import unittest
from services.user_service import UserService

class TestUserService(unittest.TestCase):
    def test_register(self):
        # 测试注册功能
        pass
```

## Git 管理

项目已配置 `.gitignore`,会自动忽略:
- `__pycache__/`
- `*.db` (数据库文件)
- IDE 配置文件

### 提交代码

```bash
cd c:\Users\uke-x\Documents\se\exp3

# 查看状态
git status

# 添加所有文件
git add .

# 提交
git commit -m "完成exp3代码框架搭建"

# 推送到远程仓库
git push origin main
```

## 常见问题

### Q1: 如何连接数据库?
A: 数据库管理器会自动创建 SQLite 数据库,不需要额外配置

### Q2: 如何添加新功能?
A: 在对应的 Service 类中添加新方法,然后在 main.py 中调用

### Q3: 如何修改数据库结构?
A: 修改 `database/db_manager.py` 中的 `init_database()` 方法

### Q4: 代码行数够吗?
A: 当前框架约3000行,实现具体功能后预计总行数会超过5000行

## 参考文档

- 详细说明: `README.md`
- 项目总结: `PROJECT_SUMMARY.md`
- UML设计: `../exp2/UML/`
- 需求分析: `../exp1/request.md`

## 联系方式

如有问题,请查看项目文档或联系开发者。

---

**提示**: 这是一个完整的代码框架,所有接口和数据结构已定义完成。
您只需要按照 TODO 标记,逐步实现具体的业务逻辑即可!

祝您开发顺利! 🚀
