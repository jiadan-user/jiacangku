#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redis 通用查询工具

用途: 从 Redis 获取任意 key 的值
支持命令行参数自定义 key
"""
import sys
import argparse
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

# 默认查询的 Key
DEFAULT_KEY = 'ucenter:verify:code:100002:wangyongli@58.com'


def get_redis_value(key, decode=True):
    """
    从 Redis 获取指定 key 的值
    
    Args:
        key (str): Redis key
        decode (bool): 是否解码为字符串
        
    Returns:
        str/bytes: key 对应的值
    """
    print("=" * 80)
    print("Redis 通用查询工具")
    print("=" * 80)
    
    try:
        # 连接 Redis
        print(f"连接 Redis: {REDIS_CONFIG['host']}:{REDIS_CONFIG['port']}")
        r = redis.Redis(
            host=REDIS_CONFIG['host'],
            port=REDIS_CONFIG['port'],
            password=REDIS_CONFIG['password'],
            decode_responses=decode
        )
        
        # 测试连接
        r.ping()
        print("✓ Redis 连接成功")
        
        # 获取值
        print(f"\n执行: GET {key}")
        value = r.get(key)
        
        if value is None:
            print(f"\n✗ Key 不存在或已过期: {key}")
            return None
        
        print("\n" + "=" * 80)
        print("查询成功")
        print("=" * 80)
        print(f"Key: {key}")
        print(f"Value: {value}")
        print("=" * 80)
        
        # 检查 TTL（剩余过期时间）
        ttl = r.ttl(key)
        if ttl > 0:
            minutes = ttl // 60
            seconds = ttl % 60
            print(f"剩余有效时间: {ttl} 秒 ({minutes} 分 {seconds} 秒)")
        elif ttl == -1:
            print("该 Key 永不过期")
        elif ttl == -2:
            print("该 Key 不存在")
        
        # 获取 key 类型
        key_type = r.type(key)
        print(f"数据类型: {key_type}")
        
        return value
        
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


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='Redis 通用查询工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 使用默认 key（邮箱验证码）
  python %(prog)s
  
  # 查询指定 key
  python %(prog)s --key "ucenter:verify:code:100002:wangyongli@58.com"
  
  # 查询其他验证码
  python %(prog)s --key "ucenter:verify:code:100002:another@58.com"
  
  # 不解码为字符串（返回原始字节）
  python %(prog)s --key "some:binary:key" --no-decode
        """
    )
    
    parser.add_argument(
        '--key',
        type=str,
        default=DEFAULT_KEY,
        help=f'要查询的 Redis key（默认: {DEFAULT_KEY}）'
    )
    
    parser.add_argument(
        '--no-decode',
        action='store_true',
        help='不解码为字符串，返回原始字节'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default=REDIS_CONFIG['host'],
        help=f'Redis 主机地址（默认: {REDIS_CONFIG["host"]}）'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=REDIS_CONFIG['port'],
        help=f'Redis 端口（默认: {REDIS_CONFIG["port"]}）'
    )
    
    parser.add_argument(
        '--password',
        type=str,
        default=REDIS_CONFIG['password'],
        help='Redis 密码'
    )
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_arguments()
    
    # 更新配置
    global REDIS_CONFIG
    REDIS_CONFIG = {
        'host': args.host,
        'port': args.port,
        'password': args.password
    }
    
    # 获取值
    decode = not args.no_decode
    value = get_redis_value(args.key, decode)
    
    if value is not None:
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
