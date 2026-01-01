"""
数据库迁移脚本：移除 sellers 表，将 seller 信息合并到 users 表
"""

import sqlite3
import os


def migrate_database(db_path: str = "anime_mall.db"):
    """执行数据库迁移"""
    
    # 如果是相对路径，将其放在 exp3 目录下
    if not os.path.isabs(db_path):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, db_path)
    
    print(f"开始数据库迁移: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # 1. 添加新字段到 users 表
        print("\n1. 为 users 表添加 seller 相关字段...")
        
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'shop_name' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN shop_name TEXT")
            print("  ✓ 添加 shop_name 字段")
        
        if 'rating' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN rating REAL DEFAULT 5.0")
            print("  ✓ 添加 rating 字段")
        
        if 'total_sales' not in columns:
            cursor.execute("ALTER TABLE users ADD COLUMN total_sales INTEGER DEFAULT 0")
            print("  ✓ 添加 total_sales 字段")
        
        # 2. 迁移 sellers 表数据到 users 表
        print("\n2. 迁移 sellers 表数据到 users 表...")
        cursor.execute("SELECT * FROM sellers")
        sellers = cursor.fetchall()
        
        for seller in sellers:
            seller_id = seller['seller_id']
            user_id = seller['user_id']
            shop_name = seller['shop_name']
            rating = seller['rating']
            total_sales = seller['total_sales']
            
            # 更新对应的 user 记录
            cursor.execute("""
                UPDATE users 
                SET shop_name=?, rating=?, total_sales=?, role='seller'
                WHERE user_id=?
            """, (shop_name, rating, total_sales, user_id))
            print(f"  ✓ 迁移 seller_id={seller_id} (user_id={user_id}) 的数据")
        
        # 3. 创建临时表来重建 products 表（改用 user_id）
        print("\n3. 重建 products 表（seller_id 改为 user_id）...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products_new (
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
                FOREIGN KEY (seller_id) REFERENCES users(user_id)
            )
        """)
        
        # 复制数据，将 old_seller_id 转换为 user_id
        cursor.execute("""
            INSERT INTO products_new 
            SELECT 
                p.product_id,
                s.user_id as seller_id,
                p.title,
                p.description,
                p.price,
                p.category,
                p.images,
                p.stock,
                p.status,
                p.auctionable,
                p.view_count,
                p.favorite_count,
                p.created_at,
                p.updated_at
            FROM products p
            LEFT JOIN sellers s ON p.seller_id = s.seller_id
        """)
        
        cursor.execute("DROP TABLE products")
        cursor.execute("ALTER TABLE products_new RENAME TO products")
        print("  ✓ products 表重建完成")
        
        # 4. 重建 orders 表
        print("\n4. 重建 orders 表（seller_id 改为 user_id）...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders_new (
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
                FOREIGN KEY (seller_id) REFERENCES users(user_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        """)
        
        cursor.execute("""
            INSERT INTO orders_new 
            SELECT 
                o.order_id,
                o.buyer_id,
                s.user_id as seller_id,
                o.product_id,
                o.quantity,
                o.total_price,
                o.status,
                o.shipping_address,
                o.tracking_number,
                o.created_at,
                o.paid_at,
                o.shipped_at,
                o.completed_at
            FROM orders o
            LEFT JOIN sellers s ON o.seller_id = s.seller_id
        """)
        
        cursor.execute("DROP TABLE orders")
        cursor.execute("ALTER TABLE orders_new RENAME TO orders")
        print("  ✓ orders 表重建完成")
        
        # 5. 重建 auctions 表
        print("\n5. 重建 auctions 表（seller_id 改为 user_id）...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auctions_new (
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
                FOREIGN KEY (seller_id) REFERENCES users(user_id),
                FOREIGN KEY (current_bidder_id) REFERENCES users(user_id)
            )
        """)
        
        cursor.execute("""
            INSERT INTO auctions_new 
            SELECT 
                a.auction_id,
                a.product_id,
                s.user_id as seller_id,
                a.start_price,
                a.current_bid,
                a.current_bidder_id,
                a.bid_increment,
                a.start_time,
                a.end_time,
                a.status
            FROM auctions a
            LEFT JOIN sellers s ON a.seller_id = s.seller_id
        """)
        
        cursor.execute("DROP TABLE auctions")
        cursor.execute("ALTER TABLE auctions_new RENAME TO auctions")
        print("  ✓ auctions 表重建完成")
        
        # 6. 删除 sellers 表
        print("\n6. 删除 sellers 表...")
        cursor.execute("DROP TABLE sellers")
        print("  ✓ sellers 表已删除")
        
        conn.commit()
        print("\n✅ 数据库迁移完成！")
        
        # 验证迁移结果
        print("\n验证迁移结果:")
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role='seller'")
        seller_count = cursor.fetchone()[0]
        print(f"  - Seller 用户数: {seller_count}")
        
        cursor.execute("SELECT COUNT(*) as count FROM products")
        product_count = cursor.fetchone()[0]
        print(f"  - 商品数: {product_count}")
        
        cursor.execute("SELECT COUNT(*) as count FROM orders")
        order_count = cursor.fetchone()[0]
        print(f"  - 订单数: {order_count}")
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    migrate_database()
