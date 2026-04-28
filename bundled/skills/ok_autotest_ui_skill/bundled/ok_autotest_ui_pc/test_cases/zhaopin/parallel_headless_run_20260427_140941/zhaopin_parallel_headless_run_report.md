# zhaopin 无头多线程并行跑测

- 输出目录: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_140941`
- **线程池总墙钟**: 1344.57 s
- **模式**: 仅重跑 JUnit 中有失败/错误的脚本，见 `rerun_source.txt`
- 各脚本 Markdown: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_140941/per_script_reports/`

## 每脚本报告路径

| 脚本 | Markdown 报告 |
| --- | --- |
| `test_ae_job_preferences_add_from_list.py` | `test_ae_job_preferences_add_from_list_run_report.md` |
| `test_ae_job_preferences_edit.py` | `test_ae_job_preferences_edit_run_report.md` |
| `test_ae_resume_edit.py` | `test_ae_resume_edit_run_report.md` |
| `test_es_jobs_detail_panel.py` | `test_es_jobs_detail_panel_run_report.md` |
| `test_es_resume_add.py` | `test_es_resume_add_run_report.md` |
| `test_es_resume_submit.py` | `test_es_resume_submit_run_report.md` |
| `test_sg_job_preferences.py` | `test_sg_job_preferences_run_report.md` |
| `test_sg_job_preferences_add_from_list.py` | `test_sg_job_preferences_add_from_list_run_report.md` |
| `test_zhaopin_job_preferences.py` | `test_zhaopin_job_preferences_run_report.md` |

## 每脚本墙钟

| 脚本 | 秒 | returncode |
| --- | ---: | ---: |
| `test_ae_job_preferences_add_from_list.py` | 37.78 | 1 |
| `test_ae_job_preferences_edit.py` | 171.55 | 1 |
| `test_ae_resume_edit.py` | 275.63 | 1 |
| `test_es_jobs_detail_panel.py` | 546.11 | 1 |
| `test_es_resume_add.py` | 846.47 | 1 |
| `test_es_resume_submit.py` | 446.76 | 1 |
| `test_sg_job_preferences.py` | 1344.55 | 1 |
| `test_sg_job_preferences_add_from_list.py` | 335.49 | 1 |
| `test_zhaopin_job_preferences.py` | 178.38 | 1 |

---

## JUnit 汇总报告

- 生成时间: 2026-04-27 14:32:05 +0800
- JUnit 输入: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_140941/zhaopin_parallel_merged_junit.xml`
- 控制台日志: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_140941/zhaopin_parallel_combined_console.log`

## 总耗时

- **pytest 汇总**: 4 failed, 1 passed
- **JUnit testsuite time 之和（近似）**: **4173.73 s**（若未并行，接近各用例 CPU 累计；与墙钟可能不同）
- 用例总数（JUnit 条目）: 198

## 各测试脚本耗时（按 JUnit 单条 time 汇总到文件）

| 脚本 | 耗时 (s) |
| --- | ---: |
| `test_cases/zhaopin/test_sg_job_preferences.py` | 1340.283 |
| `test_cases/zhaopin/test_es_resume_add.py` | 844.307 |
| `test_cases/zhaopin/test_es_jobs_detail_panel.py` | 543.955 |
| `test_cases/zhaopin/test_es_resume_submit.py` | 445.140 |
| `test_cases/zhaopin/test_sg_job_preferences_add_from_list.py` | 333.508 |
| `test_cases/zhaopin/test_ae_resume_edit.py` | 273.106 |
| `test_cases/zhaopin/test_zhaopin_job_preferences.py` | 175.516 |
| `test_cases/zhaopin/test_ae_job_preferences_edit.py` | 169.816 |
| `test_cases/zhaopin/test_ae_job_preferences_add_from_list.py` | 33.717 |

## 统计摘要（按文件）

| 脚本 | passed | failed | skipped | error |
| --- | ---: | ---: | ---: | ---: |
| `test_cases/zhaopin/test_ae_job_preferences_add_from_list.py` | 1 | 4 | 0 | 0 |
| `test_cases/zhaopin/test_ae_job_preferences_edit.py` | 14 | 1 | 0 | 0 |
| `test_cases/zhaopin/test_ae_resume_edit.py` | 26 | 4 | 0 | 0 |
| `test_cases/zhaopin/test_es_jobs_detail_panel.py` | 27 | 1 | 0 | 0 |
| `test_cases/zhaopin/test_es_resume_add.py` | 39 | 2 | 0 | 0 |
| `test_cases/zhaopin/test_es_resume_submit.py` | 4 | 2 | 0 | 0 |
| `test_cases/zhaopin/test_sg_job_preferences.py` | 56 | 2 | 0 | 0 |
| `test_cases/zhaopin/test_sg_job_preferences_add_from_list.py` | 7 | 1 | 0 | 0 |
| `test_cases/zhaopin/test_zhaopin_job_preferences.py` | 5 | 2 | 0 | 0 |

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
- `test_cases/zhaopin/test_ae_job_preferences_edit.py` :: `test_ae_edit_continue_submits_and_returns_to_return_url`
  - AssertionError: 仍停留在编辑页，当前 URL: https://aepub.58v5.cn/biz/en/jobPreference?returnUrl=https://ae.58v5.cn/en/city/cate-jobs/?iconSource=jobs
assert not True
 +  where True = is_url_contains('jobPreference')
 +    where is_url_contains = <pages.job_preference_page.JobPreferencePage object at 0x104597a3…
- `test_cases/zhaopin/test_ae_resume_edit.py` :: `test_tc023_save_education_and_echo`
  - playwright._impl._errors.TimeoutError: Page.wait_for_selector: Timeout 8000ms exceeded.
Call log:
  - waiting for locator(".modal-content") to be visible
- `test_cases/zhaopin/test_ae_resume_edit.py` :: `test_tc028_personal_info_data_echo_after_reload`
  - playwright._impl._errors.TimeoutError: Page.wait_for_selector: Timeout 8000ms exceeded.
Call log:
  - waiting for locator(".modal-content") to be visible
- `test_cases/zhaopin/test_ae_resume_edit.py` :: `test_tc029_education_data_echo_after_reload`
  - playwright._impl._errors.TimeoutError: Page.wait_for_selector: Timeout 8000ms exceeded.
Call log:
  - waiting for locator(".modal-content") to be visible
- `test_cases/zhaopin/test_ae_resume_edit.py` :: `test_tc030_personal_summary_data_echo_after_reload`
  - AssertionError: 刷新后视图页 Personal Summary 区块应显示最新摘要内容
assert False
- `test_cases/zhaopin/test_es_jobs_detail_panel.py` :: `test_tc012_other_post_shows_contact_not_withdraw_edit`
  - playwright._impl._errors.TimeoutError: Page.wait_for_selector: Timeout 45000ms exceeded.
Call log:
  - waiting for locator("[class*=\"list-components-item-job-card\"] a[href*=\"/city-\"], [class*=\"list-components-item-job-card\"] a[href*=\"/city/\"], [class*=\"JobListItem\"] a[href*=\"/city-\"], [c…
- `test_cases/zhaopin/test_es_resume_add.py` :: `test_tc016_current_location_dropdown_select`
  - AssertionError: 选择 France 后 Current Location 字段应回显 'France'，实际: Spain
assert 'Spain' == 'France'
  
  - France
  + Spain
- `test_cases/zhaopin/test_es_resume_add.py` :: `test_tc035_job_function_panel_no_search_filter`
  - AssertionError: Job Function 应显示所选分类，实际: 
assert 'Testing & Quality Assurance' in ''
- `test_cases/zhaopin/test_es_resume_submit.py` :: `test_submit_resume_without_work_experience`
  - playwright._impl._errors.TimeoutError: Page.wait_for_function: Timeout 120000ms exceeded.
- `test_cases/zhaopin/test_es_resume_submit.py` :: `test_submit_resume_change_location`
  - AssertionError: country_code 不正确，期望: FR (France), 实际: ES
assert 'ES' == 'FR'
  
  - FR
  + ES
- `test_cases/zhaopin/test_sg_job_preferences.py` :: `test_sg_jobs_icon_navigates_to_job_preferences_page`
  - AssertionError: 期望 jobPreference 中间页或带 iconSource=jobs 的职位列表，当前: https://sg.58v5.cn/en/city-singapore/
assert ('cate-jobs' in 'https://sg.58v5.cn/en/city-singapore/')
- `test_cases/zhaopin/test_sg_job_preferences.py` :: `test_sg_home_page_jobs_icon_visible_and_clickable`
  - AssertionError: 点击 Jobs 后 URL 未变化: https://sg.58v5.cn/en/city-singapore/
assert ('city-singapore' not in 'https://sg....y-singapore/'
  
  'city-singapore' is contained here:
    https://sg.58v5.cn/en/city-singapore/
  ?                       ++++++++++++++ or 'cate-jobs' in 'https://sg.58v5.cn/en/c…
- `test_cases/zhaopin/test_sg_job_preferences_add_from_list.py` :: `test_sg_add_pref_authenticated_should_redirect_directly_to_add_page`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 25000ms exceeded.
Call log:
  - waiting for get_by_text(re.compile(r"Add\s*Job\s*Preference\s*Unlock\s+more", re.IGNORECASE)).or_(get_by_text(re.compile(r"Add\s+Job\s+Preference", re.IGNORECASE))).or_(get_by_text(re.compile(r"Unlock\s+…
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
