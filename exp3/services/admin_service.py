"""
Admin Service - 管理员服务层
处理管理员相关的业务逻辑
"""

from typing import Optional, List, Dict
from datetime import datetime, timedelta
from utils.exceptions import (
    ProductNotFoundError,
    UserNotFoundError,
    PermissionDeniedError
)


class AdminService:
    """
    管理员服务类
    提供管理员专用的管理功能
    """
    
    def __init__(self, db_manager):
        """
        初始化管理员服务
        
        Args:
            db_manager: 数据库管理器实例
        """
        self.db = db_manager
    
    def verify_admin(self, user_id: int) -> Dict:
        """
        验证用户是否是管理员
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 用户信息（包含角色）
            
        Raises:
            PermissionDeniedError: 如果不是管理员
        """
        user = self.db.execute_query(
            "SELECT user_id, username, role FROM users WHERE user_id = ?",
            (user_id,)
        )
        
        if not user:
            raise UserNotFoundError(f"用户ID {user_id} 不存在")
        
        user_data = user[0]
        if user_data['role'] not in ['admin', 'superadmin']:
            raise PermissionDeniedError(f"用户 {user_data['username']} 不是管理员")
        
        return dict(user_data)
    
    def remove_product(self, admin_id: int, product_id: int, reason: str = "") -> bool:
        """
        管理员下架商品
        
        Args:
            admin_id: 管理员ID
            product_id: 商品ID
            reason: 下架原因
            
        Returns:
            bool: 下架是否成功
        """
        try:
            # 验证管理员权限
            admin = self.verify_admin(admin_id)
            
            # 检查商品是否存在
            product = self.db.execute_query(
                "SELECT product_id, title, seller_id FROM products WHERE product_id = ?",
                (product_id,)
            )
            
            if not product:
                raise ProductNotFoundError(f"商品ID {product_id} 不存在")
            
            # 软删除商品
            query = """
                UPDATE products 
                SET status = 'removed', updated_at = CURRENT_TIMESTAMP
                WHERE product_id = ?
            """
            
            affected_rows = self.db.execute_update(query, (product_id,))
            
            if affected_rows > 0:
                # 记录管理操作日志
                self._log_admin_action(
                    admin_id, 
                    'remove_product', 
                    f"下架商品: {product[0]['title']} (ID: {product_id}), 原因: {reason}"
                )
                print(f"✓ 管理员 {admin['username']} 下架了商品ID {product_id}")
                return True
            
            return False
            
        except (UserNotFoundError, PermissionDeniedError, ProductNotFoundError):
            raise
        except Exception as e:
            print(f"管理员下架商品失败: {str(e)}")
            return False
    
    def ban_user(self, admin_id: int, user_id: int, 
                 duration_days: int = 30, reason: str = "") -> bool:
        """
        封禁用户
        
        Args:
            admin_id: 管理员ID
            user_id: 要封禁的用户ID
            duration_days: 封禁天数（0表示永久封禁）
            reason: 封禁原因
            
        Returns:
            bool: 封禁是否成功
        """
        try:
            # 验证管理员权限
            admin = self.verify_admin(admin_id)
            
            # 检查用户是否存在
            user = self.db.execute_query(
                "SELECT user_id, username, role FROM users WHERE user_id = ?",
                (user_id,)
            )
            
            if not user:
                raise UserNotFoundError(f"用户ID {user_id} 不存在")
            
            # 不能封禁管理员（除非是超级管理员操作）
            if user[0]['role'] in ['admin', 'superadmin'] and admin['role'] != 'superadmin':
                raise PermissionDeniedError("普通管理员无法封禁其他管理员")
            
            # 计算封禁结束时间
            if duration_days > 0:
                ban_until = (datetime.now() + timedelta(days=duration_days)).isoformat()
            else:
                ban_until = None  # 永久封禁
            
            # 更新用户状态（添加封禁信息到profile）
            profile_update = f'{{"banned": true, "ban_until": "{ban_until}", "ban_reason": "{reason}"}}'
            
            query = """
                UPDATE users 
                SET profile = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """
            
            affected_rows = self.db.execute_update(query, (profile_update, user_id))
            
            if affected_rows > 0:
                # 记录管理操作日志
                ban_type = f"{duration_days}天" if duration_days > 0 else "永久"
                self._log_admin_action(
                    admin_id,
                    'ban_user',
                    f"封禁用户: {user[0]['username']} (ID: {user_id}), {ban_type}, 原因: {reason}"
                )
                print(f"✓ 管理员 {admin['username']} 封禁了用户 {user[0]['username']}")
                return True
            
            return False
            
        except (UserNotFoundError, PermissionDeniedError):
            raise
        except Exception as e:
            print(f"封禁用户失败: {str(e)}")
            return False
    
    def unban_user(self, admin_id: int, user_id: int) -> bool:
        """
        解封用户
        
        Args:
            admin_id: 管理员ID
            user_id: 要解封的用户ID
            
        Returns:
            bool: 解封是否成功
        """
        try:
            # 验证管理员权限
            admin = self.verify_admin(admin_id)
            
            # 检查用户是否存在
            user = self.db.execute_query(
                "SELECT user_id, username FROM users WHERE user_id = ?",
                (user_id,)
            )
            
            if not user:
                raise UserNotFoundError(f"用户ID {user_id} 不存在")
            
            # 清除封禁信息
            query = """
                UPDATE users 
                SET profile = '{}', updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """
            
            affected_rows = self.db.execute_update(query, (user_id,))
            
            if affected_rows > 0:
                # 记录管理操作日志
                self._log_admin_action(
                    admin_id,
                    'unban_user',
                    f"解封用户: {user[0]['username']} (ID: {user_id})"
                )
                print(f"✓ 管理员 {admin['username']} 解封了用户 {user[0]['username']}")
                return True
            
            return False
            
        except (UserNotFoundError, PermissionDeniedError):
            raise
        except Exception as e:
            print(f"解封用户失败: {str(e)}")
            return False
    
    def get_all_users(self, admin_id: int, limit: int = 50, offset: int = 0) -> List[Dict]:
        """
        获取所有用户列表
        
        Args:
            admin_id: 管理员ID
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            List[Dict]: 用户列表
        """
        try:
            # 验证管理员权限
            self.verify_admin(admin_id)
            
            query = """
                SELECT user_id, username, email, role, is_verified, 
                       profile, created_at, updated_at
                FROM users
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            
            users = self.db.execute_query(query, (limit, offset))
            return [dict(user) for user in users]
            
        except (UserNotFoundError, PermissionDeniedError):
            raise
        except Exception as e:
            print(f"获取用户列表失败: {str(e)}")
            return []
    
    def get_all_products(self, admin_id: int, limit: int = 50, offset: int = 0) -> List[Dict]:
        """
        获取所有商品列表
        
        Args:
            admin_id: 管理员ID
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            List[Dict]: 商品列表
        """
        try:
            # 验证管理员权限
            self.verify_admin(admin_id)
            
            query = """
                SELECT p.*, s.shop_name, u.username as seller_username
                FROM products p
                JOIN sellers s ON p.seller_id = s.seller_id
                JOIN users u ON s.user_id = u.user_id
                ORDER BY p.created_at DESC
                LIMIT ? OFFSET ?
            """
            
            products = self.db.execute_query(query, (limit, offset))
            return [dict(product) for product in products]
            
        except (UserNotFoundError, PermissionDeniedError):
            raise
        except Exception as e:
            print(f"获取商品列表失败: {str(e)}")
            return []
    
    def get_pending_reports(self, admin_id: int) -> List[Dict]:
        """
        获取待审核的举报列表
        
        Args:
            admin_id: 管理员ID
            
        Returns:
            List[Dict]: 举报列表
        """
        try:
            # 验证管理员权限
            self.verify_admin(admin_id)
            
            query = """
                SELECT r.*, u.username as reporter_username
                FROM reports r
                JOIN users u ON r.reporter_id = u.user_id
                WHERE r.status = 'pending'
                ORDER BY r.created_at ASC
            """
            
            reports = self.db.execute_query(query)
            return [dict(report) for report in reports]
            
        except (UserNotFoundError, PermissionDeniedError):
            raise
        except Exception as e:
            print(f"获取举报列表失败: {str(e)}")
            return []
    
    def review_report(self, admin_id: int, report_id: int, 
                     approved: bool, result: str = "") -> bool:
        """
        审核举报
        
        Args:
            admin_id: 管理员ID
            report_id: 举报ID
            approved: 是否通过
            result: 审核结果说明
            
        Returns:
            bool: 审核是否成功
        """
        try:
            # 验证管理员权限
            admin = self.verify_admin(admin_id)
            
            # 检查举报是否存在
            report = self.db.execute_query(
                "SELECT * FROM reports WHERE report_id = ?",
                (report_id,)
            )
            
            if not report:
                raise ValueError(f"举报ID {report_id} 不存在")
            
            # 更新举报状态
            status = 'approved' if approved else 'rejected'
            query = """
                UPDATE reports 
                SET status = ?, admin_id = ?, result = ?, 
                    reviewed_at = CURRENT_TIMESTAMP
                WHERE report_id = ?
            """
            
            affected_rows = self.db.execute_update(
                query, 
                (status, admin_id, result, report_id)
            )
            
            if affected_rows > 0:
                # 如果举报通过，执行相应的处理（如下架商品、封禁用户等）
                if approved:
                    self._handle_approved_report(report[0])
                
                # 记录管理操作日志
                self._log_admin_action(
                    admin_id,
                    'review_report',
                    f"审核举报ID {report_id}: {status}, 结果: {result}"
                )
                print(f"✓ 管理员 {admin['username']} 审核了举报ID {report_id}")
                return True
            
            return False
            
        except (UserNotFoundError, PermissionDeniedError):
            raise
        except Exception as e:
            print(f"审核举报失败: {str(e)}")
            return False
    
    def get_statistics(self, admin_id: int) -> Dict:
        """
        获取平台统计数据
        
        Args:
            admin_id: 管理员ID
            
        Returns:
            Dict: 统计数据
        """
        try:
            # 验证管理员权限
            self.verify_admin(admin_id)
            
            stats = {}
            
            # 用户统计
            user_count = self.db.execute_query("SELECT COUNT(*) as count FROM users")
            stats['total_users'] = user_count[0]['count'] if user_count else 0
            
            # 商品统计
            product_count = self.db.execute_query("SELECT COUNT(*) as count FROM products")
            stats['total_products'] = product_count[0]['count'] if product_count else 0
            
            # 订单统计
            order_count = self.db.execute_query("SELECT COUNT(*) as count FROM orders")
            stats['total_orders'] = order_count[0]['count'] if order_count else 0
            
            # 待审核举报数
            pending_reports = self.db.execute_query(
                "SELECT COUNT(*) as count FROM reports WHERE status = 'pending'"
            )
            stats['pending_reports'] = pending_reports[0]['count'] if pending_reports else 0
            
            # 今日新增用户
            today_users = self.db.execute_query(
                "SELECT COUNT(*) as count FROM users WHERE DATE(created_at) = DATE('now')"
            )
            stats['today_new_users'] = today_users[0]['count'] if today_users else 0
            
            return stats
            
        except (UserNotFoundError, PermissionDeniedError):
            raise
        except Exception as e:
            print(f"获取统计数据失败: {str(e)}")
            return {}
    
    def set_user_role(self, admin_id: int, user_id: int, new_role: str) -> bool:
        """
        设置用户角色（超级管理员专用）
        
        Args:
            admin_id: 管理员ID（必须是超级管理员）
            user_id: 目标用户ID
            new_role: 新角色 (user/admin/superadmin)
            
        Returns:
            bool: 设置是否成功
        """
        try:
            # 验证是否是超级管理员
            admin = self.verify_admin(admin_id)
            if admin['role'] != 'superadmin':
                raise PermissionDeniedError("只有超级管理员可以设置用户角色")
            
            # 验证新角色
            if new_role not in ['user', 'admin', 'superadmin']:
                raise ValueError(f"无效的角色: {new_role}")
            
            # 检查目标用户
            user = self.db.execute_query(
                "SELECT user_id, username, role FROM users WHERE user_id = ?",
                (user_id,)
            )
            
            if not user:
                raise UserNotFoundError(f"用户ID {user_id} 不存在")
            
            # 更新角色
            query = """
                UPDATE users 
                SET role = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """
            
            affected_rows = self.db.execute_update(query, (new_role, user_id))
            
            if affected_rows > 0:
                # 记录管理操作日志
                self._log_admin_action(
                    admin_id,
                    'set_user_role',
                    f"设置用户 {user[0]['username']} 的角色: {user[0]['role']} -> {new_role}"
                )
                print(f"✓ 超级管理员设置用户 {user[0]['username']} 为 {new_role}")
                return True
            
            return False
            
        except (UserNotFoundError, PermissionDeniedError):
            raise
        except Exception as e:
            print(f"设置用户角色失败: {str(e)}")
            return False
    
    def _handle_approved_report(self, report: Dict) -> None:
        """
        处理通过的举报
        
        Args:
            report: 举报信息
        """
        report_type = report.get('report_type')
        target_id = report.get('target_id')
        
        # 根据举报类型执行相应操作
        if report_type == 'product' and target_id:
            # 下架商品
            self.db.execute_update(
                "UPDATE products SET status = 'removed' WHERE product_id = ?",
                (target_id,)
            )
        elif report_type == 'user' and target_id:
            # 封禁用户
            profile_update = '{"banned": true, "ban_reason": "违规行为"}'
            self.db.execute_update(
                "UPDATE users SET profile = ? WHERE user_id = ?",
                (profile_update, target_id)
            )
    
    def _log_admin_action(self, admin_id: int, action_type: str, details: str) -> None:
        """
        记录管理员操作日志
        
        Args:
            admin_id: 管理员ID
            action_type: 操作类型
            details: 操作详情
        """
        try:
            # 创建日志表（如果不存在）
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS admin_logs (
                        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        admin_id INTEGER NOT NULL,
                        action_type TEXT NOT NULL,
                        details TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (admin_id) REFERENCES users(user_id)
                    )
                """)
            
            # 插入日志
            self.db.execute_insert(
                "INSERT INTO admin_logs (admin_id, action_type, details) VALUES (?, ?, ?)",
                (admin_id, action_type, details)
            )
        except Exception as e:
            print(f"记录管理员日志失败: {str(e)}")
