---
name: ok-ui-autotest
description: 当需要根据站点、模块、功能或脚本路径选择并执行 OK PC UI 自动化、先 dry-run 再真实回归、生成 Allure 报告和上线建议时使用；新增、修改或 promotion 测试脚本后，也用它刷新 catalog 并审计标识。
---

# OK UI 自动化 Skill

这个 skill 的职责很简单：

- 开发告诉 AI 改了哪个模块和功能
- AI 先参考 `module-map`，再核对文本用例和自动化脚本
- 如果本轮新增、修改或 promotion 了脚本，AI 先刷新 catalog 并审计标识
- AI 先 `--dry-run` 预览，再真实执行
- 如果目标 case 有已配置前置，CLI 会先自动补跑前置再回到目标执行
- AI 直接返回 Allure、执行结果和上线建议
- `coverage-dashboard.md` 是随 skill 发布的静态汇报快照，不在日常执行中改写

## 首次环境准备

以下命令默认从本 skill 根目录执行，也就是包含 `SKILL.md` 和 `scripts/ok_test.py` 的目录。

```bash
python3 -m venv bundled/ok_autotest_ui_pc/venv
source bundled/ok_autotest_ui_pc/venv/bin/activate
python -m pip install --upgrade pip
pip install -r bundled/ok_autotest_ui_pc/requirements.txt
playwright install chromium
```

如果本机还没有 Allure CLI，`run` 会优先尝试自动安装；手动安装命令保留如下：

```bash
brew install allure
```

## 主流程

1. 第一次使用或环境异常时，运行 `doctor`
2. 如果本轮新增、修改或 promotion 了 `test_cases/**/*.py`，先运行 `ops catalog-build`，再运行 `ops audit-identifiers`
3. AI 先看 `references/module-map.md`，再核对文本用例和自动化脚本，确定 `run --dry-run` 参数
4. AI 确认范围后运行 `run`

`run/list` 都依赖 `catalog/catalog.generated.json` 做选择。catalog 已存在时不会自动重建；新增脚本如果不先刷新 catalog，`--module`、`--feature`、`--path`、`--nodeid` 都可能选不到它。

## 公开命令

### `doctor`

只检查环境，不安装依赖。


| 参数  | 是否必填 | 作用                                                   | 示例                                 |
| --- | ---- | ---------------------------------------------------- | ---------------------------------- |
| 无   | 是    | 检查 Python、venv、pytest collect、Playwright 和 marker 状态 | `python3 scripts/ok_test.py doctor` |


### `run`

`python3 scripts/ok_test.py run` 是主执行入口。

- 带 `--dry-run`：只预览会跑哪些用例
- 不带 `--dry-run`：真实执行，并自动生成：
  - `reports/allure-results/`
  - `reports/allure-report/`
  - `reports/junit.xml`
  - 覆盖率和上线建议
  - `allure_url`
- 如果目标 case 有已配置前置，CLI 会先自动补跑前置，再重新执行目标集合


| 参数           | 是否必填 | 作用                                    | 示例                                                                          |
| ------------ | ---- | ------------------------------------- | --------------------------------------------------------------------------- |
| `--module`   | 否    | 按模块筛选，例如 `wallet`、`publish_job`、`car` | `--module wallet`                                                           |
| `--feature`  | 否    | 按功能筛选，优先用于已定义 feature 的模块             | `--feature publish_job_step1_validation`                                    |
| `--story`    | 否    | 按 `allure.story` 筛选                   | `--story 钱包-提现`                                                             |
| `--priority` | 否    | 按优先级筛选，支持 `p0/p1/p2/p3`               | `--priority p0`                                                             |
| `--site`     | 否    | 按站点筛选，例如 `ae/us/sg/au`                | `--site ae`                                                                 |
| `--case-id`  | 否    | 按单条 `case_id` 精确筛选                    | `--case-id case_id_wallet_withdraw_tc056`                                   |
| `--path`     | 否    | 按测试文件或目录子串筛选，适合功能映射不细的模块              | `--path test_cases/wallet/test_wallet_withdrawal.py`                        |
| `--nodeid`   | 否    | 按单条 pytest nodeid 筛选                  | `--nodeid test_cases/test_car/test_ae_car_publish.py::test_publish_success` |
| `--dry-run`  | 否    | 只预览，不真实执行                             | `--dry-run`                                                                 |
| `--workers`  | 否    | 真实执行并发 worker，支持 `1`、正整数或 `auto`；默认 `1`，有前置映射时强制串行 | `--workers auto`                                                            |
| `--max-workers` | 否 | `auto` 或显式并发的安全上限，默认 `4` | `--max-workers 4` |
| `--artifact-retention` | 否 | 产物保留策略，`lean` 仅在真实执行通过后清理重复中间件，失败/阻塞不清理 | `--artifact-retention lean` |

### `ops catalog-build`

新增、修改或 promotion 脚本后必须先刷新 catalog：

```bash
python3 scripts/ok_test.py ops catalog-build
```

### `ops audit-identifiers`

刷新 catalog 后审计脚本标识；失败时先补齐优先级、`case_id`、模块/功能标识，再继续 dry-run：

```bash
python3 scripts/ok_test.py ops audit-identifiers
```

新增脚本接入细节见 `references/new-script-onboarding.md`，不要把完整接入规范重复塞进本文件。

## 报告路径

真实执行后重点看这几个路径：

- `bundled/ok_autotest_ui_pc/reports/allure-results/`
- `bundled/ok_autotest_ui_pc/reports/allure-report/`
- `bundled/ok_autotest_ui_pc/reports/junit.xml`
- `bundled/ok_autotest_ui_pc/reports/screenshots/`
- `bundled/ok_autotest_ui_pc/reports/ok_test_runs/<run_id>/`
- `references/coverage-dashboard.md`
- `references/dashboard-modules/`

## 何时读取 References

- 需要功能名到 `run` 参数的映射时，读 `references/module-map.md`
- 需要看 3 个 AI 执行示例时，读 `references/usage.md`
- 需要看自动化覆盖汇报时，读静态的 `references/coverage-dashboard.md`
- 新增、修改或 promotion 脚本后，读 `references/new-script-onboarding.md`
- 需要维护 catalog 或标识治理时，读 `references/governance.md` 和 `references/identifier-rules.md`
