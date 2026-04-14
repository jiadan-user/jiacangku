---

## name: ok-ui-autotest
description: 当开发告诉 AI 改了哪个模块、哪个功能、哪个站点，且需要 AI 结合映射文档、文本用例和自动化脚本来挑选并执行 OK UI 自动化、自动生成 Allure 报告并输出上线建议时，使用这个 skill。

# OK UI 自动化 Skill

这个 skill 的职责很简单：

- 开发告诉 AI 改了哪个模块和功能
- AI 先参考 `module-map`，再核对文本用例和自动化脚本
- AI 先 `--dry-run` 预览，再真实执行
- 如果目标 case 有已配置前置，CLI 会先自动补跑前置再回到目标执行
- AI 直接返回 Allure、执行结果和上线建议
- `coverage-dashboard.md` 是随 skill 发布的静态汇报快照，不在日常执行中改写

## 首次环境准备

```bash
cd /Users/a58/Desktop/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
```

如果本机还没有 Allure CLI，`run` 会优先尝试自动安装；手动安装命令保留如下：

```bash
brew install allure
```

## 主流程

1. 第一次使用或环境异常时，运行 `doctor`
2. AI 先看 `references/module-map.md`，再核对文本用例和自动化脚本，确定 `run --dry-run` 参数
3. AI 确认范围后运行 `run`

## 公开命令

### `doctor`

只检查环境，不安装依赖。


| 参数  | 是否必填 | 作用                                                   | 示例                                 |
| --- | ---- | ---------------------------------------------------- | ---------------------------------- |
| 无   | 是    | 检查 Python、venv、pytest collect、Playwright 和 marker 状态 | `python scripts/ok_test.py doctor` |


### `run`

`python scripts/ok_test.py run` 是主执行入口。

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
- 需要维护 catalog 或标识治理时，读 `references/governance.md` 和 `references/identifier-rules.md`

