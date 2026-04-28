# `test_es_resume_submit.py` 无头跑测报告

- 生成时间: 2026-04-27 14:32:05 +0800
- JUnit 输入: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_140941/junit/test_es_resume_submit_junit.xml`
- 控制台日志: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_140941/per_script_logs/test_es_resume_submit.log`

## 总耗时

- **pytest 汇总**: 2 failed, 4 passed
- **JUnit testsuite time 之和（近似）**: **445.91 s**（若未并行，接近各用例 CPU 累计；与墙钟可能不同）
- 用例总数（JUnit 条目）: 6

## 各测试脚本耗时（按 JUnit 单条 time 汇总到文件）

| 脚本 | 耗时 (s) |
| --- | ---: |
| `test_cases/zhaopin/test_es_resume_submit.py` | 445.140 |

## 统计摘要（按文件）

| 脚本 | passed | failed | skipped | error |
| --- | ---: | ---: | ---: | ---: |
| `test_cases/zhaopin/test_es_resume_submit.py` | 4 | 2 | 0 | 0 |

## 失败用例

- `test_cases/zhaopin/test_es_resume_submit.py` :: `test_submit_resume_without_work_experience`
  - playwright._impl._errors.TimeoutError: Page.wait_for_function: Timeout 120000ms exceeded.
- `test_cases/zhaopin/test_es_resume_submit.py` :: `test_submit_resume_change_location`
  - AssertionError: country_code 不正确，期望: FR (France), 实际: ES
assert 'ES' == 'FR'
  
  - FR
  + ES

## 错误（setup/teardown 等）

（无）

## 跳过用例

（无）

## 子进程与线程元数据

- 子进程 **returncode**: 1
- 本脚本墙钟: **446.76** s（线程内 pytest 子进程起止）
