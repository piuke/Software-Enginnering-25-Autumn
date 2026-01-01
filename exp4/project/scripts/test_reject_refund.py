import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
EXP3_ROOT = os.path.dirname(CURRENT_DIR)
if EXP3_ROOT not in sys.path:
    sys.path.insert(0, EXP3_ROOT)

from database.db_manager import DatabaseManager
from services.order_service import OrderService


def main():
    db = DatabaseManager()
    svc = OrderService(db)

    buyer_username = 'buyer_reject_test'
    seller_username = 'seller_reject_test'

    # Ensure buyer exists
    rows = db.execute_query("SELECT user_id FROM users WHERE username=?", (buyer_username,))
    if rows:
        buyer_id = rows[0]['user_id']
    else:
        buyer_id = db.execute_insert(
            "INSERT INTO users (username, password, email, role, is_verified) VALUES (?, ?, ?, 'user', 1)",
            (buyer_username, 'pass', 'buyer_reject@example.com')
        )

    # Ensure seller exists as role
    rows = db.execute_query("SELECT user_id FROM users WHERE username=? AND role='seller'", (seller_username,))
    if rows:
        seller_id = rows[0]['user_id']
    else:
        seller_id = db.execute_insert(
            "INSERT INTO users (username, password, email, role, is_verified, shop_name) VALUES (?, ?, ?, 'seller', 1, ?)",
            (seller_username, 'pass', 'seller_reject@example.com', 'Reject Test Shop')
        )

    # Ensure product exists
    rows = db.execute_query("SELECT product_id FROM products WHERE seller_id=? AND title=?", (seller_id, 'Reject Test Product'))
    if rows:
        product_id = rows[0]['product_id']
        db.execute_update("UPDATE products SET stock=?, status='available' WHERE product_id=?", (2, product_id))
    else:
        product_id = db.execute_insert(
            """
            INSERT INTO products (seller_id, title, description, price, category, stock, status)
            VALUES (?, 'Reject Test Product', 'Desc', 19.99, 'Test', 2, 'available')
            """,
            (seller_id,)
        )

    # Create and pay order
    order_id = svc.create_order(buyer_id, product_id, 1, 'Addr')
    print('create_order:', order_id)
    svc.pay_order(order_id, 'confirm')

    # Request refund and then reject
    ok1 = svc.request_refund(order_id, buyer_id, 'changed mind')
    print('request_refund:', ok1)
    ok2 = svc.reject_refund(order_id, seller_id, 'store policy')
    print('reject_refund:', ok2)

    # Verify status
    order = svc.get_order_by_id(order_id)
    print('order status:', order.status.value)

    # Show service messages for buyer
    print('\n--- Buyer messages ---')
    msgs = db.execute_query("SELECT content FROM messages WHERE receiver_id=? AND content LIKE ? ORDER BY created_at DESC", (buyer_id, f'%订单 #{order_id}%'))
    for m in msgs:
        print('  ', m['content'])


if __name__ == '__main__':
    main()
