"""
Models package for the Anime Shopping Mall System.
包含所有数据模型类的定义。
"""

from .user import User
from .product import Product
from .order import Order, OrderStatus
from .auction import Auction
from .message import Message
from .report import Report
from .admin import Admin

__all__ = [
    'User',
    'Product',
    'Order',
    'OrderStatus',
    'Auction',
    'Message',
    'Report',
    'Admin'
]
