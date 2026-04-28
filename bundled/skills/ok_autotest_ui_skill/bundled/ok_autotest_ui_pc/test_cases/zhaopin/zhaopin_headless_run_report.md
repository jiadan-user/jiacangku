# zhaopin 无头跑测汇总报告

- 生成时间: 2026-04-22 11:05:04 +0800
- JUnit 输入: `test_cases/zhaopin/zhaopin_headless_junit.xml`
- 控制台日志: `test_cases/zhaopin/zhaopin_headless_console.log`

## 总耗时

- **pytest 汇总**: 20 failed, 322 passed, 1 skipped
- **墙钟（time real）**: **4598.82 s**（约 76.65 min）
- 用例总数（JUnit 条目）: 343

## 各测试脚本耗时（按 JUnit 单条 time 汇总到文件）

| 脚本 | 耗时 (s) |
| --- | ---: |
| `test_cases/zhaopin/test_sg_job_preferences.py` | 907.042 |
| `test_cases/zhaopin/test_es_jobs_detail_panel.py` | 669.449 |
| `test_cases/zhaopin/test_es_jobs_list_search_and_filter.py` | 556.088 |
| `test_cases/zhaopin/test_es_resume_add.py` | 505.154 |
| `test_cases/zhaopin/test_ae_jobs_list_search_and_filter.py` | 396.716 |
| `test_cases/zhaopin/test_sg_jobs_list_search_and_filter.py` | 367.896 |
| `test_cases/zhaopin/test_sg_jobs_pref_submit.py` | 285.932 |
| `test_cases/zhaopin/test_ae_resume_edit.py` | 260.007 |
| `test_cases/zhaopin/test_ae_job_preferences_edit.py` | 182.661 |
| `test_cases/zhaopin/test_es_resume_submit.py` | 158.427 |
| `test_cases/zhaopin/test_sg_job_preferences_add_from_list.py` | 111.683 |
| `test_cases/zhaopin/test_ae_job_preferences_add_from_list.py` | 103.768 |
| `test_cases/zhaopin/test_zhaopin_job_preferences.py` | 64.881 |
| `test_cases/zhaopin/test_ae_jobs_list_location_and_add_pref.py` | 15.878 |

## 统计摘要（按文件）

| 脚本 | passed | failed | skipped | error |
| --- | ---: | ---: | ---: | ---: |
| `test_cases/zhaopin/test_ae_job_preferences_add_from_list.py` | 5 | 0 | 0 | 0 |
| `test_cases/zhaopin/test_ae_job_preferences_edit.py` | 15 | 0 | 0 | 0 |
| `test_cases/zhaopin/test_ae_jobs_list_location_and_add_pref.py` | 2 | 0 | 0 | 0 |
| `test_cases/zhaopin/test_ae_jobs_list_search_and_filter.py` | 62 | 0 | 0 | 0 |
| `test_cases/zhaopin/test_ae_resume_edit.py` | 30 | 0 | 0 | 0 |
| `test_cases/zhaopin/test_es_jobs_detail_panel.py` | 15 | 12 | 1 | 0 |
| `test_cases/zhaopin/test_es_jobs_list_search_and_filter.py` | 65 | 0 | 0 | 0 |
| `test_cases/zhaopin/test_es_resume_add.py` | 40 | 1 | 0 | 0 |
| `test_cases/zhaopin/test_es_resume_submit.py` | 6 | 0 | 0 | 0 |
| `test_cases/zhaopin/test_sg_job_preferences.py` | 58 | 0 | 0 | 0 |
| `test_cases/zhaopin/test_sg_job_preferences_add_from_list.py` | 8 | 0 | 0 | 0 |
| `test_cases/zhaopin/test_sg_jobs_list_search_and_filter.py` | 2 | 5 | 0 | 0 |
| `test_cases/zhaopin/test_sg_jobs_pref_submit.py` | 7 | 2 | 0 | 0 |
| `test_cases/zhaopin/test_zhaopin_job_preferences.py` | 7 | 0 | 0 | 0 |

## 失败用例

- `test_cases/zhaopin/test_es_jobs_detail_panel.py` :: `test_tc002_own_post_title_correct`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 20000ms exceeded.
Call log:
  - waiting for locator("a[href*=\"6522669642316510\"]").first to be visible
- `test_cases/zhaopin/test_es_jobs_detail_panel.py` :: `test_tc006_own_post_description_visible`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 20000ms exceeded.
Call log:
  - waiting for locator("a[href*=\"6522669642316510\"]").first to be visible
- `test_cases/zhaopin/test_es_jobs_detail_panel.py` :: `test_tc008_own_post_edit_navigates_to_edit_page`
  - AssertionError: 编辑页URL应包含帖子ID '6522669642316510'，实际: https://espub.58v5.cn/biz/en/publish/job?id=2046487355497406464
assert '6522669642316510' in 'https://espub.58v5.cn/biz/en/publish/job?id=2046487355497406464'
- `test_cases/zhaopin/test_es_jobs_detail_panel.py` :: `test_tc012_other_post_shows_contact_not_withdraw_edit`
  - playwright._impl._errors.TimeoutError: Page.wait_for_selector: Timeout 45000ms exceeded.
Call log:
  - waiting for locator("[class*=\"list-components-item-job-card\"] a[href*=\"/city-\"], [class*=\"JobListItem\"] a[href*=\"/city-\"], main [class*=\"list\"] a[href*=\"/city-\"][href*=\"cate-jobs\"]") …
- `test_cases/zhaopin/test_es_jobs_detail_panel.py` :: `test_tc013_other_post_contact_navigates_to_chat`
  - playwright._impl._errors.TimeoutError: Page.wait_for_selector: Timeout 45000ms exceeded.
Call log:
  - waiting for locator("[class*=\"list-components-item-job-card\"] a[href*=\"/city-\"], [class*=\"JobListItem\"] a[href*=\"/city-\"], main [class*=\"list\"] a[href*=\"/city-\"][href*=\"cate-jobs\"]") …
- `test_cases/zhaopin/test_es_jobs_detail_panel.py` :: `test_tc015_favourites_not_collected_shows_added_toast`
  - playwright._impl._errors.TimeoutError: Page.wait_for_selector: Timeout 45000ms exceeded.
Call log:
  - waiting for locator("[class*=\"list-components-item-job-card\"] a[href*=\"/city-\"], [class*=\"JobListItem\"] a[href*=\"/city-\"], main [class*=\"list\"] a[href*=\"/city-\"][href*=\"cate-jobs\"]") …
- `test_cases/zhaopin/test_es_jobs_detail_panel.py` :: `test_tc016_favourites_collected_shows_removed_toast`
  - playwright._impl._errors.TimeoutError: Page.wait_for_selector: Timeout 45000ms exceeded.
Call log:
  - waiting for locator("[class*=\"list-components-item-job-card\"] a[href*=\"/city-\"], [class*=\"JobListItem\"] a[href*=\"/city-\"], main [class*=\"list\"] a[href*=\"/city-\"][href*=\"cate-jobs\"]") …
- `test_cases/zhaopin/test_es_jobs_detail_panel.py` :: `test_tc018_share_shows_link_copied_toast`
  - playwright._impl._errors.TimeoutError: Page.wait_for_selector: Timeout 45000ms exceeded.
Call log:
  - waiting for locator("[class*=\"list-components-item-job-card\"] a[href*=\"/city-\"], [class*=\"JobListItem\"] a[href*=\"/city-\"], main [class*=\"list\"] a[href*=\"/city-\"][href*=\"cate-jobs\"]") …
- `test_cases/zhaopin/test_es_jobs_detail_panel.py` :: `test_tc020_new_tab_opens_post_detail_in_new_tab`
  - AssertionError: 新标签页URL应包含帖子ID '6522669642316510'，实际: https://es.58v5.cn/en/city/cate-client-sales-administration/hello-client-%26-sales-administration-2046487355497406464/
assert ('https://es.58v5.cn/en/city/cate-project-management/drast-back-6522669642316510/' in 'https://es.58v5.cn/en/city/cate-c…
- `test_cases/zhaopin/test_es_jobs_detail_panel.py` :: `test_tc021_switch_own_to_other_updates_buttons`
  - playwright._impl._errors.TimeoutError: Page.wait_for_selector: Timeout 45000ms exceeded.
Call log:
  - waiting for locator("[class*=\"list-components-item-job-card\"] a[href*=\"/city-\"], [class*=\"JobListItem\"] a[href*=\"/city-\"], main [class*=\"list\"] a[href*=\"/city-\"][href*=\"cate-jobs\"]") …
- `test_cases/zhaopin/test_es_jobs_detail_panel.py` :: `test_tc022_switch_other_to_own_updates_buttons`
  - playwright._impl._errors.TimeoutError: Page.wait_for_selector: Timeout 45000ms exceeded.
Call log:
  - waiting for locator("[class*=\"list-components-item-job-card\"] a[href*=\"/city-\"], [class*=\"JobListItem\"] a[href*=\"/city-\"], main [class*=\"list\"] a[href*=\"/city-\"][href*=\"cate-jobs\"]") …
- `test_cases/zhaopin/test_es_jobs_detail_panel.py` :: `test_tc026_unauthenticated_all_posts_show_contact`
  - playwright._impl._errors.TimeoutError: Page.wait_for_selector: Timeout 45000ms exceeded.
Call log:
  - waiting for locator("[class*=\"list-components-item-job-card\"] a[href*=\"/city-\"], [class*=\"JobListItem\"] a[href*=\"/city-\"], main [class*=\"list\"] a[href*=\"/city-\"][href*=\"cate-jobs\"]") …
- `test_cases/zhaopin/test_es_resume_add.py` :: `test_tc031_education_to_date_cannot_be_before_from`
  - AssertionError: Education To 早于 From 时，Step2 底部 Done 按钮应保持禁用
assert False
 +  where False = wait_until_step2_done_disabled(10000)
 +    where wait_until_step2_done_disabled = <pages.resume_add_page_es.ResumeAddPageEs object at 0x10679d3a0>.wait_until_step2_done_disabled
- `test_cases/zhaopin/test_sg_jobs_list_search_and_filter.py` :: `test_search_with_empty_keyword_should_stay_or_default`
  - AssertionError: 页面未正常加载
assert False
 +  where False = is_page_loaded()
 +    where is_page_loaded = <pages.jobs_list_page_sg.JobsListPageSG object at 0x1071736a0>.is_page_loaded
- `test_cases/zhaopin/test_sg_jobs_list_search_and_filter.py` :: `test_search_with_special_characters_should_handle`
  - playwright._impl._errors.TimeoutError: Locator.fill: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("input[placeholder*='Search']").first
- `test_cases/zhaopin/test_sg_jobs_list_search_and_filter.py` :: `test_search_with_long_text_should_handle`
  - playwright._impl._errors.TimeoutError: Locator.fill: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("input[placeholder*='Search']").first
- `test_cases/zhaopin/test_sg_jobs_list_search_and_filter.py` :: `test_location_filter_can_switch_city`
  - AssertionError: 页面未正常加载
assert False
 +  where False = is_page_loaded()
 +    where is_page_loaded = <pages.jobs_list_page_sg.JobsListPageSG object at 0x106484400>.is_page_loaded
- `test_cases/zhaopin/test_sg_jobs_list_search_and_filter.py` :: `test_location_filter_can_select_multiple`
  - AssertionError: 筛选未生效，当前URL: https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconSource=jobs
assert ('location' in 'https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconsource=jobs' or False)
 +  where 'https://sg.58v5.cn/en/city-singapore/cate-jobs/?iconsource=jobs' = <built-in method lower of str o…
- `test_cases/zhaopin/test_sg_jobs_pref_submit.py` :: `test_submit_with_all_fields_filled_should_success`
  - playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for get_by_role("checkbox", name="Singapore", exact=True)
- `test_cases/zhaopin/test_sg_jobs_pref_submit.py` :: `test_submit_without_job_functions_should_be_blocked`
  - playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for get_by_role("checkbox", name="Singapore", exact=True)

## 错误（setup/teardown 等）

（无）

## 跳过用例

- `test_cases/zhaopin/test_es_jobs_detail_panel.py` :: `test_tc014_other_post_detail_info_complete`
  - 当前列表无可点击的非本人职位卡片（结构与种子文案可能变化）：Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for get_by_text("software engineer").first
