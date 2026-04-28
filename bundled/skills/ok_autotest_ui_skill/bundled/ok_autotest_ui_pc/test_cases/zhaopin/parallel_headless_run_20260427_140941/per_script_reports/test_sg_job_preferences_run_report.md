# `test_sg_job_preferences.py` 无头跑测报告

- 生成时间: 2026-04-27 14:32:05 +0800
- JUnit 输入: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_140941/junit/test_sg_job_preferences_junit.xml`
- 控制台日志: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_140941/per_script_logs/test_sg_job_preferences.log`

## 总耗时

- **pytest 汇总**: 2 failed, 56 passed
- **JUnit testsuite time 之和（近似）**: **1343.64 s**（若未并行，接近各用例 CPU 累计；与墙钟可能不同）
- 用例总数（JUnit 条目）: 58

## 各测试脚本耗时（按 JUnit 单条 time 汇总到文件）

| 脚本 | 耗时 (s) |
| --- | ---: |
| `test_cases/zhaopin/test_sg_job_preferences.py` | 1340.283 |

## 统计摘要（按文件）

| 脚本 | passed | failed | skipped | error |
| --- | ---: | ---: | ---: | ---: |
| `test_cases/zhaopin/test_sg_job_preferences.py` | 56 | 2 | 0 | 0 |

## 失败用例

- `test_cases/zhaopin/test_sg_job_preferences.py` :: `test_sg_jobs_icon_navigates_to_job_preferences_page`
  - AssertionError: 期望 jobPreference 中间页或带 iconSource=jobs 的职位列表，当前: https://sg.58v5.cn/en/city-singapore/
assert ('cate-jobs' in 'https://sg.58v5.cn/en/city-singapore/')
- `test_cases/zhaopin/test_sg_job_preferences.py` :: `test_sg_home_page_jobs_icon_visible_and_clickable`
  - AssertionError: 点击 Jobs 后 URL 未变化: https://sg.58v5.cn/en/city-singapore/
assert ('city-singapore' not in 'https://sg....y-singapore/'
  
  'city-singapore' is contained here:
    https://sg.58v5.cn/en/city-singapore/
  ?                       ++++++++++++++ or 'cate-jobs' in 'https://sg.58v5.cn/en/c…

## 错误（setup/teardown 等）

（无）

## 跳过用例

（无）

## 子进程与线程元数据

- 子进程 **returncode**: 1
- 本脚本墙钟: **1344.55** s（线程内 pytest 子进程起止）
