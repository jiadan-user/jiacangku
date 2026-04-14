# Airwallex 充值流程 - 文件索引

## 📂 项目结构

```
ok_autotest_ui_pc/
│
└── test_cases/
    └── airwallex_recharge/                          # Airwallex 充值流程目录
        ├── airwallex_recharge_cli.py                # 命令行增强版（推荐）⭐
        ├── airwallex_recharge_flow.py               # 基础版充值脚本
        ├── redis_get_token.py                       # Redis Token 获取工具
        ├── airwallex_config_template.py             # 配置文件模板
        ├── airwallex_transfer_body_template.json    # API 请求体模板
        ├── AIRWALLEX_QUICKREF.txt                   # 快速参考卡片
        ├── Airwallex_Recharge_Flow_README.md        # 完整使用文档
        ├── Airwallex_Recharge_Summary.md            # 执行总结文档
        ├── AIRWALLEX_FILE_INDEX.md                  # 本文件
        └── README.md                                # 目录说明文档
```

## 📄 文件详细说明

### 1. 核心脚本

#### `airwallex_recharge_flow.py`
- **类型**: Python 脚本
- **用途**: 基础版充值流程，使用固定参数
- **特点**: 简单直接，适合快速执行
- **使用**: `python airwallex_recharge_flow.py`
- **配置**: 需在脚本内修改参数

#### `airwallex_recharge_cli.py` ⭐ **推荐使用**
- **类型**: Python 脚本（命令行版）
- **用途**: 支持命令行参数的充值流程
- **特点**: 
  - 灵活的参数配置
  - 支持试运行模式（--dry-run）
  - 完整的参数验证
  - 详细的帮助信息
- **使用**: 
  ```bash
  # 查看帮助
  python airwallex_recharge_cli.py --help
  
  # 默认参数执行
  python airwallex_recharge_cli.py
  
  # 自定义参数
  python airwallex_recharge_cli.py --amount 50.00 --reason travel
  
  # 试运行
  python airwallex_recharge_cli.py --amount 100.00 --dry-run
  ```

#### `redis_get_token.py`
- **类型**: Python 工具脚本
- **用途**: 独立的 Redis Token 获取工具
- **特点**: 可单独使用，便于调试
- **使用**: `python redis_get_token.py`
- **输出**: 
  - JWT Token（完整格式）
  - Token 过期时间戳
  - Hex 格式数据

### 2. 配置文件

#### `airwallex_config_template.py`
- **类型**: Python 配置文件模板
- **用途**: 提供所有可配置项的模板
- **内容**:
  - Redis 连接配置
  - PostgreSQL 数据库配置
  - Airwallex API 配置
  - 充值默认参数配置
  - 完整的 reason 枚举值说明
- **使用**: 复制为 `airwallex_config.py` 并修改

#### `airwallex_transfer_body.json`
- **类型**: JSON 数据文件
- **用途**: API 请求体示例
- **内容**: 标准的充值请求 JSON 格式
- **使用**: 配合 curl 命令行工具
- **示例**:
  ```bash
  curl.exe -s -w "\n" \
    --request POST \
    --url "https://api-demo.airwallex.com/api/v1/connected_account_transfers/create" \
    --header "Content-Type: application/json" \
    --header "Authorization: Bearer YOUR_TOKEN" \
    --data "@airwallex_transfer_body.json"
  ```

### 3. 文档

#### `docs/Airwallex_Recharge_Flow_README.md`
- **类型**: Markdown 文档
- **用途**: 完整的使用文档和参考手册
- **内容**:
  - 概述和快速开始
  - 环境要求和依赖安装
  - 详细的配置说明
  - Reason 枚举值完整列表
  - 自定义参数方法
  - 独立工具使用
  - 故障排查指南
  - API 响应字段说明
  - 安全注意事项
  - 更新日志
- **适用**: 新用户、参考查询

#### `docs/Airwallex_Recharge_Summary.md`
- **类型**: Markdown 文档
- **用途**: 项目执行总结和技术文档
- **内容**:
  - 任务完成情况清单
  - 自动化流程图
  - 实际执行结果示例
  - 技术细节（依赖、配置、API）
  - 问题排查记录
  - 改进点和特色功能
  - 使用建议
  - 学习价值总结
- **适用**: 技术回顾、交接文档

#### `AIRWALLEX_QUICKREF.txt`
- **类型**: 纯文本快速参考卡片
- **用途**: 快速查询常用命令和配置
- **内容**:
  - 文件清单
  - 快速开始命令
  - 常用参数说明
  - Reason 枚举值速查
  - 配置信息摘要
  - 执行流程图
  - 成功示例
  - 常见问题 FAQ
- **适用**: 日常使用、快速查询

#### `docs/AIRWALLEX_FILE_INDEX.md`（本文件）
- **类型**: Markdown 索引文档
- **用途**: 项目文件导航和说明
- **内容**: 所有文件的详细说明和使用指南
- **适用**: 项目总览、文件查找

## 🚀 使用路径推荐

### 第一次使用
1. 进入目录:
   ```bash
   cd test_cases/airwallex_recharge
   ```
2. 阅读 `README.md`（快速入门）
3. 查看 `AIRWALLEX_QUICKREF.txt`（快速参考）
4. 运行试运行模式验证配置：
   ```bash
   python airwallex_recharge_cli.py --dry-run
   ```
5. 执行实际充值：
   ```bash
   python airwallex_recharge_cli.py --amount 20.01
   ```

### 日常使用
1. 从项目根目录执行：
   ```bash
   python test_cases/airwallex_recharge/airwallex_recharge_cli.py [参数]
   ```
2. 或进入目录后执行：
   ```bash
   cd test_cases/airwallex_recharge
   python airwallex_recharge_cli.py [参数]
   ```
3. 遇到问题查看 `Airwallex_Recharge_Flow_README.md` 的故障排查部分

### 开发/维护
1. 参考 `Airwallex_Recharge_Summary.md` 了解技术细节
2. 使用 `airwallex_config_template.py` 管理配置
3. 使用 `redis_get_token.py` 调试 Token 问题

## 📊 文件关系图

```
┌─────────────────────────────────────────────────────────────┐
│                      用户操作入口                           │
└─────────────────────────────────────────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ↓                ↓                ↓
    ┌─────────────┐  ┌──────────────────┐  ┌──────────────┐
    │  基础版脚本 │  │  命令行增强版 ⭐ │  │ Token工具   │
    │    .py      │  │     _cli.py      │  │   .py       │
    └─────────────┘  └──────────────────┘  └──────────────┘
              │                │                │
              └────────────────┼────────────────┘
                               ↓
              ┌────────────────────────────────┐
              │    配置来源（三选一）          │
              ├────────────────────────────────┤
              │ 1. 脚本内置                    │
              │ 2. 命令行参数（推荐）          │
              │ 3. 配置文件（模板可用）        │
              └────────────────────────────────┘
                               ↓
              ┌────────────────────────────────┐
              │         执行流程               │
              ├────────────────────────────────┤
              │ Redis → PostgreSQL → API       │
              └────────────────────────────────┘
                               ↓
              ┌────────────────────────────────┐
              │        文档支持                │
              ├────────────────────────────────┤
              │ - 完整文档（README）           │
              │ - 快速参考（QUICKREF）         │
              │ - 技术总结（Summary）          │
              │ - 文件索引（本文件）           │
              └────────────────────────────────┘
```

## 🔧 依赖关系

```
Python 3.7+
├── redis           (Redis 客户端)
├── psycopg2-binary (PostgreSQL 客户端)
└── requests        (HTTP 客户端)

安装命令:
pip install redis psycopg2-binary requests
```

## 📝 版本信息

| 项目 | 版本 | 状态 |
|------|------|------|
| 脚本版本 | v1.0 | ✅ 稳定 |
| 文档版本 | v1.0 | ✅ 完整 |
| 测试状态 | 已测试 | ✅ 通过 |
| 最后更新 | 2026-03-04 | - |

## 🎯 快速链接

- **立即开始**: 运行 `python test_cases/airwallex_recharge/airwallex_recharge_cli.py --help`
- **快速入门**: 查看 `test_cases/airwallex_recharge/README.md`
- **快速参考**: 查看 `test_cases/airwallex_recharge/AIRWALLEX_QUICKREF.txt`
- **完整文档**: 打开 `test_cases/airwallex_recharge/Airwallex_Recharge_Flow_README.md`
- **技术细节**: 阅读 `test_cases/airwallex_recharge/Airwallex_Recharge_Summary.md`

## 💡 提示

- ⭐ 推荐使用 `airwallex_recharge_cli.py`（命令行增强版）
- 🔍 使用 `--dry-run` 参数进行安全测试
- 📚 所有文档均为 Markdown 格式，支持 IDE 预览
- 🔐 配置文件包含敏感信息，请勿提交到代码仓库

---

**创建时间**: 2026-03-04  
**维护状态**: 活跃  
**联系方式**: 参考项目文档
