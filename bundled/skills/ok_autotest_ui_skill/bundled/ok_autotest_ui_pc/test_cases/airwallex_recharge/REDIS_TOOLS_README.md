# Redis 查询工具使用说明

## 📋 概述

本目录提供了多个 Redis 查询工具，用于从不同的 Redis 服务器获取数据。

## 🔧 工具列表

### 1. `redis_query_tool.py` - 通用 Redis 查询工具 ⭐ **推荐**

**用途**: 查询任意 Redis key 的值，支持命令行参数自定义配置

**默认配置**:
```
Host: test-yongjia01.rdb.58dns.org
Port: 50584
Password: 1c34ca4035bf7bc6
默认 Key: ucenter:verify:code:100002:wangyongli@58.com
```

**使用示例**:

```bash
# 查看帮助
python redis_query_tool.py --help

# 使用默认配置查询邮箱验证码
python redis_query_tool.py

# 查询指定 key
python redis_query_tool.py --key "ucenter:verify:code:100002:wangyongli@58.com"

# 查询其他用户的验证码
python redis_query_tool.py --key "ucenter:verify:code:100002:another@58.com"

# 使用不同的 Redis 服务器
python redis_query_tool.py \
    --host another-redis.58dns.org \
    --port 6379 \
    --password your_password \
    --key "your:key"
```

**输出示例**:
```
================================================================================
Redis 通用查询工具
================================================================================
连接 Redis: test-yongjia01.rdb.58dns.org:50584
✓ Redis 连接成功

执行: GET ucenter:verify:code:100002:wangyongli@58.com

================================================================================
查询成功
================================================================================
Key: ucenter:verify:code:100002:wangyongli@58.com
Value: 3277
================================================================================
剩余有效时间: 1163 秒 (19 分 23 秒)
数据类型: string
```

---

### 2. `get_email_verify_code.py` - 邮箱验证码获取工具

**用途**: 快速获取指定邮箱的验证码（固定配置）

**配置**:
```
Host: test-yongjia01.rdb.58dns.org
Port: 50584
Password: 1c34ca4035bf7bc6
Key: ucenter:verify:code:100002:wangyongli@58.com
```

**使用示例**:

```bash
# 直接运行
python get_email_verify_code.py
```

**输出示例**:
```
================================================================================
Redis 邮箱验证码获取工具
================================================================================
连接 Redis: test-yongjia01.rdb.58dns.org:50584
✓ Redis 连接成功

执行: GET ucenter:verify:code:100002:wangyongli@58.com

================================================================================
验证码获取成功
================================================================================
Key: ucenter:verify:code:100002:wangyongli@58.com
验证码: 3277
================================================================================
剩余有效时间: 1219 秒 (20 分钟)
```

---

### 3. `redis_get_token.py` - Airwallex Token 获取工具

**用途**: 获取 Airwallex API Token

**配置**:
```
Host: redis-shark-test.rdb.58dns.org
Port: 50554
Password: 6b0d1d0d640eb6fa
Key: \xac\xed\x00\x05t\x00\x0fairwallex:token
```

**使用示例**:

```bash
# 直接运行
python redis_get_token.py
```

---

## 🔑 参数说明

### `redis_query_tool.py` 支持的参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--key` | 要查询的 Redis key | ucenter:verify:code:100002:wangyongli@58.com |
| `--host` | Redis 主机地址 | test-yongjia01.rdb.58dns.org |
| `--port` | Redis 端口 | 50584 |
| `--password` | Redis 密码 | 1c34ca4035bf7bc6 |
| `--no-decode` | 不解码为字符串 | false |

---

## 📊 Redis 服务器配置

### 邮箱验证码服务器

```yaml
Host: test-yongjia01.rdb.58dns.org
Port: 50584
Password: 1c34ca4035bf7bc6
用途: 用户中心邮箱验证码存储
Key 格式: ucenter:verify:code:{tenant_id}:{email}
```

### Airwallex Token 服务器

```yaml
Host: redis-shark-test.rdb.58dns.org
Port: 50554
Password: 6b0d1d0d640eb6fa
用途: Airwallex API Token 存储
Key 格式: \xac\xed\x00\x05t\x00\x0fairwallex:token (Java 序列化格式)
```

---

## 🎯 常见使用场景

### 场景 1: 获取邮箱验证码用于测试

```bash
# 方式 1: 使用专用工具
python get_email_verify_code.py

# 方式 2: 使用通用工具
python redis_query_tool.py
```

### 场景 2: 查询不同用户的验证码

```bash
python redis_query_tool.py --key "ucenter:verify:code:100002:user@example.com"
```

### 场景 3: 查询其他类型的数据

```bash
python redis_query_tool.py --key "session:user:12345"
```

### 场景 4: 连接其他 Redis 服务器

```bash
python redis_query_tool.py \
    --host your-redis.example.com \
    --port 6379 \
    --password your_password \
    --key "your:key"
```

---

## 🐛 常见问题

### Q1: 验证码不存在或已过期

**现象**: 输出 "Key 不存在或已过期"

**原因**:
- 验证码还未生成
- 验证码已过期（通常 5-30 分钟）
- Key 拼写错误

**解决**:
- 先触发验证码发送（登录页面点击发送验证码）
- 立即查询 Redis
- 确认 Key 格式正确

### Q2: Redis 连接失败

**现象**: "Redis 连接错误"

**原因**:
- 网络不通
- Redis 服务器地址或端口错误
- 防火墙阻止

**解决**:
- 检查网络连通性
- 确认 host 和 port 配置正确
- 联系运维开通访问权限

### Q3: Redis 认证失败

**现象**: "Redis 认证错误"

**原因**:
- 密码错误
- Redis 服务器配置了认证但未提供密码

**解决**:
- 确认密码正确
- 使用 `--password` 参数指定密码

---

## 💡 高级用法

### 在 Python 代码中使用

```python
import redis

# 连接 Redis
r = redis.Redis(
    host='test-yongjia01.rdb.58dns.org',
    port=50584,
    password='1c34ca4035bf7bc6',
    decode_responses=True
)

# 获取验证码
verify_code = r.get('ucenter:verify:code:100002:wangyongli@58.com')
print(f"验证码: {verify_code}")

# 检查剩余有效时间
ttl = r.ttl('ucenter:verify:code:100002:wangyongli@58.com')
print(f"剩余时间: {ttl} 秒")
```

### 在自动化测试中使用

```python
from pages.login_page import LoginPage
import redis

def test_login_with_email_verification():
    # 打开登录页面
    login_page = LoginPage(page)
    login_page.goto()
    
    # 输入邮箱
    email = "wangyongli@58.com"
    login_page.input_email(email)
    
    # 点击发送验证码
    login_page.click_send_code()
    
    # 从 Redis 获取验证码
    r = redis.Redis(
        host='test-yongjia01.rdb.58dns.org',
        port=50584,
        password='1c34ca4035bf7bc6',
        decode_responses=True
    )
    
    verify_code = r.get(f'ucenter:verify:code:100002:{email}')
    
    # 输入验证码
    login_page.input_verify_code(verify_code)
    
    # 点击登录
    login_page.click_login()
    
    # 验证登录成功
    assert login_page.is_logged_in()
```

---

## 📚 相关文档

- **Airwallex 充值流程**: 查看 `README.md`
- **快速参考**: 查看 `AIRWALLEX_QUICKREF.txt`
- **Redis 官方文档**: https://redis.io/documentation

---

## 📝 更新日志

### v1.1 (2026-03-04)
- ✅ 新增通用 Redis 查询工具 (`redis_query_tool.py`)
- ✅ 新增邮箱验证码获取工具 (`get_email_verify_code.py`)
- ✅ 支持命令行参数自定义配置
- ✅ 支持 TTL 显示
- ✅ 支持数据类型显示

### v1.0 (2026-03-04)
- ✅ 初始版本：Airwallex Token 获取工具

---

**创建时间**: 2026-03-04  
**最后更新**: 2026-03-04  
**维护状态**: 活跃
