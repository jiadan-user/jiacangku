# PostgreSQL 支付状态更新工具使用说明

## 📋 概述

用于更新 `payment_flow` 表的 `status` 字段，通常在测试充值流程时使用。

## 🔧 工具信息

**文件**: `update_payment_status.py`

**数据库配置**:
```yaml
Host: pgsql-test.pdb.58dns.org
Port: 29000
Database: pdb58_easypost
User: epost_test
Password: GUGXzw49K6Ndp7
```

**表结构**: `payment_flow`
```sql
payment_no   VARCHAR    支付单号（主键/唯一键）
status       INTEGER    状态值
amount       DECIMAL    金额
currency     VARCHAR    币种
create_time  TIMESTAMP  创建时间
update_time  TIMESTAMP  更新时间
```

## 🚀 使用方法

### 1. 查看帮助

```bash
python test_cases/airwallex_recharge/update_payment_status.py --help
```

### 2. 查询支付记录（不更新）

```bash
# 仅查询，不做任何更改
python test_cases/airwallex_recharge/update_payment_status.py \
    --payment-no PMT20260304172445 \
    --query-only
```

**输出示例**:
```
================================================================================
PostgreSQL 支付流水查询工具
================================================================================

连接数据库: pgsql-test.pdb.58dns.org:29000/pdb58_easypost
✓ 数据库连接成功

查询记录...
✓ 查询成功

================================================================================
记录详情
================================================================================
payment_no: PMT20260304172445
status: 0
amount: 20.01
currency: USD
create_time: 2026-03-04 17:24:45
update_time: 2026-03-04 17:24:45
================================================================================
```

### 3. 更新支付状态为 1（默认）

```bash
python test_cases/airwallex_recharge/update_payment_status.py \
    --payment-no PMT20260304172445
```

**输出示例**:
```
================================================================================
PostgreSQL 支付流水状态更新工具
================================================================================
执行时间: 2026-03-04 17:45:30
================================================================================

连接数据库: pgsql-test.pdb.58dns.org:29000/pdb58_easypost
✓ 数据库连接成功

查询当前记录...
✓ 找到记录
  payment_no: PMT20260304172445
  当前 status: 0

执行更新...
SQL: UPDATE payment_flow SET status = %s WHERE payment_no = %s
参数: status=1, payment_no=PMT20260304172445
✓ 更新成功！影响行数: 1

确认更新结果...
✓ 确认成功
  payment_no: PMT20260304172445
  更新后 status: 1

================================================================================
更新完成
================================================================================
payment_no: PMT20260304172445
状态变更: 0 → 1
================================================================================
```

### 4. 更新支付状态为指定值

```bash
# 更新状态为 2
python test_cases/airwallex_recharge/update_payment_status.py \
    --payment-no PMT20260304172445 \
    --status 2
```

### 5. 使用不同的数据库

```bash
python test_cases/airwallex_recharge/update_payment_status.py \
    --payment-no PMT20260304172445 \
    --host your-db.example.com \
    --port 5432 \
    --database your_database \
    --user your_user \
    --password your_password
```

## 🔄 完整充值测试流程

### 步骤 1: 创建充值

```bash
python test_cases/airwallex_recharge/airwallex_recharge_cli.py \
    --amount 20.01 \
    --reason travel
```

**记录返回的 reference**:
```json
{
  "reference": "PMT20260304172445",
  "status": "NEW"
}
```

### 步骤 2: 查询数据库中的支付记录

```bash
python test_cases/airwallex_recharge/update_payment_status.py \
    --payment-no PMT20260304172445 \
    --query-only
```

### 步骤 3: 更新支付状态

```bash
# 模拟支付成功，更新状态为 1
python test_cases/airwallex_recharge/update_payment_status.py \
    --payment-no PMT20260304172445 \
    --status 1
```

### 步骤 4: 再次确认状态已更新

```bash
python test_cases/airwallex_recharge/update_payment_status.py \
    --payment-no PMT20260304172445 \
    --query-only
```

## 📊 状态值说明

| Status | 说明 | 备注 |
|--------|------|------|
| 0 | 待支付 | 初始状态 |
| 1 | 支付成功 | 充值完成 |
| 2 | 支付失败 | 充值失败 |
| 3 | 已退款 | 已退款 |
| 4 | 处理中 | 处理中 |

*注: 实际状态值含义请参考业务文档*

## 🎯 命令行参数

| 参数 | 说明 | 默认值 | 必需 |
|------|------|--------|------|
| `--payment-no` | 支付单号（Reference_ID） | - | ✅ |
| `--status` | 目标状态值 | 1 | ❌ |
| `--query-only` | 仅查询，不更新 | false | ❌ |
| `--host` | 数据库主机 | pgsql-test.pdb.58dns.org | ❌ |
| `--port` | 数据库端口 | 29000 | ❌ |
| `--database` | 数据库名 | pdb58_easypost | ❌ |
| `--user` | 数据库用户 | epost_test | ❌ |
| `--password` | 数据库密码 | GUGXzw49K6Ndp7 | ❌ |

## 💡 在自动化测试中使用

### Python 代码示例

```python
import subprocess
import json

def test_recharge_flow():
    # 1. 创建充值
    result = subprocess.run(
        ['python', 'test_cases/airwallex_recharge/airwallex_recharge_cli.py',
         '--amount', '20.01'],
        capture_output=True,
        text=True
    )
    
    # 解析 reference
    # 假设从输出中提取 reference
    payment_no = "PMT20260304172445"
    
    # 2. 查询初始状态
    result = subprocess.run(
        ['python', 'test_cases/airwallex_recharge/update_payment_status.py',
         '--payment-no', payment_no,
         '--query-only'],
        capture_output=True,
        text=True
    )
    
    # 3. 更新状态为成功
    result = subprocess.run(
        ['python', 'test_cases/airwallex_recharge/update_payment_status.py',
         '--payment-no', payment_no,
         '--status', '1'],
        capture_output=True,
        text=True
    )
    
    # 4. 验证状态已更新
    assert '更新成功' in result.stdout
```

### 直接使用 psycopg2

```python
import psycopg2

def update_payment_status(payment_no, status=1):
    """更新支付状态"""
    conn = psycopg2.connect(
        host='pgsql-test.pdb.58dns.org',
        port=29000,
        database='pdb58_easypost',
        user='epost_test',
        password='GUGXzw49K6Ndp7'
    )
    
    try:
        cursor = conn.cursor()
        
        # 更新状态
        sql = "UPDATE payment_flow SET status = %s WHERE payment_no = %s"
        cursor.execute(sql, (status, payment_no))
        conn.commit()
        
        print(f"✓ 更新成功: {payment_no} -> status={status}")
        
        cursor.close()
    finally:
        conn.close()
```

## 🐛 常见问题

### Q1: 提示 "未找到记录"

**原因**:
- payment_no 不存在
- payment_no 拼写错误
- 数据库中还未创建该记录

**解决**:
- 确认 payment_no 正确
- 先执行充值流程创建记录
- 检查是否连接了正确的数据库

### Q2: 数据库连接失败

**原因**:
- 网络不通
- 数据库地址或端口错误
- 用户名密码错误

**解决**:
- 检查网络连通性
- 确认配置信息正确
- 联系 DBA 确认权限

### Q3: 更新失败

**原因**:
- 权限不足
- 表或字段不存在
- 数据类型不匹配

**解决**:
- 确认用户有 UPDATE 权限
- 确认表结构正确
- 检查 status 值类型（应为整数）

## 🔒 安全注意事项

1. **不要在生产环境直接更新数据**
2. **更新前先备份或查询确认**
3. **使用事务确保数据一致性**（工具已内置）
4. **敏感信息不要提交到代码仓库**

## 📚 相关工具

- **充值创建**: `airwallex_recharge_cli.py`
- **Redis 查询**: `redis_query_tool.py`
- **验证码获取**: `get_email_verify_code.py`

---

**创建时间**: 2026-03-04  
**最后更新**: 2026-03-04  
**工具版本**: v1.0
