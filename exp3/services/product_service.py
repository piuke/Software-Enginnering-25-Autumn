"""
Product Service - 商品服务层
处理商品相关的业务逻辑
"""

from typing import Optional, List, Dict
from models.product import Product, ProductStatus

from utils.exceptions import (
    ProductNotFoundError,
    InsufficientStockError
)


class ProductService:
    """
    商品服务类
    提供商品发布、编辑、搜索、浏览等功能
    """
    
    def __init__(self, db_manager):
        """
        初始化商品服务
        
        Args:
            db_manager: 数据库管理器实例
        """
        self.db = db_manager
    
    def create_product(self, seller_id: int, product_data: dict) -> Optional[int]:
        """
        创建商品
        
        Args:
            seller_id: 卖家ID
            product_data: 商品信息 (必须包含: title, description, price, category)
            
        Returns:
            Optional[int]: 成功返回商品ID,失败返回None
        """
        try:
            # 验证必填字段
            required_fields = ['title', 'description', 'price', 'category']
            for field in required_fields:
                if field not in product_data:
                    raise ValueError(f"缺少必填字段: {field}")
            
            # 准备插入数据
            query = """
                INSERT INTO products (
                    seller_id, title, description, price, category,
                    images, stock, status, auctionable
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            # 获取参数，使用默认值
            params = (
                seller_id,
                product_data['title'],
                product_data['description'],
                product_data['price'],
                product_data['category'],
                product_data.get('images', '[]'),  # 默认空图片列表
                product_data.get('stock', 1),       # 默认库存1
                product_data.get('status', 'available'),  # 默认可售
                product_data.get('auctionable', 0)  # 默认不支持拍卖
            )
            
            # 执行插入
            product_id = self.db.execute_insert(query, params)
            
            return product_id
            
        except Exception as e:
            print(f"创建商品失败: {str(e)}")
            return None
    
    def update_product(self, product_id: int, product_data: dict) -> bool:
        """
        更新商品信息
        
        Args:
            product_id: 商品ID
            product_data: 更新的商品信息 (只包含要更新的字段)
            
        Returns:
            bool: 更新是否成功
        """
        try:
            # 检查商品是否存在
            existing = self.db.execute_query(
                "SELECT product_id FROM products WHERE product_id = ?",
                (product_id,)
            )
            if not existing:
                raise ProductNotFoundError(f"商品ID {product_id} 不存在")
            
            # 允许更新的字段
            allowed_fields = ['title', 'description', 'price', 'category', 
                            'images', 'stock', 'status', 'auctionable']
            
            # 构建动态更新语句
            update_fields = []
            params = []
            
            for field in allowed_fields:
                if field in product_data:
                    update_fields.append(f"{field} = ?")
                    params.append(product_data[field])
            
            # 如果没有要更新的字段
            if not update_fields:
                return False
            
            # 添加 updated_at 字段
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            
            # 添加 product_id 到参数列表末尾
            params.append(product_id)
            
            # 构建完整的更新语句
            query = f"UPDATE products SET {', '.join(update_fields)} WHERE product_id = ?"
            
            # 执行更新
            affected_rows = self.db.execute_update(query, tuple(params))
            
            return affected_rows > 0
            
        except ProductNotFoundError:
            raise
        except Exception as e:
            print(f"更新商品失败: {str(e)}")
            return False
    
    def delete_product(self, product_id: int, seller_id: int = None, 
                      is_admin: bool = False) -> bool:
        """
        删除商品 (实际是软删除，将状态改为 removed)
        
        Args:
            product_id: 商品ID
            seller_id: 卖家ID(验证权限，管理员可为None)
            is_admin: 是否是管理员操作
            
        Returns:
            bool: 删除是否成功
        """
        try:
            # 检查商品是否存在
            existing = self.db.execute_query(
                "SELECT product_id, seller_id FROM products WHERE product_id = ?",
                (product_id,)
            )
            
            if not existing:
                raise ProductNotFoundError(f"商品ID {product_id} 不存在")
            
            # 权限验证：管理员可以删除任何商品，卖家只能删除自己的商品
            if not is_admin:
                if seller_id is None or existing[0]['seller_id'] != seller_id:
                    print(f"权限不足: 卖家ID {seller_id} 无权删除商品ID {product_id}")
                    return False
            
            # 软删除：将状态改为 removed
            query = """
                UPDATE products 
                SET status = 'removed', updated_at = CURRENT_TIMESTAMP
                WHERE product_id = ?
            """
            
            affected_rows = self.db.execute_update(query, (product_id,))
            
            if affected_rows > 0:
                action_by = "管理员" if is_admin else f"卖家ID {seller_id}"
                print(f"✓ 商品ID {product_id} 已被{action_by}删除")
            
            return affected_rows > 0
            
        except ProductNotFoundError:
            raise
        except Exception as e:
            print(f"删除商品失败: {str(e)}")
            return False
    
    def get_product_by_id(self, product_id: int, increment_view: bool = True) -> Optional[Product]:
        """
        根据ID获取商品
        
        Args:
            product_id: 商品ID
            increment_view: 是否增加浏览次数，默认True
            
        Returns:
            Optional[Product]: 商品对象
        """
        try:
            # 查询商品
            products = self.db.execute_query(
                "SELECT * FROM products WHERE product_id = ?",
                (product_id,)
            )
            
            if not products:
                raise ProductNotFoundError(f"商品ID {product_id} 不存在")
            
            product_data = products[0]
            
            # 增加浏览次数
            if increment_view:
                self.db.execute_update(
                    "UPDATE products SET view_count = view_count + 1 WHERE product_id = ?",
                    (product_id,)
                )
            
            # 创建 Product 对象
            product = Product(
                seller_id=product_data['seller_id'],
                title=product_data['title'],
                description=product_data['description'],
                price=product_data['price'],
                category=product_data['category'],
                stock=product_data['stock']
            )
            
            # 设置其他属性
            product.product_id = product_data['product_id']
            product.images = eval(product_data['images']) if product_data['images'] else []
            product.status = ProductStatus(product_data['status'])
            product.auctionable = bool(product_data['auctionable'])
            product.view_count = product_data['view_count'] + (1 if increment_view else 0)
            product.favorite_count = product_data['favorite_count']
            
            return product
            
        except ProductNotFoundError:
            raise
        except Exception as e:
            print(f"获取商品失败: {str(e)}")
            return None

    def search_products(self, keyword: str = None, category: str = None,
                       min_price: float = None, max_price: float = None,
                       limit: int = 20, offset: int = 0) -> List[Dict]:
        """
        搜索商品
        
        Args:
            keyword: 搜索关键词
            category: 商品分类(IP)
            min_price: 最低价格
            max_price: 最高价格
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            List[Dict]: 商品列表
        """
        try:
            # 构建基础查询（只搜索可售商品）
            query = "SELECT * FROM products WHERE status = 'available'"
            params = []
            
            # 添加关键词搜索（标题或描述中包含）
            if keyword:
                query += " AND (title LIKE ? OR description LIKE ?)"
                keyword_pattern = f"%{keyword}%"
                params.extend([keyword_pattern, keyword_pattern])
            
            # 添加分类筛选
            if category:
                query += " AND category = ?"
                params.append(category)
            
            # 添加价格范围筛选
            if min_price is not None:
                query += " AND price >= ?"
                params.append(min_price)
            
            if max_price is not None:
                query += " AND price <= ?"
                params.append(max_price)
            
            # 按创建时间降序排序
            query += " ORDER BY created_at DESC"
            
            # 添加分页
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            # 执行查询
            products = self.db.execute_query(query, tuple(params))
            
            # 转换为字典列表
            return [dict(product) for product in products]
            
        except Exception as e:
            print(f"搜索商品失败: {str(e)}")
            return []
    
    def get_products_by_seller(self, seller_id: int, include_removed: bool = False) -> List[Dict]:
        """
        获取卖家的所有商品
        
        Args:
            seller_id: 卖家ID
            include_removed: 是否包含已下架商品，默认False
            
        Returns:
            List[Dict]: 商品列表
        """
        try:
            # 构建查询
            if include_removed:
                # 包含所有状态的商品（用于卖家管理）
                query = """
                    SELECT * FROM products 
                    WHERE seller_id = ? 
                    ORDER BY created_at DESC
                """
            else:
                # 只返回可售商品（用于店铺展示）
                query = """
                    SELECT * FROM products 
                    WHERE seller_id = ? AND status = 'available'
                    ORDER BY created_at DESC
                """
            
            products = self.db.execute_query(query, (seller_id,))
            
            return [dict(product) for product in products]
            
        except Exception as e:
            print(f"获取卖家商品失败: {str(e)}")
            return []
    
    def get_products_by_category(self, category: str, 
                                limit: int = 20, offset: int = 0,
                                sort_by: str = 'newest') -> List[Dict]:
        """
        根据分类获取商品
        
        Args:
            category: 商品分类(IP)
            limit: 返回数量限制
            offset: 偏移量，用于分页
            sort_by: 排序方式 ('newest'=最新, 'price_asc'=价格升序, 
                    'price_desc'=价格降序, 'popular'=最受欢迎)
            
        Returns:
            List[Dict]: 商品列表
        """
        try:
            # 基础查询（只返回可售商品）
            query = """
                SELECT * FROM products 
                WHERE category = ? AND status = 'available'
            """
            
            # 根据排序方式添加 ORDER BY 子句
            if sort_by == 'newest':
                query += " ORDER BY created_at DESC"
            elif sort_by == 'price_asc':
                query += " ORDER BY price ASC"
            elif sort_by == 'price_desc':
                query += " ORDER BY price DESC"
            elif sort_by == 'popular':
                query += " ORDER BY view_count DESC, favorite_count DESC"
            else:
                # 默认按最新排序
                query += " ORDER BY created_at DESC"
            
            # 添加分页
            query += " LIMIT ? OFFSET ?"
            
            products = self.db.execute_query(query, (category, limit, offset))
            
            return [dict(product) for product in products]
            
        except Exception as e:
            print(f"获取分类商品失败: {str(e)}")
            return []
    
    def favorite_product(self, user_id: int, product_id: int) -> bool:
        """
        收藏商品
        
        Args:
            user_id: 用户ID
            product_id: 商品ID
            
        Returns:
            bool: 收藏是否成功
        """
        try:
            # 检查商品是否存在
            product = self.db.execute_query(
                "SELECT product_id FROM products WHERE product_id = ?",
                (product_id,)
            )
            if not product:
                raise ProductNotFoundError(f"商品ID {product_id} 不存在")
            
            # 检查是否已经收藏
            existing = self.db.execute_query(
                "SELECT * FROM favorites WHERE user_id = ? AND product_id = ?",
                (user_id, product_id)
            )
            
            if existing:
                print(f"商品ID {product_id} 已经在收藏列表中")
                return False
            
            # 添加收藏记录
            favorite_id = self.db.execute_insert(
                "INSERT INTO favorites (user_id, product_id) VALUES (?, ?)",
                (user_id, product_id)
            )
            
            if favorite_id:
                # 更新商品的收藏计数
                self.db.execute_update(
                    "UPDATE products SET favorite_count = favorite_count + 1 WHERE product_id = ?",
                    (product_id,)
                )
                print(f"✓ 收藏商品ID {product_id} 成功")
                return True
            
            return False
            
        except ProductNotFoundError:
            raise
        except Exception as e:
            print(f"收藏商品失败: {str(e)}")
            return False
    
    def unfavorite_product(self, user_id: int, product_id: int) -> bool:
        """
        取消收藏
        
        Args:
            user_id: 用户ID
            product_id: 商品ID
            
        Returns:
            bool: 取消收藏是否成功
        """
        try:
            # 检查收藏记录是否存在
            existing = self.db.execute_query(
                "SELECT * FROM favorites WHERE user_id = ? AND product_id = ?",
                (user_id, product_id)
            )
            
            if not existing:
                print(f"商品ID {product_id} 不在收藏列表中")
                return False
            
            # 删除收藏记录
            affected = self.db.execute_delete(
                "DELETE FROM favorites WHERE user_id = ? AND product_id = ?",
                (user_id, product_id)
            )
            
            if affected > 0:
                # 更新商品的收藏计数
                self.db.execute_update(
                    "UPDATE products SET favorite_count = favorite_count - 1 WHERE product_id = ?",
                    (product_id,)
                )
                print(f"✓ 取消收藏商品ID {product_id} 成功")
                return True
            
            return False
            
        except Exception as e:
            print(f"取消收藏失败: {str(e)}")
            return False
    
    def get_favorite_products(self, user_id: int) -> List[Dict]:
        """
        获取用户收藏的商品
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[Dict]: 收藏的商品列表
        """
        try:
            # 联表查询：获取收藏的商品详情
            query = """
                SELECT p.*, f.created_at as favorited_at
                FROM favorites f
                JOIN products p ON f.product_id = p.product_id
                WHERE f.user_id = ?
                ORDER BY f.created_at DESC
            """
            
            products = self.db.execute_query(query, (user_id,))
            
            return [dict(product) for product in products]
            
        except Exception as e:
            print(f"获取收藏商品失败: {str(e)}")
            return []
    
    def get_all_categories(self) -> List[str]:
        """
        获取所有商品分类
        
        Returns:
            List[str]: 分类列表
        """
        try:
            # 查询所有不重复的分类
            query = """
                SELECT DISTINCT category 
                FROM products 
                WHERE status = 'available'
                ORDER BY category
            """
            
            results = self.db.execute_query(query)
            
            # 提取分类名称
            categories = [row['category'] for row in results]
            
            return categories
            
        except Exception as e:
            print(f"获取分类列表失败: {str(e)}")
            return []
