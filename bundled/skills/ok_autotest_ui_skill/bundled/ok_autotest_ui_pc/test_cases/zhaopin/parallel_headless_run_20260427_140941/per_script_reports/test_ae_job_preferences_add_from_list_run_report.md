# `test_ae_job_preferences_add_from_list.py` 无头跑测报告

- 生成时间: 2026-04-27 14:32:05 +0800
- JUnit 输入: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_140941/junit/test_ae_job_preferences_add_from_list_junit.xml`
- 控制台日志: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_140941/per_script_logs/test_ae_job_preferences_add_from_list.log`

## 总耗时

- **pytest 汇总**: 4 failed, 1 passed
- **JUnit testsuite time 之和（近似）**: **36.70 s**（若未并行，接近各用例 CPU 累计；与墙钟可能不同）
- 用例总数（JUnit 条目）: 5

## 各测试脚本耗时（按 JUnit 单条 time 汇总到文件）

| 脚本 | 耗时 (s) |
| --- | ---: |
| `test_cases/zhaopin/test_ae_job_preferences_add_from_list.py` | 33.717 |

## 统计摘要（按文件）

| 脚本 | passed | failed | skipped | error |
| --- | ---: | ---: | ---: | ---: |
| `test_cases/zhaopin/test_ae_job_preferences_add_from_list.py` | 1 | 4 | 0 | 0 |

## 失败用例

- `test_cases/zhaopin/test_ae_job_preferences_add_from_list.py` :: `test_ae_add_pref_unauthenticated_should_show_add_banner`
  - AssertionError: 未找到 'Add Job Preference' 文本，未登录状态下应显示该卡片
assert False
 +  where False = is_visible(timeout=8000)
 +    where is_visible = <Locator frame=<Frame name= url='https://ae.58v5.cn/en/city/cate-jobs/?iconSource=jobs'> selector='internal:text="Add Job Preference"i >> nth=0'>.is_visible
- `test_cases/zhaopin/test_ae_job_preferences_add_from_list.py` :: `test_ae_add_pref_login_via_banner_should_redirect_to_edit_page`
  - AssertionError: 调用 _login_via_add_job_pref_banner 前，Add Job Preference 卡片应可见（未登录状态）
assert False
 +  where False = is_visible(timeout=5000)
 +    where is_visible = <Locator frame=<Frame name= url='https://ae.58v5.cn/en/city/cate-jobs/?iconSource=jobs'> selector='internal:text="Add Job Preference"i …
- `test_cases/zhaopin/test_ae_job_preferences_add_from_list.py` :: `test_ae_add_pref_back_button_should_redirect_to_jobs_list`
  - AssertionError: 调用 _login_via_add_job_pref_banner 前，Add Job Preference 卡片应可见（未登录状态）
assert False
 +  where False = is_visible(timeout=5000)
 +    where is_visible = <Locator frame=<Frame name= url='https://ae.58v5.cn/en/city/cate-jobs/?iconSource=jobs'> selector='internal:text="Add Job Preference"i …
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
- 本脚本墙钟: **37.78** s（线程内 pytest 子进程起止）
