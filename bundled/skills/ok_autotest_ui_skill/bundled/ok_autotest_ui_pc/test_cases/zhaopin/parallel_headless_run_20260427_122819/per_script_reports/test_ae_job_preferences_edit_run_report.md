# `test_ae_job_preferences_edit.py` 无头跑测报告

- 生成时间: 2026-04-27 12:50:44 +0800
- JUnit 输入: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_122819/junit/test_ae_job_preferences_edit_junit.xml`
- 控制台日志: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_122819/per_script_logs/test_ae_job_preferences_edit.log`

## 总耗时

- **pytest 汇总**: 1 failed, 14 passed
- **JUnit testsuite time 之和（近似）**: **173.48 s**（若未并行，接近各用例 CPU 累计；与墙钟可能不同）
- 用例总数（JUnit 条目）: 15

## 各测试脚本耗时（按 JUnit 单条 time 汇总到文件）

| 脚本 | 耗时 (s) |
| --- | ---: |
| `test_cases/zhaopin/test_ae_job_preferences_edit.py` | 172.824 |

## 统计摘要（按文件）

| 脚本 | passed | failed | skipped | error |
| --- | ---: | ---: | ---: | ---: |
| `test_cases/zhaopin/test_ae_job_preferences_edit.py` | 14 | 1 | 0 | 0 |

## 失败用例

- `test_cases/zhaopin/test_ae_job_preferences_edit.py` :: `test_ae_edit_continue_submits_and_returns_to_return_url`
  - AssertionError: 仍停留在编辑页，当前 URL: https://aepub.58v5.cn/biz/en/jobPreference?returnUrl=https://ae.58v5.cn/en/city/cate-jobs/?iconSource=jobs
assert not True
 +  where True = is_url_contains('jobPreference')
 +    where is_url_contains = <pages.job_preference_page.JobPreferencePage object at 0x1064081c…

## 错误（setup/teardown 等）

（无）

## 跳过用例

（无）

## 子进程与线程元数据

- 子进程 **returncode**: 1
- 本脚本墙钟: **174.15** s（线程内 pytest 子进程起止）
