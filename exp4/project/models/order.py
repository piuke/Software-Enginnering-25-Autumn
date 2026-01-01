"""
Order model - 订单模型
管理订单流程和状态
"""

from typing import Optional
from datetime import datetime
from enum import Enum


class OrderStatus(Enum):
    """订单状态枚举"""
    PENDING = "pending"          # 待支付
    PAID = "paid"                # 已支付
    SHIPPED = "shipped"          # 已发货
    COMPLETED = "completed"      # 已完成
    CANCELLED = "cancelled"      # 已取消
    CANCEL_REQUESTED = "cancel_requested"  # 取消申请中
    CANCEL_REJECTED = "cancel_rejected"    # 取消被拒绝
    REFUND_REQUESTED = "refund_requested"  # 退款申请中
    REFUND_REJECTED = "refund_rejected"    # 退款被拒绝
    REFUNDED = "refunded"        # 已退款


class Order:
    """
    订单类
    
    Attributes:
        order_id (int): 订单ID
        buyer_id (int): 买家ID
        seller_id (int): 卖家ID
        product_id (int): 商品ID
        quantity (int): 购买数量
        total_price (float): 总价
        status (OrderStatus): 订单状态
        shipping_address (str): 收货地址
        tracking_number (str): 物流单号
        refund_reject_reason (str): 拒绝退款原因
        created_at (datetime): 创建时间
        paid_at (datetime): 支付时间
        shipped_at (datetime): 发货时间
        completed_at (datetime): 完成时间
    """
    
    def __init__(self, buyer_id: int, seller_id: int, product_id: int,
                 quantity: int, total_price: float, shipping_address: str):
        """
        初始化订单对象
        
        Args:
            buyer_id: 买家ID
            seller_id: 卖家ID
            product_id: 商品ID
            quantity: 购买数量
            total_price: 总价
            shipping_address: 收货地址
        """
        self.order_id: Optional[int] = None
        self.buyer_id: int = buyer_id
        self.seller_id: int = seller_id
        self.product_id: int = product_id
        self.quantity: int = quantity
        self.total_price: float = total_price
        self.status: OrderStatus = OrderStatus.PENDING
        self.shipping_address: str = shipping_address
        self.tracking_number: Optional[str] = None
        self.refund_reject_reason: Optional[str] = None
        self.cancel_reject_reason: Optional[str] = None
        self.created_at: datetime = datetime.now()
        self.paid_at: Optional[datetime] = None
        self.shipped_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
    
    def create_order(self) -> bool:
        """
        创建订单
        
        Returns:
            bool: 创建是否成功
        """
        # TODO: 实现创建订单逻辑
        pass
    
    def pay(self, payment_method: str) -> bool:
        """
        支付订单
        
        Args:
            payment_method: 支付方式
            
        Returns:
            bool: 支付是否成功
        """
        # TODO: 实现支付逻辑
        pass
    
    def ship(self, tracking_number: str) -> bool:
        """
        发货
        
        Args:
            tracking_number: 物流单号
            
        Returns:
            bool: 发货是否成功
        """
        # TODO: 实现发货逻辑
        pass
    
    def confirm_receipt(self) -> bool:
        """
        确认收货
        
        Returns:
            bool: 确认是否成功
        """
        # TODO: 实现确认收货逻辑
        pass
    
    def cancel(self, reason: str) -> bool:
        """
        取消订单
        
        Args:
            reason: 取消原因
            
        Returns:
            bool: 取消是否成功
        """
        # TODO: 实现取消订单逻辑
        pass
    
    def request_refund(self, reason: str) -> bool:
        """
        申请退款
        
        Args:
            reason: 退款原因
            
        Returns:
            bool: 申请是否成功
        """
        # TODO: 实现退款申请逻辑
        pass
    
    def to_dict(self) -> dict:
        """
        将订单对象转换为字典
        
        Returns:
            dict: 订单信息字典
        """
        return {
            'order_id': self.order_id,
            'buyer_id': self.buyer_id,
            'seller_id': self.seller_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'total_price': self.total_price,
            'status': self.status.value,
            'shipping_address': self.shipping_address,
            'tracking_number': self.tracking_number,
            'created_at': self.created_at.isoformat(),
            'paid_at': self.paid_at.isoformat() if self.paid_at else None,
            'shipped_at': self.shipped_at.isoformat() if self.shipped_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def __repr__(self) -> str:
        """订单对象的字符串表示"""
        return f"<Order(id={self.order_id}, status={self.status.value})>"
