#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis 邮箱验证码获取工具

用途: 从 Redis 获取用户邮箱验证码
"""
import sys
import redis

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Redis 配置
REDIS_CONFIG = {
    'host': 'test-yongjia01.rdb.58dns.org',
    'port': 50584,
    'password': '1c34ca4035bf7bc6'
}

# 验证码 Key
VERIFY_CODE_KEY = 'ucenter:verify:code:100002:wangyongli@58.com'


def get_verify_code():
    """
    从 Redis 获取邮箱验证码
    
    Returns:
        str: 验证码
    """
    print("=" * 80)
    print("Redis 邮箱验证码获取工具")
    print("=" * 80)
    
    try:
        # 连接 Redis
        print(f"连接 Redis: {REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}")
        r = redis.Redis(
            host=REDIS_CONFIG['host'],
            port=REDIS_CONFIG['port'],
            password=REDIS_CONFIG['password'],
            decode_responses=True  # 自动解码为字符串
        )
        
        # 测试连接
        r.ping()
        print("✓ Redis 连接成功")
        
        # 获取验证码
        print(f"\n执行: GET {VERIFY_CODE_KEY}")
        verify_code = r.get(VERIFY_CODE_KEY)
        
        if verify_code is None:
            print("✗ 验证码不存在或已过期")
            return None
        
        print("\n" + "=" * 80)
        print("验证码获取成功")
        print("=" * 80)
        print(f"Key: {VERIFY_CODE_KEY}")
        print(f"验证码: {verify_code}")
        print("=" * 80)
        
        # 检查 TTL（剩余过期时间）
        ttl = r.ttl(VERIFY_CODE_KEY)
        if ttl > 0:
            print(f"剩余有效时间: {ttl} 秒 ({ttl // 60} 分钟)")
        elif ttl == -1:
            print("该 Key 永不过期")
        elif ttl == -2:
            print("该 Key 不存在")
        
        return verify_code
        
    except redis.ConnectionError as e:
        print(f"✗ Redis 连接错误: {e}")
        return None
    except redis.AuthenticationError as e:
        print(f"✗ Redis 认证错误: {e}")
        return None
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主函数"""
    verify_code = get_verify_code()
    
    if verify_code:
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
