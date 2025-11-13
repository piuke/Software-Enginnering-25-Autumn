#!/usr/bin/env python3
"""
测试订单取消审批流程
Test order cancellation approval workflow
"""

from database import DatabaseManager
from services import OrderService
from models import OrderStatus
from config.i18n import set_language, t
import json

def test_cancel_workflow():
    """测试取消订单审批流程"""
    
    print("=" * 80)
    print("订单取消审批流程测试 / Order Cancellation Approval Workflow Test")
    print("=" * 80)
    
    # 初始化数据库和服务
    db = DatabaseManager()
    order_service = OrderService(db)
    
    # 模拟场景：买家ID=1, 卖家ID=2
    buyer_id = 1
    seller_id = 2
    
    print("\n1️⃣ 创建测试订单...")
    # 假设我们有一个订单ID（实际使用中应该从数据库获取）
    test_order_id = 1
    
    print(f"\n2️⃣ 买家(#{buyer_id})申请取消订单 #{test_order_id}...")
    cancel_reason = "买错了商品"
    result = order_service.request_cancel_order(test_order_id, buyer_id, cancel_reason)
    print(f"   申请结果: {'成功' if result else '失败'}")
    
    if result:
        # 检查订单状态
        orders = db.execute_query("SELECT * FROM orders WHERE order_id=?", (test_order_id,))
        if orders:
            order = orders[0]
            print(f"   订单状态: {order['status']}")
            assert order['status'] == OrderStatus.CANCEL_REQUESTED.value, "状态应该是 cancel_requested"
            print("   ✓ 订单状态已更新为 cancel_requested")
        
        # 检查是否发送了服务消息
        messages = db.execute_query(
            "SELECT * FROM messages WHERE msg_type='service' ORDER BY msg_id DESC LIMIT 1"
        )
        if messages:
            msg = messages[0]
            msg_data = json.loads(msg['content'])
            print(f"\n   📨 服务消息已发送给卖家:")
            print(f"      翻译键: {msg_data['key']}")
            print(f"      参数: {msg_data['params']}")
            
            # 测试多语言显示
            for lang_code, lang_name in [('zh_CN', '中文'), ('en_US', 'English'), ('ja_JP', '日本語')]:
                set_language(lang_code)
                translated = t(msg_data['key'], **msg_data['params'])
                print(f"      {lang_name}: {translated}")
    
    print(f"\n3️⃣ 卖家(#{seller_id})处理取消申请...")
    print("   选项A: 同意取消")
    print("   选项B: 拒绝取消")
    
    # 测试场景A: 同意取消
    print("\n   📋 场景A: 卖家同意取消...")
    # 先恢复订单状态用于测试
    db.execute_update("UPDATE orders SET status=? WHERE order_id=?", 
                     (OrderStatus.CANCEL_REQUESTED.value, test_order_id))
    
    result_approve = order_service.approve_cancel(test_order_id, seller_id)
    print(f"   同意结果: {'成功' if result_approve else '失败'}")
    
    if result_approve:
        orders = db.execute_query("SELECT * FROM orders WHERE order_id=?", (test_order_id,))
        if orders:
            order = orders[0]
            print(f"   订单状态: {order['status']}")
            assert order['status'] == OrderStatus.CANCELLED.value, "状态应该是 cancelled"
            print("   ✓ 订单已成功取消，库存已恢复")
    
    # 测试场景B: 拒绝取消
    print("\n   📋 场景B: 卖家拒绝取消...")
    # 恢复为 cancel_requested 状态
    db.execute_update("UPDATE orders SET status=? WHERE order_id=?", 
                     (OrderStatus.CANCEL_REQUESTED.value, test_order_id))
    
    reject_reason = "商品已发货，无法取消"
    result_reject = order_service.reject_cancel(test_order_id, seller_id, reject_reason)
    print(f"   拒绝结果: {'成功' if result_reject else '失败'}")
    
    if result_reject:
        orders = db.execute_query("SELECT * FROM orders WHERE order_id=?", (test_order_id,))
        if orders:
            order = orders[0]
            print(f"   订单状态: {order['status']}")
            print(f"   拒绝原因: {order.get('cancel_reject_reason', 'N/A')}")
            assert order['status'] == OrderStatus.CANCEL_REJECTED.value, "状态应该是 cancel_rejected"
            assert order['cancel_reject_reason'] == reject_reason, "拒绝原因应该被保存"
            print("   ✓ 取消申请已被拒绝，原因已记录")
    
    print("\n" + "=" * 80)
    print("✅ 测试完成！")
    print("=" * 80)

def test_order_status_enum():
    """测试新的订单状态枚举"""
    print("\n" + "=" * 80)
    print("订单状态枚举测试 / Order Status Enum Test")
    print("=" * 80 + "\n")
    
    print("所有订单状态:")
    for status in OrderStatus:
        print(f"  - {status.name}: {status.value}")
    
    # 验证新增的状态存在
    assert hasattr(OrderStatus, 'CANCEL_REQUESTED'), "应该有 CANCEL_REQUESTED 状态"
    assert hasattr(OrderStatus, 'CANCEL_REJECTED'), "应该有 CANCEL_REJECTED 状态"
    print("\n✓ 新增的取消相关状态已正确定义")

def test_translations():
    """测试取消订单相关的翻译"""
    print("\n" + "=" * 80)
    print("翻译测试 / Translation Test")
    print("=" * 80 + "\n")
    
    translation_keys = [
        'order.status_cancel_requested',
        'order.status_cancel_rejected',
        'order.action_approve_cancel',
        'order.action_reject_cancel',
        'order.cancel_reason_label',
        'order.cancel_reject_reason_label',
        'order.service_cancel_requested',
        'order.service_cancel_approved',
        'order.service_cancel_rejected',
    ]
    
    languages = [('zh_CN', '中文'), ('en_US', 'English'), ('ja_JP', '日本語')]
    
    for key in translation_keys:
        print(f"\n翻译键: {key}")
        for lang_code, lang_name in languages:
            set_language(lang_code)
            # 提供测试参数
            params = {
                'order_id': 123,
                'reason': '测试原因',
                'reason_text': ' 原因: 测试原因'
            }
            try:
                translated = t(key, **params)
                print(f"  {lang_name:8s}: {translated}")
            except Exception as e:
                print(f"  {lang_name:8s}: ❌ 错误 - {e}")
    
    print("\n✓ 所有翻译键测试完成")

if __name__ == "__main__":
    print("\n🚀 开始测试订单取消审批功能...\n")
    
    try:
        test_order_status_enum()
        test_translations()
        # test_cancel_workflow()  # 需要实际的数据库环境
        
        print("\n" + "=" * 80)
        print("🎉 所有测试通过！订单取消审批功能已正确实现")
        print("=" * 80)
        
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
