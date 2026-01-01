"""
Configuration file for the Anime Shopping Mall System.
系统配置文件
"""

# 数据库配置
DATABASE_CONFIG = {
    'db_path': 'anime_mall.db',
    'timeout': 30
}

# 系统配置
SYSTEM_CONFIG = {
    'app_name': '二次元网络商场系统',
    'version': '1.0.0',
    'debug': True
}

# 分页配置
PAGINATION_CONFIG = {
    'default_page_size': 20,
    'max_page_size': 100
}

# 商品分类(IP分类)
PRODUCT_CATEGORIES = [
    '原神',
    '明日方舟',
    '崩坏:星穹铁道',
    '蓝色档案',
    'Vtuber',
    '东方Project',
    '舰队Collection',
    'LoveLive!',
    'BanG Dream!',
    'Fate',
    '其他'
]

# 拍卖配置
AUCTION_CONFIG = {
    'min_duration_hours': 1,
    'max_duration_hours': 168,  # 7天
    'default_bid_increment': 1.0
}

# 消息配置
MESSAGE_CONFIG = {
    'max_content_length': 1000,
    'supported_types': ['text', 'voice', 'image', 'emoji']
}

# 安全配置
SECURITY_CONFIG = {
    'password_min_length': 6,
    'password_max_length': 20,
    'max_login_attempts': 5,
    'ban_duration_days': 7
}
