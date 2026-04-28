# `test_sg_job_preferences_add_from_list.py` 无头跑测报告

- 生成时间: 2026-04-27 14:32:05 +0800
- JUnit 输入: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_140941/junit/test_sg_job_preferences_add_from_list_junit.xml`
- 控制台日志: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_140941/per_script_logs/test_sg_job_preferences_add_from_list.log`

## 总耗时

- **pytest 汇总**: 1 failed, 7 passed
- **JUnit testsuite time 之和（近似）**: **334.43 s**（若未并行，接近各用例 CPU 累计；与墙钟可能不同）
- 用例总数（JUnit 条目）: 8

## 各测试脚本耗时（按 JUnit 单条 time 汇总到文件）

| 脚本 | 耗时 (s) |
| --- | ---: |
| `test_cases/zhaopin/test_sg_job_preferences_add_from_list.py` | 333.508 |

## 统计摘要（按文件）

| 脚本 | passed | failed | skipped | error |
| --- | ---: | ---: | ---: | ---: |
| `test_cases/zhaopin/test_sg_job_preferences_add_from_list.py` | 7 | 1 | 0 | 0 |

## 失败用例

- `test_cases/zhaopin/test_sg_job_preferences_add_from_list.py` :: `test_sg_add_pref_authenticated_should_redirect_directly_to_add_page`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 25000ms exceeded.
Call log:
  - waiting for get_by_text(re.compile(r"Add\s*Job\s*Preference\s*Unlock\s+more", re.IGNORECASE)).or_(get_by_text(re.compile(r"Add\s+Job\s+Preference", re.IGNORECASE))).or_(get_by_text(re.compile(r"Unlock\s+…

## 错误（setup/teardown 等）

（无）

## 跳过用例

（无）

## 子进程与线程元数据

- 子进程 **returncode**: 1
- 本脚本墙钟: **335.49** s（线程内 pytest 子进程起止）
