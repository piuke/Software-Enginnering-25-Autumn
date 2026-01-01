import pytest
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.order_service import OrderService
from models.order import OrderStatus


class MockDB:
    """模拟数据库 - 支持集成测试"""
    def __init__(self):
        self.orders = {}
        self.products = {}
        self.messages = []
        self.oid_counter = 1
    
    def execute_query(self, query, params):
        if "SELECT * FROM orders WHERE order_id=?" in query:
            return [self.orders[params[0]]] if params[0] in self.orders else []
        if "SELECT * FROM products WHERE product_id=?" in query:
            pid = params[0]
            if pid in self.products:
                if "AND status='available'" in query:
                    if self.products[pid].get('status') == 'available':
                        return [self.products[pid]]
                    else:
                        return []
                else:
                    return [self.products[pid]]
            return []
        if "SELECT stock FROM products" in query:
            return [{'stock': self.products[params[0]]['stock']}] if params[0] in self.products else []
        if "SELECT * FROM orders WHERE buyer_id=?" in query:
            return [o for o in self.orders.values() if o['buyer_id'] == params[0]]
        if "SELECT * FROM orders WHERE seller_id=?" in query:
            return [o for o in self.orders.values() if o['seller_id'] == params[0]]
        return []
    
    def execute_insert(self, query, params):
        if "INSERT INTO orders" in query:
            oid = self.oid_counter
            self.oid_counter += 1
            self.orders[oid] = {
                'order_id': oid, 'buyer_id': params[0], 'seller_id': params[1],
                'product_id': params[2], 'quantity': params[3], 'total_price': params[4],
                'status': params[5], 'shipping_address': params[6],
                'tracking_number': None, 'paid_at': None, 'shipped_at': None,
                'completed_at': None, 'cancel_reject_reason': None, 'refund_reject_reason': None
            }
            return oid
        if "INSERT INTO messages" in query:
            self.messages.append({
                'sender_id': params[0],
                'receiver_id': params[1],
                'content': params[2],
                'type': 'service',
                'status': 'sent'
            })
            return len(self.messages)
        return None
    
    def execute_update(self, query, params):
        if "UPDATE orders" in query and "WHERE order_id=?" in query:
            oid = params[-1]
            if "SET status=?, paid_at=?" in query:
                self.orders[oid]['status'] = params[0]
                self.orders[oid]['paid_at'] = params[1]
            elif "SET status=?, tracking_number=?, shipped_at=?" in query:
                self.orders[oid]['status'] = params[0]
                self.orders[oid]['tracking_number'] = params[1]
                self.orders[oid]['shipped_at'] = params[2]
            elif "SET status=?, completed_at=?" in query:
                self.orders[oid]['status'] = params[0]
                self.orders[oid]['completed_at'] = params[1]
            elif "SET status=?" in query:
                self.orders[oid]['status'] = params[0]
            elif "SET status=?, cancel_reject_reason=?" in query:
                self.orders[oid]['status'] = params[0]
                self.orders[oid]['cancel_reject_reason'] = params[1]
            elif "SET status=?, refund_reject_reason=?" in query:
                self.orders[oid]['status'] = params[0]
                self.orders[oid]['refund_reject_reason'] = params[1]
            return 1
        if "UPDATE products SET stock=?" in query:
            if "WHERE product_id=?" in query:
                pid = params[-1]
                if pid in self.products:
                    self.products[pid]['stock'] = params[0]
                    if "status=?" in query:
                        self.products[pid]['status'] = params[1]
            return 1
        return 0


class TestIntegrationNormalFlow:
    """集成测试 - 正常订单流程"""
    
    def setup_method(self):
        self.db = MockDB()
        self.service = OrderService(self.db)
        # 初始化商品
        self.db.products[1] = {
            'product_id': 1, 'seller_id': 2, 'price': 100.0, 'stock': 10, 'status': 'available'
        }
    
    def test_complete_order_lifecycle(self):
        """完整订单生命周期：创建->支付->发货->收货"""
        # 第1步：买家创建订单
        order_id = self.service.create_order(buyer_id=1, product_id=1, quantity=2, shipping_address='北京')
        assert order_id is not None
        assert self.db.orders[order_id]['status'] == OrderStatus.PENDING.value
        assert self.db.orders[order_id]['total_price'] == 200.0
        
        # 验证库存减少
        assert self.db.products[1]['stock'] == 8
        
        # 第2步：买家支付订单
        pay_result = self.service.pay_order(order_id, 'wechat')
        assert pay_result is True
        assert self.db.orders[order_id]['status'] == OrderStatus.PAID.value
        assert self.db.orders[order_id]['paid_at'] is not None
        
        # 第3步：卖家发货
        ship_result = self.service.ship_order(order_id, seller_id=2, tracking_number='SF123456')
        assert ship_result is True
        assert self.db.orders[order_id]['status'] == OrderStatus.SHIPPED.value
        assert self.db.orders[order_id]['tracking_number'] == 'SF123456'
        assert self.db.orders[order_id]['shipped_at'] is not None
        
        # 第4步：买家确认收货
        confirm_result = self.service.confirm_receipt(order_id, buyer_id=1)
        assert confirm_result is True
        assert self.db.orders[order_id]['status'] == OrderStatus.COMPLETED.value
        assert self.db.orders[order_id]['completed_at'] is not None
        
        # 验证消息被发送
        assert len(self.db.messages) > 0
    
    def test_order_prevents_invalid_state_transitions(self):
        """测试订单状态转换的有效性"""
        order_id = self.service.create_order(1, 1, 2, '地址')
        
        # 不能直接发货（未支付）
        assert self.service.ship_order(order_id, 2, 'SF123') is False
        
        # 不能收货（未发货）
        assert self.service.confirm_receipt(order_id, 1) is False
        
        # 必须按正确顺序
        self.service.pay_order(order_id, 'wechat')
        assert self.service.ship_order(order_id, 2, 'SF123') is True
        assert self.service.confirm_receipt(order_id, 1) is True


class TestIntegrationCancelFlow:
    """集成测试 - 订单取消流程"""
    
    def setup_method(self):
        self.db = MockDB()
        self.service = OrderService(self.db)
        self.db.products[1] = {
            'product_id': 1, 'seller_id': 2, 'price': 100.0, 'stock': 10, 'status': 'available'
        }
    
    def test_cancel_order_from_paid_state(self):
        """从已支付状态取消订单并恢复库存"""
        # 创建并支付订单
        order_id = self.service.create_order(1, 1, 5, '地址')
        initial_stock = self.db.products[1]['stock']  # 应为 5 (10-5)
        
        self.service.pay_order(order_id, 'wechat')
        assert self.db.orders[order_id]['status'] == OrderStatus.PAID.value
        
        # 买家请求取消
        cancel_result = self.service.request_cancel_order(order_id, buyer_id=1, reason='changed mind')
        assert cancel_result is True
        assert self.db.orders[order_id]['status'] == OrderStatus.CANCEL_REQUESTED.value
        
        # 卖家批准取消
        approve_result = self.service.approve_cancel(order_id, seller_id=2)
        assert approve_result is True
        assert self.db.orders[order_id]['status'] == OrderStatus.CANCELLED.value
        
        # 验证库存被恢复为原来的10件
        assert self.db.products[1]['stock'] == 10
    
    def test_cancel_then_reject(self):
        """取消请求被拒绝"""
        order_id = self.service.create_order(1, 1, 2, '地址')
        self.service.pay_order(order_id, 'wechat')
        
        # 买家请求取消
        self.service.request_cancel_order(order_id, 1, 'reason')
        assert self.db.orders[order_id]['status'] == OrderStatus.CANCEL_REQUESTED.value
        
        # 卖家拒绝取消
        reject_result = self.service.reject_cancel(order_id, 2, 'not allowed')
        assert reject_result is True
        assert self.db.orders[order_id]['status'] == OrderStatus.CANCEL_REJECTED.value
        
        # 库存不变
        assert self.db.products[1]['stock'] == 8


class TestIntegrationRefundFlow:
    """集成测试 - 退款流程"""
    
    def setup_method(self):
        self.db = MockDB()
        self.service = OrderService(self.db)
        self.db.products[1] = {
            'product_id': 1, 'seller_id': 2, 'price': 100.0, 'stock': 10, 'status': 'available'
        }
    
    def test_refund_after_receipt(self):
        """收货后退款的完整流程"""
        # 正常完成订单
        order_id = self.service.create_order(1, 1, 3, '地址')
        self.service.pay_order(order_id, 'wechat')
        self.service.ship_order(order_id, 2, 'SF123')
        self.service.confirm_receipt(order_id, 1)
        
        assert self.db.orders[order_id]['status'] == OrderStatus.COMPLETED.value
        
        # 买家申请退款
        refund_result = self.service.request_refund(order_id, buyer_id=1, reason='defective product')
        assert refund_result is True
        assert self.db.orders[order_id]['status'] == OrderStatus.REFUND_REQUESTED.value
        
        # 卖家批准退款
        approve_result = self.service.approve_refund(order_id, seller_id=2)
        assert approve_result is True
        assert self.db.orders[order_id]['status'] == OrderStatus.REFUNDED.value
    
    def test_refund_rejection(self):
        """退款请求被拒绝"""
        order_id = self.service.create_order(1, 1, 2, '地址')
        self.service.pay_order(order_id, 'wechat')
        self.service.ship_order(order_id, 2, 'SF123')
        self.service.confirm_receipt(order_id, 1)
        
        # 申请退款
        self.service.request_refund(order_id, 1, 'reason')
        
        # 卖家拒绝
        reject_result = self.service.reject_refund(order_id, 2, 'no reason given')
        assert reject_result is True
        assert self.db.orders[order_id]['status'] == OrderStatus.REFUND_REJECTED.value


class TestIntegrationMultipleOrders:
    """集成测试 - 多订单场景"""
    
    def setup_method(self):
        self.db = MockDB()
        self.service = OrderService(self.db)
        # 初始化两个商品，来自不同卖家
        self.db.products[1] = {
            'product_id': 1, 'seller_id': 2, 'price': 100.0, 'stock': 10, 'status': 'available'
        }
        self.db.products[2] = {
            'product_id': 2, 'seller_id': 3, 'price': 50.0, 'stock': 20, 'status': 'available'
        }
    
    def test_buyer_creates_multiple_orders(self):
        """买家创建多个订单"""
        # 创建第一个订单
        order1 = self.service.create_order(buyer_id=1, product_id=1, quantity=2, shipping_address='北京')
        assert order1 == 1
        assert self.db.orders[1]['seller_id'] == 2
        
        # 创建第二个订单
        order2 = self.service.create_order(buyer_id=1, product_id=2, quantity=3, shipping_address='上海')
        assert order2 == 2
        assert self.db.orders[2]['seller_id'] == 3
        
        # 验证两个订单独立
        assert self.db.orders[1]['product_id'] == 1
        assert self.db.orders[2]['product_id'] == 2
        assert self.db.orders[1]['total_price'] == 200.0
        assert self.db.orders[2]['total_price'] == 150.0
    
    def test_seller_manages_multiple_orders(self):
        """卖家管理多个订单"""
        # 买家从两个不同的卖家各买一个商品
        order1 = self.service.create_order(1, 1, 2, '地址')  # seller_id=2
        order2 = self.service.create_order(1, 2, 3, '地址')  # seller_id=3
        
        # 支付订单
        self.service.pay_order(order1, 'wechat')
        self.service.pay_order(order2, 'wechat')
        
        # seller_id=2 只能发货order1
        assert self.service.ship_order(order1, seller_id=2, tracking_number='SF1') is True
        
        # seller_id=2 无法发货order2（属于seller_id=3）
        assert self.service.ship_order(order2, seller_id=2, tracking_number='SF2') is False
        
        # seller_id=3 可以发货order2
        assert self.service.ship_order(order2, seller_id=3, tracking_number='SF2') is True
    
    def test_stock_consistency_across_orders(self):
        """验证库存在多订单中的一致性"""
        initial_stock = 10
        
        # 订单1：买2件
        o1 = self.service.create_order(1, 1, 2, '地址')
        assert self.db.products[1]['stock'] == 8
        
        # 订单2：买3件
        o2 = self.service.create_order(2, 1, 3, '地址')
        assert self.db.products[1]['stock'] == 5
        
        # 取消订单1：恢复2件
        self.service.pay_order(o1, 'wechat')
        self.service.request_cancel_order(o1, 1, 'reason')
        self.service.approve_cancel(o1, 2)
        assert self.db.products[1]['stock'] == 7
        
        # 取消订单2：恢复3件
        self.service.pay_order(o2, 'wechat')
        self.service.request_cancel_order(o2, 2, 'reason')
        self.service.approve_cancel(o2, 2)
        assert self.db.products[1]['stock'] == 10


class TestIntegrationDataConsistency:
    """集成测试 - 数据一致性"""
    
    def setup_method(self):
        self.db = MockDB()
        self.service = OrderService(self.db)
        self.db.products[1] = {
            'product_id': 1, 'seller_id': 2, 'price': 100.0, 'stock': 100, 'status': 'available'
        }
    
    def test_order_data_integrity(self):
        """验证订单数据的完整性"""
        order_id = self.service.create_order(1, 1, 5, '北京市朝阳区')
        order = self.db.orders[order_id]
        
        # 验证所有必要字段
        assert order['order_id'] == order_id
        assert order['buyer_id'] == 1
        assert order['seller_id'] == 2
        assert order['product_id'] == 1
        assert order['quantity'] == 5
        assert order['total_price'] == 500.0
        assert order['shipping_address'] == '北京市朝阳区'
        assert order['status'] == OrderStatus.PENDING.value
        
        # 支付后检查时间戳
        self.service.pay_order(order_id, 'wechat')
        assert order['paid_at'] is not None
        
        # 发货后检查时间戳和物流号
        self.service.ship_order(order_id, 2, 'SF12345')
        assert order['shipped_at'] is not None
        assert order['tracking_number'] == 'SF12345'
        
        # 收货后检查时间戳
        self.service.confirm_receipt(order_id, 1)
        assert order['completed_at'] is not None
    
    def test_state_transition_consistency(self):
        """验证状态转换的一致性"""
        order_id = self.service.create_order(1, 1, 1, '地址')
        
        # 追踪所有状态转换
        states = [self.db.orders[order_id]['status']]
        
        self.service.pay_order(order_id, 'wechat')
        states.append(self.db.orders[order_id]['status'])
        
        self.service.ship_order(order_id, 2, 'SF')
        states.append(self.db.orders[order_id]['status'])
        
        self.service.confirm_receipt(order_id, 1)
        states.append(self.db.orders[order_id]['status'])
        
        # 验证正确的状态序列
        expected = [
            OrderStatus.PENDING.value,
            OrderStatus.PAID.value,
            OrderStatus.SHIPPED.value,
            OrderStatus.COMPLETED.value
        ]
        assert states == expected


class TestIntegrationErrorRecovery:
    """集成测试 - 错误恢复"""
    
    def setup_method(self):
        self.db = MockDB()
        self.service = OrderService(self.db)
        self.db.products[1] = {
            'product_id': 1, 'seller_id': 2, 'price': 100.0, 'stock': 10, 'status': 'available'
        }
    
    def test_insufficient_stock_prevents_order(self):
        """库存不足时无法创建订单"""
        # 第一个订单使用8件
        o1 = self.service.create_order(1, 1, 8, '地址')
        assert o1 is not None
        assert self.db.products[1]['stock'] == 2
        
        # 第二个订单要求5件，应该失败
        o2 = self.service.create_order(2, 1, 5, '地址')
        assert o2 is None
        
        # 第三个订单要求2件，应该成功
        o3 = self.service.create_order(2, 1, 2, '地址')
        assert o3 is not None
        assert self.db.products[1]['stock'] == 0
    
    def test_invalid_product_prevents_order(self):
        """无效商品ID时无法创建订单"""
        order_id = self.service.create_order(1, 99, 1, '地址')
        assert order_id is None
    
    def test_wrong_user_cannot_modify_order(self):
        """错误的用户无法修改订单"""
        order_id = self.service.create_order(1, 1, 2, '地址')
        self.service.pay_order(order_id, 'wechat')
        
        # 错误的卖家无法发货
        assert self.service.ship_order(order_id, seller_id=99, tracking_number='SF') is False
        
        # 错误的买家无法收货
        assert self.service.confirm_receipt(order_id, buyer_id=99) is False
