# Airwallex 充值流程自动化

## 📁 目录说明

本目录包含完整的 Airwallex 充值流程自动化工具及相关文档。

## 📦 文件清单

### 🎯 核心脚本

| 文件 | 说明 | 推荐度 |
|------|------|--------|
| `airwallex_recharge_cli.py` | 命令行增强版（支持参数） | ⭐⭐⭐⭐⭐ |
| `airwallex_recharge_flow.py` | 基础版（固定参数） | ⭐⭐⭐ |
| `redis_get_token.py` | Redis Token 获取工具 | ⭐⭐⭐⭐ |

### 📋 配置文件

| 文件 | 说明 |
|------|------|
| `airwallex_config_template.py` | 配置文件模板 |
| `airwallex_transfer_body_template.json` | API 请求体模板 |

### 📚 文档

| 文件 | 说明 |
|------|------|
| `Airwallex_Recharge_Flow_README.md` | 完整使用文档 |
| `Airwallex_Recharge_Summary.md` | 执行总结文档 |
| `AIRWALLEX_FILE_INDEX.md` | 文件索引文档 |
| `AIRWALLEX_QUICKREF.txt` | 快速参考卡片 |
| `README.md` | 本文件 |

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install redis psycopg2-binary requests
```

### 2. 查看帮助

```bash
# 从项目根目录执行
python test_cases/airwallex_recharge/airwallex_recharge_cli.py --help

# 或进入本目录执行
cd test_cases/airwallex_recharge
python airwallex_recharge_cli.py --help
```

### 3. 试运行（不实际充值）

```bash
# 从项目根目录执行
python test_cases/airwallex_recharge/airwallex_recharge_cli.py --amount 30.00 --dry-run

# 或进入本目录执行
cd test_cases/airwallex_recharge
python airwallex_recharge_cli.py --amount 30.00 --dry-run
```

### 4. 执行充值

```bash
# 使用默认参数（20.01 USD, travel）
python test_cases/airwallex_recharge/airwallex_recharge_cli.py

# 自定义金额和原因
python test_cases/airwallex_recharge/airwallex_recharge_cli.py \
    --amount 50.00 \
    --reason living_expenses
```

## 📊 执行流程

```
┌─────────────────────────────────────────┐
│  步骤 1: 从 Redis 获取 Token            │
│  - 连接 Redis 服务器                    │
│  - 提取 JWT Token                       │
│  - 检查过期时间                         │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  步骤 2: 从数据库获取 payment_account_id│
│  - 连接 PostgreSQL                      │
│  - 查询用户绑定账户                     │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  步骤 3: 调用 Airwallex API 创建充值    │
│  - 生成唯一 request_id                  │
│  - POST 请求到 API                      │
│  - 返回充值结果                         │
└─────────────────────────────────────────┘
```

## 🔑 常用参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--user-id` | 用户ID | 796133836057336352 |
| `--amount` | 充值金额 | 20.01 |
| `--currency` | 币种 | USD |
| `--reason` | 充值原因 | travel |
| `--dry-run` | 试运行模式 | false |

## 📌 有效的 reason 枚举值

- `travel` - 旅行（默认）
- `living_expenses` - 生活费用
- `education_training` - 教育培训
- `family_support` - 家庭支持
- `personal_remittance` - 个人汇款
- 更多值请查看帮助信息

## ✅ 验证测试结果

### 测试 1：帮助信息显示
```bash
✓ 命令行参数解析正常
✓ 帮助信息显示完整
```

### 测试 2：试运行模式
```bash
✓ Redis 连接成功
✓ 数据库查询成功
✓ 参数验证通过
✓ 未实际调用 API（符合预期）
```

### 测试 3：实际充值执行
```bash
✓ 成功创建充值（18.88 USD, family_support）
✓ 转账ID: tr_8NUwBYq7PMiJP6XBL9z9xQ
✓ 状态: NEW
✓ 短参考ID: D260304-UBF712I
```

### 测试 4：Token 获取工具
```bash
✓ Redis 连接成功
✓ Token 提取成功
✓ 过期时间显示正常
```

## 📚 详细文档

- **快速查询**: `AIRWALLEX_QUICKREF.txt` - 常用命令速查
- **完整文档**: `Airwallex_Recharge_Flow_README.md` - 详细使用说明
- **技术总结**: `Airwallex_Recharge_Summary.md` - 技术细节和最佳实践
- **文件索引**: `AIRWALLEX_FILE_INDEX.md` - 所有文件导航

## 🔧 配置信息

### Redis
```
Host: redis-shark-test.rdb.58dns.org:50554
Key: \xac\xed\x00\x05t\x00\x0fairwallex:token
```

### PostgreSQL
```
Host: pgsql-test.pdb.58dns.org:29000
Database: pdb58_easypost
Table: user_payment_binding
```

### Airwallex API
```
URL: https://api-demo.airwallex.com/api/v1/connected_account_transfers/create
Method: POST
```

## 🐛 常见问题

**Q: 如何验证配置是否正确？**  
A: 使用 `--dry-run` 参数进行试运行

**Q: Token 过期怎么办？**  
A: 脚本会自动从 Redis 获取最新 token

**Q: 如何查看所有支持的充值原因？**  
A: 运行 `python airwallex_recharge_cli.py --help`

**Q: 充值失败如何排查？**  
A: 查看脚本输出的详细错误信息，或参考 `Airwallex_Recharge_Flow_README.md` 的故障排查部分

## 📞 支持

如有问题，请查看：
1. `AIRWALLEX_QUICKREF.txt` - 快速参考
2. `Airwallex_Recharge_Flow_README.md` - 故障排查指南
3. `Airwallex_Recharge_Summary.md` - 技术细节

## 📅 版本信息

- **版本**: v1.0
- **创建日期**: 2026-03-04
- **状态**: ✅ 已测试并验证
- **最后更新**: 2026-03-04

---

**所有脚本已完成开发、测试并验证，可直接投入使用！** 🎉
