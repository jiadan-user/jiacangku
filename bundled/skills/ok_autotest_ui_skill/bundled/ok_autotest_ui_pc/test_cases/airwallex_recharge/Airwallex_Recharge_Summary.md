# Airwallex 充值流程 - 执行总结

## ✅ 任务完成情况

已成功创建完整的 Airwallex 充值流程自动化工具，包含：

### 📦 交付物清单

| 文件名 | 说明 | 状态 |
|--------|------|------|
| `airwallex_recharge_flow.py` | 基础版充值流程脚本 | ✅ 已完成并测试 |
| `airwallex_recharge_cli.py` | 命令行增强版（支持参数） | ✅ 已完成并测试 |
| `redis_get_token.py` | 独立的 Redis Token 获取工具 | ✅ 已完成 |
| `airwallex_transfer_body.json` | API 请求体示例文件 | ✅ 已完成 |
| `airwallex_config_template.py` | 配置文件模板 | ✅ 已完成 |
| `docs/Airwallex_Recharge_Flow_README.md` | 完整使用文档 | ✅ 已完成 |

---

## 🎯 核心功能

### 1️⃣ 自动化流程

脚本按顺序自动执行以下步骤：

```
┌─────────────────────────────────────────────────────────────┐
│  步骤 1: 从 Redis 获取 Airwallex Token                      │
│  - 连接: redis-shark-test.rdb.58dns.org:50554              │
│  - 获取 key: \xac\xed\x00\x05t\x00\x0fairwallex:token      │
│  - 解析 JWT token                                            │
│  - 检查过期时间                                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  步骤 2: 从 PostgreSQL 数据库获取 payment_account_id        │
│  - 连接: pgsql-test.pdb.58dns.org:29000                    │
│  - 数据库: pdb58_easypost                                    │
│  - SQL: SELECT payment_account_id FROM user_payment_binding │
│         WHERE app_user_id='796133836057336352'              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  步骤 3: 调用 Airwallex API 创建充值                        │
│  - URL: /api/v1/connected_account_transfers/create         │
│  - Method: POST                                              │
│  - 生成唯一 request_id（时间戳）                            │
│  - 返回转账记录                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2️⃣ 两种使用方式

#### 方式 A: 基础版（固定参数）

```bash
# 直接运行，使用脚本内置的默认参数
python airwallex_recharge_flow.py
```

**默认配置：**
- 用户ID: `796133836057336352`
- 金额: `20.01 USD`
- 原因: `travel`

#### 方式 B: 命令行版（灵活参数）

```bash
# 使用默认参数
python airwallex_recharge_cli.py

# 指定金额和原因
python airwallex_recharge_cli.py --amount 50.00 --reason living_expenses

# 完整参数
python airwallex_recharge_cli.py \
    --user-id 796133836057336352 \
    --amount 100.00 \
    --currency USD \
    --reason living_expenses

# 试运行模式（不实际创建充值，只验证流程）
python airwallex_recharge_cli.py --amount 100.00 --dry-run
```

---

## 📊 实际执行结果

### 成功执行示例

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
  过期时间戳: 1772617773000

步骤 2: 从数据库获取 payment_account_id
✓ 数据库连接成功
✓ payment_account_id: acct__z8GKFiwOYezx60YxHiyMg

步骤 3: 调用 Airwallex API 创建充值
✓ 充值创建成功!

响应数据:
{
  "amount": 20.01,
  "created_at": "2026-03-04T09:24:45+0000",
  "currency": "USD",
  "destination": "acct__z8GKFiwOYezx60YxHiyMg",
  "fee": 0,
  "id": "tr_WfaAp-yLOOu0AexSZMyQ2Q",
  "reason": "travel",
  "reference": "PMT20260304172445",
  "request_id": "1772616285167",
  "short_reference_id": "D260304-DG07ZKQ",
  "status": "NEW",
  "updated_at": "2026-03-04T09:24:45+0000"
}

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

---

## 🔧 技术细节

### 依赖包

```python
redis          # Redis 客户端
psycopg2       # PostgreSQL 客户端
requests       # HTTP 客户端
```

### 连接配置

**Redis:**
```python
host: redis-shark-test.rdb.58dns.org
port: 50554
password: 6b0d1d0d640eb6fa
```

**PostgreSQL:**
```python
host: pgsql-test.pdb.58dns.org
port: 29000
database: pdb58_easypost
user: epost_test
password: GUGXzw49K6Ndp7
```

**Airwallex API:**
```
URL: https://api-demo.airwallex.com/api/v1/connected_account_transfers/create
Method: POST
Authorization: Bearer {token}
```

### API 请求格式

```json
{
  "amount": "20.01",
  "currency": "USD",
  "destination": "acct__z8GKFiwOYezx60YxHiyMg",
  "reason": "travel",
  "reference": "PMT20260304172445",
  "request_id": "1772616285167"
}
```

### 有效的 reason 枚举值（24个）

| 分类 | 枚举值 |
|------|--------|
| 收入类 | `wages_salary`, `pension`, `investment_proceeds` |
| 支付类 | `living_expenses`, `education_training`, `travel`, `medical_services` |
| 家庭类 | `family_support`, `personal_remittance` |
| 商业类 | `business_expenses`, `professional_business_services`, `technical_services`, `goods_purchased` |
| 金融类 | `loan_credit_repayment`, `investment_capital`, `taxes` |
| 其他 | `donation_charitable_contribution`, `transfer_to_own_account`, `other_services`, `construction`, `freight`, `real_estate`, `settlement`, `commission` |

---

## 🐛 问题排查记录

### 问题 1: Reason 参数错误 ❌

**错误信息:**
```json
{
  "code": "invalid_argument",
  "message": "Reason must be one of [wages_salary, ...]",
  "source": "reason"
}
```

**原因:** 使用了 `lwf-test` 作为 reason 值，但这不在 Airwallex 的枚举列表中。

**解决:** 修改为有效值 `travel`

### 问题 2: HTTP 状态码判断不完整 ❌

**现象:** API 返回 201（创建成功），但脚本判断为失败。

**原因:** 脚本只判断了 `status_code == 200`

**解决:** 修改为 `status_code in [200, 201]`

### 问题 3: Windows PowerShell 中 curl 别名冲突 ❌

**现象:** `curl` 命令被 PowerShell 解析为 `Invoke-WebRequest`

**解决:** 使用 `curl.exe` 直接调用真正的 curl

---

## 📈 改进点和特色功能

### ✨ 功能特色

1. **完整的错误处理**
   - Redis 连接失败处理
   - 数据库查询失败处理
   - API 调用失败处理
   - Token 过期提示

2. **友好的输出格式**
   - 清晰的步骤分隔
   - 彩色标记（✓/✗）
   - JSON 格式化输出
   - 进度提示

3. **灵活的参数配置**
   - 支持命令行参数
   - 支持试运行模式（--dry-run）
   - 参数验证（reason 枚举值）
   - 默认值设置

4. **安全性考虑**
   - 配置文件模板（敏感信息分离）
   - Token 过期时间检查
   - 使用环境变量建议（文档中）

5. **可维护性**
   - 代码模块化
   - 详细注释
   - 完整文档
   - 使用示例

---

## 📝 使用建议

### 开发/测试环境

1. **快速测试:** 使用 `--dry-run` 验证配置
   ```bash
   python airwallex_recharge_cli.py --dry-run
   ```

2. **小额测试:** 先用小金额测试
   ```bash
   python airwallex_recharge_cli.py --amount 0.01
   ```

3. **查看帮助:** 了解所有参数
   ```bash
   python airwallex_recharge_cli.py --help
   ```

### 生产环境

1. **敏感信息保护:**
   - 将配置放在环境变量或独立配置文件
   - 不要将密码提交到 Git

2. **日志记录:**
   - 可扩展脚本添加日志文件输出
   - 记录所有充值操作

3. **监控告警:**
   - 监控 API 调用失败率
   - Token 即将过期时提醒
   - 数据库连接异常告警

---

## 🎓 学习价值

本脚本演示了以下最佳实践：

1. ✅ Python 脚本化自动化流程
2. ✅ Redis 客户端使用（处理二进制 key）
3. ✅ PostgreSQL 数据库查询
4. ✅ RESTful API 调用
5. ✅ 命令行参数解析（argparse）
6. ✅ 错误处理和异常捕获
7. ✅ JSON 数据处理
8. ✅ 时间戳生成和处理
9. ✅ Windows 控制台编码问题处理
10. ✅ 试运行模式（dry-run）实现

---

## 📞 后续支持

如需以下扩展，请提出需求：

- [ ] 支持批量充值（从 CSV/Excel 读取）
- [ ] 支持多币种转换
- [ ] 添加充值历史查询功能
- [ ] 集成到自动化测试框架
- [ ] Web 界面版本
- [ ] 定时任务支持

---

**创建时间:** 2026-03-04  
**最后更新:** 2026-03-04  
**脚本版本:** v1.0
