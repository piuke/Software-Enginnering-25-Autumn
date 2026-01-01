import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.validators import Validator


class TestValidateEmail:
    """测试邮箱验证功能"""
    
    def test_valid_email_simple(self):
        """测试有效邮箱 - 简单格式"""
        assert Validator.validate_email("user@example.com") is True
    
    def test_valid_email_with_numbers(self):
        """测试有效邮箱 - 包含数字"""
        assert Validator.validate_email("user123@example.com") is True
    
    def test_valid_email_with_dots(self):
        """测试有效邮箱 - 用户名包含点"""
        assert Validator.validate_email("user.name@example.com") is True
    
    def test_valid_email_with_underscore(self):
        """测试有效邮箱 - 用户名包含下划线"""
        assert Validator.validate_email("user_name@example.co.uk") is True
    
    def test_valid_email_with_plus(self):
        """测试有效邮箱 - 用户名包含加号"""
        assert Validator.validate_email("user+tag@example.com") is True
    
    def test_valid_email_with_hyphen(self):
        """测试有效邮箱 - 域名包含连字符"""
        assert Validator.validate_email("user@ex-ample.com") is True
    
    def test_invalid_email_no_at_sign(self):
        """测试无效邮箱 - 缺少@符号"""
        assert Validator.validate_email("userexample.com") is False
    
    def test_invalid_email_no_domain(self):
        """测试无效邮箱 - 缺少域名"""
        assert Validator.validate_email("user@") is False
    
    def test_invalid_email_no_extension(self):
        """测试无效邮箱 - 缺少顶级域名"""
        assert Validator.validate_email("user@example") is False
    
    def test_invalid_email_no_username(self):
        """测试无效邮箱 - 缺少用户名"""
        assert Validator.validate_email("@example.com") is False
    
    def test_invalid_email_space(self):
        """测试无效邮箱 - 包含空格"""
        assert Validator.validate_email("user name@example.com") is False
    
    def test_invalid_email_multiple_at_signs(self):
        """测试无效邮箱 - 多个@符号"""
        assert Validator.validate_email("user@@example.com") is False
    
    def test_invalid_email_empty_string(self):
        """测试无效邮箱 - 空字符串"""
        assert Validator.validate_email("") is False
    
    def test_invalid_email_only_dot(self):
        """测试无效邮箱 - 不合法格式"""
        assert Validator.validate_email("user.@.com") is False


class TestValidateUsername:
    """测试用户名验证功能"""
    
    def test_valid_username_letters_only(self):
        """测试有效用户名 - 仅字母"""
        assert Validator.validate_username("abcDEF") is True
    
    def test_valid_username_with_numbers(self):
        """测试有效用户名 - 包含数字"""
        assert Validator.validate_username("user123") is True
    
    def test_valid_username_with_underscore(self):
        """测试有效用户名 - 包含下划线"""
        assert Validator.validate_username("user_name") is True
    
    def test_valid_username_minimum_length(self):
        """测试有效用户名 - 最小长度(3个字符)"""
        assert Validator.validate_username("abc") is True
    
    def test_valid_username_maximum_length(self):
        """测试有效用户名 - 最大长度(20个字符)"""
        assert Validator.validate_username("abcdefghij1234567890") is True
    
    def test_valid_username_mixed_format(self):
        """测试有效用户名 - 混合格式"""
        assert Validator.validate_username("user_name_123") is True
    
    def test_invalid_username_too_short(self):
        """测试无效用户名 - 过短(少于3个字符)"""
        assert Validator.validate_username("ab") is False
    
    def test_invalid_username_too_long(self):
        """测试无效用户名 - 过长(超过20个字符)"""
        assert Validator.validate_username("abcdefghij12345678901") is False
    
    def test_invalid_username_with_hyphen(self):
        """测试无效用户名 - 包含连字符"""
        assert Validator.validate_username("user-name") is False
    
    def test_invalid_username_with_space(self):
        """测试无效用户名 - 包含空格"""
        assert Validator.validate_username("user name") is False
    
    def test_invalid_username_with_special_char(self):
        """测试无效用户名 - 包含特殊字符"""
        assert Validator.validate_username("user@name") is False
    
    def test_invalid_username_empty_string(self):
        """测试无效用户名 - 空字符串"""
        assert Validator.validate_username("") is False
    
    def test_invalid_username_chinese_char(self):
        """测试无效用户名 - 包含中文"""
        assert Validator.validate_username("用户名123") is False


class TestValidatePassword:
    """测试密码验证功能"""
    
    def test_valid_password_minimum_length(self):
        """测试有效密码 - 最小长度(6个字符)"""
        is_valid, err = Validator.validate_password("123456")
        assert is_valid is True
        assert err is None
    
    def test_valid_password_maximum_length(self):
        """测试有效密码 - 最大长度(20个字符)"""
        is_valid, err = Validator.validate_password("12345678901234567890")
        assert is_valid is True
        assert err is None
    
    def test_valid_password_with_letters_and_numbers(self):
        """测试有效密码 - 包含字母和数字"""
        is_valid, err = Validator.validate_password("password123")
        assert is_valid is True
        assert err is None
    
    def test_valid_password_with_special_chars(self):
        """测试有效密码 - 包含特殊字符"""
        is_valid, err = Validator.validate_password("pass@123!")
        assert is_valid is True
        assert err is None
    
    def test_invalid_password_too_short(self):
        """测试无效密码 - 过短(少于6个字符)"""
        is_valid, err = Validator.validate_password("12345")
        assert is_valid is False
        assert err == "密码至少6个字符"
    
    def test_invalid_password_too_long(self):
        """测试无效密码 - 过长(超过20个字符)"""
        is_valid, err = Validator.validate_password("123456789012345678901")
        assert is_valid is False
        assert err == "密码最多20个字符"
    
    def test_invalid_password_empty_string(self):
        """测试无效密码 - 空字符串"""
        is_valid, err = Validator.validate_password("")
        assert is_valid is False
        assert err == "密码至少6个字符"
    
    def test_invalid_password_boundary_5_chars(self):
        """测试无效密码 - 边界5个字符"""
        is_valid, err = Validator.validate_password("abcde")
        assert is_valid is False
        assert err == "密码至少6个字符"
    
    def test_valid_password_boundary_7_chars(self):
        """测试有效密码 - 边界7个字符"""
        is_valid, err = Validator.validate_password("abcdefg")
        assert is_valid is True
        assert err is None
    
    def test_valid_password_boundary_19_chars(self):
        """测试有效密码 - 边界19个字符"""
        is_valid, err = Validator.validate_password("1234567890123456789")
        assert is_valid is True
        assert err is None
    
    def test_invalid_password_boundary_21_chars(self):
        """测试无效密码 - 边界21个字符"""
        is_valid, err = Validator.validate_password("123456789012345678901")
        assert is_valid is False
        assert err == "密码最多20个字符"


class TestValidatePrice:
    """测试价格验证功能"""
    
    def test_valid_price_positive_integer(self):
        """测试有效价格 - 正整数"""
        assert Validator.validate_price(100) is True
    
    def test_valid_price_positive_float(self):
        """测试有效价格 - 正浮点数"""
        assert Validator.validate_price(99.99) is True
    
    def test_valid_price_small_amount(self):
        """测试有效价格 - 小金额"""
        assert Validator.validate_price(0.01) is True
    
    def test_valid_price_large_amount(self):
        """测试有效价格 - 大金额"""
        assert Validator.validate_price(999999.99) is True
    
    def test_invalid_price_zero(self):
        """测试无效价格 - 零"""
        assert Validator.validate_price(0) is False
    
    def test_invalid_price_negative(self):
        """测试无效价格 - 负数"""
        assert Validator.validate_price(-100) is False
    
    def test_invalid_price_negative_float(self):
        """测试无效价格 - 负浮点数"""
        assert Validator.validate_price(-99.99) is False
    
    def test_boundary_price_very_small_positive(self):
        """测试边界价格 - 非常小的正数"""
        assert Validator.validate_price(0.001) is True
    
    def test_boundary_price_near_zero_negative(self):
        """测试边界价格 - 接近零的负数"""
        assert Validator.validate_price(-0.001) is False


class TestValidatePhone:
    """测试手机号验证功能"""
    
    def test_valid_phone_13_prefix(self):
        """测试有效手机号 - 13开头"""
        assert Validator.validate_phone("13800138000") is True
    
    def test_valid_phone_14_prefix(self):
        """测试有效手机号 - 14开头"""
        assert Validator.validate_phone("14612345678") is True
    
    def test_valid_phone_15_prefix(self):
        """测试有效手机号 - 15开头"""
        assert Validator.validate_phone("15912345678") is True
    
    def test_valid_phone_16_prefix(self):
        """测试有效手机号 - 16开头"""
        assert Validator.validate_phone("16612345678") is True
    
    def test_valid_phone_17_prefix(self):
        """测试有效手机号 - 17开头"""
        assert Validator.validate_phone("17712345678") is True
    
    def test_valid_phone_18_prefix(self):
        """测试有效手机号 - 18开头"""
        assert Validator.validate_phone("18812345678") is True
    
    def test_valid_phone_19_prefix(self):
        """测试有效手机号 - 19开头"""
        assert Validator.validate_phone("19912345678") is True
    
    def test_invalid_phone_wrong_prefix_12(self):
        """测试无效手机号 - 12开头"""
        assert Validator.validate_phone("12812345678") is False
    
    def test_invalid_phone_wrong_prefix_11(self):
        """测试无效手机号 - 11开头"""
        assert Validator.validate_phone("11812345678") is False
    
    def test_invalid_phone_too_short(self):
        """测试无效手机号 - 过短"""
        assert Validator.validate_phone("1381234567") is False
    
    def test_invalid_phone_too_long(self):
        """测试无效手机号 - 过长"""
        assert Validator.validate_phone("138001380000") is False
    
    def test_invalid_phone_with_letters(self):
        """测试无效手机号 - 包含字母"""
        assert Validator.validate_phone("138001380ab") is False
    
    def test_invalid_phone_with_spaces(self):
        """测试无效手机号 - 包含空格"""
        assert Validator.validate_phone("138 00138000") is False
    
    def test_invalid_phone_empty_string(self):
        """测试无效手机号 - 空字符串"""
        assert Validator.validate_phone("") is False
    
    def test_invalid_phone_special_chars(self):
        """测试无效手机号 - 包含特殊字符"""
        assert Validator.validate_phone("1380-01380-00") is False


# 测试用例计数：
# TestValidateEmail: 14个测试用例
# TestValidateUsername: 13个测试用例
# TestValidatePassword: 11个测试用例
# TestValidatePrice: 9个测试用例
# TestValidatePhone: 16个测试用例
# 总计：63个测试用例
