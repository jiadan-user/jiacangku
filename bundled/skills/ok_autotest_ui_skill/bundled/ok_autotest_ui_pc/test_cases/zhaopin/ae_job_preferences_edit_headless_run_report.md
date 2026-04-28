# test_ae_job_preferences_edit.py 无头模式执行报告

- **执行时间**: 2026-04-17（本地）
- **工作目录**: `bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc`
- **无头开关**: `HEADLESS=true`（由 `test_cases/conftest.py` 中 `config` fixture 覆盖 `_CONFIG["browser"]["headless"]`）

## 总耗时

| 指标 | 数值 |
| --- | --- |
| **墙钟时间 (real)** | **183.29 s**（约 **3 分 3 秒**） |
| pytest 统计 (tests duration) | **182.67 s**（约 **3 分 2 秒**） |
| user / sys (time -p) | 25.36 s / 4.30 s |

## 汇总（JUnit）

- **总计**: 15
- **通过**: 15
- **失败**: 0
- **跳过**: 0
- **错误**: 0

## 失败用例

无。

## 跳过用例

无。

（脚本头部说明曾含「半自动化 skip」；本次 pytest 收集并执行 **15** 条，与 JUnit `tests="15"`、`skipped="0"` 一致。）

## 每条用例耗时（秒，来自 JUnit）

| nodeid 后缀 | 耗时 (s) |
| --- | ---: |
| test_ae_edit_enter_from_jobs_list_should_show_prefilled_data | 16.371 |
| test_ae_edit_prefill_job_functions_tags_and_count | 10.876 |
| test_ae_edit_prefill_location_tags_and_count | 10.909 |
| test_ae_edit_prefill_salary_pay_type_and_amount | 10.895 |
| test_ae_edit_prefill_workplace_type_and_job_type_checkboxes | 10.897 |
| test_ae_edit_continue_submits_and_returns_to_return_url | 13.002 |
| test_ae_edit_job_functions_has_oil_gas_and_skilled_trades | 13.125 |
| test_ae_edit_location_shows_only_uae_cities | 12.117 |
| test_ae_edit_salary_currency_prefix_is_aed | 11.039 |
| test_ae_edit_back_without_changes_goes_directly_to_return_url | 15.338 |
| test_ae_edit_back_with_unsaved_changes_shows_dialog_and_discards | 16.115 |
| test_ae_edit_open_redirect_tampered_return_url_blocked | 14.718 |
| test_ae_edit_refresh_page_refills_data_from_server | 13.110 |
| test_ae_edit_expired_session_redirects_to_login | 13.756 |
| test_ae_edit_horizontal_privilege_escalation_blocked | 0.266 |

## 产物路径

- **JUnit XML**: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/ae_job_preferences_edit_headless_junit.xml`
- **控制台完整日志**: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/ae_job_preferences_edit_headless_console.log`

## 复现命令

```bash
cd /Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc
HEADLESS=true /usr/bin/time -p pytest test_cases/zhaopin/test_ae_job_preferences_edit.py -v --tb=short \
  --junit-xml=test_cases/zhaopin/ae_job_preferences_edit_headless_junit.xml -o junit_family=xunit2 \
  2>&1 | tee test_cases/zhaopin/ae_job_preferences_edit_headless_console.log
```
