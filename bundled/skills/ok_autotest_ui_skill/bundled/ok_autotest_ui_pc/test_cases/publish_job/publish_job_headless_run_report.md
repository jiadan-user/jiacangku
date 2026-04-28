# publish_job 无头跑测汇总报告

- 生成时间: 2026-04-20 15:56:26 +0800
- JUnit: `test_cases/publish_job/publish_job_headless_junit.xml`
- 控制台日志: `test_cases/publish_job/publish_job_headless_console.log`
- 墙钟秒数文件: `test_cases/publish_job/publish_job_headless_duration_sec.txt`

## 总耗时

- **pytest 汇总行**: 54 passed
- **墙钟（`/usr/bin/time -p` real）**: **834.54 s**（约 13.91 min）
- **user / sys**: 150.43 s / 25.23 s
- **JUnit testsuite time（近似）**: **833.83 s**
- 用例条目数: 54

## 各测试脚本耗时（JUnit 单条 time 按文件汇总）

| 脚本 | 耗时 (s) |
| --- | ---: |
| `test_cases/publish_job/test_publish_job_supplemental.py` | 385.681 |
| `test_cases/publish_job/test_publish_job_step3_and_navigation.py` | 92.808 |
| `test_cases/publish_job/test_publish_job_core_flow.py` | 86.757 |
| `test_cases/publish_job/test_publish_job_step1_validation.py` | 70.057 |
| `test_cases/publish_job/test_publish_job_step2_validation.py` | 54.435 |
| `test_cases/publish_job/test_publish_job_step1_extended.py` | 46.159 |
| `test_cases/publish_job/test_publish_job_security_and_ui.py` | 42.037 |
| `test_cases/publish_job/test_publish_job_i18n_and_compatibility.py` | 34.099 |
| `test_cases/publish_job/test_publish_job_smoke.py` | 21.354 |

## 统计摘要（按文件）

| 脚本 | passed | failed | skipped | error |
| --- | ---: | ---: | ---: | ---: |
| `test_cases/publish_job/test_publish_job_core_flow.py` | 4 | 0 | 0 | 0 |
| `test_cases/publish_job/test_publish_job_i18n_and_compatibility.py` | 4 | 0 | 0 | 0 |
| `test_cases/publish_job/test_publish_job_security_and_ui.py` | 5 | 0 | 0 | 0 |
| `test_cases/publish_job/test_publish_job_smoke.py` | 4 | 0 | 0 | 0 |
| `test_cases/publish_job/test_publish_job_step1_extended.py` | 4 | 0 | 0 | 0 |
| `test_cases/publish_job/test_publish_job_step1_validation.py` | 9 | 0 | 0 | 0 |
| `test_cases/publish_job/test_publish_job_step2_validation.py` | 4 | 0 | 0 | 0 |
| `test_cases/publish_job/test_publish_job_step3_and_navigation.py` | 4 | 0 | 0 | 0 |
| `test_cases/publish_job/test_publish_job_supplemental.py` | 16 | 0 | 0 | 0 |

## 失败用例

（无）

## 错误（setup/teardown 等）

（无）

## 跳过用例

（无）
