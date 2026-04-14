#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Airwallex 充值流程自动化脚本（增强版 - 支持命令行参数）

使用示例：
    # 使用默认参数
    python airwallex_recharge_cli.py
    
    # 指定用户ID和金额
    python airwallex_recharge_cli.py --user-id 796133836057336352 --amount 50.00
    
    # 完整参数
    python airwallex_recharge_cli.py \
        --user-id 796133836057336352 \
        --amount 100.00 \
        --currency USD \
        --reason living_expenses
"""
import sys
import json
import time
import argparse
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

# 有效的 reason 枚举值
VALID_REASONS = [
    'wages_salary', 'donation_charitable_contribution', 'personal_remittance',
    'transfer_to_own_account', 'pension', 'family_support', 'living_expenses',
    'education_training', 'travel', 'investment_proceeds', 'investment_capital',
    'loan_credit_repayment', 'taxes', 'goods_purchased', 'business_expenses',
    'medical_services', 'professional_business_services', 'technical_services',
    'other_services', 'construction', 'freight', 'real_estate', 'settlement',
    'commission'
]


def get_token_from_redis():
    """从 Redis 获取 Airwallex token"""
    print("=" * 80)
    print("步骤 1: 从 Redis 获取 Airwallex Token")
    print("=" * 80)
    
    try:
        print(f"连接 Redis: {REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}")
        r = redis.Redis(
            host=REDIS_CONFIG['host'],
            port=REDIS_CONFIG['port'],
            password=REDIS_CONFIG['password'],
            decode_responses=False
        )
        
        r.ping()
        print("✓ Redis 连接成功")
        
        key = b"\xac\xed\x00\x05t\x00\x0fairwallex:token"
        value = r.get(key)
        
        if value is None:
            raise ValueError("Token 未找到")
        
        token_start = value.find(b'eyJ')
        if token_start == -1:
            raise ValueError("无法解析 token 格式")
        
        token_data = value[token_start:].decode('utf-8')
        
        if ':' in token_data:
            token, timestamp = token_data.rsplit(':', 1)
            print(f"✓ Token 获取成功")
            print(f"  过期时间戳: {timestamp}")
            
            # 检查 token 是否即将过期（提前 5 分钟警告）
            current_ts = int(time.time() * 1000)
            expire_ts = int(timestamp)
            if expire_ts - current_ts < 300000:  # 5 分钟 = 300000 毫秒
                print(f"  ⚠️  警告: Token 即将过期！")
            
            return token
        else:
            return token_data
            
    except Exception as e:
        print(f"✗ Redis 错误: {e}")
        raise


def get_payment_account_id_from_db(app_user_id):
    """从 PostgreSQL 数据库获取 payment_account_id"""
    print("\n" + "=" * 80)
    print("步骤 2: 从数据库获取 payment_account_id")
    print("=" * 80)
    
    conn = None
    try:
        print(f"连接数据库: {PG_CONFIG['host']}:{PG_CONFIG['port']}/{PG_CONFIG['database']}")
        conn = psycopg2.connect(
            host=PG_CONFIG['host'],
            port=PG_CONFIG['port'],
            database=PG_CONFIG['database'],
            user=PG_CONFIG['user'],
            password=PG_CONFIG['password']
        )
        print("✓ 数据库连接成功")
        
        cursor = conn.cursor()
        sql = """
            SELECT payment_account_id 
            FROM user_payment_binding 
            WHERE app_user_id = %s 
            ORDER BY id DESC 
            LIMIT 1
        """
        print(f"执行 SQL 查询用户 {app_user_id} 的 payment_account_id")
        
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


def create_transfer(token, payment_account_id, amount, currency, reason):
    """调用 Airwallex API 创建充值转账"""
    print("\n" + "=" * 80)
    print("步骤 3: 调用 Airwallex API 创建充值")
    print("=" * 80)
    
    try:
        request_id = str(int(time.time() * 1000))
        timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
        
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
        
        print("\n发送 POST 请求...")
        response = requests.post(
            AIRWALLEX_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"响应状态码: {response.status_code}")
        
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


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='Airwallex 充值流程自动化工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
示例用法:
  # 使用默认参数（用户: 796133836057336352, 金额: 21.01 USD）
  python %(prog)s
  
  # 指定用户ID和金额
  python %(prog)s --user-id 796133836057336352 --amount 50.00
  
  # 完整参数
  python %(prog)s --user-id 796133836057336352 --amount 100.00 --currency USD --reason living_expenses
  
有效的 reason 枚举值:
  {', '.join(VALID_REASONS[:5])}
  {', '.join(VALID_REASONS[5:10])}
  {', '.join(VALID_REASONS[10:15])}
  {', '.join(VALID_REASONS[15:20])}
  {', '.join(VALID_REASONS[20:])}
        """
    )
    
    parser.add_argument(
        '--user-id',
        type=str,
        default='796133836057336352',
        help='用户ID（用于查询 payment_account_id）'
    )
    
    parser.add_argument(
        '--amount',
        type=str,
        default='21.01',
        help='充值金额（默认: 21.01）'
    )
    
    parser.add_argument(
        '--currency',
        type=str,
        default='USD',
        help='币种（默认: USD）'
    )
    
    parser.add_argument(
        '--reason',
        type=str,
        default='travel',
        choices=VALID_REASONS,
        help='充值原因（默认: travel）'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='试运行模式：只获取数据，不实际创建充值'
    )
    
    return parser.parse_args()


def main():
    """主流程"""
    args = parse_arguments()
    
    print("\n")
    print("*" * 80)
    print(" " * 25 + "Airwallex 充值流程自动化")
    print("*" * 80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"目标用户: {args.user_id}")
    print(f"充值金额: {args.amount} {args.currency}")
    print(f"充值原因: {args.reason}")
    if args.dry_run:
        print("运行模式: 试运行（不会实际创建充值）")
    print("*" * 80)
    
    try:
        # 步骤 1: 获取 token
        token = get_token_from_redis()
        
        # 步骤 2: 获取 payment_account_id
        payment_account_id = get_payment_account_id_from_db(args.user_id)
        
        if args.dry_run:
            print("\n" + "=" * 80)
            print("试运行模式 - 跳过 API 调用")
            print("=" * 80)
            print(f"✓ Token 已获取")
            print(f"✓ payment_account_id: {payment_account_id}")
            print(f"如果执行，将创建充值:")
            print(f"  - 金额: {args.amount} {args.currency}")
            print(f"  - 目标: {payment_account_id}")
            print(f"  - 原因: {args.reason}")
            return 0
        
        # 步骤 3: 创建充值
        result = create_transfer(
            token=token,
            payment_account_id=payment_account_id,
            amount=args.amount,
            currency=args.currency,
            reason=args.reason
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
