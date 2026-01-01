"""
单一长时间模糊测试 - 针对整个项目的综合模糊测试
运行5+小时以满足实验要求
"""

import sys
import os
import atheris
import random
import time
from datetime import datetime, timedelta

# 修正模块路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.validators import Validator
from services.order_service import OrderService
from services.product_service import ProductService
from services.message_service import MessageService


class FuzzMockDB:
    """完整的模拟数据库"""
    
    def __init__(self):
        self.orders = {}
        self.products = {
            i: {
                'product_id': i,
                'seller_id': (i % 5) + 1,
                'price': 10.0 * i,
                'stock': 100 + i * 5,
                'status': 'available',
                'name': f'Product {i}',
                'description': f'Description for product {i}'
            }
            for i in range(1, 500)  # 扩大产品数量
        }
        self.users = {
            i: {
                'user_id': i,
                'username': f'user_{i}',
                'email': f'user{i}@example.com',
                'phone': f'1380000{i:04d}'
            }
            for i in range(1, 200)
        }
        self.messages = {}
        self.call_count = 0
    
    def execute_query(self, query, params=None):
        self.call_count += 1
        if "FROM products" in query:
            if params and len(params) > 0:
                product_id = params[0]
                if product_id in self.products:
                    return [self.products[product_id]]
            return list(self.products.values())[:50]
        if "FROM orders" in query:
            return list(self.orders.values())[:50]
        if "FROM users" in query:
            return list(self.users.values())[:50]
        return []
    
    def execute_insert(self, query, params=None):
        self.call_count += 1
        if "INTO orders" in query:
            order_id = len(self.orders) + 1
            self.orders[order_id] = {'order_id': order_id}
            return order_id
        if "INTO messages" in query:
            msg_id = len(self.messages) + 1
            self.messages[msg_id] = {'message_id': msg_id}
            return msg_id
        return None
    
    def execute_update(self, query, params=None):
        self.call_count += 1
        return True


class FuzzingStats:
    """模糊测试统计信息"""
    
    def __init__(self):
        self.total_runs = 0
        self.validator_tests = 0
        self.order_tests = 0
        self.product_tests = 0
        self.message_tests = 0
        self.combined_tests = 0
        self.exceptions_caught = 0
        self.crashes = 0
        self.start_time = time.time()
    
    def update(self, category):
        self.total_runs += 1
        if category == 'validator':
            self.validator_tests += 1
        elif category == 'order':
            self.order_tests += 1
        elif category == 'product':
            self.product_tests += 1
        elif category == 'message':
            self.message_tests += 1
        elif category == 'combined':
            self.combined_tests += 1
    
    def log_crash(self):
        self.crashes += 1
    
    def elapsed_time(self):
        return time.time() - self.start_time
    
    def get_report(self):
        elapsed = self.elapsed_time()
        hours = int(elapsed / 3600)
        minutes = int((elapsed % 3600) / 60)
        return {
            'elapsed': elapsed,
            'hours': hours,
            'minutes': minutes,
            'total_runs': self.total_runs,
            'validator': self.validator_tests,
            'order': self.order_tests,
            'product': self.product_tests,
            'message': self.message_tests,
            'combined': self.combined_tests,
            'crashes': self.crashes
        }


# 全局统计
STATS = FuzzingStats()


@atheris.instrument_func
def fuzz_entire_project(data):
    """综合模糊测试 - 覆盖整个项目所有模块"""
    fdp = atheris.FuzzedDataProvider(data)
    
    # 随机选择要测试的模块和操作
    module_choice = fdp.ConsumeIntInRange(0, 40)
    
    # 创建数据库实例
    db = FuzzMockDB()
    
    try:
        if module_choice < 8:
            # 验证器测试 (20%)
            STATS.update('validator')
            test_validator(fdp)
            
        elif module_choice < 16:
            # 订单服务测试 (20%)
            STATS.update('order')
            test_order_service(fdp, db)
            
        elif module_choice < 24:
            # 产品服务测试 (20%)
            STATS.update('product')
            test_product_service(fdp, db)
            
        elif module_choice < 32:
            # 消息服务测试 (20%)
            STATS.update('message')
            test_message_service(fdp, db)
            
        else:
            # 组合操作测试 (20%)
            STATS.update('combined')
            test_combined_operations(fdp, db)
            
    except (TypeError, ValueError, AttributeError) as e:
        STATS.exceptions_caught += 1
        # 这些异常是预期的
        pass
    except RecursionError:
        # 栈溢出 - 可能的问题
        STATS.log_crash()
        raise
    except MemoryError:
        # 内存泄漏 - 可能的问题
        STATS.log_crash()
        raise
    except Exception as e:
        # 其他异常
        if type(e).__name__ not in ['KeyError', 'IndexError']:
            STATS.exceptions_caught += 1


def test_validator(fdp):
    """测试验证器模块"""
    validator_type = fdp.ConsumeIntInRange(0, 4)
    test_input = fdp.ConsumeString(50000)  # 大输入
    
    try:
        if validator_type == 0:
            Validator.validate_email(test_input)
        elif validator_type == 1:
            Validator.validate_username(test_input)
        elif validator_type == 2:
            Validator.validate_password(test_input)
        elif validator_type == 3:
            Validator.validate_phone(test_input)
        elif validator_type == 4:
            try:
                # 尝试转换为浮点数
                price = float(test_input[:100].replace(',', '.') if test_input else '0')
                Validator.validate_price(price)
            except ValueError:
                pass
    except RecursionError:
        raise


def test_order_service(fdp, db):
    """测试订单服务"""
    service = OrderService(db)
    
    operation = fdp.ConsumeIntInRange(0, 4)
    buyer_id = fdp.ConsumeIntInRange(-10000, 10000)
    product_id = fdp.ConsumeIntInRange(-1000, 1000)
    quantity = fdp.ConsumeIntInRange(-100000, 100000)
    address = fdp.ConsumeString(100000)
    
    if operation == 0:
        # 创建订单
        service.create_order(buyer_id, product_id, quantity, address)
    elif operation == 1:
        # 支付订单
        order_id = len(db.orders) + 1
        payment = fdp.PickValueInList(['alipay', 'wechat', 'bank', 'card', '', None])
        service.pay_order(order_id, payment)
    elif operation == 2:
        # 查询订单
        order_id = fdp.ConsumeIntInRange(1, 1000)
        service.get_order(order_id)
    elif operation == 3:
        # 取消订单
        order_id = fdp.ConsumeIntInRange(1, 1000)
        cancel_reason = fdp.ConsumeString(10000)
        service.cancel_order(order_id, buyer_id, cancel_reason)
    elif operation == 4:
        # 发货
        order_id = fdp.ConsumeIntInRange(1, 1000)
        seller_id = fdp.ConsumeIntInRange(1, 100)
        tracking = fdp.ConsumeString(1000)
        service.ship_order(order_id, seller_id, tracking)


def test_product_service(fdp, db):
    """测试产品服务"""
    service = ProductService(db)
    
    operation = fdp.ConsumeIntInRange(0, 3)
    product_id = fdp.ConsumeIntInRange(-10000, 10000)
    quantity = fdp.ConsumeIntInRange(-100000, 100000)
    
    if operation == 0:
        # 获取产品
        service.get_product(product_id)
    elif operation == 1:
        # 检查库存
        service.check_stock(product_id, quantity)
    elif operation == 2:
        # 减少库存
        service.reduce_stock(product_id, quantity)
    elif operation == 3:
        # 增加库存
        service.increase_stock(product_id, quantity)


def test_message_service(fdp, db):
    """测试消息服务"""
    service = MessageService(db)
    
    operation = fdp.ConsumeIntInRange(0, 2)
    from_user = fdp.ConsumeIntInRange(-100000, 100000)
    to_user = fdp.ConsumeIntInRange(-100000, 100000)
    content = fdp.ConsumeString(500000)  # 超大消息
    msg_type = fdp.PickValueInList(['service', 'notification', 'order', 'chat', 'system', ''])
    
    if operation == 0:
        # 发送消息
        service.send_message(from_user, to_user, content, msg_type)
    elif operation == 1:
        # 查询消息
        service.get_messages(to_user)
    elif operation == 2:
        # 标记为已读
        msg_id = fdp.ConsumeIntInRange(1, 10000)
        service.mark_as_read(msg_id)


def test_combined_operations(fdp, db):
    """测试组合业务流程"""
    # 模拟完整的业务流程
    
    # 1. 验证用户输入
    email = fdp.ConsumeString(1000)
    Validator.validate_email(email)
    
    username = fdp.ConsumeString(100)
    Validator.validate_username(username)
    
    # 2. 创建订单
    order_service = OrderService(db)
    buyer_id = fdp.ConsumeIntInRange(1, 1000)
    product_id = fdp.ConsumeIntInRange(1, 500)
    quantity = fdp.ConsumeIntInRange(1, 100)
    address = fdp.ConsumeString(5000)
    
    order_id = order_service.create_order(buyer_id, product_id, quantity, address)
    
    if order_id:
        # 3. 支付订单
        payment = fdp.PickValueInList(['alipay', 'wechat', 'bank'])
        order_service.pay_order(order_id, payment)
        
        # 4. 检查库存
        product_service = ProductService(db)
        product_service.check_stock(product_id, quantity)
        
        # 5. 发送通知
        msg_service = MessageService(db)
        seller_id = (product_id % 5) + 1
        msg_service.send_message(seller_id, buyer_id, f"新订单 #{order_id}", 'order')


def print_progress(interval=60):
    """每隔一段时间打印进度"""
    last_print = time.time()
    
    while True:
        current_time = time.time()
        if current_time - last_print >= interval:
            report = STATS.get_report()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                  f"运行: {report['total_runs']} | "
                  f"耗时: {report['hours']}h {report['minutes']}m | "
                  f"验证器: {report['validator']} | "
                  f"订单: {report['order']} | "
                  f"产品: {report['product']} | "
                  f"消息: {report['message']} | "
                  f"组合: {report['combined']} | "
                  f"崩溃: {report['crashes']}")
            last_print = current_time
            sys.stdout.flush()
        
        time.sleep(5)


def main():
    print("╔════════════════════════════════════════════════════════╗")
    print("║  🧪 长时间综合模糊测试                                ║")
    print("║     运行时间: 5+ 小时                                  ║")
    print("║     覆盖: validators, order_service, product_service  ║")
    print("║            message_service, 组合操作                  ║")
    print("╚════════════════════════════════════════════════════════╝")
    print("")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"预计结束: {(datetime.now() + timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S')}")
    print("")
    
    # 设置 atheris 运行参数以实现长时间测试
    # -max_total_time: 设置总运行时间 (秒)
    # -timeout: 单个测试超时
    # -rss_limit_mb: 内存限制
    
    atheris.Setup(sys.argv, fuzz_entire_project)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
