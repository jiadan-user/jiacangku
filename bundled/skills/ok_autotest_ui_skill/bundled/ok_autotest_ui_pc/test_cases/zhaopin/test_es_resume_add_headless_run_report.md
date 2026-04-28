# test_es_resume_add.py 无头跑测汇总报告

- 生成时间: 2026-04-17 19:12:10 +0800
- JUnit 输入: `test_es_resume_add_headless_junit.xml`
- 控制台日志: `test_es_resume_add_headless_console.log`

## 总耗时

- **pytest 汇总**: 1 failed, 40 passed
- **墙钟（time real）**: **498.12 s**（约 8.30 min）
- 用例总数（JUnit 条目）: 41

## 各测试脚本耗时（按 JUnit 单条 time 汇总到文件）

| 脚本 | 耗时 (s) |
| --- | ---: |
| `test_cases/zhaopin/test_es_resume_add.py` | 497.455 |

## 统计摘要（按文件）

| 脚本 | passed | failed | skipped | error |
| --- | ---: | ---: | ---: | ---: |
| `test_cases/zhaopin/test_es_resume_add.py` | 40 | 1 | 0 | 0 |

## 失败用例

- `test_cases/zhaopin/test_es_resume_add.py` :: `test_tc031_education_to_date_cannot_be_before_from`
  - AssertionError: Education To 早于 From 时，Done 应禁用或页面应显示日期相关错误（未点击 Done）
assert (False or False)

## 错误（setup/teardown 等）

（无）

## 跳过用例

（无）
