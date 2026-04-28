# `test_es_resume_add.py` 无头跑测报告

- 生成时间: 2026-04-27 14:32:05 +0800
- JUnit 输入: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_140941/junit/test_es_resume_add_junit.xml`
- 控制台日志: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_140941/per_script_logs/test_es_resume_add.log`

## 总耗时

- **pytest 汇总**: 2 failed, 39 passed
- **JUnit testsuite time 之和（近似）**: **845.53 s**（若未并行，接近各用例 CPU 累计；与墙钟可能不同）
- 用例总数（JUnit 条目）: 41

## 各测试脚本耗时（按 JUnit 单条 time 汇总到文件）

| 脚本 | 耗时 (s) |
| --- | ---: |
| `test_cases/zhaopin/test_es_resume_add.py` | 844.307 |

## 统计摘要（按文件）

| 脚本 | passed | failed | skipped | error |
| --- | ---: | ---: | ---: | ---: |
| `test_cases/zhaopin/test_es_resume_add.py` | 39 | 2 | 0 | 0 |

## 失败用例

- `test_cases/zhaopin/test_es_resume_add.py` :: `test_tc016_current_location_dropdown_select`
  - AssertionError: 选择 France 后 Current Location 字段应回显 'France'，实际: Spain
assert 'Spain' == 'France'
  
  - France
  + Spain
- `test_cases/zhaopin/test_es_resume_add.py` :: `test_tc035_job_function_panel_no_search_filter`
  - AssertionError: Job Function 应显示所选分类，实际: 
assert 'Testing & Quality Assurance' in ''

## 错误（setup/teardown 等）

（无）

## 跳过用例

（无）

## 子进程与线程元数据

- 子进程 **returncode**: 1
- 本脚本墙钟: **846.47** s（线程内 pytest 子进程起止）
