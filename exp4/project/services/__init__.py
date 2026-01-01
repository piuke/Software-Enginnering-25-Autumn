"""
Services package for the Anime Shopping Mall System.
业务逻辑服务层
"""

from .user_service import UserService
from .product_service import ProductService
from .order_service import OrderService
from .auction_service import AuctionService
from .message_service import MessageService
from .report_service import ReportService

__all__ = [
    'UserService',
    'ProductService',
    'OrderService',
    'AuctionService',
    'MessageService',
    'ReportService'
]
