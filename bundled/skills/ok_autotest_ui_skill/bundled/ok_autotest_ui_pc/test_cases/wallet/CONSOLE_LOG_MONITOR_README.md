# 控制台日志监听 - 自动清除提现限制

## 功能说明

测试框架现在支持监听浏览器控制台日志，当检测到 `validation_status=Withdrawing` 时，会自动执行 SQL 语句清除提现限制。

## 工作原理

### 1. 监听机制

在 `test_wallet_withdrawal.py` 的 `shared_page` fixture 中，添加了控制台消息监听器：

```python
def handle_console_message(msg):
    """处理浏览器控制台消息"""
    text = msg.text
    # 检查是否包含 validation_status=Withdrawing
    if 'validation_status=Withdrawing' in text:
        logger.warning(f"⚠️ 检测到控制台日志: validation_status=Withdrawing")
        logger.info("🔧 自动执行SQL清除提现限制...")
        # 执行SQL清除限制
        subprocess.run(['python', 'test_cases/airwallex_recharge/update_payment_status.py', 
                       '--clear-withdrawal-restriction'])

# 绑定监听器
page.on("console", handle_console_message)
```

### 2. SQL 执行

当检测到目标日志时，会调用 `update_payment_status.py` 脚本执行以下 SQL：

```sql
UPDATE payment_flow
SET status = 1
WHERE payment_no = (
    SELECT payment_no
    FROM payment_flow
    WHERE payer_id = (
        SELECT payment_account_id
        FROM user_payment_binding
        WHERE app_user_id = '796133836057336352'
        ORDER BY id DESC
        LIMIT 1
    )
    AND payee_id = (
        SELECT payment_account_id
        FROM user_payment_binding
        WHERE app_user_id = '796133836057336352'
        ORDER BY id DESC
        LIMIT 1
    )
    ORDER BY id DESC
    LIMIT 1
)
```

## 使用方法

### 自动模式（推荐）

运行测试时，监听器会自动启用：

```bash
pytest test_cases/wallet/test_wallet_withdrawal.py -v
```

测试运行时会显示：
```
✓ 已启用控制台日志监听（自动清除提现限制）
```

当检测到目标日志时会显示：
```
⚠️ 检测到控制台日志: validation_status=Withdrawing
🔧 自动执行SQL清除提现限制...
✅ 提现限制已自动清除
```

### 手动模式

也可以手动执行清除命令：

```bash
# 使用默认用户ID (796133836057336352)
python test_cases/airwallex_recharge/update_payment_status.py --clear-withdrawal-restriction

# 指定用户ID
python test_cases/airwallex_recharge/update_payment_status.py \
    --clear-withdrawal-restriction \
    --app-user-id YOUR_USER_ID
```

## 配置

### 修改用户ID

如需修改默认用户ID，编辑 `update_payment_status.py`：

```python
def clear_withdrawal_restriction_by_user(app_user_id='YOUR_NEW_USER_ID'):
    ...
```

或在命令行指定：

```bash
python test_cases/airwallex_recharge/update_payment_status.py \
    --clear-withdrawal-restriction \
    --app-user-id YOUR_USER_ID
```

### 数据库配置

数据库连接配置在 `update_payment_status.py` 中：

```python
PG_CONFIG = {
    'host': 'pgsql-test.pdb.58dns.org',
    'port': 29000,
    'database': 'pdb58_easypost',
    'user': 'epost_test',
    'password': 'GUGXzw49K6Ndp7'
}
```

## 日志示例

### 成功清除

```
================================================================================
PostgreSQL 清除提现限制工具
================================================================================
执行时间: 2026-04-03 11:32:24
用户ID: 796133836057336352
================================================================================

连接数据库: pgsql-test.pdb.58dns.org:29000/pdb58_easypost
✓ 数据库连接成功

执行清除提现限制...
✓ 清除成功！影响行数: 1
  payment_no: 2039907313964855296
  更新后 status: 1

================================================================================
清除完成
================================================================================
```

### 无需清除

```
⚠️  未找到匹配的记录，可能没有需要清除的提现限制
```

## 注意事项

1. **仅测试环境使用**：此功能仅用于测试环境，请勿在生产环境使用
2. **权限要求**：需要数据库写入权限
3. **自动触发**：监听器会在整个测试会话期间保持活跃
4. **错误处理**：SQL 执行失败不会中断测试，只会记录错误日志

## 故障排查

### 问题：未检测到控制台日志

**原因**：浏览器可能未输出目标日志

**解决方案**：
1. 检查浏览器开发者工具中的控制台
2. 确认日志格式是否包含 `validation_status=Withdrawing`

### 问题：SQL 执行失败

**原因**：数据库连接问题或权限不足

**解决方案**：
1. 检查数据库配置
2. 验证数据库连接：`python test_cases/airwallex_recharge/update_payment_status.py --clear-withdrawal-restriction`
3. 检查数据库用户权限

### 问题：清除后仍有限制

**原因**：可能有多条待处理记录

**解决方案**：
1. 多次运行清除命令
2. 手动检查数据库中的 `payment_flow` 表

## 扩展

如需监听其他控制台日志并执行自定义操作，可以在 `handle_console_message` 函数中添加更多条件判断：

```python
def handle_console_message(msg):
    text = msg.text
    
    # 监听提现限制
    if 'validation_status=Withdrawing' in text:
        # 执行清除提现限制
        ...
    
    # 监听其他日志
    elif 'some_other_pattern' in text:
        # 执行其他操作
        ...
```
