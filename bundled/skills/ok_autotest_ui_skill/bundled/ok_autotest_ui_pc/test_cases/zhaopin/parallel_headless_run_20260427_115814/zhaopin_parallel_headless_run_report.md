# zhaopin 无头多线程并行跑测

- 输出目录: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_115814`
- **线程池总墙钟**: 1359.50 s
- 各脚本 Markdown: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_115814/per_script_reports/`

## 每脚本报告路径

| 脚本 | Markdown 报告 |
| --- | --- |
| `test_ae_job_preferences_add_from_list.py` | `test_ae_job_preferences_add_from_list_run_report.md` |
| `test_ae_job_preferences_edit.py` | `test_ae_job_preferences_edit_run_report.md` |
| `test_ae_jobs_list_location_and_add_pref.py` | `test_ae_jobs_list_location_and_add_pref_run_report.md` |
| `test_ae_jobs_list_search_and_filter.py` | `test_ae_jobs_list_search_and_filter_run_report.md` |
| `test_ae_resume_edit.py` | `test_ae_resume_edit_run_report.md` |
| `test_es_jobs_detail_panel.py` | `test_es_jobs_detail_panel_run_report.md` |
| `test_es_jobs_list_search_and_filter.py` | `test_es_jobs_list_search_and_filter_run_report.md` |
| `test_es_resume_add.py` | `test_es_resume_add_run_report.md` |
| `test_es_resume_submit.py` | `test_es_resume_submit_run_report.md` |
| `test_sg_job_preferences.py` | `test_sg_job_preferences_run_report.md` |
| `test_sg_job_preferences_add_from_list.py` | `test_sg_job_preferences_add_from_list_run_report.md` |
| `test_sg_jobs_list_search_and_filter.py` | `test_sg_jobs_list_search_and_filter_run_report.md` |
| `test_sg_jobs_pref_submit.py` | `test_sg_jobs_pref_submit_run_report.md` |
| `test_zhaopin_job_preferences.py` | `test_zhaopin_job_preferences_run_report.md` |

## 每脚本墙钟

| 脚本 | 秒 | returncode |
| --- | ---: | ---: |
| `test_ae_job_preferences_add_from_list.py` | 42.99 | 1 |
| `test_ae_job_preferences_edit.py` | 176.99 | 1 |
| `test_ae_jobs_list_location_and_add_pref.py` | 10.28 | 0 |
| `test_ae_jobs_list_search_and_filter.py` | 346.99 | 1 |
| `test_ae_resume_edit.py` | 273.70 | 1 |
| `test_es_jobs_detail_panel.py` | 540.43 | 0 |
| `test_es_jobs_list_search_and_filter.py` | 592.20 | 0 |
| `test_es_resume_add.py` | 874.49 | 1 |
| `test_es_resume_submit.py` | 107.56 | 1 |
| `test_sg_job_preferences.py` | 1359.48 | 1 |
| `test_sg_job_preferences_add_from_list.py` | 352.22 | 1 |
| `test_sg_jobs_list_search_and_filter.py` | 297.26 | 0 |
| `test_sg_jobs_pref_submit.py` | 319.67 | 0 |
| `test_zhaopin_job_preferences.py` | 187.94 | 1 |

---

## JUnit 汇总报告

- 生成时间: 2026-04-27 12:20:54 +0800
- JUnit 输入: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_115814/zhaopin_parallel_merged_junit.xml`
- 控制台日志: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_115814/zhaopin_parallel_combined_console.log`

## 总耗时

- **pytest 汇总**: 3 failed, 2 passed
- **JUnit testsuite time 之和（近似）**: **5471.54 s**（若未并行，接近各用例 CPU 累计；与墙钟可能不同）
- 用例总数（JUnit 条目）: 343

## 各测试脚本耗时（按 JUnit 单条 time 汇总到文件）

| 脚本 | 耗时 (s) |
| --- | ---: |
| `test_cases/zhaopin/test_sg_job_preferences.py` | 1357.179 |
| `test_cases/zhaopin/test_es_resume_add.py` | 872.209 |
| `test_cases/zhaopin/test_es_jobs_list_search_and_filter.py` | 590.547 |
| `test_cases/zhaopin/test_es_jobs_detail_panel.py` | 539.302 |
| `test_cases/zhaopin/test_sg_job_preferences_add_from_list.py` | 350.193 |
| `test_cases/zhaopin/test_ae_jobs_list_search_and_filter.py` | 345.177 |
| `test_cases/zhaopin/test_sg_jobs_pref_submit.py` | 318.126 |
| `test_cases/zhaopin/test_sg_jobs_list_search_and_filter.py` | 295.923 |
| `test_cases/zhaopin/test_ae_resume_edit.py` | 271.636 |
| `test_cases/zhaopin/test_zhaopin_job_preferences.py` | 185.219 |
| `test_cases/zhaopin/test_ae_job_preferences_edit.py` | 175.658 |
| `test_cases/zhaopin/test_es_resume_submit.py` | 105.703 |
| `test_cases/zhaopin/test_ae_job_preferences_add_from_list.py` | 39.286 |
| `test_cases/zhaopin/test_ae_jobs_list_location_and_add_pref.py` | 9.307 |

## 统计摘要（按文件）

| 脚本 | passed | failed | skipped | error |
| --- | ---: | ---: | ---: | ---: |
| `test_cases/zhaopin/test_ae_job_preferences_add_from_list.py` | 2 | 3 | 0 | 0 |
| `test_cases/zhaopin/test_ae_job_preferences_edit.py` | 14 | 1 | 0 | 0 |
| `test_cases/zhaopin/test_ae_jobs_list_location_and_add_pref.py` | 2 | 0 | 0 | 0 |
| `test_cases/zhaopin/test_ae_jobs_list_search_and_filter.py` | 61 | 1 | 0 | 0 |
| `test_cases/zhaopin/test_ae_resume_edit.py` | 26 | 4 | 0 | 0 |
| `test_cases/zhaopin/test_es_jobs_detail_panel.py` | 28 | 0 | 0 | 0 |
| `test_cases/zhaopin/test_es_jobs_list_search_and_filter.py` | 65 | 0 | 0 | 0 |
| `test_cases/zhaopin/test_es_resume_add.py` | 37 | 3 | 1 | 0 |
| `test_cases/zhaopin/test_es_resume_submit.py` | 4 | 1 | 1 | 0 |
| `test_cases/zhaopin/test_sg_job_preferences.py` | 55 | 3 | 0 | 0 |
| `test_cases/zhaopin/test_sg_job_preferences_add_from_list.py` | 7 | 1 | 0 | 0 |
| `test_cases/zhaopin/test_sg_jobs_list_search_and_filter.py` | 7 | 0 | 0 | 0 |
| `test_cases/zhaopin/test_sg_jobs_pref_submit.py` | 9 | 0 | 0 | 0 |
| `test_cases/zhaopin/test_zhaopin_job_preferences.py` | 4 | 3 | 0 | 0 |

## 失败用例

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
 +    where is_url_contains = <pages.job_preference_page.JobPreferencePage object at 0x1062158b…
- `test_cases/zhaopin/test_ae_jobs_list_search_and_filter.py` :: `test_tc008_search_focus_shows_recent_searches`
  - AssertionError: 聚焦搜索框后应显示 'Recent Searches' 历史下拉
assert False
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
- `test_cases/zhaopin/test_es_resume_add.py` :: `test_tc008_email_prefilled_with_login_account`
  - AssertionError: Current Location预填值错误，期望: Spain，实际: France
assert 'France' == 'Spain'
  
  - Spain
  + France
- `test_cases/zhaopin/test_es_resume_add.py` :: `test_tc016_current_location_dropdown_select`
  - AssertionError: 选择 France 后 Current Location 字段应回显 'France'，实际: Spain
assert 'Spain' == 'France'
  
  - France
  + Spain
- `test_cases/zhaopin/test_es_resume_add.py` :: `test_tc035_job_function_panel_no_search_filter`
  - AssertionError: Job Function 应显示所选分类，实际: 
assert 'Testing & Quality Assurance' in ''
- `test_cases/zhaopin/test_es_resume_submit.py` :: `test_submit_resume_set_work_to_date`
  - AssertionError: resume_work_experience 表应有1条记录
assert 0 == 1
 +  where 0 = len([])
- `test_cases/zhaopin/test_sg_job_preferences.py` :: `test_sg_jobs_icon_navigates_to_job_preferences_page`
  - AssertionError: 期望 jobPreference 中间页或带 iconSource=jobs 的职位列表，当前: https://sg.58v5.cn/en/city-singapore/
assert ('cate-jobs' in 'https://sg.58v5.cn/en/city-singapore/')
- `test_cases/zhaopin/test_sg_job_preferences.py` :: `test_sg_job_preferences_page_shows_all_form_blocks`
  - AssertionError: Job Functions 触发器不可见
assert False
 +  where False = is_visible(timeout=5000)
 +    where is_visible = <Locator frame=<Frame name= url='https://sgpub.58v5.cn/biz/en/jobPreference?showSkip=1&returnUrl=https%3A%2F%2Fsg.58v5.cn%2Fen%2Fcity-singapore%2Fcate-jobs%2F%3FiconSource%3Djobs'> s…
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
- `test_cases/zhaopin/test_zhaopin_job_preferences.py` :: `test_tc007_unnamed`
  - AssertionError: 未登录应触发登录流程，当前: https://sgpub.58v5.cn/biz/en/jobPreference?showSkip=1&returnUrl=https%3A%2F%2Fsg.58v5.cn%2Fen%2Fcity-singapore%2Fcate-jobs%2F%3FiconSource%3Djobs
assert ('login' in 'https://sgpub.58v5.cn/biz/en/jobpreference?showskip=1&returnurl=https%3a%2f%2fsg.58v5.cn%2fen%2fcity-si…

## 错误（setup/teardown 等）

（无）

## 跳过用例

- `test_cases/zhaopin/test_es_resume_add.py` :: `test_tc001_enter_resume_add_via_resume_button`
  - 未进入简历添加页（当前 https://espub.58v5.cn/biz/en/resume），账号可能已有简历
- `test_cases/zhaopin/test_es_resume_submit.py` :: `test_verify_resume_data_display`
  - test_verify_resume_data_display depends on es_resume_submit_tc004
