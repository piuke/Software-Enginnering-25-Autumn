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
        
    def display_banner(self):
        """显示系统标题"""
        print("=" * 50)
        print(f"{SYSTEM_CONFIG['app_name']}")
        print(f"版本: {SYSTEM_CONFIG['version']}")
        print("=" * 50)
    
    def main_menu(self):
        """显示主菜单"""
        while True:
            print("\n" + "=" * 50)
            if self.current_user:
                print(f"当前用户: {self.current_user['username']}")
            else:
                print("未登录")
            print("=" * 50)
            
            if not self.current_user:
                print("1. 用户注册")
                print("2. 用户登录")
                print("3. 浏览商品")
                print("4. 搜索商品")
                print("0. 退出系统")
            else:
                print("1. 浏览商品")
                print("2. 搜索商品")
                print("3. 我的收藏")
                print("4. 我的订单")
                print("5. 消息中心")
                print("6. 个人中心")
                print("7. 卖家功能")
                print("8. 举报功能")
                print("9. 注销登录")
                print("0. 退出系统")
            
            choice = input("\n请选择功能: ").strip()
            
            if choice == '0':
                print("感谢使用,再见!")
                sys.exit(0)
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
                    print("无效选择,请重试")
    
    def register_menu(self):
        """用户注册菜单"""
        print("\n--- 用户注册 ---")
        username = input("用户名: ").strip()
        password = input("密码: ").strip()
        email = input("邮箱: ").strip()
        
        is_seller = input("是否注册为卖家? (y/n): ").strip().lower() == 'y'
        shop_name = None
        if is_seller:
            shop_name = input("店铺名称: ").strip()
        
        # TODO: 调用用户服务注册
        user_id = self.user_service.register(username, password, email, is_seller, shop_name)
        if user_id:
            print(f"注册成功! 用户ID: {user_id}.")
        else:
            print(f"注册失败,请重试. Error_id: {user_id}")
    
    def login_menu(self):
        """用户登录菜单"""
        print("\n--- 用户登录 ---")
        username = input("用户名: ").strip()
        password = input("密码: ").strip()
        
        # TODO: 调用用户服务登录
        print("登录功能待实现...")
    
    def logout(self):
        """注销登录"""
        self.current_user = None
        print("已注销登录")
    
    def browse_products_menu(self):
        """浏览商品菜单"""
        print("\n--- 浏览商品 ---")
        print("1. 全部商品")
        print("2. 按分类浏览")
        print("3. 正在拍卖")
        
        choice = input("请选择: ").strip()
        # TODO: 实现浏览商品功能
        print("浏览商品功能待实现...")
    
    def search_products_menu(self):
        """搜索商品菜单"""
        print("\n--- 搜索商品 ---")
        keyword = input("请输入搜索关键词: ").strip()
        # TODO: 实现搜索功能
        print("搜索功能待实现...")
    
    def favorites_menu(self):
        """收藏菜单"""
        print("\n--- 我的收藏 ---")
        # TODO: 实现收藏功能
        print("收藏功能待实现...")
    
    def orders_menu(self):
        """订单菜单"""
        print("\n--- 我的订单 ---")
        # TODO: 实现订单功能
        print("订单功能待实现...")
    
    def messages_menu(self):
        """消息菜单"""
        print("\n--- 消息中心 ---")
        # TODO: 实现消息功能
        print("消息功能待实现...")
    
    def profile_menu(self):
        """个人中心菜单"""
        print("\n--- 个人中心 ---")
        # TODO: 实现个人中心功能
        print("个人中心功能待实现...")
    
    def seller_menu(self):
        """卖家功能菜单"""
        print("\n--- 卖家功能 ---")
        print("1. 发布商品")
        print("2. 我的商品")
        print("3. 创建拍卖")
        print("4. 订单管理")
        
        choice = input("请选择: ").strip()
        # TODO: 实现卖家功能
        print("卖家功能待实现...")
    
    def report_menu(self):
        """举报功能菜单"""
        print("\n--- 举报功能 ---")
        # TODO: 实现举报功能
        print("举报功能待实现...")
    
    def run(self):
        """运行系统"""
        self.display_banner()
        print("\n欢迎使用二次元网络商场系统!")
        print("这是一个基于UML设计实现的完整系统框架")
        print("目前已完成数据模型、服务层和数据库的框架搭建")
        self.main_menu()


def main():
    """主函数"""
    try:
        app = AnimeShoppingMall()
        app.run()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n发生错误: {e}")
        if SYSTEM_CONFIG['debug']:
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
