# `test_ae_job_preferences_add_from_list.py` 无头跑测报告

- 生成时间: 2026-04-27 12:50:44 +0800
- JUnit 输入: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_122819/junit/test_ae_job_preferences_add_from_list_junit.xml`
- 控制台日志: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_122819/per_script_logs/test_ae_job_preferences_add_from_list.log`

## 总耗时

- **pytest 汇总**: 2 failed, 3 passed
- **JUnit testsuite time 之和（近似）**: **61.84 s**（若未并行，接近各用例 CPU 累计；与墙钟可能不同）
- 用例总数（JUnit 条目）: 5

## 各测试脚本耗时（按 JUnit 单条 time 汇总到文件）

| 脚本 | 耗时 (s) |
| --- | ---: |
| `test_cases/zhaopin/test_ae_job_preferences_add_from_list.py` | 59.720 |

## 统计摘要（按文件）

| 脚本 | passed | failed | skipped | error |
| --- | ---: | ---: | ---: | ---: |
| `test_cases/zhaopin/test_ae_job_preferences_add_from_list.py` | 3 | 2 | 0 | 0 |

## 失败用例

- `test_cases/zhaopin/test_ae_job_preferences_add_from_list.py` :: `test_ae_add_pref_back_button_should_redirect_to_jobs_list`
  - playwright._impl._errors.Error: Locator.is_visible: Error: strict mode violation: get_by_text("Edit") resolved to 2 elements:
    1) <div class="Preference_preferenceItem__qJtyw">Accounts Receivable/Credit Control</div> aka get_by_text("Accounts Receivable/Credit")
    2) <a href="" class="Preferenc…
- `test_cases/zhaopin/test_ae_job_preferences_add_from_list.py` :: `test_ae_add_pref_continue_should_submit_and_redirect_to_jobs_list`
  - AssertionError: 调用 _login_via_add_job_pref_banner 前，Add Job Preference 卡片应可见（未登录状态）
assert False
 +  where False = is_visible(timeout=5000)
 +    where is_visible = <Locator frame=<Frame name= url='https://ae.58v5.cn/en/city/cate-jobs/?iconSource=jobs'> selector='internal:text="Add Job Preference"i …

## 错误（setup/teardown 等）

（无）

## 跳过用例

（无）

## 子进程与线程元数据

- 子进程 **returncode**: 1
- 本脚本墙钟: **62.55** s（线程内 pytest 子进程起止）
