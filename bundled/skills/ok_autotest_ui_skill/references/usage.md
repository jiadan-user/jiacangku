# AI 执行示例

以下示例默认在最终 skill 根目录执行：

```bash
cd /Users/a58/Desktop/ok_autotest_ui_skill
```

## 示例 1：开发说“我改了 wallet 提现”

AI 先预览：

```bash
python scripts/ok_test.py run --module wallet --path test_cases/wallet/test_wallet_withdrawal.py --dry-run
```

确认后真实执行：

```bash
python scripts/ok_test.py run --module wallet --path test_cases/wallet/test_wallet_withdrawal.py
```

如果命中的目标 case 有已配置前置，`run` 会先自动补跑前置，再回到目标集合执行。

## 示例 2：开发说“我改了职位发布 step1”

AI 先预览：

```bash
python scripts/ok_test.py run --module publish_job --feature publish_job_step1_validation --dry-run
```

确认后真实执行：

```bash
python scripts/ok_test.py run --module publish_job --feature publish_job_step1_validation
```

## 示例 3：开发说“我改了 car publish”

AI 先预览：

```bash
python scripts/ok_test.py run --module car --feature car_publish --site ae --dry-run
```

确认后真实执行：

```bash
python scripts/ok_test.py run --module car --feature car_publish --site ae
```

## AI 如何选用例

AI 选用例时固定做两步：

1. 先参考 `references/module-map.md`
2. 再核对 `/Users/a58/Desktop/knowledge_base/文本用例` 和 `bundled/ok_autotest_ui_pc/test_cases/...`

映射文档只是第一层导航，不是最终真相。

## 结果怎么看

真实执行后，AI 优先读取：

1. 终端输出中的 `run_id`
2. 终端输出中的 `run_status`、风险建议和通过率
3. 终端输出中的 `allure_url`
4. `bundled/ok_autotest_ui_pc/reports/allure-report/`
5. `bundled/ok_autotest_ui_pc/reports/screenshots/`

## 覆盖汇报怎么看

汇报优先看 skill 自带的静态参考资料：

1. `references/coverage-dashboard.md`
2. `references/dashboard-modules/car.md`
3. `references/dashboard-modules/wallet.md`
4. `references/dashboard-modules/zhaopin.md`

这些文件不在日常执行中自动刷新；如果 dashboard 内容更新，按新版本 skill 发布。

## 维护模式

以下命令不属于普通开发主流程，只在维护 catalog 或标识治理时使用：

```bash
python -m tooling.ok_test ops catalog-build
python -m tooling.ok_test ops audit-identifiers
```
