"""
Order Service - 订单服务层
处理订单相关的业务逻辑
"""

from typing import Optional, List, Dict
from models.order import Order, OrderStatus
from datetime import datetime


class OrderService:
    """
    订单服务类
    提供订单创建、支付、发货、完成等功能
    """
    
    def __init__(self, db_manager):
        """
        初始化订单服务
        
        Args:
            db_manager: 数据库管理器实例
        """
        self.db = db_manager
    
    def create_order(self, buyer_id: int, product_id: int, quantity: int,
                    shipping_address: str) -> Optional[int]:
        """
        创建订单
        
        Args:
            buyer_id: 买家ID
            product_id: 商品ID
            quantity: 购买数量
            shipping_address: 收货地址
            
        Returns:
            Optional[int]: 成功返回订单ID,失败返回None
        """
        # 1. 查询商品信息
        product_query = "SELECT * FROM products WHERE product_id=? AND status='available'"
        products = self.db.execute_query(product_query, (product_id,))
        if not products:
            return None  # 商品不存在或不可售
        product = products[0]
        if product['stock'] < quantity:
            return None  # 库存不足
        # 2. 计算总价
        total_price = product['price'] * quantity
        seller_id = product['seller_id']
        # 3. 创建订单
        order_insert = """
            INSERT INTO orders (buyer_id, seller_id, product_id, quantity, total_price, status, shipping_address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        order_id = self.db.execute_insert(order_insert, (
            buyer_id, seller_id, product_id, quantity, total_price, OrderStatus.PENDING.value, shipping_address
        ))
        if not order_id:
            return None
        # 4. 减少商品库存
        new_stock = product['stock'] - quantity
        product_update = "UPDATE products SET stock=?, status=? WHERE product_id=?"
        new_status = 'sold_out' if new_stock == 0 else 'available'
        self.db.execute_update(product_update, (new_stock, new_status, product_id))
        # 5. 发送服务消息给卖家
        self._send_service_message(buyer_id, seller_id, 'order.service_order_created', order_id=order_id)
        return order_id
    
    def pay_order(self, order_id: int, payment_method: str) -> bool:
        """
        支付订单
        
        Args:
            order_id: 订单ID
            payment_method: 支付方式
            
        Returns:
            bool: 支付是否成功
        """
        # 1. 查询订单
        order_query = "SELECT * FROM orders WHERE order_id=?"
        orders = self.db.execute_query(order_query, (order_id,))
        if not orders:
            return False  # 订单不存在
        order = orders[0]
        if order['status'] != OrderStatus.PENDING.value:
            return False  # 订单状态异常
        # 2. 支付逻辑（买家确认即支付成功）
        paid_at = datetime.now().isoformat()
        update_query = "UPDATE orders SET status=?, paid_at=? WHERE order_id=?"
        updated = self.db.execute_update(update_query, (OrderStatus.PAID.value, paid_at, order_id))
        if updated > 0:
            # 3. 发送服务消息给卖家
            self._send_service_message(order['buyer_id'], order['seller_id'], 'order.service_order_paid', order_id=order_id)
        return updated > 0
    
    def ship_order(self, order_id: int, seller_id: int,
                  tracking_number: str) -> bool:
        """
        发货
        
        Args:
            order_id: 订单ID
            seller_id: 卖家ID(验证权限)
            tracking_number: 物流单号
            
        Returns:
            bool: 发货是否成功
        """
        # 查询订单
        order_query = "SELECT * FROM orders WHERE order_id=?"
        orders = self.db.execute_query(order_query, (order_id,))
        if not orders:
            return False
        order = orders[0]
        if order['seller_id'] != seller_id:
            return False  # 权限校验
        if order['status'] != OrderStatus.PAID.value:
            return False  # 仅已支付订单可发货
        shipped_at = datetime.now().isoformat()
        update_query = "UPDATE orders SET status=?, tracking_number=?, shipped_at=? WHERE order_id=?"
        updated = self.db.execute_update(update_query, (OrderStatus.SHIPPED.value, tracking_number, shipped_at, order_id))
        if updated > 0:
            # 发送服务消息给买家
            self._send_service_message(seller_id, order['buyer_id'], 'order.service_order_shipped', 
                                      order_id=order_id, tracking_number=tracking_number)
        return updated > 0
    
    def confirm_receipt(self, order_id: int, buyer_id: int) -> bool:
        """
        确认收货
        
        Args:
            order_id: 订单ID
            buyer_id: 买家ID(验证权限)
            
        Returns:
            bool: 确认收货是否成功
        """
        # 查询订单
        order_query = "SELECT * FROM orders WHERE order_id=?"
        orders = self.db.execute_query(order_query, (order_id,))
        if not orders:
            return False
        order = orders[0]
        if order['buyer_id'] != buyer_id:
            return False  # 权限校验
        if order['status'] != OrderStatus.SHIPPED.value:
            return False  # 仅已发货订单可确认收货
        completed_at = datetime.now().isoformat()
        update_query = "UPDATE orders SET status=?, completed_at=? WHERE order_id=?"
        updated = self.db.execute_update(update_query, (OrderStatus.COMPLETED.value, completed_at, order_id))
        if updated > 0:
            # 发送服务消息给卖家
            self._send_service_message(buyer_id, order['seller_id'], 'order.service_order_completed', order_id=order_id)
        return updated > 0
    
    def request_cancel_order(self, order_id: int, buyer_id: int, reason: str) -> bool:
        """
        买家申请取消订单（状态改为 cancel_requested，待卖家审批）
        
        Args:
            order_id: 订单ID
            buyer_id: 买家ID
            reason: 取消原因
            
        Returns:
            bool: 申请是否成功
        """
        # 查询订单
        order_query = "SELECT * FROM orders WHERE order_id=?"
        orders = self.db.execute_query(order_query, (order_id,))
        if not orders:
            return False
        order = orders[0]
        
        # 权限校验：必须是买家
        if order['buyer_id'] != buyer_id:
            return False
            
        # 仅待支付/已支付/已发货状态可申请取消
        if order['status'] not in [OrderStatus.PENDING.value, OrderStatus.PAID.value, OrderStatus.SHIPPED.value]:
            return False
        
        # 状态改为 cancel_requested（待卖家审批）
        update_query = "UPDATE orders SET status=? WHERE order_id=?"
        updated = self.db.execute_update(update_query, (OrderStatus.CANCEL_REQUESTED.value, order_id))
        
        if updated > 0:
            # 发送服务消息给卖家
            self._send_service_message(buyer_id, order['seller_id'], 'order.service_cancel_requested', 
                                     order_id=order_id, reason=reason)
        return updated > 0
    
    def approve_cancel(self, order_id: int, seller_id: int) -> bool:
        """
        卖家同意取消订单（状态从 cancel_requested 改为 cancelled）
        
        Args:
            order_id: 订单ID
            seller_id: 卖家ID(验证权限)
            
        Returns:
            bool: 审批是否成功
        """
        order_query = "SELECT * FROM orders WHERE order_id=?"
        orders = self.db.execute_query(order_query, (order_id,))
        if not orders:
            return False
        order = orders[0]
        if order['seller_id'] != seller_id:
            return False  # 权限校验
        if order['status'] != OrderStatus.CANCEL_REQUESTED.value:
            return False  # 仅待审批状态可审批
        
        # 更新订单状态为已取消
        update_query = "UPDATE orders SET status=? WHERE order_id=?"
        updated = self.db.execute_update(update_query, (OrderStatus.CANCELLED.value, order_id))
        
        if updated > 0:
            # 恢复商品库存
            product_query = "SELECT stock FROM products WHERE product_id=?"
            products = self.db.execute_query(product_query, (order['product_id'],))
            if products:
                new_stock = products[0]['stock'] + order['quantity']
                product_update = "UPDATE products SET stock=?, status=? WHERE product_id=?"
                self.db.execute_update(product_update, (new_stock, 'available', order['product_id']))
            
            # 发送服务消息给买家
            self._send_service_message(seller_id, order['buyer_id'], 'order.service_cancel_approved', 
                                     order_id=order_id)
        return updated > 0
    
    def reject_cancel(self, order_id: int, seller_id: int, reason: str = "") -> bool:
        """
        卖家拒绝取消订单（状态从 cancel_requested 改为原状态或 cancel_rejected）
        
        Args:
            order_id: 订单ID
            seller_id: 卖家ID(验证权限)
            reason: 拒绝原因
        
        Returns:
            bool: 是否拒绝成功
        """
        order_query = "SELECT * FROM orders WHERE order_id=?"
        orders = self.db.execute_query(order_query, (order_id,))
        if not orders:
            return False
        order = orders[0]
        if order['seller_id'] != seller_id:
            return False  # 权限校验
        if order['status'] != OrderStatus.CANCEL_REQUESTED.value:
            return False  # 仅待审批状态可审批
        
        # 更新状态和拒绝原因
        update_query = "UPDATE orders SET status=?, cancel_reject_reason=? WHERE order_id=?"
        updated = self.db.execute_update(update_query, (OrderStatus.CANCEL_REJECTED.value, reason, order_id))
        
        if updated > 0:
            # 发送服务消息给买家
            reason_text = f" 原因: {reason}" if reason else ""
            self._send_service_message(seller_id, order['buyer_id'], 'order.service_cancel_rejected', 
                                     order_id=order_id, reason_text=reason_text)
        return updated > 0
    
    def request_refund(self, order_id: int, buyer_id: int, 
                      reason: str) -> bool:
        """
        申请退款（买家发起，状态变为 refund_requested，需卖家审批）
        
        Args:
            order_id: 订单ID
            buyer_id: 买家ID
            reason: 退款原因
            
        Returns:
            bool: 申请是否成功
        """
        # 查询订单
        order_query = "SELECT * FROM orders WHERE order_id=?"
        orders = self.db.execute_query(order_query, (order_id,))
        if not orders:
            return False
        order = orders[0]
        if order['buyer_id'] != buyer_id:
            return False  # 权限校验
        # 仅已支付/已发货/已完成状态可申请退款
        if order['status'] not in [OrderStatus.PAID.value, OrderStatus.SHIPPED.value, OrderStatus.COMPLETED.value]:
            return False
        # 状态改为 refund_requested（待卖家审批）
        update_query = "UPDATE orders SET status=? WHERE order_id=?"
        updated = self.db.execute_update(update_query, (OrderStatus.REFUND_REQUESTED.value, order_id))
        if updated > 0:
            # 发送服务消息给卖家
            self._send_service_message(buyer_id, order['seller_id'], 'order.service_refund_requested', order_id=order_id, reason=reason)
        return updated > 0
    
    def approve_refund(self, order_id: int, seller_id: int) -> bool:
        """
        同意退款（卖家审批，状态从 refund_requested 改为 refunded）
        
        Args:
            order_id: 订单ID
            seller_id: 卖家ID(验证权限)
            
        Returns:
            bool: 审批是否成功
        """
        order_query = "SELECT * FROM orders WHERE order_id=?"
        orders = self.db.execute_query(order_query, (order_id,))
        if not orders:
            return False
        order = orders[0]
        if order['seller_id'] != seller_id:
            return False  # 权限校验
        if order['status'] != OrderStatus.REFUND_REQUESTED.value:
            return False  # 仅待审批状态可审批
        update_query = "UPDATE orders SET status=? WHERE order_id=?"
        updated = self.db.execute_update(update_query, (OrderStatus.REFUNDED.value, order_id))
        if updated > 0:
            # 发送服务消息给买家
            self._send_service_message(seller_id, order['buyer_id'], 'order.service_refund_approved', order_id=order_id)
        return updated > 0
    
    def reject_refund(self, order_id: int, seller_id: int, reason: str = "") -> bool:
        """
        拒绝退款（卖家审批，状态从 refund_requested 改为 refund_rejected）
        
        Args:
            order_id: 订单ID
            seller_id: 卖家ID(验证权限)
            reason: 拒绝原因
        
        Returns:
            bool: 是否拒绝成功
        """
        order_query = "SELECT * FROM orders WHERE order_id=?"
        orders = self.db.execute_query(order_query, (order_id,))
        if not orders:
            return False
        order = orders[0]
        if order['seller_id'] != seller_id:
            return False  # 权限校验
        if order['status'] != OrderStatus.REFUND_REQUESTED.value:
            return False  # 仅待审批状态可审批
        # 更新状态和拒绝原因
        update_query = "UPDATE orders SET status=?, refund_reject_reason=? WHERE order_id=?"
        updated = self.db.execute_update(update_query, (OrderStatus.REFUND_REJECTED.value, reason, order_id))
        if updated > 0:
            # 发送服务消息给买家
            reason_text = f" 原因: {reason}" if reason else ""
            self._send_service_message(seller_id, order['buyer_id'], 'order.service_refund_rejected', 
                                     order_id=order_id, reason_text=reason_text)
        return updated > 0
    
    def _send_service_message(self, sender_id: int, receiver_id: int, translation_key: str, **params):
        """
        发送服务消息（内部辅助方法）
        
        Args:
            sender_id: 发送者user_id
            receiver_id: 接收者user_id
            translation_key: 翻译键（如 'order.service_order_created'）
            **params: 翻译参数（如 order_id=123）
        """
        try:
            import json
            # 将翻译键和参数存储为 JSON
            content_data = {
                'key': translation_key,
                'params': params
            }
            content = json.dumps(content_data, ensure_ascii=False)
            
            # 插入消息表，msg_type 为 'service'
            insert_query = """
                INSERT INTO messages (sender_id, receiver_id, content, msg_type, status)
                VALUES (?, ?, ?, 'service', 'sent')
            """
            self.db.execute_insert(insert_query, (sender_id, receiver_id, content))
        except Exception as e:
            # 静默失败，不影响订单主流程
            pass
    
    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """
        根据ID获取订单
        
        Args:
            order_id: 订单ID
            
        Returns:
            Optional[Order]: 订单对象
        """
        query = "SELECT * FROM orders WHERE order_id=?"
        rows = self.db.execute_query(query, (order_id,))
        if not rows:
            return None
        row = rows[0]
        # 构造 Order 对象
        order = Order(
            buyer_id=row['buyer_id'],
            seller_id=row['seller_id'],
            product_id=row['product_id'],
            quantity=row['quantity'],
            total_price=row['total_price'],
            shipping_address=row['shipping_address']
        )
        order.order_id = row['order_id']
        order.status = OrderStatus(row['status']) if row['status'] else OrderStatus.PENDING
        # 时间字段转换
        def parse_dt(v):
            if v is None:
                return None
            try:
                return datetime.fromisoformat(v)
            except Exception:
                return None
        order.created_at = parse_dt(row.get('created_at')) or order.created_at
        order.paid_at = parse_dt(row.get('paid_at'))
        order.shipped_at = parse_dt(row.get('shipped_at'))
        order.completed_at = parse_dt(row.get('completed_at'))
        order.tracking_number = row.get('tracking_number')
        order.refund_reject_reason = row.get('refund_reject_reason')
        return order
    
    def get_orders_by_buyer(self, buyer_id: int, 
                           status: str = None) -> List[Dict]:
        """
        获取买家的订单列表
        
        Args:
            buyer_id: 买家ID
            status: 订单状态筛选
            
        Returns:
            List[Dict]: 订单列表
        """
        if status:
            query = """
                SELECT * FROM orders
                WHERE buyer_id=? AND status=?
                ORDER BY created_at DESC
            """
            return self.db.execute_query(query, (buyer_id, status))
        else:
            query = """
                SELECT * FROM orders
                WHERE buyer_id=?
                ORDER BY created_at DESC
            """
            return self.db.execute_query(query, (buyer_id,))
    
    def get_orders_by_seller(self, seller_id: int, 
                            status: str = None) -> List[Dict]:
        """
        获取卖家的订单列表
        
        Args:
            seller_id: 卖家ID
            status: 订单状态筛选
            
        Returns:
            List[Dict]: 订单列表
        """
        if status:
            query = """
                SELECT * FROM orders
                WHERE seller_id=? AND status=?
                ORDER BY created_at DESC
            """
            return self.db.execute_query(query, (seller_id, status))
        else:
            query = """
                SELECT * FROM orders
                WHERE seller_id=?
                ORDER BY created_at DESC
            """
            return self.db.execute_query(query, (seller_id,))
    
    def get_order_statistics(self, user_id: int, 
                            is_seller: bool = False) -> Dict:
        """
        获取订单统计信息
        
        Args:
            user_id: 用户ID
            is_seller: 是否为卖家
            
        Returns:
            Dict: 统计信息
        """
        role_field = 'seller_id' if is_seller else 'buyer_id'
        base_params = (user_id,)
        # 总数
        total = self.db.execute_query(
            f"SELECT COUNT(*) AS c FROM orders WHERE {role_field}=?",
            base_params
        )[0]['c']
        # 各状态计数
        stats = {}
        for st in [s.value for s in OrderStatus]:
            rows = self.db.execute_query(
                f"SELECT COUNT(*) AS c FROM orders WHERE {role_field}=? AND status=?",
                (user_id, st)
            )
            stats[st] = rows[0]['c']
        # 金额统计
        sum_field = 'total_price'
        amount_row = self.db.execute_query(
            f"SELECT COALESCE(SUM({sum_field}), 0) AS s FROM orders WHERE {role_field}=?",
            base_params
        )[0]
        total_amount = amount_row['s']
        return {
            'total_orders': total,
            'by_status': stats,
            ('total_revenue' if is_seller else 'total_spent'): total_amount
        }
