# `test_ae_resume_edit.py` 无头跑测报告

- 生成时间: 2026-04-27 12:50:44 +0800
- JUnit 输入: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_122819/junit/test_ae_resume_edit_junit.xml`
- 控制台日志: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_122819/per_script_logs/test_ae_resume_edit.log`

## 总耗时

- **pytest 汇总**: 4 failed, 26 passed
- **JUnit testsuite time 之和（近似）**: **283.65 s**（若未并行，接近各用例 CPU 累计；与墙钟可能不同）
- 用例总数（JUnit 条目）: 30

## 各测试脚本耗时（按 JUnit 单条 time 汇总到文件）

| 脚本 | 耗时 (s) |
| --- | ---: |
| `test_cases/zhaopin/test_ae_resume_edit.py` | 281.898 |

## 统计摘要（按文件）

| 脚本 | passed | failed | skipped | error |
| --- | ---: | ---: | ---: | ---: |
| `test_cases/zhaopin/test_ae_resume_edit.py` | 26 | 4 | 0 | 0 |

## 失败用例

- `test_cases/zhaopin/test_ae_resume_edit.py` :: `test_tc023_save_education_and_echo`
  - playwright._impl._errors.TimeoutError: Page.wait_for_selector: Timeout 8000ms exceeded.
Call log:
  - waiting for locator(".modal-content") to be visible
- `test_cases/zhaopin/test_ae_resume_edit.py` :: `test_tc028_personal_info_data_echo_after_reload`
  - playwright._impl._errors.TimeoutError: Page.wait_for_selector: Timeout 8000ms exceeded.
Call log:
  - waiting for locator(".modal-content") to be visible
- `test_cases/zhaopin/test_ae_resume_edit.py` :: `test_tc029_education_data_echo_after_reload`
  - playwright._impl._errors.TimeoutError: Page.wait_for_selector: Timeout 8000ms exceeded.
Call log:
  - waiting for locator(".modal-content") to be visible
- `test_cases/zhaopin/test_ae_resume_edit.py` :: `test_tc030_personal_summary_data_echo_after_reload`
  - AssertionError: 刷新后视图页 Personal Summary 区块应显示最新摘要内容
assert False

## 错误（setup/teardown 等）

（无）

## 跳过用例

（无）

## 子进程与线程元数据

- 子进程 **returncode**: 1
- 本脚本墙钟: **284.35** s（线程内 pytest 子进程起止）
