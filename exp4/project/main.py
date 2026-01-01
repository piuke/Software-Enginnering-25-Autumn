"""
二次元网络商场系统 - 主程序入口
Anime Shopping Mall System - Main Entry Point

这是一个基于UML设计实现的二次元网络商场系统
支持商品交易、拍卖、社交交流等功能
"""

import sys
import json
from database import DatabaseManager
from services import (
    UserService, ProductService, OrderService,
    AuctionService, MessageService, ReportService
)
from models import User, Product, Order, Auction, Message, Report, Admin
from utils import Validator, Helper
from config import SYSTEM_CONFIG, PRODUCT_CATEGORIES
from config.i18n import get_i18n, t, set_language


class AnimeShoppingMall:
    """二次元网络商场系统主类"""
    
    def __init__(self):
        """初始化系统"""
        self.db_manager = DatabaseManager()
        self.user_service = UserService(self.db_manager)
        self.product_service = ProductService(self.db_manager)
        self.order_service = OrderService(self.db_manager)
        self.auction_service = AuctionService(self.db_manager)
        self.message_service = MessageService(self.db_manager)
        self.report_service = ReportService(self.db_manager)
        self.current_user = None
        self.i18n = get_i18n()
        
    def display_banner(self):
        """显示系统标题"""
        print("=" * 50)
        print(t('system.banner'))
        print(f"{t('common.version')}: {SYSTEM_CONFIG['version']}")
        print("=" * 50)
    
    def main_menu(self):
        """显示主菜单"""
        while True:
            print("\n" + "=" * 50)
            if self.current_user:
                print(f"{t('user.username')}: {self.current_user['username']}")
            else:
                print(t('system.not_logged_in'))
            print("=" * 50)
            
            if not self.current_user:
                print(f"1. {t('user.register')}")
                print(f"2. {t('user.login')}")
                print(f"3. {t('product.browse_products')}")
                print(f"4. {t('product.search_products')}")
                print(f"L. {t('system.switch_language')}")
                print(f"0. {t('common.exit')}")
            else:
                print(f"1. {t('product.browse_products')}")
                print(f"2. {t('product.search_products')}")
                print(f"3. {t('favorite.my_favorites')}")
                print(f"4. {t('order.my_orders')}")
                print(f"5. {t('message.messages')}")
                print(f"6. {t('user.profile')}")
                print(f"7. {t('seller.seller_functions')}")
                print(f"8. {t('report.report')}")
                print(f"9. {t('user.logout')}")
                print(f"L. {t('system.switch_language')}")
                print(f"0. {t('common.exit')}")
            
            choice = input(f"\n{t('common.please_select')}: ").strip()
            
            if choice == '0':
                print(t('system.thank_you'))
                sys.exit(0)
            elif choice.upper() == 'L':
                self.language_menu()
            elif not self.current_user:
                if choice == '1':
                    self.register_menu()
                elif choice == '2':
                    self.login_menu()
                elif choice == '3':
                    self.browse_products_menu()
                elif choice == '4':
                    self.search_products_menu()
                else:
                    print(t('common.invalid_choice'))
            else:
                if choice == '1':
                    self.browse_products_menu()
                elif choice == '2':
                    self.search_products_menu()
                elif choice == '3':
                    self.favorites_menu()
                elif choice == '4':
                    self.orders_menu()
                elif choice == '5':
                    self.messages_menu()
                elif choice == '6':
                    self.profile_menu()
                elif choice == '7':
                    self.seller_menu()
                elif choice == '8':
                    self.report_menu()
                elif choice == '9':
                    self.logout()
                else:
                    print(t('common.invalid_choice'))
    
    def language_menu(self):
        """语言切换菜单"""
        print("\n" + "=" * 50)
        print(f"{t('system.language_selection')} / Language Selection")
        print("=" * 50)
        print(f"1. {t('system.lang_zh_cn')}")
        print(f"2. {t('system.lang_en_us')}")
        print(f"3. {t('system.lang_ja_jp')}")
        print(f"0. {t('common.back')}")
        
        choice = input(f"\n{t('common.please_select')} / Please select: ").strip()
        
        if choice == '1':
            set_language('zh_CN')
            print(f"✓ {t('system.language_switched_zh')}")
        elif choice == '2':
            set_language('en_US')
            print(f"✓ {t('system.language_switched_en')}")
        elif choice == '3':
            set_language('ja_JP')
            print(f"✓ {t('system.language_switched_ja')}")
        elif choice == '0':
            return
        else:
            print(f"{t('system.invalid_choice_bilingual')} / Invalid choice")
    
    def register_menu(self):
        """用户注册菜单"""
        print(f"\n--- {t('user.register')} ---")
        username = input(f"{t('user.username')}: ").strip()
        password = input(f"{t('user.password')}: ").strip()
        email = input(f"{t('user.email')}: ").strip()
        
        is_seller_input = input(f"{t('user.is_seller')} (y/n): ").strip().lower()
        is_seller = is_seller_input == 'y'
        shop_name = None
        if is_seller:
            shop_name = input(f"{t('user.shop_name')}: ").strip()
        
        try:
            user_id = self.user_service.register(username, password, email, is_seller, shop_name)
            print(t('user.register_success', user_id=user_id))
        except Exception as e:
            print(t('user.register_failed', error=str(e)))
    
    def login_menu(self):
        """用户登录菜单"""
        print(f"\n--- {t('user.login')} ---")
        username = input(f"{t('user.username')}: ").strip()
        password = input(f"{t('user.password')}: ").strip()
        
        try:
            user = self.user_service.login(username, password)
            self.current_user = user
            print(t('user.login_success', username=user['username']))
        except Exception as e:
            print(t('user.login_failed', error=str(e)))
    
    def logout(self):
        """注销登录"""
        self.current_user = None
        print(t('user.logout_success'))
    
    def browse_products_menu(self):
        """浏览商品菜单"""
        while True:
            print(f"\n--- {t('product.browse_products')} ---")
            print(f"1. {t('feature.all_products')}")
            print(f"2. {t('feature.by_category')}")
            print(f"3. {t('feature.ongoing_auctions')}")
            print(f"0. {t('common.back')}")
            
            choice = input(f"\n{t('common.please_select')}: ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                self.show_all_products()
            elif choice == '2':
                self.browse_by_category()
            elif choice == '3':
                print(t('system.feature_not_implemented'))
            else:
                print(t('common.invalid_choice'))
    
    def show_all_products(self):
        """显示所有商品"""
        page = 1
        per_page = 10
        
        while True:
            print(f"\n{'='*50}")
            print(f"{t('feature.all_products')} - {t('common.page')} {page}")
            print(f"{'='*50}")
            
            offset = (page - 1) * per_page
            products = self.product_service.search_products(limit=per_page, offset=offset)
            
            if not products:
                print(t('product.no_products'))
                break
            
            for i, product in enumerate(products, 1):
                print(f"\n{i}. [{product['product_id']}] {product['title']}")
                print(f"   {t('product.price')}: ¥{product['price']:.2f}")
                print(f"   {t('product.category')}: {product['category']}")
                print(f"   {t('product.stock')}: {product['stock']}")
                print(f"   {t('product.views')}: {product['view_count']} | {t('product.favorites')}: {product['favorite_count']}")
            
            print(f"\n{'='*50}")
            print(f"1-{len(products)}: {t('common.view_details')}")
            print(f"N: {t('common.next_page')}")
            if page > 1:
                print(f"P: {t('common.previous_page')}")
            print(f"0: {t('common.back')}")
            
            action = input(f"\n{t('common.please_select')}: ").strip().upper()
            
            if action == '0':
                break
            elif action == 'N':
                page += 1
            elif action == 'P' and page > 1:
                page -= 1
            elif action.isdigit() and 1 <= int(action) <= len(products):
                self.show_product_detail(products[int(action) - 1]['product_id'])
    
    def browse_by_category(self):
        """按分类浏览"""
        # 获取所有分类
        categories = self.product_service.get_all_categories()
        
        if not categories:
            print(t('product.no_categories'))
            return
        
        print(f"\n{'='*50}")
        print(t('product.category_list'))
        print(f"{'='*50}")
        
        for i, category in enumerate(categories, 1):
            print(f"{i}. {category}")
        
        print(f"0. {t('common.back')}")
        
        choice = input(f"\n{t('common.please_select')}: ").strip()
        
        if choice == '0':
            return
        
        if choice.isdigit() and 1 <= int(choice) <= len(categories):
            selected_category = categories[int(choice) - 1]
            self.show_category_products(selected_category)
    
    def show_category_products(self, category):
        """显示指定分类的商品"""
        page = 1
        per_page = 10
        sort_by = 'newest'
        
        while True:
            print(f"\n{'='*50}")
            print(f"{t('product.category')}: {category} - {t('common.page')} {page}")
            print(f"{'='*50}")
            print(f"{t('product.sort_by')}: ", end='')
            if sort_by == 'newest':
                print(t('product.newest'))
            elif sort_by == 'price_asc':
                print(t('product.price_low_to_high'))
            elif sort_by == 'price_desc':
                print(t('product.price_high_to_low'))
            elif sort_by == 'popular':
                print(t('product.most_popular'))
            print(f"{'='*50}")
            
            offset = (page - 1) * per_page
            products = self.product_service.get_products_by_category(
                category=category,
                limit=per_page,
                offset=offset,
                sort_by=sort_by
            )
            
            if not products:
                print(t('product.no_products'))
                break
            
            for i, product in enumerate(products, 1):
                print(f"\n{i}. [{product['product_id']}] {product['title']}")
                print(f"   {t('product.price')}: ¥{product['price']:.2f}")
                print(f"   {t('product.stock')}: {product['stock']}")
            
            print(f"\n{'='*50}")
            print(f"1-{len(products)}: {t('common.view_details')}")
            print(f"S: {t('product.change_sort')}")
            print(f"N: {t('common.next_page')}")
            if page > 1:
                print(f"P: {t('common.previous_page')}")
            print(f"0: {t('common.back')}")
            
            action = input(f"\n{t('common.please_select')}: ").strip().upper()
            
            if action == '0':
                break
            elif action == 'N':
                page += 1
            elif action == 'P' and page > 1:
                page -= 1
            elif action == 'S':
                sort_by = self.select_sort_order()
                page = 1  # 重置到第一页
            elif action.isdigit() and 1 <= int(action) <= len(products):
                self.show_product_detail(products[int(action) - 1]['product_id'])
    
    def select_sort_order(self):
        """选择排序方式"""
        print(f"\n{t('product.sort_options')}:")
        print(f"1. {t('product.newest')}")
        print(f"2. {t('product.price_low_to_high')}")
        print(f"3. {t('product.price_high_to_low')}")
        print(f"4. {t('product.most_popular')}")
        
        choice = input(f"\n{t('common.please_select')}: ").strip()
        
        if choice == '1':
            return 'newest'
        elif choice == '2':
            return 'price_asc'
        elif choice == '3':
            return 'price_desc'
        elif choice == '4':
            return 'popular'
        else:
            return 'newest'
    
    def show_product_detail(self, product_id):
        """显示商品详情"""
        try:
            product = self.product_service.get_product_by_id(product_id)
            
            if not product:
                print(t('product.not_found'))
                return
            
            print(f"\n{'='*50}")
            print(f"{t('product.detail')}")
            print(f"{'='*50}")
            print(f"{t('product.id')}: {product.product_id}")
            print(f"{t('product.title')}: {product.title}")
            print(f"{t('product.description')}: {product.description}")
            print(f"{t('product.price')}: ¥{product.price:.2f}")
            print(f"{t('product.category')}: {product.category}")
            print(f"{t('product.stock')}: {product.stock}")
            print(f"{t('product.status')}: {product.status.value}")
            print(f"{t('product.views')}: {product.view_count}")
            print(f"{t('product.favorites')}: {product.favorite_count}")
            
            # 显示卖家信息
            seller_info = self.db_manager.execute_query(
                "SELECT shop_name, username FROM users WHERE user_id = ?",
                (product.seller_id,)
            )
            if seller_info:
                print(f"\n🏪 {t('message.seller_label')}: {seller_info[0]['shop_name']} (@{seller_info[0]['username']})")
            
            if self.current_user:
                print(f"\n{'='*50}")
                print(f"1. {t('favorite.add_to_favorites')}")
                print(f"2. {t('order.buy_now')}")
                print(f"3. 💬 {t('message.contact_seller')}")  # 新增：联系卖家
                print(f"0. {t('common.back')}")
                
                action = input(f"\n{t('common.please_select')}: ").strip()
                
                if action == '1':
                    if self.product_service.favorite_product(self.current_user['user_id'], product_id):
                        print(t('favorite.added'))
                    else:
                        print(t('favorite.already_added'))
                elif action == '2':
                    self._buy_now_flow(product.product_id, product)
                elif action == '3':
                    # 联系卖家（seller_id 现在就是 user_id）
                    seller_user_id = product.seller_id
                    # 防止自己联系自己
                    if seller_user_id == self.current_user['user_id']:
                        print(t('common.cannot_message_self'))
                    else:
                        # 直接打开与卖家的会话
                        self._conversation_menu(self.current_user['user_id'], seller_user_id)
            else:
                input(f"\n{t('common.press_enter')}")
                
        except Exception as e:
            print(f"{t('common.error')}: {str(e)}")
    
    def search_products_menu(self):
        """搜索商品菜单"""
        print(f"\n--- {t('product.search_products')} ---")
        
        # 输入搜索条件
        keyword = input(f"{t('product.search_keyword')} ({t('common.optional')}): ").strip()
        keyword = keyword if keyword else None
        
        # 选择分类
        print(f"\n{t('product.select_category')} ({t('common.optional')})")
        categories = self.product_service.get_all_categories()
        print(f"0. {t('common.all')}")
        for i, cat in enumerate(categories, 1):
            print(f"{i}. {cat}")
        
        cat_choice = input(f"\n{t('common.please_select')}: ").strip()
        category = None
        if cat_choice.isdigit() and int(cat_choice) > 0 and int(cat_choice) <= len(categories):
            category = categories[int(cat_choice) - 1]
        
        # 输入价格范围
        print(f"\n{t('product.price_range')} ({t('common.optional')})")
        min_price_input = input(f"{t('product.min_price')}: ").strip()
        max_price_input = input(f"{t('product.max_price')}: ").strip()
        
        min_price = float(min_price_input) if min_price_input else None
        max_price = float(max_price_input) if max_price_input else None
        
        # 执行搜索
        self.show_search_results(keyword, category, min_price, max_price)
    
    def show_search_results(self, keyword=None, category=None, min_price=None, max_price=None):
        """显示搜索结果"""
        page = 1
        per_page = 10
        
        # 构建搜索条件描述
        conditions = []
        if keyword:
            conditions.append(f"{t('product.keyword')}: {keyword}")
        if category:
            conditions.append(f"{t('product.category')}: {category}")
        if min_price is not None:
            conditions.append(f"{t('product.min_price')}: ¥{min_price}")
        if max_price is not None:
            conditions.append(f"{t('product.max_price')}: ¥{max_price}")
        
        while True:
            print(f"\n{'='*50}")
            print(f"{t('product.search_results')} - {t('common.page')} {page}")
            if conditions:
                print(f"{t('product.search_conditions')}: {', '.join(conditions)}")
            print(f"{'='*50}")
            
            offset = (page - 1) * per_page
            products = self.product_service.search_products(
                keyword=keyword,
                category=category,
                min_price=min_price,
                max_price=max_price,
                limit=per_page,
                offset=offset
            )
            
            if not products:
                print(t('product.no_results'))
                input(f"\n{t('common.press_enter')}")
                break
            
            print(f"\n{t('common.found')} {len(products)} {t('product.products')}")
            
            for i, product in enumerate(products, 1):
                print(f"\n{i}. [{product['product_id']}] {product['title']}")
                print(f"   {t('product.price')}: ¥{product['price']:.2f}")
                print(f"   {t('product.category')}: {product['category']}")
                print(f"   {t('product.stock')}: {product['stock']}")
                print(f"   {t('product.views')}: {product['view_count']} | {t('product.favorites')}: {product['favorite_count']}")
            
            print(f"\n{'='*50}")
            print(f"1-{len(products)}: {t('common.view_details')}")
            print(f"S: {t('product.new_search')}")
            print(f"N: {t('common.next_page')}")
            if page > 1:
                print(f"P: {t('common.previous_page')}")
            print(f"0: {t('common.back')}")
            
            action = input(f"\n{t('common.please_select')}: ").strip().upper()
            
            if action == '0':
                break
            elif action == 'N':
                page += 1
            elif action == 'P' and page > 1:
                page -= 1
            elif action == 'S':
                self.search_products_menu()
                break
            elif action.isdigit() and 1 <= int(action) <= len(products):
                self.show_product_detail(products[int(action) - 1]['product_id'])
    
    def favorites_menu(self):
        """收藏菜单"""
        if not self.current_user:
            print(t('user.please_login'))
            return
        
        while True:
            print(f"\n{'='*50}")
            print(f"{t('favorite.my_favorites')}")
            print(f"{'='*50}")
            
            # 获取收藏列表
            favorites = self.product_service.get_favorite_products(self.current_user['user_id'])
            
            if not favorites:
                print(t('favorite.empty'))
                print(f"\n0. {t('common.back')}")
                choice = input(f"\n{t('common.please_select')}: ").strip()
                if choice == '0':
                    break
                continue
            
            print(f"\n{t('common.total')}: {len(favorites)} {t('product.products')}\n")
            
            # 显示收藏列表
            for i, product in enumerate(favorites, 1):
                print(f"{i}. [{product['product_id']}] {product['title']}")
                print(f"   {t('product.price')}: ¥{product['price']:.2f}")
                print(f"   {t('product.category')}: {product['category']}")
                print(f"   {t('product.stock')}: {product['stock']}")
                print(f"   {t('product.status')}: {product['status']}")
                print(f"   {t('favorite.favorited_at')}: {product['favorited_at']}")
                print()
            
            print(f"{'='*50}")
            print(f"1-{len(favorites)}: {t('common.view_details')}")
            print(f"R: {t('favorite.remove_favorite')}")
            print(f"0: {t('common.back')}")
            
            action = input(f"\n{t('common.please_select')}: ").strip().upper()
            
            if action == '0':
                break
            elif action == 'R':
                self.remove_favorite_menu(favorites)
            elif action.isdigit() and 1 <= int(action) <= len(favorites):
                product_id = favorites[int(action) - 1]['product_id']
                self.show_product_detail_with_favorite_option(product_id)
    
    def remove_favorite_menu(self, favorites):
        """取消收藏菜单"""
        print(f"\n{t('favorite.select_to_remove')}:")
        
        for i, product in enumerate(favorites, 1):
            print(f"{i}. {product['title']}")
        
        print(f"0. {t('common.cancel')}")
        
        choice = input(f"\n{t('common.please_select')}: ").strip()
        
        if choice == '0':
            return
        
        if choice.isdigit() and 1 <= int(choice) <= len(favorites):
            product_id = favorites[int(choice) - 1]['product_id']
            product_title = favorites[int(choice) - 1]['title']
            
            # 确认
            confirm = input(f"\n{t('favorite.confirm_remove')} '{product_title}'? (y/n): ").strip().lower()
            
            if confirm == 'y':
                if self.product_service.unfavorite_product(self.current_user['user_id'], product_id):
                    print(f"✓ {t('favorite.removed')}")
                else:
                    print(f"✗ {t('favorite.remove_failed')}")
            else:
                print(t('common.cancelled'))
        else:
            print(t('common.invalid_choice'))
    
    def show_product_detail_with_favorite_option(self, product_id):
        """显示商品详情（带收藏选项）"""
        try:
            product = self.product_service.get_product_by_id(product_id, increment_view=False)
            
            if not product:
                print(t('product.not_found'))
                return
            
            # 检查是否已收藏
            favorites = self.product_service.get_favorite_products(self.current_user['user_id'])
            is_favorited = any(f['product_id'] == product_id for f in favorites)
            
            print(f"\n{'='*50}")
            print(f"{t('product.detail')}")
            print(f"{'='*50}")
            print(f"{t('product.id')}: {product.product_id}")
            print(f"{t('product.title')}: {product.title}")
            print(f"{t('product.description')}: {product.description}")
            print(f"{t('product.price')}: ¥{product.price:.2f}")
            print(f"{t('product.category')}: {product.category}")
            print(f"{t('product.stock')}: {product.stock}")
            print(f"{t('product.status')}: {product.status.value}")
            print(f"{t('product.views')}: {product.view_count}")
            print(f"{t('product.favorites')}: {product.favorite_count}")
            
            print(f"\n{'='*50}")
            if is_favorited:
                print(f"1. {t('favorite.remove_from_favorites')}")
            else:
                print(f"1. {t('favorite.add_to_favorites')}")
            print(f"2. {t('order.buy_now')}")
            print(f"0. {t('common.back')}")
            
            action = input(f"\n{t('common.please_select')}: ").strip()
            
            if action == '1':
                if is_favorited:
                    if self.product_service.unfavorite_product(self.current_user['user_id'], product_id):
                        print(f"✓ {t('favorite.removed')}")
                else:
                    if self.product_service.favorite_product(self.current_user['user_id'], product_id):
                        print(f"✓ {t('favorite.added')}")
                    else:
                        print(t('favorite.already_added'))
            elif action == '2':
                self._buy_now_flow(product.product_id, product)
                
        except Exception as e:
            print(f"{t('common.error')}: {str(e)}")
    
    def orders_menu(self):
        """订单菜单"""
        if not self.current_user:
            print(t('user.please_login'))
            return
        user_id = self.current_user['user_id']
        while True:
            print(f"\n{'='*50}")
            print(f"--- {t('order.my_orders')} ---")
            print(f"{'='*50}")
            print(f"1. {t('order.orders')}")
            print(f"2. {t('order.statistics')}")
            print(f"0. {t('common.back')}")

            choice = input(f"\n{t('common.please_select')}: ").strip()
            if choice == '0':
                break
            elif choice == '1':
                self._buyer_orders_list(user_id)
            elif choice == '2':
                stats = self.order_service.get_order_statistics(user_id, is_seller=False)
                print(f"\n{t('order.statistics')}: ")
                print(f"- {t('common.total')}: {stats.get('total_orders',0)}")
                by_status = stats.get('by_status', {})
                for k, v in by_status.items():
                    print(f"  · {self._display_order_status(k)}: {v}")
                print(f"- total_spent: {stats.get('total_spent', 0):.2f}")
                input(f"\n{t('common.press_enter')}")
            else:
                print(t('common.invalid_choice'))

    def _display_order_status(self, status: str) -> str:
        mapping = {
            'pending': t('order.status_pending'),
            'paid': t('order.status_paid'),
            'shipped': t('order.status_shipped'),
            'completed': t('order.status_completed'),
            'cancelled': t('order.status_cancelled'),
            'refunded': t('order.status_refunded'),
            'refund_requested': t('order.status_refund_requested'),
            'refund_rejected': t('order.status_refund_rejected'),
            'cancel_requested': t('order.status_cancel_requested'),
            'cancel_rejected': t('order.status_cancel_rejected'),
        }
        return mapping.get(status, status)

    def _buyer_orders_list(self, buyer_id: int):
        rows = self.order_service.get_orders_by_buyer(buyer_id)
        if not rows:
            print(t('order.no_orders'))
            return
        while True:
            print(f"\n{'='*50}")
            print(f"{t('order.orders')}")
            print(f"{'='*50}")
            for i, o in enumerate(rows, 1):
                print(f"{i}. [#{o['order_id']}] P#{o['product_id']} x{o['quantity']}  ¥{o['total_price']:.2f}  {self._display_order_status(o['status'])}")
                print(f"   {o.get('created_at','')}")
            print(f"\n1-{len(rows)}: {t('common.view_details')}")
            print(f"0. {t('common.back')}")
            sel = input(f"\n{t('common.please_select')}: ").strip()
            if sel == '0':
                break
            if sel.isdigit() and 1 <= int(sel) <= len(rows):
                self._buyer_order_detail(rows[int(sel)-1], buyer_id)
                # 刷新
                rows = self.order_service.get_orders_by_buyer(buyer_id)
            else:
                print(t('common.invalid_choice'))

    def _buyer_order_detail(self, order_row: dict, buyer_id: int):
        o = order_row
        print(f"\n{'='*50}")
        print(f"{t('order.order')} #{o['order_id']}")
        print(f"{'='*50}")
        print(f"Product: #{o['product_id']}  x{o['quantity']}  ¥{o['total_price']:.2f}")
        print(f"{t('order.order_status')}: {self._display_order_status(o['status'])}")
        print(f"{t('product.created_at')}: {o.get('created_at','')}")
        
        # 如果订单状态是退款被拒绝，显示拒绝原因
        if o['status'] == 'refund_rejected' and o.get('refund_reject_reason'):
            print(f"🚫 {t('order.refund_reject_reason')}: {o['refund_reject_reason']}")
        
        # 如果订单状态是取消被拒绝，显示拒绝原因
        if o['status'] == 'cancel_rejected' and o.get('cancel_reject_reason'):
            print(f"🚫 {t('order.cancel_reject_reason_label')}: {o['cancel_reject_reason']}")
        
        # 动态操作
        actions = []
        if o['status'] == 'pending':
            actions = [('1', t('order.action_pay')), ('2', t('order.action_cancel'))]
        elif o['status'] == 'paid':
            actions = [('1', t('order.action_cancel')), ('2', t('order.action_request_refund'))]
        elif o['status'] == 'shipped':
            actions = [('1', t('order.action_confirm_receipt')), ('2', t('order.action_cancel'))]
        elif o['status'] == 'completed':
            actions = [('1', t('order.action_request_refund'))]
        elif o['status'] == 'refund_requested':
            actions = []  # 等待卖家审批退款
        elif o['status'] == 'cancel_requested':
            actions = []  # 等待卖家审批取消
        else:
            actions = []
        for key, label in actions:
            print(f"{key}. {label}")
        # 新增：联系卖家
        print(f"C. 💬 {t('message.contact_seller')}")
        print(f"0. {t('common.back')}")
        act = input(f"\n{t('common.please_select')}: ").strip().upper()
        if act == '0':
            return
        if act == 'C':
            # 联系卖家（seller_id 现在就是 user_id）
            seller_user_id = o['seller_id']
            self._conversation_menu(buyer_id, seller_user_id)
            return
        try:
            if o['status'] == 'pending' and act == '1':
                ok = self.order_service.pay_order(o['order_id'], 'confirm')
                print(t('order.pay_success') if ok else t('order.pay_failed'))
            elif o['status'] == 'pending' and act == '2':
                reason = input(f"{t('order.cancel_reason_label')}: ").strip()
                ok = self.order_service.request_cancel_order(o['order_id'], buyer_id, reason or 'buyer_cancel')
                print(t('common.success') if ok else t('common.failed'))
            elif o['status'] == 'paid' and act == '1':
                reason = input(f"{t('order.cancel_reason_label')}: ").strip()
                ok = self.order_service.request_cancel_order(o['order_id'], buyer_id, reason or 'buyer_cancel')
                print(t('common.success') if ok else t('common.failed'))
            elif o['status'] == 'paid' and act == '2':
                reason = input(f"{t('order.refund_reason_label')}: ").strip()
                ok = self.order_service.request_refund(o['order_id'], buyer_id, reason or 'buyer_refund')
                print(t('common.success') if ok else t('common.failed'))
            elif o['status'] == 'shipped' and act == '1':
                ok = self.order_service.confirm_receipt(o['order_id'], buyer_id)
                print(t('common.success') if ok else t('common.failed'))
            elif o['status'] == 'shipped' and act == '2':
                reason = input(f"{t('order.cancel_reason_label')}: ").strip()
                ok = self.order_service.request_cancel_order(o['order_id'], buyer_id, reason or 'buyer_cancel_after_ship')
                print(t('common.success') if ok else t('common.failed'))
            elif o['status'] == 'completed' and act == '1':
                reason = input(f"{t('order.refund_reason_label')}: ").strip()
                ok = self.order_service.request_refund(o['order_id'], buyer_id, reason or 'buyer_refund_after_complete')
                print(t('common.success') if ok else t('common.failed'))
            else:
                print(t('common.invalid_choice'))
        except Exception as e:
            print(f"{t('common.error')}: {str(e)}")

    def _buy_now_flow(self, product_id: int, product=None):
        if not self.current_user:
            print(t('user.please_login'))
            return
        # 尝试获取商品（若未提供）
        if product is None:
            product = self.product_service.get_product_by_id(product_id)
            if not product:
                print(t('product.not_found'))
                return
        try:
            qty_input = input(f"{t('order.quantity')}: ").strip()
            quantity = int(qty_input or '1')
            if quantity <= 0:
                print(t('product.stock_invalid_format'))
                return
        except ValueError:
            print(t('product.stock_invalid_format'))
            return
        address = input(f"{t('order.shipping_address')}: ").strip()
        if not address:
            print(t('common.cancelled'))
            return
        order_id = self.order_service.create_order(
            buyer_id=self.current_user['user_id'],
            product_id=product_id,
            quantity=quantity,
            shipping_address=address
        )
        if order_id:
            print(t('order.create_success_brief', order_id=order_id))
            pay_now = input(t('order.pay_now')).strip().lower()
            if pay_now == 'y':
                ok = self.order_service.pay_order(order_id, 'confirm')
                print(t('order.pay_success') if ok else t('order.pay_failed'))
        else:
            print(t('order.create_failed'))
    
    def messages_menu(self):
        """消息菜单 - Telegram风格联系人列表"""
        if not self.current_user:
            print(t('user.please_login'))
            return

        user_id = self.current_user['user_id']
        while True:
            unread_total = self.message_service.get_unread_count(user_id)
            print(f"\n{'='*50}")
            print(f"--- {t('message.messages')} ---")
            print(t('message.unread_total', count=unread_total))
            print(f"{'='*50}")
            print(f"1. {t('message.contacts')}")  # 默认联系人列表
            print(f"2. {t('message.search_users')}")  # 搜索用户开始聊天
            print(f"3. {t('message.search_messages')}")  # 搜索消息内容
            print(f"0. {t('common.back')}")

            choice = input(f"\n{t('common.please_select')}: ").strip()
            if choice == '0':
                break
            elif choice == '1':
                self._contacts_list_menu(user_id)  # 重命名为联系人列表
            elif choice == '2':
                self._search_users_and_chat(user_id)  # 新功能：搜索用户并聊天
            elif choice == '3':
                self._search_messages_flow(user_id)
            else:
                print(t('common.invalid_choice'))

    def _contacts_list_menu(self, user_id: int):
        """联系人列表 - Telegram风格"""
    def _contacts_list_menu(self, user_id: int):
        """联系人列表 - Telegram风格"""
        rows = self.message_service.get_user_messages(user_id, limit=50)
        
        # 构建联系人列表（按最后消息时间排序）
        contacts = []
        for row in rows:
            peer_id = row['receiver_id'] if row['sender_id'] == user_id else row['sender_id']
            peer = self._get_user_by_id(peer_id)
            if not peer:
                continue
            
            peer_name = peer['username']
            unread_from_peer = self._get_unread_from_peer(user_id, peer_id)
            
            # 检查是否是卖家
            seller_info = self.db_manager.execute_query(
                "SELECT shop_name FROM users WHERE user_id = ?",
                (peer_id,)
            )
            is_seller = len(seller_info) > 0
            shop_name = seller_info[0]['shop_name'] if is_seller else None
            
            contacts.append({
                'peer_id': peer_id,
                'peer_name': peer_name,
                'shop_name': shop_name,
                'is_seller': is_seller,
                'last': row,
                'unread': unread_from_peer,
            })

        while True:
            print(f"\n{'='*50}")
            print(f"📱 {t('message.contacts')}")
            print(f"{'='*50}")
            
            if not contacts:
                print(t('message.no_conversations'))
                print(f"\n💡 {t('message.search_users')} → 2")
                print(f"0. {t('common.back')}")
                choice = input(f"\n{t('common.please_select')}: ").strip()
                if choice == '0':
                    break
                elif choice == '2':
                    # 跳转到搜索用户
                    self._search_users_and_chat(user_id)
                    # 刷新联系人列表
                    rows = self.message_service.get_user_messages(user_id, limit=50)
                    contacts = []
                    for row in rows:
                        peer_id = row['receiver_id'] if row['sender_id'] == user_id else row['sender_id']
                        peer = self._get_user_by_id(peer_id)
                        if not peer:
                            continue
                        peer_name = peer['username']
                        unread_from_peer = self._get_unread_from_peer(user_id, peer_id)
                        seller_info = self.db_manager.execute_query(
                            "SELECT shop_name FROM users WHERE user_id = ?", (peer_id,)
                        )
                        is_seller = len(seller_info) > 0
                        shop_name = seller_info[0]['shop_name'] if is_seller else None
                        contacts.append({
                            'peer_id': peer_id,
                            'peer_name': peer_name,
                            'shop_name': shop_name,
                            'is_seller': is_seller,
                            'last': row,
                            'unread': unread_from_peer,
                        })
                continue
            
            for i, c in enumerate(contacts, 1):
                last = c['last']
                prefix = t('message.me_label') if last['sender_id'] == user_id else c['peer_name']
                content = (last['content'] or '')
                content = content if len(content) <= 25 else content[:22] + '...'
                ts = last.get('created_at', '')
                
                # 未读徽标
                unread_badge = f"🔴{c['unread']}" if c['unread'] else ''
                
                # 卖家标识
                seller_badge = f"🏪{c['shop_name']}" if c['is_seller'] else ''
                
                # 组合显示
                display_name = c['peer_name']
                if seller_badge:
                    display_name = f"{display_name} [{seller_badge}]"
                
                print(f"{i}. {display_name}")
                print(f"   {prefix}: {content} {unread_badge}")
                print(f"   {ts}")
            
            print(f"\n{'='*50}")
            print(f"1-{len(contacts)}: {t('common.view_details')}")
            print(f"0. {t('common.back')}")

            sel = input(f"\n{t('common.please_select')}: ").strip()
            if sel == '0':
                break
            if sel.isdigit() and 1 <= int(sel) <= len(contacts):
                self._conversation_menu(user_id, contacts[int(sel)-1]['peer_id'])
                # 刷新联系人列表
                rows = self.message_service.get_user_messages(user_id, limit=50)
                contacts = []
                for row in rows:
                    peer_id = row['receiver_id'] if row['sender_id'] == user_id else row['sender_id']
                    peer = self._get_user_by_id(peer_id)
                    if not peer:
                        continue
                    peer_name = peer['username']
                    unread_from_peer = self._get_unread_from_peer(user_id, peer_id)
                    seller_info = self.db_manager.execute_query(
                        "SELECT shop_name FROM users WHERE user_id = ?", (peer_id,)
                    )
                    is_seller = len(seller_info) > 0
                    shop_name = seller_info[0]['shop_name'] if is_seller else None
                    contacts.append({
                        'peer_id': peer_id,
                        'peer_name': peer_name,
                        'shop_name': shop_name,
                        'is_seller': is_seller,
                        'last': row,
                        'unread': unread_from_peer,
                    })
            else:
                print(t('common.invalid_choice'))

    def _search_users_and_chat(self, user_id: int):
        """搜索用户并开始聊天"""
        print(f"\n{'='*50}")
        print(f"🔍 {t('message.search_users')}")
        print(f"{'='*50}")
        
        keyword = input(f"{t('message.enter_username')}: ").strip()
        if not keyword:
            print(t('common.cancelled'))
            return
        
        # 搜索用户（模糊匹配）
        users = self.db_manager.execute_query(
            "SELECT user_id, username, email FROM users WHERE username LIKE ? AND user_id != ? LIMIT 20",
            (f"%{keyword}%", user_id)
        )
        
        if not users:
            print(t('message.no_users_found'))
            return
        
        print(f"\n{t('message.user_search_results')}:")
        for i, user in enumerate(users, 1):
            # 检查是否是卖家
            seller_info = self.db_manager.execute_query(
                "SELECT shop_name FROM users WHERE user_id = ?",
                (user['user_id'],)
            )
            seller_badge = f" [🏪{seller_info[0]['shop_name']}]" if seller_info else ""
            print(f"{i}. {user['username']}{seller_badge}")
        
        print(f"0. {t('common.back')}")
        
        choice = input(f"\n{t('common.please_select')}: ").strip()
        if choice == '0':
            return
        
        if choice.isdigit() and 1 <= int(choice) <= len(users):
            selected_user = users[int(choice) - 1]
            # 直接打开会话
            self._conversation_menu(user_id, selected_user['user_id'])
        else:
            print(t('common.invalid_choice'))

    def _conversation_menu(self, user_id: int, other_user_id: int):
        """会话详情菜单"""
        other = self._get_user_by_id(other_user_id)
        other_name = other['username'] if other else f"User#{other_user_id}"
        
        # 检查是否是卖家
        seller_info = self.db_manager.execute_query(
            "SELECT shop_name FROM users WHERE user_id = ?",
            (other_user_id,)
        )
        shop_display = f" [🏪{seller_info[0]['shop_name']}]" if seller_info else ""
        
        # 自动标记该会话的所有消息为已读
        self.message_service.mark_conversation_as_read(user_id, other_user_id)
        
        while True:
            rows = self.message_service.get_conversation(user_id, other_user_id, limit=200, offset=0)
            print(f"\n{'='*50}")
            print(t('message.conversation_with', username=other_name + shop_display))
            print(f"{'='*50}")
            if not rows:
                print(t('message.no_messages'))
            else:
                for r in rows:
                    mine = (r['sender_id'] == user_id)
                    sender = t('message.me_label') if mine else other_name
                    status = r.get('status', '')
                    read_tag = '' if mine or status == 'read' else f"({t('message.unread_tag')})"
                    ts = r.get('created_at', '')
                    
                    # 处理服务消息的翻译
                    msg_type = r.get('msg_type', 'text')
                    if msg_type == 'service':
                        try:
                            # 解析 JSON 格式的服务消息
                            msg_data = json.loads(r['content'])
                            translation_key = msg_data.get('key', '')
                            params = msg_data.get('params', {})
                            # 使用翻译键和参数获取本地化消息
                            content = t(translation_key, **params)
                        except (json.JSONDecodeError, KeyError):
                            # 如果解析失败,显示原始内容(兼容旧格式)
                            content = r['content']
                    else:
                        content = r['content']
                    
                    print(f"{sender}: {content}  {read_tag}  [{ts}]  ({t('message.message_id_label')}: {r['msg_id']})")

            print(f"\n1. {t('message.send_message')}")
            print(f"2. {t('message.delete_message')}")
            print(f"3. {t('message.refresh_conversation')}")
            print(f"0. {t('common.back')}")

            act = input(f"\n{t('common.please_select')}: ").strip()
            if act == '0':
                break
            elif act == '1':
                content = input(f"{t('message.content_label')}: ").strip()
                if content:
                    try:
                        self.message_service.send_message(user_id, other_user_id, content)
                        print(f"✓ {t('message.sent_success')}")
                    except Exception as e:
                        print(f"✗ {str(e)}")
            elif act == '2':
                msg_id_input = input(f"{t('message.enter_message_id')}: ").strip()
                if msg_id_input.isdigit():
                    ok = self.message_service.delete_message(int(msg_id_input), user_id)
                    print(f"✓ {t('message.delete_success')}" if ok else t('message.delete_failed'))
                else:
                    print(t('common.invalid_choice'))
            elif act == '3':
                # 刷新会话，重新标记为已读
                self.message_service.mark_conversation_as_read(user_id, other_user_id)
                continue
            else:
                print(t('common.invalid_choice'))

    def _send_message_flow(self, user_id: int):
        to_username = input(f"{t('message.receiver_username')}: ").strip()
        if not to_username:
            print(t('common.cancelled'))
            return
        target = self._get_user_by_name(to_username)
        if not target:
            print(t('user.user_not_found', identifier=to_username))
            return
        content = input(f"{t('message.content_label')}: ").strip()
        if not content:
            print(t('common.cancelled'))
            return
        try:
            self.message_service.send_message(user_id, target['user_id'], content)
            print(f"✓ {t('message.sent_success')}")
        except Exception as e:
            print(f"✗ {str(e)}")

    def _search_messages_flow(self, user_id: int):
        keyword = input(f"{t('message.search_keyword_label')}: ").strip()
        if not keyword:
            print(t('common.cancelled'))
            return
        rows = self.message_service.search_messages(user_id, keyword, limit=50)
        if not rows:
            print(t('message.no_messages_found'))
            return
        print(f"\n{'='*50}")
        print(t('message.search_found', count=len(rows)))
        for r in rows:
            s = self._get_user_by_id(r['sender_id'])
            sname = s['username'] if s else f"User#{r['sender_id']}"
            rv = self._get_user_by_id(r['receiver_id'])
            rname = rv['username'] if rv else f"User#{r['receiver_id']}"
            ts = r.get('created_at','')
            content = r['content']
            print(f"[{r['msg_id']}] {sname} -> {rname}: {content} [{ts}]")

    def _get_user_by_id(self, uid: int):
        rows = self.db_manager.execute_query("SELECT user_id, username FROM users WHERE user_id=?", (uid,))
        return rows[0] if rows else None

    def _get_user_by_name(self, username: str):
        rows = self.db_manager.execute_query("SELECT user_id, username FROM users WHERE username=?", (username,))
        return rows[0] if rows else None

    def _get_unread_from_peer(self, me: int, peer: int) -> int:
        rows = self.db_manager.execute_query(
            "SELECT COUNT(*) AS cnt FROM messages WHERE receiver_id=? AND sender_id=? AND status <> 'read'",
            (me, peer)
        )
        return int(rows[0]['cnt']) if rows else 0
    
    def profile_menu(self):
        """个人中心菜单"""
        print(f"\n--- {t('feature.personal_center')} ---")
        # TODO: 实现个人中心功能
        print(t('system.feature_not_implemented'))
    
    def seller_menu(self):
        """卖家功能菜单"""
        if not self.current_user:
            print(t('user.please_login'))
            return
        
        # 检查当前用户是否是卖家
        if self.current_user.get('role') != 'seller':
            print(f"\n{t('seller.not_seller_error')}")
            print(t('seller.not_seller_hint'))
            return
        
        while True:
            print(f"\n{'='*50}")
            print(f"--- {t('seller.seller_functions')} ---")
            print(f"{t('seller.shop_label')}: {self.current_user.get('shop_name', 'N/A')}")
            print(f"{'='*50}")
            print(f"1. {t('product.add_product')}")
            print(f"2. {t('seller.manage_products')}")
            print(f"3. {t('auction.auction')}")
            print(f"4. {t('seller.manage_orders')}")
            print(f"0. {t('common.back')}")
            
            choice = input(f"\n{t('common.please_select')}: ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                self.add_product_menu(self.current_user['user_id'])
            elif choice == '2':
                self.manage_products_menu(self.current_user['user_id'])
            elif choice == '3':
                print(t('system.feature_not_implemented'))
            elif choice == '4':
                self.manage_orders_menu(self.current_user['user_id'])
            else:
                print(t('common.invalid_choice'))

    def manage_orders_menu(self, seller_id: int):
        while True:
            rows = self.order_service.get_orders_by_seller(seller_id)
            print(f"\n{'='*50}")
            print(f"--- {t('seller.manage_orders')} ---")
            print(f"{'='*50}")
            if not rows:
                print(t('order.no_orders'))
                print(f"0. {t('common.back')}")
                if input(f"\n{t('common.please_select')}: ").strip() == '0':
                    break
                continue
            for i, o in enumerate(rows, 1):
                print(f"{i}. [#{o['order_id']}] Buyer#{o['buyer_id']} P#{o['product_id']} x{o['quantity']}  ¥{o['total_price']:.2f}  {self._display_order_status(o['status'])}")
                print(f"   {o.get('created_at','')}")
            print(f"\n1-{len(rows)}: {t('common.view_details')}")
            print(f"0. {t('common.back')}")
            sel = input(f"\n{t('common.please_select')}: ").strip()
            if sel == '0':
                break
            if sel.isdigit() and 1 <= int(sel) <= len(rows):
                self._seller_order_detail(rows[int(sel)-1], seller_id)
            else:
                print(t('common.invalid_choice'))

    def _seller_order_detail(self, order_row: dict, seller_id: int):
        o = order_row
        print(f"\n{'='*50}")
        print(f"{t('order.order')} #{o['order_id']}")
        print(f"{'='*50}")
        print(f"Buyer: #{o['buyer_id']}  Product: #{o['product_id']}  x{o['quantity']}  ¥{o['total_price']:.2f}")
        print(f"{t('order.order_status')}: {self._display_order_status(o['status'])}")
        print(f"{t('product.created_at')}: {o.get('created_at','')}")
        
        # 如果订单状态是退款被拒绝，显示拒绝原因（卖家也能看到自己的拒绝理由）
        if o['status'] == 'refund_rejected' and o.get('refund_reject_reason'):
            print(f"🚫 {t('order.refund_reject_reason')}: {o['refund_reject_reason']}")
        
        # 如果订单状态是取消被拒绝，显示拒绝原因
        if o['status'] == 'cancel_rejected' and o.get('cancel_reject_reason'):
            print(f"🚫 {t('order.cancel_reject_reason_label')}: {o['cancel_reject_reason']}")
        
        actions = []
        if o['status'] == 'paid':
            actions = [('1', t('order.action_ship'))]
        elif o['status'] == 'refund_requested':
            actions = [('1', t('order.action_approve_refund')), ('2', t('order.action_reject_refund'))]
        elif o['status'] == 'cancel_requested':
            actions = [('1', t('order.action_approve_cancel')), ('2', t('order.action_reject_cancel'))]
        elif o['status'] == 'shipped':
            actions = []
        print("\n".join([f"{k}. {label}" for k, label in actions]))
        # 新增：联系买家
        print(f"C. 💬 {t('message.contact_buyer')}")
        print(f"0. {t('common.back')}")
        act = input(f"\n{t('common.please_select')}: ").strip().upper()
        if act == '0':
            return
        if act == 'C':
            # 联系买家
            self._conversation_menu(self.current_user['user_id'], o['buyer_id'])
            return
        if o['status'] == 'paid' and act == '1':
            tn = input(f"{t('order.enter_tracking_number')}: ").strip()
            if not tn:
                print(t('common.cancelled'))
                return
            ok = self.order_service.ship_order(o['order_id'], seller_id, tn)
            print(t('common.success') if ok else t('common.failed'))
        elif o['status'] == 'refund_requested' and act == '1':
            ok = self.order_service.approve_refund(o['order_id'], seller_id)
            print(t('common.success') if ok else t('common.failed'))
        elif o['status'] == 'refund_requested' and act == '2':
            reason = input(f"{t('order.enter_reject_reason')} ").strip()
            ok = self.order_service.reject_refund(o['order_id'], seller_id, reason)
            print(t('common.success') if ok else t('common.failed'))
        elif o['status'] == 'cancel_requested' and act == '1':
            ok = self.order_service.approve_cancel(o['order_id'], seller_id)
            print(t('common.success') if ok else t('common.failed'))
        elif o['status'] == 'cancel_requested' and act == '2':
            reason = input(f"{t('order.enter_reject_reason')} ").strip()
            ok = self.order_service.reject_cancel(o['order_id'], seller_id, reason)
            print(t('common.success') if ok else t('common.failed'))
    
    def add_product_menu(self, seller_id: int):
        """添加商品菜单"""
        print(f"\n{'='*50}")
        print(f"--- {t('product.add_product')} ---")
        print(f"{'='*50}")
        
        # 输入商品标题
        title = input(f"{t('product.title')}: ").strip()
        if not title:
            print(t('product.title_required'))
            return
        
        # 输入商品描述
        description = input(f"{t('product.description')}: ").strip()
        if not description:
            print(t('product.description_required'))
            return
        
        # 输入价格
        try:
            price_input = input(f"{t('product.price')} (¥): ").strip()
            price = float(price_input)
            if price <= 0:
                print(t('product.price_must_positive'))
                return
        except ValueError:
            print(t('product.price_invalid_format'))
            return
        
        # 选择分类
        print(f"\n{t('product.select_category')}:")
        for i, category in enumerate(PRODUCT_CATEGORIES, 1):
            print(f"{i}. {category}")
        
        try:
            cat_choice = input(f"\n{t('common.please_select')}: ").strip()
            cat_index = int(cat_choice) - 1
            if cat_index < 0 or cat_index >= len(PRODUCT_CATEGORIES):
                print(t('product.category_invalid'))
                return
            category = PRODUCT_CATEGORIES[cat_index]
        except ValueError:
            print(t('product.category_invalid_format'))
            return
        
        # 输入库存
        try:
            stock_input = input(f"{t('product.stock')} ({t('product.stock_default_hint', value=1)}): ").strip()
            stock = int(stock_input) if stock_input else 1
            if stock < 0:
                print(t('product.stock_negative'))
                return
        except ValueError:
            print(t('product.stock_invalid_format'))
            return
        
        # 是否支持拍卖
        auctionable_input = input(f"{t('product.auctionable_prompt')}: ").strip().lower()
        auctionable = 1 if auctionable_input == 'y' else 0
        
        # 确认创建
        print(f"\n{'='*50}")
        print(t('product.preview'))
        print(f"{t('product.preview_title')}: {title}")
        print(f"{t('product.preview_description')}: {description}")
        print(f"{t('product.preview_price')}: ¥{price:.2f}")
        print(f"{t('product.preview_category')}: {category}")
        print(f"{t('product.preview_stock')}: {stock}")
        print(f"{t('product.preview_auctionable')}: {t('common.yes') if auctionable else t('common.no')}")
        print(f"{'='*50}")
        
        confirm = input("\n" + t('product.confirm_create')).strip().lower()
        
        if confirm != 'y':
            print(t('common.cancelled'))
            return
        
        # 创建商品
        product_data = {
            'title': title,
            'description': description,
            'price': price,
            'category': category,
            'stock': stock,
            'auctionable': auctionable
        }
        
        product_id = self.product_service.create_product(seller_id, product_data)
        
        if product_id:
            print(f"\n{t('product.create_success', product_id=product_id)}")
        else:
            print(f"\n{t('product.create_failed')}")
    
    def manage_products_menu(self, seller_id: int):
        """管理商品菜单"""
        while True:
            print(f"\n{'='*50}")
            print(f"--- {t('seller.manage_products')} ---")
            print(f"{'='*50}")
            
            # 获取卖家的所有商品（包括已下架）
            products = self.product_service.get_products_by_seller(seller_id, include_removed=True)
            
            if not products:
                print(f"\n{t('product.no_products')}")
                print(f"\n0. {t('common.back')}")
                choice = input(f"\n{t('common.please_select')}: ").strip()
                if choice == '0':
                    break
                continue
            
            print(f"\n{t('product.total_products', count=len(products))}:\n")
            
            # 显示商品列表
            for i, product in enumerate(products, 1):
                status_display = {
                    'available': t('product.status_available'),
                    'sold_out': t('product.status_sold_out'),
                    'removed': t('product.status_removed')
                }.get(product['status'], product['status'])
                
                print(f"{i}. [{product['product_id']}] {product['title']}")
                print(f"   {t('product.price')}: ¥{product['price']:.2f} | {t('product.stock')}: {product['stock']} | {t('product.status')}: {status_display}")
                print(f"   {t('product.category')}: {product['category']} | {t('product.views')}: {product['view_count']} | {t('product.favorites')}: {product['favorite_count']}")
                print()
            
            print(f"{'='*50}")
            print(f"1-{len(products)}: {t('product.view_edit')}")
            print(f"0: {t('common.back')}")
            
            action = input(f"\n{t('common.please_select')}: ").strip()
            
            if action == '0':
                break
            elif action.isdigit() and 1 <= int(action) <= len(products):
                self.edit_product_menu(products[int(action) - 1], seller_id)
            else:
                print(t('common.invalid_choice'))
    
    def edit_product_menu(self, product_data: dict, seller_id: int):
        """编辑商品菜单"""
        while True:
            print(f"\n{'='*50}")
            print(f"{t('product.detail')} - {t('product.id')}: {product_data['product_id']}")
            print(f"{'='*50}")
            print(f"{t('product.preview_title')}: {product_data['title']}")
            print(f"{t('product.preview_description')}: {product_data['description']}")
            print(f"{t('product.price')}: ¥{product_data['price']:.2f}")
            print(f"{t('product.category')}: {product_data['category']}")
            print(f"{t('product.stock')}: {product_data['stock']}")
            print(f"{t('product.status')}: {product_data['status']}")
            print(f"{t('product.views')}: {product_data['view_count']}")
            print(f"{t('product.favorites')}: {product_data['favorite_count']}")
            print(f"{t('product.created_at')}: {product_data['created_at']}")
            print(f"{'='*50}")
            print(f"1. {t('product.menu_edit_title')}")
            print(f"2. {t('product.menu_edit_description')}")
            print(f"3. {t('product.menu_edit_price')}")
            print(f"4. {t('product.menu_edit_category')}")
            print(f"5. {t('product.menu_edit_stock')}")
            print(f"6. {t('product.remove_product') if product_data['status'] == 'available' else t('product.relist_product')}")
            print(f"0. {t('common.back')}")
            
            choice = input(f"\n{t('common.please_select')}: ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                new_title = input(t('product.new_title_prompt', current=product_data['title'])).strip()
                if new_title:
                    if self.product_service.update_product(product_data['product_id'], {'title': new_title}):
                        print(t('product.title_updated'))
                        product_data['title'] = new_title
                    else:
                        print(t('product.update_failed'))
            elif choice == '2':
                new_desc = input(t('product.new_description_prompt', current=product_data['description'])).strip()
                if new_desc:
                    if self.product_service.update_product(product_data['product_id'], {'description': new_desc}):
                        print(t('product.description_updated'))
                        product_data['description'] = new_desc
                    else:
                        print(t('product.update_failed'))
            elif choice == '3':
                try:
                    new_price = float(input(t('product.new_price_prompt', current=f"{product_data['price']:.2f}")).strip())
                    if new_price > 0:
                        if self.product_service.update_product(product_data['product_id'], {'price': new_price}):
                            print(t('product.price_updated'))
                            product_data['price'] = new_price
                        else:
                            print(t('product.update_failed'))
                    else:
                        print(t('product.price_must_positive'))
                except ValueError:
                    print(t('product.price_invalid_format'))
            elif choice == '4':
                print(f"\n{t('product.select_category')}:")
                for i, category in enumerate(PRODUCT_CATEGORIES, 1):
                    print(f"{i}. {category}")
                try:
                    cat_choice = int(input(f"\n{t('common.please_select')}: ").strip())
                    if 1 <= cat_choice <= len(PRODUCT_CATEGORIES):
                        new_category = PRODUCT_CATEGORIES[cat_choice - 1]
                        if self.product_service.update_product(product_data['product_id'], {'category': new_category}):
                            print(t('product.category_updated'))
                            product_data['category'] = new_category
                        else:
                            print(t('product.update_failed'))
                    else:
                        print(t('common.invalid_choice'))
                except ValueError:
                    print(t('product.input_invalid_format'))
            elif choice == '5':
                try:
                    new_stock = int(input(t('product.new_stock_prompt', current=product_data['stock'])).strip())
                    if new_stock >= 0:
                        if self.product_service.update_product(product_data['product_id'], {'stock': new_stock}):
                            print(t('product.stock_updated'))
                            product_data['stock'] = new_stock
                        else:
                            print(t('product.update_failed'))
                    else:
                        print(t('product.stock_negative'))
                except ValueError:
                    print(t('product.stock_invalid_format'))
            elif choice == '6':
                if product_data['status'] == 'available':
                    # 下架商品
                    confirm = input(t('product.confirm_remove')).strip().lower()
                    if confirm == 'y':
                        if self.product_service.delete_product(product_data['product_id'], seller_id):
                            print(t('product.remove_success'))
                            product_data['status'] = 'removed'
                        else:
                            print(t('product.remove_failed'))
                else:
                    # 重新上架
                    confirm = input(t('product.confirm_relist')).strip().lower()
                    if confirm == 'y':
                        if self.product_service.update_product(product_data['product_id'], {'status': 'available'}):
                            print(t('product.relist_success'))
                            product_data['status'] = 'available'
                        else:
                            print(t('product.relist_failed'))
            else:
                print(t('common.invalid_choice'))
    
    def report_menu(self):
        """举报功能菜单"""
        print(f"\n--- {t('report.report')} ---")
        # TODO: 实现举报功能
        print(t('system.feature_not_implemented'))
    
    def run(self):
        """运行系统"""
        self.display_banner()
        print(f"\n{t('system.welcome_message')}")
        print(t('system.system_info'))
        print(t('system.framework_complete'))
        self.main_menu()


def main():
    """主函数"""
    try:
        app = AnimeShoppingMall()
        app.run()
    except KeyboardInterrupt:
        print(f"\n\n{t('system.interrupted')}")
    except Exception as e:
        print(t('system.error_occurred', error=str(e)))
        if SYSTEM_CONFIG['debug']:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
