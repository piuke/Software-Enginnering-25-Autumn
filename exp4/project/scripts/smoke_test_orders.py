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

    buyer_username = 'buyer_test'
    seller_username = 'seller_test'

    # Ensure buyer exists
    rows = db.execute_query("SELECT user_id FROM users WHERE username=?", (buyer_username,))
    if rows:
        buyer_id = rows[0]['user_id']
    else:
        buyer_id = db.execute_insert(
            "INSERT INTO users (username, password, email, role, is_verified) VALUES (?, ?, ?, 'user', 1)",
            (buyer_username, 'pass', 'buyer_test@example.com')
        )

    # Ensure seller user exists
    rows = db.execute_query("SELECT user_id FROM users WHERE username=?", (seller_username,))
    if rows:
        seller_user_id = rows[0]['user_id']
    else:
        seller_user_id = db.execute_insert(
            "INSERT INTO users (username, password, email, role, is_verified) VALUES (?, ?, ?, 'user', 1)",
            (seller_username, 'pass', 'seller_test@example.com')
        )

    # Ensure seller record exists
    rows = db.execute_query("SELECT seller_id FROM sellers WHERE user_id=?", (seller_user_id,))
    if rows:
        seller_id = rows[0]['seller_id']
    else:
        seller_id = db.execute_insert(
            "INSERT INTO sellers (user_id, shop_name, rating, total_sales) VALUES (?, ?, 5.0, 0)",
            (seller_user_id, 'Test Shop')
        )

    # Ensure product exists with stock
    rows = db.execute_query("SELECT product_id, stock FROM products WHERE seller_id=? AND title=?", (seller_id, 'Test Product'))
    if rows:
        product_id = rows[0]['product_id']
        # Reset stock to at least 2
        db.execute_update("UPDATE products SET stock=?, status='available' WHERE product_id=?", (2, product_id))
    else:
        product_id = db.execute_insert(
            """
            INSERT INTO products (seller_id, title, description, price, category, stock, status)
            VALUES (?, 'Test Product', 'Desc', 19.99, 'TestCat', 2, 'available')
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
    shipped = svc.ship_order(order_id, seller_id, 'TRACK-123456')
    print('ship_order:', shipped)

    # Confirm receipt
    received = svc.confirm_receipt(order_id, buyer_id)
    print('confirm_receipt:', received)

    # Fetch order by id
    order_obj = svc.get_order_by_id(order_id)
    print('get_order_by_id.status:', order_obj.status.value if order_obj else None)

    # Stats
    buyer_stats = svc.get_order_statistics(buyer_id, is_seller=False)
    seller_stats = svc.get_order_statistics(seller_id, is_seller=True)
    print('buyer_stats:', buyer_stats)
    print('seller_stats:', seller_stats)


if __name__ == '__main__':
    main()
