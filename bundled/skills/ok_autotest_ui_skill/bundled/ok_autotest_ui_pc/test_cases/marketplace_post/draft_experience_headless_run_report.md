# AE Marketplace Post — 草稿体验优化（无头）跑测汇总

- 生成时间: 2026-04-20 11:44:01 +0800
- 脚本: `test_ok_ae_marketplace_post_draft_experience_20260407.py`
- 模式: `HEADLESS=true`（`conftest` 中 `config` fixture 覆盖 `_CONFIG['browser']['headless']`）
- JUnit 输入: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/marketplace_post/draft_experience_headless_junit.xml`
- 控制台日志: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/marketplace_post/draft_experience_headless_console.log`
- 墙钟秒数（同目录）: `draft_experience_headless_duration_sec.txt`（与 `time -p` 的 `real` 一致）

## 总耗时

- **pytest 汇总**: 58 failed, 9 passed
- **墙钟（time real）**: **5653.97 s**（约 94.23 min）
- 用例总数（JUnit 条目）: 67

## 各测试脚本耗时（按 JUnit 单条 time 汇总到文件）

| 脚本 | 耗时 (s) |
| --- | ---: |
| `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` | 5635.912 |

## 统计摘要（按文件）

| 脚本 | passed | failed | skipped | error |
| --- | ---: | ---: | ---: | ---: |
| `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` | 9 | 58 | 0 | 0 |

## 失败用例

- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc001_draft_entry_hidden_after_description_input`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc002_draft_entry_visible_with_drafts_empty_form`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc003_draft_count_matches_list`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc004_drafts_scoped_by_category`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc005_localstorage_ai_history_draft_entry`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc006_rapid_click_draft_entry_single_dialog`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc007_click_draft_opens_box`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc008_close_draft_box_with_close_button`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc009_close_without_selecting_draft_no_fill`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc010_reopen_draft_box_after_close`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc011_esc_closes_draft_box`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc012_click_outside_dialog_closes`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc013_open_close_three_cycles`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc014_close_and_immediate_reopen`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc015_close_x_vs_load_draft_url`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc016_list_shows_title_and_save_time`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc017_draft_list_newest_on_top`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc018_draft_list_scroll_shows_oldest_row`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc019_empty_draft_box_copy`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc020_draft_box_open_under_two_seconds`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 15000ms exceeded.
Call log:
waiting for locator("button.draft-entry") to be visible
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc021_draft_row_thumbnail_image_vs_text_only`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc022_load_draft_fills_form`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc023_dialog_closes_after_pick_draft`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc024_switch_between_two_drafts`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc025_after_load_no_draft_entry`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc026_edit_loaded_draft_save_same_id`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc027_delete_one_draft_decrements_counter`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc028_delete_keeps_draft_box_open`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc029_delete_cancel_keeps_row`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc030_last_draft_deleted_hides_entry`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc031_three_sequential_deletes`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc032_delete_b_keeps_a`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc033_delete_offline_then_online`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc034_delete_only_target`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc035_load_draft_then_publish`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc036_save_loaded_draft_same_id`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc037_first_save_toast`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc038_stay_on_publish_no_id_draft_saved_button`
  - playwright._impl._errors.TimeoutError: Timeout 30000ms exceeded while waiting for event "response"
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc039_after_toast_dismiss_still_draft_saved`
  - playwright._impl._errors.TimeoutError: Timeout 30000ms exceeded while waiting for event "response"
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc040_second_save_toast_after_edit`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc041_save_then_no_extra_request_on_reclick`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc042_edit_restores_save_the_draft`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc043_edit_revert_content_still_allows_save`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc044_slow_network_save_still_single_success`
  - playwright._impl._errors.TimeoutError: Timeout 30000ms exceeded while waiting for event "response"
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc045_rapid_triple_click_save_single_toast`
  - playwright._impl._errors.TimeoutError: Timeout 30000ms exceeded while waiting for event "response"
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc046_saved_no_edit_back_no_discard_dialog`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc047_saved_then_edit_back_shows_leave_dialog`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc049_close_leave_dialog_stays_on_form`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc052_offline_save_shows_error_then_retry_ok`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc053_save_api_500_shows_feedback`
  - playwright._impl._errors.TimeoutError: Timeout 25000ms exceeded while waiting for event "response"
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc054_title_max_two_hundred`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc056_draft_count_limit_blocked`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc057_second_tab_sees_new_draft_count`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc058_core_path_on_current_browser`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc059_english_copy_present`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc065_xss_title_and_content_stored_as_text`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc066_xss_extra_vectors`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` :: `test_tc067_end_to_end_draft_flow`
  - AssertionError: 既未捕获 easypost posts/publish 响应，也未在 UI 上观察到保存成功

## 错误（setup/teardown 等）

（无）

## 跳过用例

（无）
