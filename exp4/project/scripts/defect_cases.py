"""
缺陷测试模块 - 植入常见 Python 安全与资源管理缺陷

本模块故意包含以下类型的缺陷：
1. 资源泄漏（文件未关闭）
2. SQL 注入
3. 不安全的反序列化
4. 硬编码密码/凭证
5. 弱随机数生成
6. 通配符导入
7. 使用危险函数（eval）
8. 无异常处理的资源操作
9. 日志泄露敏感信息
10. 不安全的临时文件创建
"""

import os
import pickle
import random
import sqlite3
import tempfile
from models import *  # 缺陷 7: 通配符导入


# ============================================================================
# 缺陷 1: 文件资源泄漏 - 文件未正确关闭
# ============================================================================
def defect_1_file_not_closed(filename: str) -> str:
    """
    CWE-775: Missing Release of File Descriptor
    文件打开后未关闭，可能导致文件描述符泄漏
    """
    f = open(filename, 'r')  # ❌ 文件未关闭
    content = f.read()
    return content  # 文件仍保持打开状态


# ============================================================================
# 缺陷 2: 数据库连接泄漏
# ============================================================================
def defect_2_database_connection_leak(db_path: str) -> list:
    """
    CWE-775: Missing Release of Database Connection
    数据库连接未正确关闭
    """
    conn = sqlite3.connect(db_path)  # ❌ 连接未关闭
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    return cursor.fetchall()


# ============================================================================
# 缺陷 3: SQL 注入
# ============================================================================
def defect_3_sql_injection(user_id: str, db_path: str) -> list:
    """
    CWE-89: SQL Injection
    用户输入直接拼接到 SQL 语句中，无参数化查询
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # ❌ 直接字符串拼接，存在 SQL 注入风险
    query = f"SELECT * FROM users WHERE user_id = '{user_id}'"
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result


# ============================================================================
# 缺陷 4: 不安全的反序列化
# ============================================================================
def defect_4_unsafe_deserialization(data_bytes: bytes):
    """
    CWE-502: Deserialization of Untrusted Data
    使用 pickle 反序列化不受信任的数据
    """
    # ❌ pickle.loads() 可被利用执行任意代码
    obj = pickle.loads(data_bytes)
    return obj


# ============================================================================
# 缺陷 5: 硬编码密钥/密码
# ============================================================================
def defect_5_hardcoded_credentials():
    """
    CWE-798: Use of Hard-coded Credentials
    敏感信息（API密钥、密码）硬编码在代码中
    """
    # ❌ 硬编码 API 密钥
    API_KEY = "sk-1234567890abcdefghijklmnop"
    DB_PASSWORD = "admin@123"
    OAUTH_SECRET = "secret_client_secret_12345"
    
    return {
        'api_key': API_KEY,
        'db_password': DB_PASSWORD,
        'oauth_secret': OAUTH_SECRET
    }


# ============================================================================
# 缺陷 6: 弱随机数生成
# ============================================================================
def defect_6_weak_random_generation():
    """
    CWE-338: Use of Cryptographically Weak Pseudo-Random Number Generator
    使用 random 模块而非 secrets，用于生成安全敏感的值
    """
    # ❌ random 不安全，应用 secrets 或 os.urandom()
    token = str(random.randint(1000000, 9999999))
    session_id = "".join(chr(random.randint(0, 255)) for _ in range(32))
    return token, session_id


# ============================================================================
# 缺陷 7: 通配符导入
# ============================================================================
def defect_7_wildcard_import():
    """
    CWE-95: Improper Neutralization of Directives in Dynamically Evaluated Code
    使用 from module import * 导入不明确，难以追踪依赖
    
    注：此缺陷已在模块顶部示现（from models import *）
    """
    pass


# ============================================================================
# 缺陷 8: 使用 eval() 执行不受信任的代码
# ============================================================================
def defect_8_eval_untrusted_code(user_input: str):
    """
    CWE-95: Improper Neutralization of Directives in Dynamically Evaluated Code
    使用 eval() 执行用户输入
    """
    # ❌ eval() 可执行任意代码，极其危险
    result = eval(user_input)
    return result


# ============================================================================
# 缺陷 9: 日志中泄露敏感信息
# ============================================================================
def defect_9_sensitive_info_in_logs(user_password: str, api_token: str):
    """
    CWE-532: Insertion of Sensitive Information into Log File
    敏感信息（密码、token）被写入日志或输出
    """
    print(f"用户登录密码: {user_password}")  # ❌ 泄露密码
    print(f"API Token: {api_token}")  # ❌ 泄露 token
    
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Credit Card: 1234-5678-9012-3456")  # ❌ 泄露信用卡号
    
    return True


# ============================================================================
# 缺陷 10: 不安全的临时文件创建
# ============================================================================
def defect_10_insecure_temp_file() -> str:
    """
    CWE-377: Insecure Temporary File
    使用不安全的方式创建临时文件，可被利用进行竞态攻击
    """
    # ❌ 预测文件名，存在竞态条件
    temp_path = f"/tmp/tempfile_{random.randint(0, 1000)}.txt"
    with open(temp_path, 'w') as f:
        f.write("sensitive data")
    return temp_path


# ============================================================================
# 缺陷 11: 广泛异常捕获（bonus）
# ============================================================================
def defect_11_broad_exception_handling(user_id: int):
    """
    W0718: Catching too general exception Exception
    捕获泛用 Exception，无法区分错误类型
    """
    try:
        # 某些操作
        result = None
        if user_id < 0:
            raise ValueError("user_id 必须为正数")
        result = {"user_id": user_id}
    except Exception:  # ❌ 太泛用，掩盖真实错误
        return None


# ============================================================================
# 缺陷 12: assert 在生产代码中
# ============================================================================
def defect_12_assert_in_production(value: int) -> bool:
    """
    B101: Assert in production code
    使用 assert 进行参数验证，生产优化时会被移除
    """
    assert value > 0, "value 必须为正数"  # ❌ 会被优化移除
    assert isinstance(value, int), "value 必须为整数"
    return True


# ============================================================================
# 缺陷 13: 命令注入
# ============================================================================
def defect_13_command_injection(filename: str):
    """
    CWE-78: Improper Neutralization of Special Elements used in OS Command
    使用 os.system() 或 subprocess 执行用户输入的命令
    """
    import subprocess
    # ❌ 用户输入直接传入命令，存在命令注入风险
    result = subprocess.call(f"cat {filename}", shell=True)
    return result


# ============================================================================
# 测试与调试函数
# ============================================================================
def safe_file_operation(filename: str) -> str:
    """
    ✅ 正确的做法：使用 with 语句自动关闭资源
    """
    with open(filename, 'r') as f:
        return f.read()


def safe_database_operation(db_path: str) -> list:
    """
    ✅ 正确的做法：使用 context manager 自动释放连接
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products LIMIT 10")
        return cursor.fetchall()


def safe_sql_query(user_id: int, db_path: str) -> list:
    """
    ✅ 正确的做法：使用参数化查询防止 SQL 注入
    """
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM users WHERE user_id = ?"
        cursor.execute(query, (user_id,))
        return cursor.fetchall()


def safe_password_generation():
    """
    ✅ 正确的做法：使用 secrets 模块生成密码
    """
    import secrets
    token = secrets.token_urlsafe(32)
    return token


if __name__ == "__main__":
    print("缺陷演示模块已加载")
    print("包含 13 个故意植入的缺陷，用于测试静态分析工具的检测能力")
