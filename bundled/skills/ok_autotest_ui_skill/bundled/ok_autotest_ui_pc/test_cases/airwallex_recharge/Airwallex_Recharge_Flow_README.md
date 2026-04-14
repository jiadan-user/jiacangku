# Airwallex 充值流程自动化文档

## 📋 概述

这是一个完整的 Airwallex 充值流程自动化脚本，自动完成以下步骤：

1. 从 Redis 获取 Airwallex API Token
2. 从 PostgreSQL 数据库查询用户的 payment_account_id
3. 调用 Airwallex API 创建充值转账

## 📁 文件说明

| 文件名 | 说明 |
|--------|------|
| `airwallex_recharge_flow.py` | 主执行脚本 |
| `airwallex_config_template.py` | 配置文件模板（包含所有可配置项） |
| `redis_get_token.py` | 单独的 Redis token 获取工具 |
| `airwallex_transfer_body.json` | API 请求体示例（用于 curl） |

## 🚀 快速开始

### 1. 环境要求

- Python 3.7+
- 依赖包：
  - `redis` - Redis 客户端
  - `psycopg2-binary` - PostgreSQL 客户端
  - `requests` - HTTP 客户端

### 2. 安装依赖

```bash
pip install redis psycopg2-binary requests
```

### 3. 执行充值流程

直接运行主脚本：

```bash
python airwallex_recharge_flow.py
```

### 4. 执行结果示例

```
********************************************************************************
                         Airwallex 充值流程自动化
********************************************************************************
执行时间: 2026-03-04 17:24:44
目标用户: 796133836057336352
********************************************************************************

步骤 1: 从 Redis 获取 Airwallex Token
✓ Redis 连接成功
✓ Token 获取成功

步骤 2: 从数据库获取 payment_account_id
✓ 数据库连接成功
✓ payment_account_id: acct__z8GKFiwOYezx60YxHiyMg

步骤 3: 调用 Airwallex API 创建充值
✓ 充值创建成功!

================================================================================
执行完成
================================================================================
✓ 转账ID: tr_WfaAp-yLOOu0AexSZMyQ2Q
✓ 金额: 20.01 USD
✓ 状态: NEW
✓ 短参考ID: D260304-DG07ZKQ
✓ 创建时间: 2026-03-04T09:24:45+0000
================================================================================
```

## ⚙️ 配置说明

### Redis 配置

```python
REDIS_CONFIG = {
    'host': 'redis-shark-test.rdb.58dns.org',
    'port': 50554,
    'password': '6b0d1d0d640eb6fa'
}
```

### PostgreSQL 配置

```python
PG_CONFIG = {
    'host': 'pgsql-test.pdb.58dns.org',
    'port': 29000,
    'database': 'pdb58_easypost',
    'user': 'epost_test',
    'password': 'GUGXzw49K6Ndp7'
}
```

### 充值参数配置

在脚本中修改以下参数：

- `APP_USER_ID`: 用户ID（用于查询 payment_account_id）
- `amount`: 充值金额（默认 "20.01"）
- `currency`: 币种（默认 "USD"）
- `reason`: 充值原因（必须是 Airwallex 允许的枚举值）

### Reason 枚举值说明

`reason` 字段必须是以下值之一：

| 枚举值 | 中文说明 |
|--------|---------|
| `wages_salary` | 工资 |
| `donation_charitable_contribution` | 捐赠 |
| `personal_remittance` | 个人汇款 |
| `transfer_to_own_account` | 转账到自己账户 |
| `pension` | 养老金 |
| `family_support` | 家庭支持 |
| `living_expenses` | 生活费用 |
| `education_training` | 教育培训 |
| `travel` | 旅行 ⭐（默认值） |
| `investment_proceeds` | 投资收益 |
| `investment_capital` | 投资资本 |
| `loan_credit_repayment` | 贷款偿还 |
| `taxes` | 税费 |
| `goods_purchased` | 购买商品 |
| `business_expenses` | 业务费用 |
| `medical_services` | 医疗服务 |
| `professional_business_services` | 专业商业服务 |
| `technical_services` | 技术服务 |
| `other_services` | 其他服务 |
| `construction` | 建筑 |
| `freight` | 货运 |
| `real_estate` | 房地产 |
| `settlement` | 结算 |
| `commission` | 佣金 |

## 📝 自定义充值参数

### 方法 1：修改脚本中的默认值

编辑 `airwallex_recharge_flow.py`，找到 `main()` 函数中的充值调用：

```python
result = create_transfer(
    token=token,
    payment_account_id=payment_account_id,
    amount="20.01",          # 修改充值金额
    currency="USD",           # 修改币种
    reason="travel"           # 修改充值原因
)
```

### 方法 2：修改脚本支持命令行参数

可以扩展脚本支持命令行参数，例如：

```bash
python airwallex_recharge_flow.py --amount 50.00 --currency USD --reason travel
```

## 🔧 独立工具使用

### 1. 单独获取 Redis Token

```bash
python redis_get_token.py
```

### 2. 使用 curl 发送请求

修改 `airwallex_transfer_body.json` 中的参数，然后执行：

```bash
curl.exe -s -w "\n" ^
  --request POST ^
  --url "https://api-demo.airwallex.com/api/v1/connected_account_transfers/create" ^
  --header "Content-Type: application/json" ^
  --header "Authorization: Bearer {你的token}" ^
  --data "@airwallex_transfer_body.json"
```

## 🔍 故障排查

### 问题 1: Redis 连接失败

**症状**: `Connection error` 或 `Authentication error`

**解决方案**:
- 检查 Redis 配置（host、port、password）
- 确认网络连通性
- 验证密码是否正确

### 问题 2: 数据库连接失败

**症状**: `Database connection error`

**解决方案**:
- 检查 PostgreSQL 配置
- 确认数据库服务是否运行
- 验证用户名和密码

### 问题 3: API 返回 400 错误

**症状**: `invalid_argument` 错误

**常见原因**:
- `reason` 字段值不在允许的枚举值中
- `amount` 格式不正确
- `destination` 账户ID无效

**解决方案**:
- 确认 `reason` 使用了正确的枚举值
- 确认金额格式为字符串类型（如 "20.01"）
- 验证 payment_account_id 是否存在

### 问题 4: Token 过期

**症状**: `401 Unauthorized` 或 `403 Forbidden`

**解决方案**:
- Token 有过期时间，脚本会显示过期时间戳
- 重新执行脚本会自动获取最新 token

## 📊 API 响应字段说明

成功创建充值后，API 返回以下字段：

| 字段 | 说明 |
|------|------|
| `id` | 转账唯一标识符 |
| `amount` | 转账金额 |
| `currency` | 币种 |
| `destination` | 目标账户ID |
| `reason` | 转账原因 |
| `reference` | 参考编号 |
| `request_id` | 请求ID（时间戳） |
| `short_reference_id` | 短参考ID |
| `status` | 转账状态（NEW/PROCESSING/COMPLETED/FAILED） |
| `fee` | 手续费 |
| `created_at` | 创建时间 |
| `updated_at` | 更新时间 |

## 🔐 安全注意事项

1. **不要提交敏感信息到代码仓库**
   - Redis 密码
   - 数据库密码
   - API Token

2. **使用环境变量或配置文件**
   - 将敏感配置放在 `.env` 文件中
   - 在 `.gitignore` 中排除配置文件

3. **定期轮换密码和 Token**
   - Redis 密码应定期更换
   - Token 设置合理的过期时间

## 📞 联系方式

如有问题，请联系开发团队。

## 📄 更新日志

### v1.0 (2026-03-04)
- ✅ 初始版本发布
- ✅ 支持从 Redis 获取 Token
- ✅ 支持从数据库查询 payment_account_id
- ✅ 支持调用 Airwallex API 创建充值
- ✅ 完整的错误处理和日志输出
- ✅ 支持 200 和 201 状态码判断
