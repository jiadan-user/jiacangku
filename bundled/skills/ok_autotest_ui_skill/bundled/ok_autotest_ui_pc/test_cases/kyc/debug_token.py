"""
调试脚本：检查Redis中的token格式
"""
import redis
import re
import base64

REDIS_HOST = "redis-shark-test.rdb.58dns.org"
REDIS_PORT = 50554
REDIS_PASSWORD = "6b0d1d0d640eb6fa"
REDIS_KEY = b"\xac\xed\x00\x05t\x00\x0fairwallex:token"

try:
    # 连接Redis
    print("连接Redis...")
    client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=False
    )
    client.ping()
    print("Redis连接成功\n")
    
    # 获取token
    print("获取token...")
    token_bytes = client.get(REDIS_KEY)
    
    if not token_bytes:
        print("Token不存在")
        exit(1)
    
    print(f"Token原始长度: {len(token_bytes)} bytes\n")
    
    # 显示前100字节（16进制）
    print("Token前100字节(hex):")
    print(token_bytes[:100].hex())
    print()
    
    # 尝试解码
    print("尝试解码为latin-1:")
    token_str = token_bytes.decode('latin-1')
    print(f"解码后长度: {len(token_str)}")
    # print(f"前200字符: {repr(token_str[:200])}")  # Skip to avoid encoding issues
    print()
    
    # 查找JWT token模式
    print("查找JWT token...")
    jwt_pattern = r'(eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+)'
    matches = re.findall(jwt_pattern, token_str)
    
    if matches:
        print(f"找到 {len(matches)} 个JWT token")
        for i, match in enumerate(matches):
            print(f"\nJWT Token {i+1}:")
            print(f"  长度: {len(match)}")
            print(f"  前50字符: {match[:50]}...")
            print(f"  后50字符: ...{match[-50:]}")
    else:
        print("未找到JWT token")
    
    # 查找带时间戳的token
    print("\n查找带时间戳的token...")
    expiry_pattern = r'(eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+):(\d+)'
    expiry_matches = re.findall(expiry_pattern, token_str)
    
    if expiry_matches:
        print(f"找到 {len(expiry_matches)} 个带时间戳的token")
        for i, (token, timestamp) in enumerate(expiry_matches):
            print(f"\nToken {i+1}:")
            print(f"  JWT长度: {len(token)}")
            print(f"  时间戳: {timestamp}")
            print(f"  完整格式: {token}:{timestamp}")
    else:
        print("未找到带时间戳的token")
    
    # 建议的token格式
    if expiry_matches:
        suggested_token = f"{expiry_matches[0][0]}:{expiry_matches[0][1]}"
        print(f"\n建议使用的token格式:")
        print(f"  {suggested_token[:50]}...:{expiry_matches[0][1]}")
    elif matches:
        suggested_token = matches[0]
        print(f"\n建议使用的token格式:")
        print(f"  {suggested_token[:50]}...")
    
    client.close()
    print("\n完成")
    
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
