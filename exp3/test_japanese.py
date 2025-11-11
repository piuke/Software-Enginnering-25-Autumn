#!/usr/bin/env python3
"""测试日语翻译完整性"""

import json
from config.i18n import t, set_language, LANGUAGE_NAMES

def test_translation_keys():
    """测试所有语言的翻译键是否一致"""
    with open('config/translations.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 获取所有语言的键集合
    language_keys = {}
    for lang in data.keys():
        keys = set()
        for category in data[lang].values():
            keys.update(category.keys())
        language_keys[lang] = keys
    
    # 检查键是否一致
    base_keys = language_keys['zh_CN']
    print(f"总翻译键数量: {len(base_keys)}")
    print(f"支持的语言: {list(data.keys())}\n")
    
    all_match = True
    for lang, keys in language_keys.items():
        if lang == 'zh_CN':
            continue
        missing = base_keys - keys
        extra = keys - base_keys
        
        if missing or extra:
            all_match = False
            print(f"❌ {lang} 键不匹配:")
            if missing:
                print(f"   缺失键: {missing}")
            if extra:
                print(f"   多余键: {extra}")
        else:
            print(f"✓ {lang} 键完全匹配")
    
    if all_match:
        print("\n✓ 所有语言的翻译键完全一致！")
    return all_match

def test_language_switching():
    """测试语言切换功能"""
    print("\n" + "=" * 50)
    print("测试语言切换")
    print("=" * 50)
    
    test_keys = [
        'common.welcome',
        'user.login',
        'product.products',
        'system.banner',
        'menu.main_menu'
    ]
    
    for lang in ['zh_CN', 'en_US', 'ja_JP']:
        set_language(lang)
        print(f"\n语言: {LANGUAGE_NAMES.get(lang, lang)}")
        print("-" * 40)
        for key in test_keys:
            print(f"  {key}: {t(key)}")

if __name__ == '__main__':
    print("=" * 60)
    print("日语翻译测试")
    print("=" * 60 + "\n")
    
    # 测试翻译键完整性
    keys_match = test_translation_keys()
    
    # 测试语言切换
    test_language_switching()
    
    print("\n" + "=" * 60)
    if keys_match:
        print("✓ 所有测试通过！")
    else:
        print("❌ 存在问题，请检查上述错误")
    print("=" * 60)
