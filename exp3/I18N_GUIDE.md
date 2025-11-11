# 多语言 (i18n) 文档

## 快速开始

### 运行程序
```bash
cd exp3
python main.py
```

### 切换语言
在菜单按 **`L`** 键，选择：`1` 中文 / `2` English

---

## 功能特性

- ✅ 双语支持：简体中文 + English
- ✅ 运行时切换，立即生效
- ✅ 88 个翻译键，100% 覆盖所有界面
- ✅ 异常信息自动多语言
- ✅ 支持参数化翻译（如 `{username}`）

---

## 代码使用

### 基础翻译
```python
from config.i18n import t

print(t('user.username'))  # "用户名" 或 "Username"
```

### 带参数
```python
print(t('user.login_success', username='张三'))
# 中文: "✓ 登录成功! 欢迎 张三"
# 英文: "✓ Login successful! Welcome 张三"
```

### 切换语言
```python
from config.i18n import set_language

set_language('zh_CN')  # 中文
set_language('en_US')  # English
```

---

## 常用翻译键

### 通用 (common)
- `common.success` / `failed` / `error`
- `common.yes` / `no` / `exit` / `back`
- `common.please_select` / `invalid_choice`

### 用户 (user)
- `user.username` / `password` / `email`
- `user.register` / `login` / `logout`
- `user.login_success` (需要 username 参数)
- `user.register_success` (需要 user_id 参数)

### 商品 (product)
- `product.browse_products` / `search_products`
- `product.name` / `price` / `stock`

### 订单 (order)
- `order.my_orders` / `create_order`

### 其他
- `favorite.my_favorites` - 我的收藏
- `seller.seller_functions` - 卖家功能
- `message.messages` - 消息
- `system.feature_not_implemented` - 功能待实现

完整列表见 `config/i18n.py` 中的 `TRANSLATIONS` 字典。

---

## 界面效果

**中文**:
```
用户名: FujIsAWa
1. 浏览商品
2. 搜索商品
3. 我的收藏
```

**English**:
```
Username: FujIsAWa
1. Browse Products
2. Search Products
3. My Favorites
```

---

## 添加新语言

### 1. 编辑 `config/i18n.py`

```python
# 添加语言代码
SUPPORTED_LANGUAGES = ['zh_CN', 'en_US', 'ja_JP']

# 添加语言名称
LANGUAGE_NAMES = {'ja_JP': '日本語'}

# 复制并翻译
TRANSLATIONS = {
    'ja_JP': {
        'common': {'success': '成功', ...},
        'user': {'username': 'ユーザー名', ...},
    }
}
```

### 2. 更新 `main.py` 的 `language_menu()`

```python
print("3. 日本語 (Japanese)")

if choice == '3':
    set_language('ja_JP')
```

---

## 架构说明

### 文件结构
- `config/i18n.py` - 核心实现（450 行）
- `utils/exceptions.py` - 异常类支持多语言
- `main.py` - UI 使用多语言
- `test_i18n.py` - 测试脚本

### 翻译数据结构
```
TRANSLATIONS = {
    'zh_CN': {
        'category': {
            'key': '翻译文本'
        }
    },
    'en_US': { ... }
}
```

使用点分隔访问：`t('category.key')`

### 核心类和函数
- `I18n` 类 - 国际化管理器
- `get_i18n()` - 获取全局实例
- `t()` / `translate()` - 翻译函数
- `set_language()` - 切换语言

---

## 测试

运行完整测试：
```bash
python test_i18n.py
```

测试内容：
- ✅ 基础翻译
- ✅ 参数化翻译
- ✅ 异常多语言
- ✅ 完整注册登录流程

---

## 统计信息

| 项目 | 数量 |
|-----|------|
| 翻译键总数 | 88 个 |
| 支持语言 | 2 种 |
| 覆盖率 | 100% |
| 代码行数 | ~1,200 行 |
| 新增文件 | 4 个 |
| 修改文件 | 3 个 |

---

## 最佳实践

### ✅ 推荐
```python
# 使用翻译键
print(t('user.login_success', username=username))

# 异常自动支持多语言
raise InvalidUsernameError(username)
```

### ❌ 避免
```python
# 硬编码字符串
print(f"登录成功! 欢迎 {username}")

# 硬编码异常
raise Exception("用户名格式不正确")
```

---

## 相关文件

- `config/i18n.py` - 多语言核心
- `utils/exceptions.py` - 多语言异常
- `test_i18n.py` - 测试脚本
- `EXCEPTION_HANDLING_IMPROVEMENT.md` - 异常处理文档
