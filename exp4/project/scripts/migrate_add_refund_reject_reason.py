"""
数据库迁移脚本：为 orders 表添加 refund_reject_reason 字段
"""

import sqlite3
import os


def migrate_database(db_path: str = "anime_mall.db"):
    """添加 refund_reject_reason 字段到 orders 表"""
    
    # 如果是相对路径，将其放在 exp3 目录下
    if not os.path.isabs(db_path):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, db_path)
    
    print(f"开始数据库迁移: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # 检查字段是否已存在
        cursor.execute("PRAGMA table_info(orders)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'refund_reject_reason' not in columns:
            print("\n添加 refund_reject_reason 字段到 orders 表...")
            cursor.execute("ALTER TABLE orders ADD COLUMN refund_reject_reason TEXT")
            conn.commit()
            print("  ✓ 字段添加成功")
        else:
            print("\n✓ refund_reject_reason 字段已存在，跳过迁移")
        
        # 验证
        cursor.execute("PRAGMA table_info(orders)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"\n当前 orders 表字段: {', '.join(columns)}")
        
        print("\n✅ 数据库迁移完成！")
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    migrate_database()
