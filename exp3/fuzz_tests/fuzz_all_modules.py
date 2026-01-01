"""
长时间模糊测试 - 5小时+ 模糊测试整个项目
覆盖所有模块：validators, order_service, product_service, message_service等
"""

import sys
import os
import atheris
import struct
import random

# 修正模块路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.validators import Validator
from services.order_service import OrderService
from services.product_service import ProductService
from services.message_service import MessageService


class FuzzMockDB:
    """模拟数据库用于模糊测试"""
    
    def __init__(self):
        self.orders = {}
        self.products = {
            i: {
                'product_id': i,
                'seller_id': (i % 3) + 1,
                'price': 10.0 * i,
                'stock': 100 + i,
                'status': 'available',
                'name': f'Product {i}'
            }
            for i in range(1, 100)
        }
        self.users = {i: {'user_id': i, 'username': f'user_{i}'} for i in range(1, 50)}
        self.messages = {}
        self.call_count = 0
    
    def execute_query(self, query, params=None):
        """执行查询"""
        self.call_count += 1
        if "FROM products" in query:
            if params and len(params) > 0:
                product_id = params[0]
                if product_id in self.products:
                    return [self.products[product_id]]
            return list(self.products.values())[:10]
        if "FROM orders" in query:
            return list(self.orders.values())[:10]
        if "FROM users" in query:
            return list(self.users.values())[:10]
        return []
    
    def execute_insert(self, query, params=None):
        """执行插入"""
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
        """执行更新"""
        self.call_count += 1
        return True


@atheris.instrument_func
def fuzz_all_validators(data):
    """模糊测试所有验证器"""
    fdp = atheris.FuzzedDataProvider(data)
    
    # 消费数据
    choice = fdp.ConsumeIntInRange(0, 4)
    test_input = fdp.ConsumeString(10000)
    
    try:
        if choice == 0:
            # 邮箱验证
            Validator.validate_email(test_input)
        elif choice == 1:
            # 用户名验证
            Validator.validate_username(test_input)
        elif choice == 2:
            # 密码验证
            Validator.validate_password(test_input)
        elif choice == 3:
            # 手机验证
            Validator.validate_phone(test_input)
        elif choice == 4:
            # 价格验证
            try:
                price = float(test_input[:50].replace(',', '.')) if test_input else 0
                Validator.validate_price(price)
            except (ValueError, AttributeError):
                pass
    except Exception as e:
        if type(e).__name__ in ['RecursionError', 'MemoryError', 'OverflowError']:
            raise


@atheris.instrument_func
def fuzz_order_service(data):
    """模糊测试订单服务"""
    fdp = atheris.FuzzedDataProvider(data)
    db = FuzzMockDB()
    service = OrderService(db)
    
    try:
        # 各种订单操作
        buyer_id = fdp.ConsumeIntInRange(1, 1000)
        product_id = fdp.ConsumeIntInRange(1, 100)
        quantity = fdp.ConsumeIntInRange(-1000, 10000)
        address = fdp.ConsumeString(5000)
        
        # 创建订单
        order_id = service.create_order(buyer_id, product_id, quantity, address)
        
        if order_id:
            # 支付
            payment = fdp.PickValueInList(['alipay', 'wechat', 'bank', 'card', ''])
            service.pay_order(order_id, payment)
            
            # 查询
            service.get_order(order_id)
            
            # 取消
            cancel_reason = fdp.ConsumeString(1000)
            service.cancel_order(order_id, buyer_id, cancel_reason)
            
    except (TypeError, ValueError, AttributeError):
        pass
    except Exception as e:
        if type(e).__name__ in ['RecursionError', 'MemoryError', 'OverflowError']:
            raise


@atheris.instrument_func
def fuzz_product_service(data):
    """模糊测试产品服务"""
    fdp = atheris.FuzzedDataProvider(data)
    db = FuzzMockDB()
    service = ProductService(db)
    
    try:
        product_id = fdp.ConsumeIntInRange(1, 1000)
        quantity = fdp.ConsumeIntInRange(-10000, 10000)
        
        # 获取产品
        service.get_product(product_id)
        
        # 检查库存
        service.check_stock(product_id, quantity)
        
        # 减少库存
        service.reduce_stock(product_id, quantity)
        
    except (TypeError, ValueError, AttributeError):
        pass
    except Exception as e:
        if type(e).__name__ in ['RecursionError', 'MemoryError', 'OverflowError']:
            raise


@atheris.instrument_func
def fuzz_message_service(data):
    """模糊测试消息服务"""
    fdp = atheris.FuzzedDataProvider(data)
    db = FuzzMockDB()
    service = MessageService(db)
    
    try:
        from_user = fdp.ConsumeIntInRange(1, 100)
        to_user = fdp.ConsumeIntInRange(1, 100)
        content = fdp.ConsumeString(50000)
        msg_type = fdp.PickValueInList(['service', 'notification', 'order', 'chat'])
        
        # 发送消息
        service.send_message(from_user, to_user, content, msg_type)
        
        # 查询消息
        service.get_messages(to_user)
        
    except (TypeError, ValueError, AttributeError):
        pass
    except Exception as e:
        if type(e).__name__ in ['RecursionError', 'MemoryError', 'OverflowError']:
            raise


@atheris.instrument_func
def fuzz_combined_operations(data):
    """组合模糊测试 - 模拟真实场景"""
    fdp = atheris.FuzzedDataProvider(data)
    db = FuzzMockDB()
    
    try:
        # 随机组合操作
        ops = []
        for _ in range(fdp.ConsumeIntInRange(1, 5)):
            op = fdp.ConsumeIntInRange(0, 3)
            if op == 0:
                # 验证用户输入
                email = fdp.ConsumeString(500)
                Validator.validate_email(email)
            elif op == 1:
                # 创建订单
                order_service = OrderService(db)
                buyer_id = fdp.ConsumeIntInRange(1, 100)
                product_id = fdp.ConsumeIntInRange(1, 100)
                qty = fdp.ConsumeIntInRange(1, 100)
                addr = fdp.ConsumeString(500)
                order_service.create_order(buyer_id, product_id, qty, addr)
            elif op == 2:
                # 检查库存
                product_service = ProductService(db)
                pid = fdp.ConsumeIntInRange(1, 100)
                qty = fdp.ConsumeIntInRange(1, 100)
                product_service.check_stock(pid, qty)
            elif op == 3:
                # 发送消息
                msg_service = MessageService(db)
                from_u = fdp.ConsumeIntInRange(1, 50)
                to_u = fdp.ConsumeIntInRange(1, 50)
                content = fdp.ConsumeString(1000)
                msg_service.send_message(from_u, to_u, content, 'service')
                
    except (TypeError, ValueError, AttributeError):
        pass
    except Exception as e:
        if type(e).__name__ in ['RecursionError', 'MemoryError', 'OverflowError']:
            raise


def main():
    """主函数 - 选择要运行的模糊测试"""
    if len(sys.argv) < 2:
        print("使用方法: python fuzz_all_modules.py <target>")
        print("target 选项:")
        print("  0 - validators (验证器)")
        print("  1 - order_service (订单服务)")
        print("  2 - product_service (产品服务)")
        print("  3 - message_service (消息服务)")
        print("  4 - combined (组合测试)")
        sys.exit(1)
    
    # 获取目标
    try:
        target_idx = int(sys.argv[1])
        sys.argv = sys.argv[:1] + sys.argv[2:]  # 移除我们的参数
    except:
        target_idx = 4
        sys.argv = sys.argv[:1] + sys.argv[1:]
    
    targets = [
        ("验证器模块", fuzz_all_validators),
        ("订单服务", fuzz_order_service),
        ("产品服务", fuzz_product_service),
        ("消息服务", fuzz_message_service),
        ("组合操作", fuzz_combined_operations),
    ]
    
    if target_idx < 0 or target_idx >= len(targets):
        target_idx = 4
    
    print(f"🔍 开始模糊测试: {targets[target_idx][0]}")
    print(f"⏱️  建议运行时间: 5+ 小时")
    
    atheris.Setup(sys.argv, targets[target_idx][1])
    atheris.Fuzz()


if __name__ == "__main__":
    main()
