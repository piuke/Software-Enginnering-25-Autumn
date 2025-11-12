"""
二次元网络商场系统 - 主程序入口
Anime Shopping Mall System - Main Entry Point

这是一个基于UML设计实现的二次元网络商场系统
支持商品交易、拍卖、社交交流等功能
"""

import sys
from database import DatabaseManager
from services import (
    UserService, ProductService, OrderService,
    AuctionService, MessageService, ReportService
)
from models import User, Seller, Product, Order, Auction, Message, Report, Admin
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
        print(f"版本: {SYSTEM_CONFIG['version']}")
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
                    print("无效选择,请重试")
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
        print("1. 简体中文 (Simplified Chinese)")
        print("2. English")
        print("3. 日本語 (Japanese)")
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
            
            if self.current_user:
                print(f"\n{'='*50}")
                print(f"1. {t('favorite.add_to_favorites')}")
                print(f"2. {t('order.buy_now')}")
                print(f"0. {t('common.back')}")
                
                action = input(f"\n{t('common.please_select')}: ").strip()
                
                if action == '1':
                    if self.product_service.favorite_product(self.current_user['user_id'], product_id):
                        print(t('favorite.added'))
                    else:
                        print(t('favorite.already_added'))
                elif action == '2':
                    print(t('system.feature_not_implemented'))
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
                print(t('system.feature_not_implemented'))
                
        except Exception as e:
            print(f"{t('common.error')}: {str(e)}")
    
    def orders_menu(self):
        """订单菜单"""
        print(f"\n--- {t('order.my_orders')} ---")
        # TODO: 实现订单功能
        print(t('system.feature_not_implemented'))
    
    def messages_menu(self):
        """消息菜单"""
        print(f"\n--- {t('message.messages')} ---")
        # TODO: 实现消息功能
        print(t('system.feature_not_implemented'))
    
    def profile_menu(self):
        """个人中心菜单"""
        print(f"\n--- {t('feature.personal_center')} ---")
        # TODO: 实现个人中心功能
        print(t('system.feature_not_implemented'))
    
    def seller_menu(self):
        """卖家功能菜单"""
        print(f"\n--- {t('seller.seller_functions')} ---")
        print(f"1. {t('product.add_product')}")
        print(f"2. {t('seller.manage_products')}")
        print(f"3. {t('auction.auction')}")
        print(f"4. {t('seller.manage_orders')}")
        
        choice = input(f"{t('common.please_select')}: ").strip()
        # TODO: 实现卖家功能
        print(t('system.feature_not_implemented'))
    
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
