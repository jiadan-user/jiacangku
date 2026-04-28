# `test_es_resume_submit.py` 无头跑测报告

- 生成时间: 2026-04-27 12:20:53 +0800
- JUnit 输入: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_115814/junit/test_es_resume_submit_junit.xml`
- 控制台日志: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_115814/per_script_logs/test_es_resume_submit.log`

## 总耗时

- **pytest 汇总**: 1 failed, 4 passed, 1 skipped
- **JUnit testsuite time 之和（近似）**: **106.66 s**（若未并行，接近各用例 CPU 累计；与墙钟可能不同）
- 用例总数（JUnit 条目）: 6

## 各测试脚本耗时（按 JUnit 单条 time 汇总到文件）

| 脚本 | 耗时 (s) |
| --- | ---: |
| `test_cases/zhaopin/test_es_resume_submit.py` | 105.703 |

## 统计摘要（按文件）

| 脚本 | passed | failed | skipped | error |
| --- | ---: | ---: | ---: | ---: |
| `test_cases/zhaopin/test_es_resume_submit.py` | 4 | 1 | 1 | 0 |

## 失败用例

- `test_cases/zhaopin/test_es_resume_submit.py` :: `test_submit_resume_set_work_to_date`
  - AssertionError: resume_work_experience 表应有1条记录
assert 0 == 1
 +  where 0 = len([])

## 错误（setup/teardown 等）

（无）

## 跳过用例

- `test_cases/zhaopin/test_es_resume_submit.py` :: `test_verify_resume_data_display`
  - test_verify_resume_data_display depends on es_resume_submit_tc004

## 子进程与线程元数据

- 子进程 **returncode**: 1
- 本脚本墙钟: **107.56** s（线程内 pytest 子进程起止）
