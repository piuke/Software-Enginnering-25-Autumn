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

    buyer_username = 'buyer_reject_detail_test'
    seller_username = 'seller_reject_detail_test'

    # Ensure buyer exists
    rows = db.execute_query("SELECT user_id FROM users WHERE username=?", (buyer_username,))
    if rows:
        buyer_id = rows[0]['user_id']
    else:
        buyer_id = db.execute_insert(
            "INSERT INTO users (username, password, email, role, is_verified) VALUES (?, ?, ?, 'user', 1)",
            (buyer_username, 'pass', 'buyer_detail@example.com')
        )

    # Ensure seller exists as role
    rows = db.execute_query("SELECT user_id FROM users WHERE username=? AND role='seller'", (seller_username,))
    if rows:
        seller_id = rows[0]['user_id']
    else:
        seller_id = db.execute_insert(
            "INSERT INTO users (username, password, email, role, is_verified, shop_name) VALUES (?, ?, ?, 'seller', 1, ?)",
            (seller_username, 'pass', 'seller_detail@example.com', 'Reject Detail Test Shop')
        )

    # Ensure product exists
    rows = db.execute_query("SELECT product_id FROM products WHERE seller_id=? AND title=?", (seller_id, 'Reject Detail Product'))
    if rows:
        product_id = rows[0]['product_id']
        db.execute_update("UPDATE products SET stock=?, status='available' WHERE product_id=?", (2, product_id))
    else:
        product_id = db.execute_insert(
            """
            INSERT INTO products (seller_id, title, description, price, category, stock, status)
            VALUES (?, 'Reject Detail Product', 'Desc', 29.99, 'Test', 2, 'available')
            """,
            (seller_id,)
        )

    # Create and pay order
    order_id = svc.create_order(buyer_id, product_id, 1, 'Test Address')
    print(f'✓ Created order #{order_id}')
    
    svc.pay_order(order_id, 'confirm')
    print('✓ Order paid')

    # Request refund
    ok1 = svc.request_refund(order_id, buyer_id, 'Product has defects')
    print(f'✓ Refund requested: {ok1}')
    
    # Reject refund with reason
    reject_reason = 'The product is non-returnable according to our store policy'
    ok2 = svc.reject_refund(order_id, seller_id, reject_reason)
    print(f'✓ Refund rejected: {ok2}')

    # Verify order object has the reject reason
    order_obj = svc.get_order_by_id(order_id)
    print(f'\n📋 Order Details:')
    print(f'   Order ID: {order_obj.order_id}')
    print(f'   Status: {order_obj.status.value}')
    print(f'   Refund Reject Reason: {order_obj.refund_reject_reason}')
    
    # Verify from database directly
    order_row = db.execute_query("SELECT * FROM orders WHERE order_id=?", (order_id,))[0]
    print(f'\n💾 Database Record:')
    print(f'   Order ID: {order_row["order_id"]}')
    print(f'   Status: {order_row["status"]}')
    print(f'   Refund Reject Reason: {order_row["refund_reject_reason"]}')
    
    # Verify messages
    print('\n💬 Service Messages (Buyer):')
    msgs = db.execute_query("SELECT content FROM messages WHERE receiver_id=? AND content LIKE ? ORDER BY created_at DESC", (buyer_id, f'%订单 #{order_id}%'))
    for m in msgs:
        print(f'   {m["content"]}')
    
    if order_obj.refund_reject_reason == reject_reason:
        print('\n✅ Test PASSED - Refund reject reason correctly saved and retrieved!')
    else:
        print(f'\n❌ Test FAILED - Expected: {reject_reason}, Got: {order_obj.refund_reject_reason}')


if __name__ == '__main__':
    main()
