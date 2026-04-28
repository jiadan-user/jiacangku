# zhaopin 无头多线程并行跑测

- 输出目录: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_122819`
- **线程池总墙钟**: 1345.57 s
- 各脚本 Markdown: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_122819/per_script_reports/`

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
| `test_ae_job_preferences_add_from_list.py` | 62.55 | 1 |
| `test_ae_job_preferences_edit.py` | 174.15 | 1 |
| `test_ae_jobs_list_location_and_add_pref.py` | 13.06 | 0 |
| `test_ae_jobs_list_search_and_filter.py` | 345.89 | 0 |
| `test_ae_resume_edit.py` | 284.35 | 1 |
| `test_es_jobs_detail_panel.py` | 534.69 | 1 |
| `test_es_jobs_list_search_and_filter.py` | 595.13 | 0 |
| `test_es_resume_add.py` | 862.85 | 1 |
| `test_es_resume_submit.py` | 465.41 | 1 |
| `test_sg_job_preferences.py` | 1345.55 | 1 |
| `test_sg_job_preferences_add_from_list.py` | 372.96 | 1 |
| `test_sg_jobs_list_search_and_filter.py` | 294.86 | 0 |
| `test_sg_jobs_pref_submit.py` | 314.28 | 0 |
| `test_zhaopin_job_preferences.py` | 189.17 | 1 |

---

## JUnit 汇总报告

- 生成时间: 2026-04-27 12:50:44 +0800
- JUnit 输入: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_122819/zhaopin_parallel_merged_junit.xml`
- 控制台日志: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/zhaopin/parallel_headless_run_20260427_122819/zhaopin_parallel_combined_console.log`

## 总耗时

- **pytest 汇总**: 2 failed, 3 passed
- **JUnit testsuite time 之和（近似）**: **5844.69 s**（若未并行，接近各用例 CPU 累计；与墙钟可能不同）
- 用例总数（JUnit 条目）: 343

## 各测试脚本耗时（按 JUnit 单条 time 汇总到文件）

| 脚本 | 耗时 (s) |
| --- | ---: |
| `test_cases/zhaopin/test_sg_job_preferences.py` | 1343.200 |
| `test_cases/zhaopin/test_es_resume_add.py` | 861.219 |
| `test_cases/zhaopin/test_es_jobs_list_search_and_filter.py` | 594.174 |
| `test_cases/zhaopin/test_es_jobs_detail_panel.py` | 532.962 |
| `test_cases/zhaopin/test_es_resume_submit.py` | 463.659 |
| `test_cases/zhaopin/test_sg_job_preferences_add_from_list.py` | 370.900 |
| `test_cases/zhaopin/test_ae_jobs_list_search_and_filter.py` | 344.484 |
| `test_cases/zhaopin/test_sg_jobs_pref_submit.py` | 313.030 |
| `test_cases/zhaopin/test_sg_jobs_list_search_and_filter.py` | 293.722 |
| `test_cases/zhaopin/test_ae_resume_edit.py` | 281.898 |
| `test_cases/zhaopin/test_zhaopin_job_preferences.py` | 186.281 |
| `test_cases/zhaopin/test_ae_job_preferences_edit.py` | 172.824 |
| `test_cases/zhaopin/test_ae_job_preferences_add_from_list.py` | 59.720 |
| `test_cases/zhaopin/test_ae_jobs_list_location_and_add_pref.py` | 12.105 |

## 统计摘要（按文件）

| 脚本 | passed | failed | skipped | error |
| --- | ---: | ---: | ---: | ---: |
| `test_cases/zhaopin/test_ae_job_preferences_add_from_list.py` | 3 | 2 | 0 | 0 |
| `test_cases/zhaopin/test_ae_job_preferences_edit.py` | 14 | 1 | 0 | 0 |
| `test_cases/zhaopin/test_ae_jobs_list_location_and_add_pref.py` | 2 | 0 | 0 | 0 |
| `test_cases/zhaopin/test_ae_jobs_list_search_and_filter.py` | 62 | 0 | 0 | 0 |
| `test_cases/zhaopin/test_ae_resume_edit.py` | 26 | 4 | 0 | 0 |
| `test_cases/zhaopin/test_es_jobs_detail_panel.py` | 27 | 1 | 0 | 0 |
| `test_cases/zhaopin/test_es_jobs_list_search_and_filter.py` | 65 | 0 | 0 | 0 |
| `test_cases/zhaopin/test_es_resume_add.py` | 39 | 2 | 0 | 0 |
| `test_cases/zhaopin/test_es_resume_submit.py` | 5 | 1 | 0 | 0 |
| `test_cases/zhaopin/test_sg_job_preferences.py` | 56 | 2 | 0 | 0 |
| `test_cases/zhaopin/test_sg_job_preferences_add_from_list.py` | 6 | 2 | 0 | 0 |
| `test_cases/zhaopin/test_sg_jobs_list_search_and_filter.py` | 7 | 0 | 0 | 0 |
| `test_cases/zhaopin/test_sg_jobs_pref_submit.py` | 9 | 0 | 0 | 0 |
| `test_cases/zhaopin/test_zhaopin_job_preferences.py` | 4 | 3 | 0 | 0 |

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
- `test_cases/zhaopin/test_ae_job_preferences_edit.py` :: `test_ae_edit_continue_submits_and_returns_to_return_url`
  - AssertionError: 仍停留在编辑页，当前 URL: https://aepub.58v5.cn/biz/en/jobPreference?returnUrl=https://ae.58v5.cn/en/city/cate-jobs/?iconSource=jobs
assert not True
 +  where True = is_url_contains('jobPreference')
 +    where is_url_contains = <pages.job_preference_page.JobPreferencePage object at 0x1064081c…
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
- `test_cases/zhaopin/test_es_jobs_detail_panel.py` :: `test_tc006_own_post_description_visible`
  - AssertionError: 详情面板应展示 Description 标题和内容段落，无折叠遮挡
assert False
- `test_cases/zhaopin/test_es_resume_add.py` :: `test_tc016_current_location_dropdown_select`
  - AssertionError: 选择 France 后 Current Location 字段应回显 'France'，实际: Spain
assert 'Spain' == 'France'
  
  - France
  + Spain
- `test_cases/zhaopin/test_es_resume_add.py` :: `test_tc035_job_function_panel_no_search_filter`
  - AssertionError: Job Function 应显示所选分类，实际: 
assert 'Testing & Quality Assurance' in ''
- `test_cases/zhaopin/test_es_resume_submit.py` :: `test_submit_resume_change_location`
  - playwright._impl._errors.TimeoutError: Page.wait_for_function: Timeout 120000ms exceeded.
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
- `test_cases/zhaopin/test_sg_job_preferences_add_from_list.py` :: `test_sg_add_pref_login_via_banner_should_redirect_to_add_page`
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

（无）
