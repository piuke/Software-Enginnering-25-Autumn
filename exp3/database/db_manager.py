"""
Database Manager - 数据库管理器
提供数据库连接和基础CRUD操作
"""

import sqlite3
import os
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class DatabaseManager:
    """
    数据库管理类
    使用SQLite作为数据库(可根据需要更换为MySQL/PostgreSQL等)
    """
    
    def __init__(self, db_path: str = "anime_mall.db"):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径
        """
        # 如果是相对路径，将其放在 exp3 目录下
        if not os.path.isabs(db_path):
            # 获取当前文件所在目录（database/），再向上一级到 exp3/
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, db_path)
        
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """
        获取数据库连接(上下文管理器)
        
        Yields:
            sqlite3.Connection: 数据库连接对象
        """
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row  # 使用Row对象,支持按列名访问
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_database(self) -> None:
        """
        初始化数据库表结构
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    role TEXT DEFAULT 'user',
                    is_verified BOOLEAN DEFAULT 0,
                    profile TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 检查是否存在用户，如果不存在则创建超级管理员
            cursor.execute("SELECT COUNT(*) as count FROM users")
            user_count = cursor.fetchone()[0]
            
            if user_count == 0:
                # 创建默认超级管理员账户 (密码使用哈希存储)
                # 为避免循环导入，在函数内部导入Helper
                from utils.helpers import Helper
                pwd_hashed = Helper.hash_password('admin123')
                cursor.execute("""
                    INSERT INTO users (username, password, email, role, is_verified)
                    VALUES (?, ?, ?, ?, ?)
                """, ('superadmin', pwd_hashed, 'admin@animemall.com', 'superadmin', 1))
                print("✓ 已创建默认超级管理员账户 (username: superadmin)")
            else:
                # 如果已经有用户，检查是否存在名为 superadmin 的账户且密码为明文，若是则将其哈希化
                cursor.execute("SELECT password FROM users WHERE username=?", ('superadmin',))
                row = cursor.fetchone()
                if row:
                    stored_pw = row[0]
                    # 简单判断是否已经是sha256 hex字符串
                    def looks_hashed(s: str) -> bool:
                        if not isinstance(s, str):
                            return False
                        s = s.strip().lower()
                        if len(s) != 64:
                            return False
                        try:
                            int(s, 16)
                            return True
                        except ValueError:
                            return False

                    if not looks_hashed(stored_pw):
                        from utils.helpers import Helper
                        new_hashed = Helper.hash_password(stored_pw)
                        cursor.execute("UPDATE users SET password=? WHERE username=?", (new_hashed, 'superadmin'))
                        print("✓ 已将现有 superadmin 密码哈希化")
            
            # 卖家表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sellers (
                    seller_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    shop_name TEXT NOT NULL,
                    rating REAL DEFAULT 5.0,
                    total_sales INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # 商品表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    seller_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL,
                    category TEXT NOT NULL,
                    images TEXT,
                    stock INTEGER DEFAULT 1,
                    status TEXT DEFAULT 'available',
                    auctionable BOOLEAN DEFAULT 0,
                    view_count INTEGER DEFAULT 0,
                    favorite_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
                )
            ''')
            
            # 订单表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    buyer_id INTEGER NOT NULL,
                    seller_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    total_price REAL NOT NULL,
                    status TEXT DEFAULT 'pending',
                    shipping_address TEXT NOT NULL,
                    tracking_number TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    paid_at TIMESTAMP,
                    shipped_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (buyer_id) REFERENCES users(user_id),
                    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id),
                    FOREIGN KEY (product_id) REFERENCES products(product_id)
                )
            ''')
            
            # 拍卖表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS auctions (
                    auction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER UNIQUE NOT NULL,
                    seller_id INTEGER NOT NULL,
                    start_price REAL NOT NULL,
                    current_bid REAL NOT NULL,
                    current_bidder_id INTEGER,
                    bid_increment REAL DEFAULT 1.0,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'active',
                    FOREIGN KEY (product_id) REFERENCES products(product_id),
                    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id),
                    FOREIGN KEY (current_bidder_id) REFERENCES users(user_id)
                )
            ''')
            
            # 出价历史表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bid_history (
                    bid_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    auction_id INTEGER NOT NULL,
                    bidder_id INTEGER NOT NULL,
                    bid_amount REAL NOT NULL,
                    bid_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (auction_id) REFERENCES auctions(auction_id),
                    FOREIGN KEY (bidder_id) REFERENCES users(user_id)
                )
            ''')
            
            # 消息表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    msg_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_id INTEGER NOT NULL,
                    receiver_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    msg_type TEXT DEFAULT 'text',
                    status TEXT DEFAULT 'sent',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    read_at TIMESTAMP,
                    FOREIGN KEY (sender_id) REFERENCES users(user_id),
                    FOREIGN KEY (receiver_id) REFERENCES users(user_id)
                )
            ''')
            
            # 举报表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reports (
                    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reporter_id INTEGER NOT NULL,
                    target_id INTEGER NOT NULL,
                    target_type TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    admin_id INTEGER,
                    result TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reviewed_at TIMESTAMP,
                    FOREIGN KEY (reporter_id) REFERENCES users(user_id),
                    FOREIGN KEY (admin_id) REFERENCES admins(admin_id)
                )
            ''')
            
            # 管理员表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    role TEXT DEFAULT 'admin',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 关注关系表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS follows (
                    follower_id INTEGER NOT NULL,
                    following_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (follower_id, following_id),
                    FOREIGN KEY (follower_id) REFERENCES users(user_id),
                    FOREIGN KEY (following_id) REFERENCES users(user_id)
                )
            ''')
            
            # 收藏表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS favorites (
                    user_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, product_id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (product_id) REFERENCES products(product_id)
                )
            ''')
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """
        执行查询并返回结果
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            List[Dict]: 查询结果列表
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def execute_insert(self, query: str, params: tuple = ()) -> Optional[int]:
        """
        执行插入并返回新记录的ID
        
        Args:
            query: SQL插入语句
            params: 插入参数
            
        Returns:
            Optional[int]: 新记录的ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.lastrowid
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """
        执行更新并返回受影响的行数
        
        Args:
            query: SQL更新语句
            params: 更新参数
            
        Returns:
            int: 受影响的行数
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount
    
    def execute_delete(self, query: str, params: tuple = ()) -> int:
        """
        执行删除并返回受影响的行数
        
        Args:
            query: SQL删除语句
            params: 删除参数
            
        Returns:
            int: 受影响的行数
        """
        return self.execute_update(query, params)
