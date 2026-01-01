import os
import sys

# Ensure exp3 root is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
EXP3_ROOT = os.path.dirname(CURRENT_DIR)
if EXP3_ROOT not in sys.path:
    sys.path.insert(0, EXP3_ROOT)

from database.db_manager import DatabaseManager
from services.order_service import OrderService


def main():
    db = DatabaseManager()

    buyer_username = 'buyer_refund_test'
    seller_username = 'seller_refund_test'

    # Ensure buyer exists
    rows = db.execute_query("SELECT user_id FROM users WHERE username=?", (buyer_username,))
    if rows:
        buyer_id = rows[0]['user_id']
    else:
        buyer_id = db.execute_insert(
            "INSERT INTO users (username, password, email, role, is_verified) VALUES (?, ?, ?, 'user', 1)",
            (buyer_username, 'pass', 'buyer_refund@example.com')
        )

    # Ensure seller user exists
    rows = db.execute_query("SELECT user_id FROM users WHERE username=? AND role='seller'", (seller_username,))
    if rows:
        seller_id = rows[0]['user_id']
    else:
        seller_id = db.execute_insert(
            "INSERT INTO users (username, password, email, role, is_verified, shop_name) VALUES (?, ?, ?, 'seller', 1, ?)",
            (seller_username, 'pass', 'seller_refund@example.com', 'Refund Test Shop')
        )

    # Ensure product exists with stock
    rows = db.execute_query("SELECT product_id, stock FROM products WHERE seller_id=? AND title=?", (seller_id, 'Refund Test Product'))
    if rows:
        product_id = rows[0]['product_id']
        # Reset stock to at least 2
        db.execute_update("UPDATE products SET stock=?, status='available' WHERE product_id=?", (2, product_id))
    else:
        product_id = db.execute_insert(
            """
            INSERT INTO products (seller_id, title, description, price, category, stock, status)
            VALUES (?, 'Refund Test Product', 'Desc', 29.99, 'TestCat', 2, 'available')
            """,
            (seller_id,)
        )

    svc = OrderService(db)

    # Create order
    order_id = svc.create_order(buyer_id=buyer_id, product_id=product_id, quantity=1, shipping_address='Test Address')
    print('create_order:', order_id)

    # Pay order (buyer confirms => success)
    paid = svc.pay_order(order_id, 'confirm')
    print('pay_order:', paid)

    # Ship order
    shipped = svc.ship_order(order_id, seller_id, 'TRACK-REFUND-123')
    print('ship_order:', shipped)

    # Confirm receipt
    received = svc.confirm_receipt(order_id, buyer_id)
    print('confirm_receipt:', received)

    # Request refund (buyer)
    refund_requested = svc.request_refund(order_id, buyer_id, reason='not satisfied')
    print('request_refund:', refund_requested)

    # Check order status
    order_obj = svc.get_order_by_id(order_id)
    print('order status after request_refund:', order_obj.status.value if order_obj else None)

    # Approve refund (seller)
    refund_approved = svc.approve_refund(order_id, seller_id)
    print('approve_refund:', refund_approved)

    # Check final order status
    order_obj = svc.get_order_by_id(order_id)
    print('order status after approve_refund:', order_obj.status.value if order_obj else None)

    # Check service messages
    print('\n--- Service Messages (buyer side) ---')
    buyer_msgs = db.execute_query("SELECT * FROM messages WHERE receiver_id=? ORDER BY created_at DESC LIMIT 10", (buyer_id,))
    for msg in buyer_msgs:
        print(f"  {msg['content']}")

    print('\n--- Service Messages (seller side) ---')
    # seller_id 现在就是 user_id
    seller_msgs = db.execute_query("SELECT * FROM messages WHERE receiver_id=? ORDER BY created_at DESC LIMIT 10", (seller_id,))
    for msg in seller_msgs:
        print(f"  {msg['content']}")


if __name__ == '__main__':
    main()
