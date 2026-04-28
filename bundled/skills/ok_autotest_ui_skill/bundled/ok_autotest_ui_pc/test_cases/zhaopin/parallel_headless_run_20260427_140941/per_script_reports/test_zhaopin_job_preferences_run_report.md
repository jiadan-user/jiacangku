# `test_zhaopin_job_preferences.py` 无头跑测报告

- 生成时间: 2026-04-27 14:32:05 +0800
- JUnit 输入: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_140941/junit/test_zhaopin_job_preferences_junit.xml`
- 控制台日志: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_140941/per_script_logs/test_zhaopin_job_preferences.log`

## 总耗时

- **pytest 汇总**: 2 failed, 5 passed
- **JUnit testsuite time 之和（近似）**: **177.32 s**（若未并行，接近各用例 CPU 累计；与墙钟可能不同）
- 用例总数（JUnit 条目）: 7

## 各测试脚本耗时（按 JUnit 单条 time 汇总到文件）

| 脚本 | 耗时 (s) |
| --- | ---: |
| `test_cases/zhaopin/test_zhaopin_job_preferences.py` | 175.516 |

## 统计摘要（按文件）

| 脚本 | passed | failed | skipped | error |
| --- | ---: | ---: | ---: | ---: |
| `test_cases/zhaopin/test_zhaopin_job_preferences.py` | 5 | 2 | 0 | 0 |

## 失败用例

- `test_cases/zhaopin/test_zhaopin_job_preferences.py` :: `test_tc001_unnamed`
  - playwright._impl._errors.TimeoutError: Timeout 45000ms exceeded.
=========================== logs ===========================
waiting for navigation to "**/cate-jobs**" until 'load'
  navigated to "https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs"
  navigated to "https://sg.58v5.cn/en…
- `test_cases/zhaopin/test_zhaopin_job_preferences.py` :: `test_tc002_unnamed`
  - playwright._impl._errors.TimeoutError: Timeout 45000ms exceeded.
=========================== logs ===========================
waiting for navigation to "**/cate-jobs**" until 'load'
  navigated to "https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs"
  navigated to "https://sg.58v5.cn/en…

## 错误（setup/teardown 等）

（无）

## 跳过用例

（无）

## 子进程与线程元数据

- 子进程 **returncode**: 1
- 本脚本墙钟: **178.38** s（线程内 pytest 子进程起止）
