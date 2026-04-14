#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Airwallex 充值流程自动化脚本

流程：
1. 从 Redis 获取 Airwallex token
2. 从 PostgreSQL 数据库获取 payment_account_id
3. 调用 Airwallex API 创建充值转账
"""
import sys
import json
import time
import redis
import psycopg2
import requests
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Redis 配置
REDIS_CONFIG = {
    'host': 'redis-shark-test.rdb.58dns.org',
    'port': 50554,
    'password': '6b0d1d0d640eb6fa'
}

# PostgreSQL 配置
PG_CONFIG = {
    'host': 'pgsql-test.pdb.58dns.org',
    'port': 29000,
    'database': 'pdb58_easypost',
    'user': 'epost_test',
    'password': 'GUGXzw49K6Ndp7'
}

# Airwallex API 配置
AIRWALLEX_API_URL = 'https://api-demo.airwallex.com/api/v1/connected_account_transfers/create'

# 用户配置
APP_USER_ID = '796133836057336352'


def get_token_from_redis():
    """
    从 Redis 获取 Airwallex token
    
    Returns:
        str: JWT token
    """
    print("=" * 80)
    print("步骤 1: 从 Redis 获取 Airwallex Token")
    print("=" * 80)
    
    try:
        # 连接 Redis
        print(f"连接 Redis: {REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}")
        r = redis.Redis(
            host=REDIS_CONFIG['host'],
            port=REDIS_CONFIG['port'],
            password=REDIS_CONFIG['password'],
            decode_responses=False
        )
        
        # 测试连接
        r.ping()
        print("✓ Redis 连接成功")
        
        # 获取 token
        key = b"\xac\xed\x00\x05t\x00\x0fairwallex:token"
        print(f"执行: GET {key!r}")
        value = r.get(key)
        
        if value is None:
            raise ValueError("Token 未找到")
        
        # 提取 JWT token（跳过 Java 序列化前缀）
        token_start = value.find(b'eyJ')
        if token_start == -1:
            raise ValueError("无法解析 token 格式")
        
        token_data = value[token_start:].decode('utf-8')
        
        # 分离 token 和 timestamp
        if ':' in token_data:
            token, timestamp = token_data.rsplit(':', 1)
            print(f"✓ Token 获取成功")
            print(f"  过期时间戳: {timestamp}")
            return token
        else:
            return token_data
            
    except Exception as e:
        print(f"✗ Redis 错误: {e}")
        raise


def get_payment_account_id_from_db(app_user_id):
    """
    从 PostgreSQL 数据库获取 payment_account_id
    
    Args:
        app_user_id (str): 用户ID
        
    Returns:
        str: payment_account_id
    """
    print("\n" + "=" * 80)
    print("步骤 2: 从数据库获取 payment_account_id")
    print("=" * 80)
    
    conn = None
    try:
        # 连接数据库
        print(f"连接数据库: {PG_CONFIG['host']}:{PG_CONFIG['port']}/{PG_CONFIG['database']}")
        conn = psycopg2.connect(
            host=PG_CONFIG['host'],
            port=PG_CONFIG['port'],
            database=PG_CONFIG['database'],
            user=PG_CONFIG['user'],
            password=PG_CONFIG['password']
        )
        print("✓ 数据库连接成功")
        
        # 执行查询
        cursor = conn.cursor()
        sql = """
            SELECT payment_account_id 
            FROM user_payment_binding 
            WHERE app_user_id = %s 
            ORDER BY id DESC 
            LIMIT 1
        """
        print(f"执行 SQL: {sql}")
        print(f"参数: app_user_id = {app_user_id}")
        
        cursor.execute(sql, (app_user_id,))
        result = cursor.fetchone()
        
        if result is None:
            raise ValueError(f"未找到用户 {app_user_id} 的 payment_account_id")
        
        payment_account_id = result[0]
        print(f"✓ payment_account_id: {payment_account_id}")
        
        cursor.close()
        return payment_account_id
        
    except Exception as e:
        print(f"✗ 数据库错误: {e}")
        raise
    finally:
        if conn:
            conn.close()


def create_transfer(token, payment_account_id, amount="20.01", currency="USD", reason="travel"):
    """
    调用 Airwallex API 创建充值转账
    
    Args:
        token (str): JWT token
        payment_account_id (str): 目标账户ID
        amount (str): 金额
        currency (str): 币种
        reason (str): 转账原因
        
    Returns:
        dict: API 响应结果
    """
    print("\n" + "=" * 80)
    print("步骤 3: 调用 Airwallex API 创建充值")
    print("=" * 80)
    
    try:
        # 生成请求ID（使用当前时间戳）
        request_id = str(int(time.time() * 1000))  # 毫秒级时间戳
        timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # 准备请求数据
        payload = {
            "amount": amount,
            "currency": currency,
            "destination": payment_account_id,
            "reason": reason,
            "reference": f"PMT{timestamp_str}",
            "request_id": request_id
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        
        print(f"API URL: {AIRWALLEX_API_URL}")
        print(f"请求数据:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        
        # 发送请求
        print("\n发送 POST 请求...")
        response = requests.post(
            AIRWALLEX_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"响应状态码: {response.status_code}")
        
        # 解析响应
        if response.status_code in [200, 201]:
            result = response.json()
            print("✓ 充值创建成功!")
            print("\n响应数据:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result
        else:
            print(f"✗ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            raise Exception(f"API 请求失败: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"✗ API 调用错误: {e}")
        raise


def main():
    """
    主流程
    """
    print("\n")
    print("*" * 80)
    print(" " * 25 + "Airwallex 充值流程自动化")
    print("*" * 80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"目标用户: {APP_USER_ID}")
    print("*" * 80)
    
    try:
        # 步骤 1: 获取 token
        token = get_token_from_redis()
        
        # 步骤 2: 获取 payment_account_id
        payment_account_id = get_payment_account_id_from_db(APP_USER_ID)
        
        # 步骤 3: 创建充值
        result = create_transfer(
            token=token,
            payment_account_id=payment_account_id,
            amount="20.01",
            currency="USD",
            reason="travel"  # 有效的枚举值
        )
        
        # 总结
        print("\n" + "=" * 80)
        print("执行完成")
        print("=" * 80)
        print(f"✓ 转账ID: {result.get('id')}")
        print(f"✓ 金额: {result.get('amount')} {result.get('currency')}")
        print(f"✓ 状态: {result.get('status')}")
        print(f"✓ 短参考ID: {result.get('short_reference_id')}")
        print(f"✓ 创建时间: {result.get('created_at')}")
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        print("\n" + "=" * 80)
        print("执行失败")
        print("=" * 80)
        print(f"错误: {e}")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
