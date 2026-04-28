# zhaopin 无头跑测汇总报告

- 生成时间: 2026-04-24 18:28:34 +0800
- JUnit 输入: `zhaopin_headless_junit_20260424.xml`
- 控制台日志: `zhaopin_headless_run_20260424.log`

## 总耗时

- **pytest 汇总**: 58 failed, 284 passed, 1 skipped
- **墙钟（time real）**: **6086.54 s**（约 101.44 min）
- 用例总数（JUnit 条目）: 343

## 各测试脚本耗时（按 JUnit 单条 time 汇总到文件）

| 脚本 | 耗时 (s) |
| --- | ---: |
| `test_cases/zhaopin/test_sg_job_preferences.py` | 1348.498 |
| `test_cases/zhaopin/test_es_jobs_list_search_and_filter.py` | 1022.507 |
| `test_cases/zhaopin/test_es_resume_add.py` | 885.617 |
| `test_cases/zhaopin/test_es_jobs_detail_panel.py` | 634.814 |
| `test_cases/zhaopin/test_ae_jobs_list_search_and_filter.py` | 472.763 |
| `test_cases/zhaopin/test_sg_jobs_list_search_and_filter.py` | 411.314 |
| `test_cases/zhaopin/test_sg_jobs_pref_submit.py` | 295.756 |
| `test_cases/zhaopin/test_es_resume_submit.py` | 280.736 |
| `test_cases/zhaopin/test_ae_resume_edit.py` | 249.482 |
| `test_cases/zhaopin/test_zhaopin_job_preferences.py` | 170.769 |
| `test_cases/zhaopin/test_ae_job_preferences_edit.py` | 167.166 |
| `test_cases/zhaopin/test_sg_job_preferences_add_from_list.py` | 81.089 |
| `test_cases/zhaopin/test_ae_job_preferences_add_from_list.py` | 37.293 |
| `test_cases/zhaopin/test_ae_jobs_list_location_and_add_pref.py` | 4.005 |

## 统计摘要（按文件）

| 脚本 | passed | failed | skipped | error |
| --- | ---: | ---: | ---: | ---: |
| `test_cases/zhaopin/test_ae_job_preferences_add_from_list.py` | 1 | 4 | 0 | 0 |
| `test_cases/zhaopin/test_ae_job_preferences_edit.py` | 14 | 1 | 0 | 0 |
| `test_cases/zhaopin/test_ae_jobs_list_location_and_add_pref.py` | 2 | 0 | 0 | 0 |
| `test_cases/zhaopin/test_ae_jobs_list_search_and_filter.py` | 56 | 6 | 0 | 0 |
| `test_cases/zhaopin/test_ae_resume_edit.py` | 26 | 4 | 0 | 0 |
| `test_cases/zhaopin/test_es_jobs_detail_panel.py` | 24 | 4 | 0 | 0 |
| `test_cases/zhaopin/test_es_jobs_list_search_and_filter.py` | 54 | 11 | 0 | 0 |
| `test_cases/zhaopin/test_es_resume_add.py` | 33 | 8 | 0 | 0 |
| `test_cases/zhaopin/test_es_resume_submit.py` | 1 | 4 | 1 | 0 |
| `test_cases/zhaopin/test_sg_job_preferences.py` | 55 | 3 | 0 | 0 |
| `test_cases/zhaopin/test_sg_job_preferences_add_from_list.py` | 1 | 7 | 0 | 0 |
| `test_cases/zhaopin/test_sg_jobs_list_search_and_filter.py` | 4 | 3 | 0 | 0 |
| `test_cases/zhaopin/test_sg_jobs_pref_submit.py` | 9 | 0 | 0 | 0 |
| `test_cases/zhaopin/test_zhaopin_job_preferences.py` | 4 | 3 | 0 | 0 |

## 失败用例

- `test_cases/zhaopin/test_es_resume_submit.py` :: `test_submit_resume_with_work_experience`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 10000ms exceeded.
Call log:
  - waiting for get_by_role("textbox", name="First Name") to be visible
- `test_cases/zhaopin/test_es_resume_submit.py` :: `test_submit_resume_without_work_experience`
  - playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator(".JobListItem_jobListItem__").first
- `test_cases/zhaopin/test_es_resume_submit.py` :: `test_submit_resume_change_location`
  - playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator(".JobListItem_jobListItem__").first
- `test_cases/zhaopin/test_es_resume_submit.py` :: `test_submit_resume_set_work_to_date`
  - playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator(".JobListItem_jobListItem__").first
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
 +    where is_url_contains = <pages.job_preference_page.JobPreferencePage object at 0x107d81dc…
- `test_cases/zhaopin/test_ae_jobs_list_search_and_filter.py` :: `test_tc008_search_focus_shows_recent_searches`
  - AssertionError: 聚焦搜索框后应显示 'Recent Searches' 历史下拉
assert False
- `test_cases/zhaopin/test_ae_jobs_list_search_and_filter.py` :: `test_tc037_job_preference_category_bar_visible`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("#istPageFilterArea").get_by_text("Job Type", exact=True) to be visible
- `test_cases/zhaopin/test_ae_jobs_list_search_and_filter.py` :: `test_tc038_click_preference_category_updates_url`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("#istPageFilterArea").get_by_text("Job Type", exact=True) to be visible
- `test_cases/zhaopin/test_ae_jobs_list_search_and_filter.py` :: `test_tc039_click_edit_preference_navigates`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("#istPageFilterArea").get_by_text("Job Type", exact=True) to be visible
- `test_cases/zhaopin/test_ae_jobs_list_search_and_filter.py` :: `test_tc040_preference_category_with_existing_filter_preserved`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("#istPageFilterArea").get_by_text("Job Type", exact=True) to be visible
- `test_cases/zhaopin/test_ae_jobs_list_search_and_filter.py` :: `test_tc042_reset_exists_but_no_effect_without_filter`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("#istPageFilterArea").get_by_text("Job Type", exact=True) to be visible
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
- `test_cases/zhaopin/test_es_jobs_detail_panel.py` :: `test_tc025_unauthenticated_login_dialog_close`
  - playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for get_by_role("button", name="Contact")
- `test_cases/zhaopin/test_es_jobs_detail_panel.py` :: `test_tc026_unauthenticated_all_posts_show_contact`
  - playwright._impl._errors.TimeoutError: Page.wait_for_selector: Timeout 45000ms exceeded.
Call log:
  - waiting for locator("[class*=\"list-components-item-job-card\"] a[href*=\"/city-\"], [class*=\"list-components-item-job-card\"] a[href*=\"/city/\"], [class*=\"JobListItem\"] a[href*=\"/city-\"], [c…
- `test_cases/zhaopin/test_es_jobs_detail_panel.py` :: `test_tc027_resume_entry_visible`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 25000ms exceeded.
Call log:
  - waiting for locator("text=/OKerES_/").or_(get_by_text("Log in / Register")).first to be visible
- `test_cases/zhaopin/test_es_jobs_detail_panel.py` :: `test_tc028_resume_entry_navigates_to_resume_page`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 25000ms exceeded.
Call log:
  - waiting for locator("text=/OKerES_/").or_(get_by_text("Log in / Register")).first to be visible
- `test_cases/zhaopin/test_es_jobs_list_search_and_filter.py` :: `test_search_with_keyword_should_navigate_to_results`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 25000ms exceeded.
Call log:
  - waiting for locator("text=/OKerES_/").or_(get_by_text("Log in / Register")).first to be visible
- `test_cases/zhaopin/test_es_jobs_list_search_and_filter.py` :: `test_search_with_empty_keyword_should_stay_or_default`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 25000ms exceeded.
Call log:
  - waiting for locator("text=/OKerES_/").or_(get_by_text("Log in / Register")).first to be visible
- `test_cases/zhaopin/test_es_jobs_list_search_and_filter.py` :: `test_search_with_special_characters`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 25000ms exceeded.
Call log:
  - waiting for locator("text=/OKerES_/").or_(get_by_text("Log in / Register")).first to be visible
- `test_cases/zhaopin/test_es_jobs_list_search_and_filter.py` :: `test_scroll_to_bottom_loads_more_jobs`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 25000ms exceeded.
Call log:
  - waiting for locator(".JobListItem_").first to be visible
- `test_cases/zhaopin/test_es_jobs_list_search_and_filter.py` :: `test_click_job_card_opens_sidebar`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 25000ms exceeded.
Call log:
  - waiting for locator(".JobListItem_").first to be visible
- `test_cases/zhaopin/test_es_jobs_list_search_and_filter.py` :: `test_sidebar_buttons_for_non_own_job`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 25000ms exceeded.
Call log:
  - waiting for locator(".JobListItem_").first to be visible
- `test_cases/zhaopin/test_es_jobs_list_search_and_filter.py` :: `test_sidebar_buttons_for_own_job`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 25000ms exceeded.
Call log:
  - waiting for locator(".JobListItem_").first to be visible
- `test_cases/zhaopin/test_es_jobs_list_search_and_filter.py` :: `test_quick_reply_label_is_display_only`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 25000ms exceeded.
Call log:
  - waiting for locator(".JobListItem_").first to be visible
- `test_cases/zhaopin/test_es_jobs_list_search_and_filter.py` :: `test_click_favourites_toggles_collect_state`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 25000ms exceeded.
Call log:
  - waiting for locator(".JobListItem_").first to be visible
- `test_cases/zhaopin/test_es_jobs_list_search_and_filter.py` :: `test_click_new_tab_opens_job_detail_in_new_tab`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 25000ms exceeded.
Call log:
  - waiting for locator(".JobListItem_").first to be visible
- `test_cases/zhaopin/test_es_jobs_list_search_and_filter.py` :: `test_sidebar_resume_entry_navigates_to_resume_page`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 25000ms exceeded.
Call log:
  - waiting for locator(".JobListItem_").first to be visible
- `test_cases/zhaopin/test_es_resume_add.py` :: `test_tc016_current_location_dropdown_select`
  - AssertionError: 点击后应展开国家列表（AnchorSelector_listItem 节点）
assert 0 > 0
 +  where 0 = count()
 +    where count = <Locator frame=<Frame name= url='https://espub.58v5.cn/biz/en/resume/add'> selector='.AnchorSelector_listItem__fkBdL'>.count
- `test_cases/zhaopin/test_es_resume_add.py` :: `test_tc035_job_function_panel_no_search_filter`
  - AssertionError: 打开 Job Function 面板后，一级分类应直接全部可见
assert False
- `test_cases/zhaopin/test_es_resume_add.py` :: `test_tc014_emoji_counts_as_two_chars`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 25000ms exceeded.
Call log:
  - waiting for locator("text=/OKerES_/").or_(get_by_text("Log in / Register")).first to be visible
- `test_cases/zhaopin/test_es_resume_add.py` :: `test_tc015_continue_disabled_without_first_name`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 25000ms exceeded.
Call log:
  - waiting for locator("text=/OKerES_/").or_(get_by_text("Log in / Register")).first to be visible
- `test_cases/zhaopin/test_es_resume_add.py` :: `test_tc017_country_list_anchor_follows_scroll`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 25000ms exceeded.
Call log:
  - waiting for locator("text=/OKerES_/").or_(get_by_text("Log in / Register")).first to be visible
- `test_cases/zhaopin/test_es_resume_add.py` :: `test_tc042_page_refresh_discards_local_changes`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 25000ms exceeded.
Call log:
  - waiting for locator("text=/OKerES_/").or_(get_by_text("Log in / Register")).first to be visible
- `test_cases/zhaopin/test_es_resume_add.py` :: `test_tc036_avatar_preview_updates_after_upload`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 25000ms exceeded.
Call log:
  - waiting for locator("text=/OKerES_/").or_(get_by_text("Log in / Register")).first to be visible
- `test_cases/zhaopin/test_es_resume_add.py` :: `test_tc039_session_timeout_redirects_to_login`
  - AssertionError: Session超时后应离开简历添加页，实际 URL: https://espub.58v5.cn/biz/en/resume/add
assert False
- `test_cases/zhaopin/test_sg_job_preferences.py` :: `test_sg_jobs_icon_navigates_to_job_preferences_page`
  - AssertionError: 期望 jobPreference 中间页或带 iconSource=jobs 的职位列表，当前: https://sg.58v5.cn/en/city-singapore/
assert ('cate-jobs' in 'https://sg.58v5.cn/en/city-singapore/')
- `test_cases/zhaopin/test_sg_job_preferences.py` :: `test_sg_home_page_jobs_icon_visible_and_clickable`
  - AssertionError: 点击 Jobs 后 URL 未变化: https://sg.58v5.cn/en/city-singapore/
assert ('city-singapore' not in 'https://sg....y-singapore/'
  
  'city-singapore' is contained here:
    https://sg.58v5.cn/en/city-singapore/
  ?                       ++++++++++++++ or 'cate-jobs' in 'https://sg.58v5.cn/en/c…
- `test_cases/zhaopin/test_sg_job_preferences.py` :: `test_sg_job_functions_deselect_all_restores_placeholder`
  - playwright._impl._errors.Error: Page.goto: net::ERR_SOCKET_NOT_CONNECTED at https://sgpub.58v5.cn/biz/en/jobPreference?showSkip=1&returnUrl=https%3A%2F%2Fsg.58v5.cn%2Fen%2Fcity-singapore%2Fcate-jobs%2F%3FiconSource%3Djobs
Call log:
  - navigating to "https://sgpub.58v5.cn/biz/en/jobPreference?showSk…
- `test_cases/zhaopin/test_sg_job_preferences_add_from_list.py` :: `test_sg_add_pref_authenticated_no_pref_should_show_add_banner`
  - AssertionError: SG 站登录失败
assert False
 +  where False = is_logged_in()
 +    where is_logged_in = <pages.sg_home_page.SgHomePage object at 0x107b37250>.is_logged_in
- `test_cases/zhaopin/test_sg_job_preferences_add_from_list.py` :: `test_sg_add_pref_unauthenticated_should_show_add_banner`
  - AssertionError: 未登录状态下应显示 'Add Job Preference' 卡片
assert False
 +  where False = is_visible(timeout=8000)
 +    where is_visible = <Locator frame=<Frame name= url='https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs'> selector='internal:text="Add Job Preference"i >> nth=0'>.is_visible
- `test_cases/zhaopin/test_sg_job_preferences_add_from_list.py` :: `test_sg_add_pref_authenticated_should_redirect_directly_to_add_page`
  - AssertionError: SG 站登录失败
assert False
 +  where False = is_logged_in()
 +    where is_logged_in = <pages.sg_home_page.SgHomePage object at 0x107ed3f40>.is_logged_in
- `test_cases/zhaopin/test_sg_job_preferences_add_from_list.py` :: `test_sg_add_pref_add_page_should_show_empty_form`
  - AssertionError: SG 站登录失败
assert False
 +  where False = is_logged_in()
 +    where is_logged_in = <pages.sg_home_page.SgHomePage object at 0x11919a6a0>.is_logged_in
- `test_cases/zhaopin/test_sg_job_preferences_add_from_list.py` :: `test_sg_add_pref_empty_form_continue_should_show_three_validation_errors`
  - AssertionError: SG 站登录失败
assert False
 +  where False = is_logged_in()
 +    where is_logged_in = <pages.sg_home_page.SgHomePage object at 0x11918cc40>.is_logged_in
- `test_cases/zhaopin/test_sg_job_preferences_add_from_list.py` :: `test_sg_add_pref_back_button_should_redirect_to_jobs_list`
  - AssertionError: SG 站登录失败
assert False
 +  where False = is_logged_in()
 +    where is_logged_in = <pages.sg_home_page.SgHomePage object at 0x1191b2f70>.is_logged_in
- `test_cases/zhaopin/test_sg_job_preferences_add_from_list.py` :: `test_sg_add_pref_login_via_banner_should_redirect_to_add_page`
  - AssertionError: 未登录通过弹窗登录后应跳转到 jobPreference 添加页，当前 URL: https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs
assert 'jobPreference' in 'https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs'
- `test_cases/zhaopin/test_sg_jobs_list_search_and_filter.py` :: `test_search_with_empty_keyword_should_stay_or_default`
  - AssertionError: 页面未正常加载
assert False
 +  where False = is_page_loaded()
 +    where is_page_loaded = <pages.jobs_list_page_sg.JobsListPageSG object at 0x1197a3880>.is_page_loaded
- `test_cases/zhaopin/test_sg_jobs_list_search_and_filter.py` :: `test_search_with_special_characters_should_handle`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 20000ms exceeded.
Call log:
  - waiting for locator("input[placeholder*='Search']").first to be visible
- `test_cases/zhaopin/test_sg_jobs_list_search_and_filter.py` :: `test_search_with_long_text_should_handle`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 20000ms exceeded.
Call log:
  - waiting for locator("input[placeholder*='Search']").first to be visible
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

- `test_cases/zhaopin/test_es_resume_submit.py` :: `test_verify_resume_data_display`
  - test_verify_resume_data_display depends on es_resume_submit_tc004
