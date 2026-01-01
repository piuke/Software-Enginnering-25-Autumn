import pytest
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.order_service import OrderService
from models.order import OrderStatus


class SimpleMockDB:
    """简单的Mock数据库"""
    def __init__(self):
        self.orders = {}
        self.products = {}
        self.oid_counter = 1
    
    def execute_query(self, query, params):
        if "SELECT * FROM orders WHERE order_id=?" in query:
            return [self.orders[params[0]]] if params[0] in self.orders else []
        if "SELECT * FROM products WHERE product_id=?" in query:
            pid = params[0]
            if pid in self.products:
                # 如果查询包含 status='available'，则需要检查状态
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
            # 记录库存更新
            if "WHERE product_id=?" in query:
                pid = params[-1]
                if pid in self.products:
                    self.products[pid]['stock'] = params[0]
            return 1
        return 0


def create_order(oid, status=OrderStatus.PENDING.value):
    """创建一个订单对象"""
    return {
        'order_id': oid, 'buyer_id': 1, 'seller_id': 2, 'product_id': 1,
        'quantity': 2, 'total_price': 200.0, 'status': status,
        'shipping_address': '地址', 'tracking_number': None, 'paid_at': None,
        'shipped_at': None, 'completed_at': None, 'cancel_reject_reason': None,
        'refund_reject_reason': None
    }


class TestCreateOrder:
    """创建订单功能测试"""
    
    def setup_method(self):
        self.db = SimpleMockDB()
        self.service = OrderService(self.db)
        # 初始化商品
        self.db.products[1] = {
            'product_id': 1, 'seller_id': 2, 'price': 100.0, 'stock': 10, 'status': 'available'
        }
    
    def test_create_order_success(self):
        """成功创建订单"""
        result = self.service.create_order(1, 1, 2, '地址')
        assert result == 1
        assert 1 in self.db.orders
        assert self.db.orders[1]['buyer_id'] == 1
        assert self.db.orders[1]['status'] == OrderStatus.PENDING.value
    
    def test_create_order_product_not_found(self):
        """商品不存在"""
        result = self.service.create_order(1, 99, 2, '地址')
        assert result is None
    
    def test_create_order_insufficient_stock(self):
        """库存不足"""
        self.db.products[1]['stock'] = 1
        result = self.service.create_order(1, 1, 2, '地址')
        assert result is None
    
    def test_create_order_calculates_price(self):
        """计算总价"""
        result = self.service.create_order(1, 1, 3, '地址')
        assert result is not None
        assert self.db.orders[result]['total_price'] == 300.0
    
    def test_create_order_exact_stock(self):
        """正好用完库存"""
        self.db.products[1]['stock'] = 2
        result = self.service.create_order(1, 1, 2, '地址')
        assert result is not None
    
    def test_create_order_product_not_available(self):
        """商品不可售"""
        self.db.products[1]['status'] = 'sold_out'
        result = self.service.create_order(1, 1, 2, '地址')
        assert result is None
    
    def test_create_order_large_quantity(self):
        """大数量购买"""
        self.db.products[1]['stock'] = 100
        result = self.service.create_order(1, 1, 50, '地址')
        assert result is not None
        assert self.db.orders[result]['total_price'] == 5000.0  # 50 * 100


class TestPayOrder:
    """支付订单功能测试"""
    
    def setup_method(self):
        self.db = SimpleMockDB()
        self.service = OrderService(self.db)
    
    def test_pay_success(self):
        """成功支付"""
        self.db.orders[1] = create_order(1, OrderStatus.PENDING.value)
        result = self.service.pay_order(1, 'wechat')
        assert result is True
        assert self.db.orders[1]['status'] == OrderStatus.PAID.value
    
    def test_pay_not_found(self):
        """订单不存在"""
        assert self.service.pay_order(99, 'wechat') is False
    
    def test_pay_wrong_status(self):
        """订单状态不对"""
        self.db.orders[1] = create_order(1, OrderStatus.PAID.value)
        assert self.service.pay_order(1, 'wechat') is False
    
    def test_pay_sets_timestamp(self):
        """支付时间被设置"""
        self.db.orders[1] = create_order(1, OrderStatus.PENDING.value)
        self.service.pay_order(1, 'wechat')
        assert self.db.orders[1]['paid_at'] is not None


class TestShipOrder:
    """发货功能测试"""
    
    def setup_method(self):
        self.db = SimpleMockDB()
        self.service = OrderService(self.db)
    
    def test_ship_success(self):
        """成功发货"""
        self.db.orders[1] = create_order(1, OrderStatus.PAID.value)
        result = self.service.ship_order(1, 2, 'SF123456')
        assert result is True
        assert self.db.orders[1]['status'] == OrderStatus.SHIPPED.value
        assert self.db.orders[1]['tracking_number'] == 'SF123456'
    
    def test_ship_not_found(self):
        """订单不存在"""
        assert self.service.ship_order(99, 2, 'SF123456') is False
    
    def test_ship_wrong_seller(self):
        """卖家ID不对"""
        self.db.orders[1] = create_order(1, OrderStatus.PAID.value)
        assert self.service.ship_order(1, 99, 'SF123456') is False
    
    def test_ship_not_paid(self):
        """订单未支付"""
        self.db.orders[1] = create_order(1, OrderStatus.PENDING.value)
        assert self.service.ship_order(1, 2, 'SF123456') is False
    
    def test_ship_already_shipped(self):
        """已发货无法重复发货"""
        self.db.orders[1] = create_order(1, OrderStatus.SHIPPED.value)
        assert self.service.ship_order(1, 2, 'SF123456') is False
    
    def test_ship_sets_shipping_time(self):
        """发货时间被设置"""
        self.db.orders[1] = create_order(1, OrderStatus.PAID.value)
        self.service.ship_order(1, 2, 'SF123456')
        assert self.db.orders[1]['shipped_at'] is not None
    
    def test_ship_pending_status(self):
        """待支付订单无法发货"""
        self.db.orders[1] = create_order(1, OrderStatus.PENDING.value)
        assert self.service.ship_order(1, 2, 'SF123456') is False
    
    def test_ship_completed_status(self):
        """已完成订单无法发货"""
        self.db.orders[1] = create_order(1, OrderStatus.COMPLETED.value)
        assert self.service.ship_order(1, 2, 'SF123456') is False
    
    def test_ship_cancelled_order(self):
        """已取消订单无法发货"""
        self.db.orders[1] = create_order(1, OrderStatus.CANCELLED.value)
        assert self.service.ship_order(1, 2, 'SF123456') is False


class TestConfirmReceipt:
    """收货确认功能测试"""
    
    def setup_method(self):
        self.db = SimpleMockDB()
        self.service = OrderService(self.db)
    
    def test_confirm_success(self):
        """成功确认收货"""
        self.db.orders[1] = create_order(1, OrderStatus.SHIPPED.value)
        result = self.service.confirm_receipt(1, 1)
        assert result is True
        assert self.db.orders[1]['status'] == OrderStatus.COMPLETED.value
    
    def test_confirm_not_found(self):
        """订单不存在"""
        assert self.service.confirm_receipt(99, 1) is False
    
    def test_confirm_wrong_buyer(self):
        """买家ID不对"""
        self.db.orders[1] = create_order(1, OrderStatus.SHIPPED.value)
        assert self.service.confirm_receipt(1, 99) is False
    
    def test_confirm_not_shipped(self):
        """订单未发货"""
        self.db.orders[1] = create_order(1, OrderStatus.PAID.value)
        assert self.service.confirm_receipt(1, 1) is False
    
    def test_confirm_already_completed(self):
        """已完成无法重复确认"""
        self.db.orders[1] = create_order(1, OrderStatus.COMPLETED.value)
        assert self.service.confirm_receipt(1, 1) is False
    
    def test_confirm_sets_completed_time(self):
        """完成时间被设置"""
        self.db.orders[1] = create_order(1, OrderStatus.SHIPPED.value)
        self.service.confirm_receipt(1, 1)
        assert self.db.orders[1]['completed_at'] is not None
    
    def test_confirm_pending_status(self):
        """待支付状态无法收货"""
        self.db.orders[1] = create_order(1, OrderStatus.PENDING.value)
        assert self.service.confirm_receipt(1, 1) is False
    
    def test_confirm_cancelled_order(self):
        """已取消订单无法收货"""
        self.db.orders[1] = create_order(1, OrderStatus.CANCELLED.value)
        assert self.service.confirm_receipt(1, 1) is False


class TestCancelFlow:
    """取消流程测试"""
    
    def setup_method(self):
        self.db = SimpleMockDB()
        self.service = OrderService(self.db)
    
    def test_request_cancel_success(self):
        """成功请求取消"""
        self.db.orders[1] = create_order(1, OrderStatus.PAID.value)
        result = self.service.request_cancel_order(1, 1, 'reason')
        assert result is True
        assert self.db.orders[1]['status'] == OrderStatus.CANCEL_REQUESTED.value
    
    def test_request_cancel_wrong_buyer(self):
        """买家ID不对"""
        self.db.orders[1] = create_order(1, OrderStatus.PAID.value)
        assert self.service.request_cancel_order(1, 99, 'reason') is False
    
    def test_request_cancel_already_completed(self):
        """已完成的订单无法取消"""
        self.db.orders[1] = create_order(1, OrderStatus.COMPLETED.value)
        assert self.service.request_cancel_order(1, 1, 'reason') is False
    
    def test_request_cancel_not_found(self):
        """订单不存在"""
        assert self.service.request_cancel_order(99, 1, 'reason') is False
    
    def test_request_cancel_pending_order(self):
        """待支付订单可取消"""
        self.db.orders[1] = create_order(1, OrderStatus.PENDING.value)
        result = self.service.request_cancel_order(1, 1, 'reason')
        assert result is True
    
    def test_request_cancel_shipped_order(self):
        """已发货订单可取消"""
        self.db.orders[1] = create_order(1, OrderStatus.SHIPPED.value)
        result = self.service.request_cancel_order(1, 1, 'reason')
        assert result is True
    
    def test_approve_cancel_success(self):
        """成功批准取消"""
        self.db.orders[1] = create_order(1, OrderStatus.CANCEL_REQUESTED.value)
        result = self.service.approve_cancel(1, 2)
        assert result is True
        assert self.db.orders[1]['status'] == OrderStatus.CANCELLED.value
    
    def test_approve_cancel_wrong_seller(self):
        """卖家ID不对"""
        self.db.orders[1] = create_order(1, OrderStatus.CANCEL_REQUESTED.value)
        assert self.service.approve_cancel(1, 99) is False
    
    def test_approve_cancel_not_found(self):
        """订单不存在"""
        assert self.service.approve_cancel(99, 2) is False
    
    def test_approve_cancel_wrong_status(self):
        """订单状态不对"""
        self.db.orders[1] = create_order(1, OrderStatus.PAID.value)
        assert self.service.approve_cancel(1, 2) is False
    
    def test_approve_cancel_restores_stock(self):
        """批准取消时恢复库存"""
        # 初始库存10，创建订单买2件，剩余8件
        self.db.products[1] = {
            'product_id': 1, 'seller_id': 2, 'price': 100.0, 'stock': 8, 'status': 'available'
        }
        self.db.orders[1] = create_order(1, OrderStatus.CANCEL_REQUESTED.value)
        self.db.orders[1]['product_id'] = 1
        self.db.orders[1]['quantity'] = 2
        
        # 批准取消，库存应恢复为10
        self.service.approve_cancel(1, 2)
        assert self.db.products[1]['stock'] == 10
    
    def test_reject_cancel_success(self):
        """成功拒绝取消"""
        self.db.orders[1] = create_order(1, OrderStatus.CANCEL_REQUESTED.value)
        result = self.service.reject_cancel(1, 2, 'reason')
        assert result is True
        assert self.db.orders[1]['status'] == OrderStatus.CANCEL_REJECTED.value
    
    def test_reject_cancel_wrong_seller(self):
        """卖家ID不对"""
        self.db.orders[1] = create_order(1, OrderStatus.CANCEL_REQUESTED.value)
        assert self.service.reject_cancel(1, 99, 'reason') is False
    
    def test_reject_cancel_wrong_status(self):
        """订单状态不对"""
        self.db.orders[1] = create_order(1, OrderStatus.PAID.value)
        assert self.service.reject_cancel(1, 2, 'reason') is False
    
    def test_reject_cancel_not_found(self):
        """订单不存在"""
        assert self.service.reject_cancel(99, 2, 'reason') is False


class TestRefundFlow:
    """退款流程测试"""
    
    def setup_method(self):
        self.db = SimpleMockDB()
        self.service = OrderService(self.db)
    
    def test_request_refund_success(self):
        """成功请求退款"""
        self.db.orders[1] = create_order(1, OrderStatus.PAID.value)
        result = self.service.request_refund(1, 1, 'reason')
        assert result is True
        assert self.db.orders[1]['status'] == OrderStatus.REFUND_REQUESTED.value
    
    def test_request_refund_wrong_buyer(self):
        """买家ID不对"""
        self.db.orders[1] = create_order(1, OrderStatus.PAID.value)
        assert self.service.request_refund(1, 99, 'reason') is False
    
    def test_request_refund_not_paid(self):
        """订单未支付"""
        self.db.orders[1] = create_order(1, OrderStatus.PENDING.value)
        assert self.service.request_refund(1, 1, 'reason') is False
    
    def test_request_refund_not_found(self):
        """订单不存在"""
        assert self.service.request_refund(99, 1, 'reason') is False
    
    def test_request_refund_shipped_order(self):
        """已发货订单可退款"""
        self.db.orders[1] = create_order(1, OrderStatus.SHIPPED.value)
        result = self.service.request_refund(1, 1, 'reason')
        assert result is True
    
    def test_request_refund_completed_order(self):
        """已完成订单可退款"""
        self.db.orders[1] = create_order(1, OrderStatus.COMPLETED.value)
        result = self.service.request_refund(1, 1, 'reason')
        assert result is True
    
    def test_approve_refund_success(self):
        """成功批准退款"""
        self.db.orders[1] = create_order(1, OrderStatus.REFUND_REQUESTED.value)
        result = self.service.approve_refund(1, 2)
        assert result is True
        assert self.db.orders[1]['status'] == OrderStatus.REFUNDED.value
    
    def test_approve_refund_wrong_seller(self):
        """卖家ID不对"""
        self.db.orders[1] = create_order(1, OrderStatus.REFUND_REQUESTED.value)
        assert self.service.approve_refund(1, 99) is False
    
    def test_approve_refund_wrong_status(self):
        """订单状态不对"""
        self.db.orders[1] = create_order(1, OrderStatus.PAID.value)
        assert self.service.approve_refund(1, 2) is False
    
    def test_approve_refund_not_found(self):
        """订单不存在"""
        assert self.service.approve_refund(99, 2) is False
    
    def test_reject_refund_success(self):
        """成功拒绝退款"""
        self.db.orders[1] = create_order(1, OrderStatus.REFUND_REQUESTED.value)
        result = self.service.reject_refund(1, 2, 'reason')
        assert result is True
        assert self.db.orders[1]['status'] == OrderStatus.REFUND_REJECTED.value
    
    def test_reject_refund_wrong_seller(self):
        """卖家ID不对"""
        self.db.orders[1] = create_order(1, OrderStatus.REFUND_REQUESTED.value)
        assert self.service.reject_refund(1, 99, 'reason') is False
    
    def test_reject_refund_wrong_status(self):
        """订单状态不对"""
        self.db.orders[1] = create_order(1, OrderStatus.PAID.value)
        assert self.service.reject_refund(1, 2, 'reason') is False
    
    def test_reject_refund_not_found(self):
        """订单不存在"""
        assert self.service.reject_refund(99, 2, 'reason') is False


class TestOrderQuery:
    """订单查询功能测试"""
    
    def setup_method(self):
        self.db = SimpleMockDB()
        self.service = OrderService(self.db)
    
    def test_get_order_by_id_success(self):
        """成功查询订单"""
        self.db.orders[1] = create_order(1, OrderStatus.PAID.value)
        order = self.service.get_order_by_id(1)
        assert order is not None
        assert order.order_id == 1
        assert order.buyer_id == 1
    
    def test_get_order_by_id_not_found(self):
        """订单不存在"""
        order = self.service.get_order_by_id(99)
        assert order is None
    
    def test_get_order_with_timestamps(self):
        """获取订单及其时间戳"""
        self.db.orders[1] = create_order(1, OrderStatus.PAID.value)
        self.db.orders[1]['paid_at'] = '2025-01-01T10:00:00'
        self.db.orders[1]['tracking_number'] = 'SF123456'
        order = self.service.get_order_by_id(1)
        assert order is not None
        assert order.tracking_number == 'SF123456'
    
    def test_get_order_by_buyer(self):
        """获取买家的订单列表"""
        self.db.orders[1] = create_order(1, OrderStatus.PAID.value)
        self.db.orders[2] = create_order(2, OrderStatus.PENDING.value)
        self.db.orders[2]['buyer_id'] = 1  # 同一买家
        orders = self.service.get_orders_by_buyer(1)
        assert orders is not None
    
    def test_get_order_by_seller(self):
        """获取卖家的订单列表"""
        self.db.orders[1] = create_order(1, OrderStatus.PAID.value)
        self.db.orders[2] = create_order(2, OrderStatus.PENDING.value)
        self.db.orders[2]['seller_id'] = 2  # 同一卖家
        orders = self.service.get_orders_by_seller(2)
        assert orders is not None
