#!/usr/bin/env python3
"""
测试服务消息多语言功能
Test service message internationalization
"""

import json
from config.i18n import set_language, t

def test_service_message_translation():
    """测试服务消息在不同语言下的显示"""
    
    # 模拟从数据库读取的服务消息 JSON
    test_messages = [
        {
            "key": "order.service_order_created",
            "params": {"order_id": 12345}
        },
        {
            "key": "order.service_order_paid",
            "params": {"order_id": 12345}
        },
        {
            "key": "order.service_order_shipped",
            "params": {"order_id": 12345, "tracking_number": "SF1234567890"}
        },
        {
            "key": "order.service_order_completed",
            "params": {"order_id": 12345}
        },
        {
            "key": "order.service_refund_requested",
            "params": {"order_id": 12345, "reason": "商品损坏"}
        },
        {
            "key": "order.service_refund_approved",
            "params": {"order_id": 12345}
        },
        {
            "key": "order.service_refund_rejected",
            "params": {"order_id": 12345, "reason_text": " 原因: 超过退款期限"}
        }
    ]
    
    # 测试三种语言
    languages = [
        ('zh_CN', '中文'),
        ('en_US', 'English'),
        ('ja_JP', '日本語')
    ]
    
    print("=" * 80)
    print("服务消息多语言测试 / Service Message I18n Test")
    print("=" * 80)
    
    for lang_code, lang_name in languages:
        print(f"\n{'='*80}")
        print(f"语言 / Language: {lang_name} ({lang_code})")
        print(f"{'='*80}\n")
        
        # 切换语言
        set_language(lang_code)
        
        # 显示所有测试消息
        for idx, msg_data in enumerate(test_messages, 1):
            # 模拟消息显示逻辑
            try:
                translation_key = msg_data.get('key', '')
                params = msg_data.get('params', {})
                translated_content = t(translation_key, **params)
                print(f"{idx}. {translated_content}")
            except Exception as e:
                print(f"{idx}. [ERROR] 翻译失败: {e}")
    
    print(f"\n{'='*80}")
    print("测试完成 / Test completed")
    print("=" * 80)

def test_message_format_parsing():
    """测试消息格式解析"""
    print("\n" + "=" * 80)
    print("消息格式解析测试 / Message Format Parsing Test")
    print("=" * 80 + "\n")
    
    # 测试 JSON 格式
    json_message = '{"key": "order.service_order_created", "params": {"order_id": 999}}'
    print(f"原始 JSON: {json_message}")
    
    try:
        msg_data = json.loads(json_message)
        translation_key = msg_data.get('key', '')
        params = msg_data.get('params', {})
        print(f"解析成功: key={translation_key}, params={params}")
        
        # 测试中文翻译
        set_language('zh_CN')
        content_zh = t(translation_key, **params)
        print(f"中文: {content_zh}")
        
        # 测试英文翻译
        set_language('en_US')
        content_en = t(translation_key, **params)
        print(f"英文: {content_en}")
        
    except Exception as e:
        print(f"解析失败: {e}")
    
    print("=" * 80)

if __name__ == "__main__":
    test_service_message_translation()
    test_message_format_parsing()
