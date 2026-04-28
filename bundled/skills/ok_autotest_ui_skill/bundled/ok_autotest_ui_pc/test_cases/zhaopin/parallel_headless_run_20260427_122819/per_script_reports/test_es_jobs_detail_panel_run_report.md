# `test_es_jobs_detail_panel.py` 无头跑测报告

- 生成时间: 2026-04-27 12:50:44 +0800
- JUnit 输入: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_122819/junit/test_es_jobs_detail_panel_junit.xml`
- 控制台日志: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_122819/per_script_logs/test_es_jobs_detail_panel.log`

## 总耗时

- **pytest 汇总**: 1 failed, 27 passed
- **JUnit testsuite time 之和（近似）**: **533.95 s**（若未并行，接近各用例 CPU 累计；与墙钟可能不同）
- 用例总数（JUnit 条目）: 28

## 各测试脚本耗时（按 JUnit 单条 time 汇总到文件）

| 脚本 | 耗时 (s) |
| --- | ---: |
| `test_cases/zhaopin/test_es_jobs_detail_panel.py` | 532.962 |

## 统计摘要（按文件）

| 脚本 | passed | failed | skipped | error |
| --- | ---: | ---: | ---: | ---: |
| `test_cases/zhaopin/test_es_jobs_detail_panel.py` | 27 | 1 | 0 | 0 |

## 失败用例

- `test_cases/zhaopin/test_es_jobs_detail_panel.py` :: `test_tc006_own_post_description_visible`
  - AssertionError: 详情面板应展示 Description 标题和内容段落，无折叠遮挡
assert False

## 错误（setup/teardown 等）

（无）

## 跳过用例

（无）

## 子进程与线程元数据

- 子进程 **returncode**: 1
- 本脚本墙钟: **534.69** s（线程内 pytest 子进程起止）
