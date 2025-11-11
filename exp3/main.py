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
        print(f"\n--- {t('product.browse_products')} ---")
        print(f"1. {t('feature.all_products')}")
        print(f"2. {t('feature.by_category')}")
        print(f"3. {t('feature.ongoing_auctions')}")
        
        choice = input(f"{t('common.please_select')}: ").strip()
        # TODO: 实现浏览商品功能
        print(t('system.feature_not_implemented'))
    
    def search_products_menu(self):
        """搜索商品菜单"""
        print(f"\n--- {t('product.search_products')} ---")
        keyword = input(f"{t('common.please_select')}: ").strip()
        # TODO: 实现搜索功能
        print(t('system.feature_not_implemented'))
    
    def favorites_menu(self):
        """收藏菜单"""
        print(f"\n--- {t('favorite.my_favorites')} ---")
        # TODO: 实现收藏功能
        print(t('system.feature_not_implemented'))
    
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
