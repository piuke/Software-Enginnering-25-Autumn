"""
Product model - 商品模型
管理商品信息和操作
"""

from typing import Optional, List
from datetime import datetime
from enum import Enum


class ProductStatus(Enum):
    """商品状态枚举"""
    AVAILABLE = "available"  # 可售
    SOLD_OUT = "sold_out"    # 售罄
    REMOVED = "removed"      # 已下架
    IN_AUCTION = "in_auction"  # 拍卖中


class Product:
    """
    商品类
    
    Attributes:
        product_id (int): 商品ID
        seller_id (int): 卖家ID
        title (str): 商品标题
        description (str): 商品描述
        price (float): 商品价格
        category (str): 商品分类(IP分类)
        images (List[str]): 商品图片URL列表
        stock (int): 库存数量
        status (ProductStatus): 商品状态
        auctionable (bool): 是否支持拍卖
        view_count (int): 浏览次数
        favorite_count (int): 收藏次数
        created_at (datetime): 创建时间
    """
    
    def __init__(self, seller_id: int, title: str, description: str,
                 price: float, category: str, stock: int = 1):
        """
        初始化商品对象
        
        Args:
            seller_id: 卖家ID
            title: 商品标题
            description: 商品描述
            price: 商品价格
            category: 商品分类
            stock: 库存数量
        """
        self.product_id: Optional[int] = None
        self.seller_id: int = seller_id
        self.title: str = title
        self.description: str = description
        self.price: float = price
        self.category: str = category
        self.images: List[str] = []
        self.stock: int = stock
        self.status: ProductStatus = ProductStatus.AVAILABLE
        self.auctionable: bool = False
        self.view_count: int = 0
        self.favorite_count: int = 0
        self.created_at: datetime = datetime.now()
        self.updated_at: datetime = datetime.now()
    
    def upload(self) -> bool:
        """
        上传商品到平台
        
        Returns:
            bool: 上传是否成功
        """
        # TODO: 实现商品上传逻辑
        pass
    
    def update(self, **kwargs) -> bool:
        """
        更新商品信息
        
        Args:
            **kwargs: 要更新的字段
            
        Returns:
            bool: 更新是否成功
        """
        # TODO: 实现商品更新逻辑
        pass
    
    def delete(self) -> bool:
        """
        删除商品(下架)
        
        Returns:
            bool: 删除是否成功
        """
        # TODO: 实现商品删除逻辑
        pass
    
    def add_image(self, image_url: str) -> bool:
        """
        添加商品图片
        
        Args:
            image_url: 图片URL
            
        Returns:
            bool: 添加是否成功
        """
        # TODO: 实现添加图片逻辑
        pass
    
    def increase_view_count(self) -> None:
        """增加浏览次数"""
        self.view_count += 1
    
    def increase_favorite_count(self) -> None:
        """增加收藏次数"""
        self.favorite_count += 1
    
    def decrease_stock(self, quantity: int = 1) -> bool:
        """
        减少库存
        
        Args:
            quantity: 减少数量
            
        Returns:
            bool: 操作是否成功
        """
        if self.stock >= quantity:
            self.stock -= quantity
            if self.stock == 0:
                self.status = ProductStatus.SOLD_OUT
            return True
        return False
    
    def to_dict(self) -> dict:
        """
        将商品对象转换为字典
        
        Returns:
            dict: 商品信息字典
        """
        return {
            'product_id': self.product_id,
            'seller_id': self.seller_id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'images': self.images,
            'stock': self.stock,
            'status': self.status.value,
            'auctionable': self.auctionable,
            'view_count': self.view_count,
            'favorite_count': self.favorite_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self) -> str:
        """商品对象的字符串表示"""
        return f"<Product(id={self.product_id}, title='{self.title}')>"
