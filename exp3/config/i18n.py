"""
Internationalization (i18n) - 国际化支持
提供多语言翻译功能
"""

import os
import json
from typing import Dict, Optional


class I18n:
    """国际化管理类"""
    
    # 支持的语言列表
    SUPPORTED_LANGUAGES = ['zh_CN', 'en_US', 'ja_JP']
    
    # 默认语言
    DEFAULT_LANGUAGE = 'zh_CN'
    
    # 翻译数据缓存
    _translations_cache = None
    
    def __init__(self, language: Optional[str] = None):
        """
        初始化国际化管理器
        
        Args:
            language: 语言代码（如 'zh_CN', 'en_US'）
        """
        self.current_language = language or self._get_system_language()
        self.translations = self._load_translations()
    
    def _get_system_language(self) -> str:
        """
        获取系统语言设置
        
        Returns:
            str: 语言代码
        """
        # 尝试从环境变量获取
        lang = os.environ.get('LANG', '')
        
        if 'zh' in lang.lower() or 'cn' in lang.lower():
            return 'zh_CN'
        elif 'en' in lang.lower():
            return 'en_US'
        
        return self.DEFAULT_LANGUAGE
    
    def _load_translations(self) -> Dict:
        """
        从 JSON 文件加载翻译数据
        
        Returns:
            Dict: 翻译字典
        """
        # 使用缓存避免重复读取文件
        if I18n._translations_cache is None:
            json_path = os.path.join(os.path.dirname(__file__), 'translations.json')
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    I18n._translations_cache = json.load(f)
            except FileNotFoundError:
                print(f"Warning: translations.json not found at {json_path}")
                I18n._translations_cache = {}
            except json.JSONDecodeError as e:
                print(f"Warning: Error parsing translations.json: {e}")
                I18n._translations_cache = {}
        
        return I18n._translations_cache.get(self.current_language, 
                                            I18n._translations_cache.get(self.DEFAULT_LANGUAGE, {}))
    
    def set_language(self, language: str) -> bool:
        """
        设置当前语言
        
        Args:
            language: 语言代码
            
        Returns:
            bool: 是否成功
        """
        if language not in self.SUPPORTED_LANGUAGES:
            return False
        
        self.current_language = language
        self.translations = self._load_translations()
        return True
    
    def t(self, key: str, **kwargs) -> str:
        """
        翻译函数（简写）
        
        Args:
            key: 翻译键（使用点分隔的路径，如 'user.login_success'）
            **kwargs: 格式化参数
            
        Returns:
            str: 翻译后的文本
        """
        return self.translate(key, **kwargs)
    
    def translate(self, key: str, **kwargs) -> str:
        """
        翻译函数
        
        Args:
            key: 翻译键（使用点分隔的路径，如 'user.login_success'）
            **kwargs: 格式化参数
            
        Returns:
            str: 翻译后的文本
        """
        # 按点分隔键，逐层查找
        keys = key.split('.')
        value = self.translations
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                value = None
                break
        
        # 如果找不到翻译，返回键本身
        if value is None:
            return key
        
        # 如果有格式化参数，进行格式化
        if kwargs and isinstance(value, str):
            try:
                return value.format(**kwargs)
            except KeyError:
                return value
        
        return value
    
    def get_language_name(self, language: Optional[str] = None) -> str:
        """
        获取语言名称
        
        Args:
            language: 语言代码，为 None 时返回当前语言名称
            
        Returns:
            str: 语言名称
        """
        lang = language or self.current_language
        return LANGUAGE_NAMES.get(lang, lang)


# 语言名称映射
LANGUAGE_NAMES = {
    'zh_CN': '简体中文',
    'en_US': 'English',
    'ja_JP': '日本語'
}


# 创建全局实例
_i18n_instance = None


# 翻译数据已移至 translations.json
# 保留此注释作为说明

# 翻译数据已移至 translations.json 文件



# 创建全局实例
_i18n_instance = None


def get_i18n() -> I18n:
    """
    获取全局 i18n 实例
    
    Returns:
        I18n: i18n 实例
    """
    global _i18n_instance
    if _i18n_instance is None:
        _i18n_instance = I18n()
    return _i18n_instance


def t(key: str, **kwargs) -> str:
    """
    快捷翻译函数
    
    Args:
        key: 翻译键
        **kwargs: 格式化参数
        
    Returns:
        str: 翻译后的文本
    """
    return get_i18n().translate(key, **kwargs)


def set_language(language: str) -> bool:
    """
    设置全局语言
    
    Args:
        language: 语言代码
        
    Returns:
        bool: 是否成功
    """
    return get_i18n().set_language(language)
