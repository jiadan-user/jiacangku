# marketplace_post 跑测汇总报告

- 生成时间: 2026-04-20 23:38:40 +0800
- 范围: `test_cases/marketplace_post/` 下全部测试脚本（`test_ok_ae_marketplace_post_20260325.py`、`test_ok_ae_marketplace_post_draft_experience_20260407.py`）
- JUnit 输入: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/marketplace_post/marketplace_post_run_junit.xml`
- 控制台日志: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/marketplace_post/marketplace_post_run_console.log`

## 总耗时

- **pytest 汇总**: 127 failed, 37 passed, 11 skipped, 1 xfailed
- **pytest 会话时长（汇总行）**: **13861.32 s**（约 3:51:01）
- **墙钟（`/usr/bin/time -p` real）**: **13861.58 s**（约 231.03 min）
- 用例总数（JUnit 条目）: 176
- **pytest 退出码**: 1（存在失败用例）
- **说明**: 汇总中的 **1 xfailed** 对应用例 `test_tc011_set_non_first_as_main`（标记为预期失败，JUnit 中记为 `skipped type="pytest.xfail"`）；下文「跳过用例」第一节即为该条。

## 各测试脚本耗时（按 JUnit 单条 time 汇总到文件）

| 脚本 | 耗时 (s) |
| --- | ---: |
| `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` | 8165.366 |
| `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` | 5633.905 |

## 统计摘要（按文件）

| 脚本 | passed | failed | skipped | error |
| --- | ---: | ---: | ---: | ---: |
| `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` | 28 | 69 | 12 | 0 |
| `test_cases/marketplace_post/test_ok_ae_marketplace_post_draft_experience_20260407.py` | 9 | 58 | 0 | 0 |

## 失败用例

- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc001_full_publish_apple_phone`
  - TimeoutError: 未找到配送选项文案: Seller pays for postage
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc002_ai_generate_description`
  - Exception: 未找到 Write with AI 按钮
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc003_ai_suggest_category`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 10000ms exceeded.
Call log:
  - waiting for get_by_text("Suggested Categories") to be visible
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc004_draft_save_and_load`
  - playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for get_by_text("Save the draft")
    - locator resolved to <div class="draft-button ">Save the draft</div>
  - attempting click action
    2 × waiting for element to be visible, enabled and stable
…
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc009_delete_uploaded_image`
  - AssertionError: Modal should be closed after delete
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc010_delete_main_image_auto_reassign`
  - AssertionError: Modal should be closed after delete
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc012_modal_navigation`
  - AssertionError: Modal应显示3/5，实际：['5/9']
assert '3/5' in ['5/9']
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_price_field_validation[100000000-100000000-accept-tc052_large_amount]`
  - TimeoutError: 未找到配送选项文案: No delivery required
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc059_seller_pays_postage`
  - TimeoutError: 未找到配送选项文案: Seller pays for postage
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc060_buyer_pays_postage`
  - TimeoutError: 未找到配送选项文案: Buyer pays for postage
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc061_no_delivery_required`
  - TimeoutError: 未找到配送选项文案: No delivery required
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc062_arrange_pickup_toggle`
  - TimeoutError: 未找到配送选项文案: Seller pays for postage
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc055_select_all_details`
  - playwright._impl._errors.TimeoutError: Locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_text(re.compile(r"Excellent", re.IGNORECASE)).first
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc056_details_empty_submit`
  - TimeoutError: 未找到配送选项文案: No delivery required
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc057_details_reselect`
  - AssertionError: Excellent选项应保持选中状态
assert False
 +  where False = is_visible()
 +    where is_visible = <Locator frame=<Frame name= url='https://aepub.58v5.cn/biz/en/publish/classified'> selector='internal:text="Excellent"s'>.is_visible
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc058_storage_1tb_boundary`
  - playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for get_by_text("1 TB", exact=True)
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc064_default_location_dubai`
  - TimeoutError: 未找到配送选项文案: No delivery required
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc065_search_and_select_location`
  - playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("#location")
    - locator resolved to <input value="" type="text" id="location" autocomplete="off" class="form-control" placeholder="Set the location for your post."/>
  - attempting cl…
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc066_location_search_no_results`
  - playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("input[placeholder*='location']")
    - locator resolved to <input value="" type="text" id="location" autocomplete="off" class="form-control" placeholder="Set the location for your post.…
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc069_map_zoom_in`
  - playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("button[aria-label=\"Zoom in\"], button[title=\"Zoom in\"]").first
    - locator resolved to <button type="button" title="Zoom in" draggable="false" aria-label="Zoom in" class="gm-contro…
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc070_map_zoom_out`
  - playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("button[aria-label=\"Zoom out\"], button[title=\"Zoom out\"]").first
    - locator resolved to <button type="button" title="Zoom out" draggable="false" aria-label="Zoom out" class="gm-co…
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc019_title_with_emoji`
  - TimeoutError: 未找到配送选项文案: Seller pays for postage
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc020_title_one_character`
  - TimeoutError: 未找到配送选项文案: No delivery required
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc021_title_200_chars_boundary`
  - TimeoutError: 未找到配送选项文案: Buyer pays for postage
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc023_title_only_spaces`
  - TimeoutError: 未找到配送选项文案: No delivery required
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc024_title_with_html_xss`
  - TimeoutError: 未找到配送选项文案: Seller pays for postage
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc025_title_empty_validation`
  - TimeoutError: 未找到配送选项文案: No delivery required
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc032_ai_generate_description`
  - playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for get_by_text("Write with AI")
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc033_ai_undo_description`
  - playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for get_by_text("Write with AI")
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc026_description_12_chars_min`
  - TimeoutError: 未找到配送选项文案: No delivery required
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc027_description_11_chars_below_min`
  - TimeoutError: 未找到配送选项文案: Seller pays for postage
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc028_description_empty_validation`
  - TimeoutError: 未找到配送选项文案: Buyer pays for postage
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc029_description_only_spaces`
  - TimeoutError: 未找到配送选项文案: No delivery required
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc030_description_only_newlines`
  - TimeoutError: 未找到配送选项文案: Seller pays for postage
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc031_description_paste_large_text`
  - TimeoutError: 未找到配送选项文案: Buyer pays for postage
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc034_ai_shuffle_regenerate`
  - playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for get_by_text("Write with AI")
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc035_manual_edit_ai_description`
  - playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for get_by_text("Write with AI")
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc037_ai_generate_without_title`
  - playwright._impl._errors.TimeoutError: Locator.is_disabled: Timeout 30000ms exceeded.
Call log:
  - waiting for get_by_text("Write with AI")
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc038_ai_suggested_categories_display`
  - AssertionError: 应显示Suggested Categories标题
assert False
 +  where False = is_visible()
 +    where is_visible = <Locator frame=<Frame name= url='https://aepub.58v5.cn/biz/en/publish/classified'> selector='internal:text="Suggested Categories"i'>.is_visible
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc039_ai_categories_refresh_after_title`
  - playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("#content")
    - locator resolved to <textarea id="content" placeholder="" maxlength="10000" autocomplete="off" class="limited-textarea-input form-control"></textarea>
  - attempting cl…
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc040_click_suggested_category`
  - playwright._impl._errors.TimeoutError: Locator.inner_text: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("[data-recommend-item=\"true\"]").first
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc041_manual_browse_category_tree`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 20000ms exceeded.
Call log:
  - waiting for get_by_text(re.compile(r"^\s*Condition\s*$", re.IGNORECASE)).first to be visible
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc042_category_search_function`
  - AssertionError: 搜索结果应包含phone相关类别
assert ('phone' in 'search for category\nor browse to find a category' or 'Phone' in 'Search For Category\nOr browse to find a category')
 +  where 'search for category\nor browse to find a category' = <built-in method lower of str object at 0x103340f10>()
 +    wher…
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc044_category_empty_validation`
  - AssertionError: 应显示表单验证错误提示
assert False
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc045_switch_category_details_change`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 20000ms exceeded.
Call log:
  - waiting for get_by_text(re.compile(r"^\s*Condition\s*$", re.IGNORECASE)).first to be visible
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc092_clear_error_on_focus`
  - TimeoutError: 未找到配送选项文案: No delivery required
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc093_scroll_to_first_error`
  - AssertionError: 页面应滚动到第一个错误字段
assert 1054 < 500
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc102_switch_category_after_9_images`
  - playwright._impl._errors.TimeoutError: Locator.wait_for: Timeout 20000ms exceeded.
Call log:
  - waiting for get_by_text(re.compile(r"^\s*Condition\s*$", re.IGNORECASE)).first to be visible
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc099_chrome_compatibility`
  - TimeoutError: 未找到配送选项文案: Seller pays for postage
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc085_session_expired_submit`
  - TimeoutError: 未找到配送选项文案: No delivery required
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc095_multi_category_submission[category_path0-expected_details0]`
  - playwright._impl._errors.TimeoutError: Timeout 60000ms exceeded.
=========================== logs ===========================
waiting for navigation to "**/success**" until 'load'
============================================================
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc095_multi_category_submission[category_path1-expected_details1]`
  - Exception: 未找到 Books · Movies And Music 行
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc096_payment_notice_text_display`
  - AssertionError: 应显示付款说明文案
assert False
 +  where False = is_visible()
 +    where is_visible = <Locator frame=<Frame name= url='https://aepub.58v5.cn/biz/en/publish/classified'> selector='internal:text="Due to payment limitations imposed by suppliers"i'>.is_visible
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc046_price_normal_integer`
  - TimeoutError: 未找到配送选项文案: No delivery required
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc047_price_decimal`
  - TimeoutError: 未找到配送选项文案: No delivery required
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc048_price_zero`
  - TimeoutError: 未找到配送选项文案: No delivery required
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc072_map_toggle_fullscreen`
  - playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("[aria-label*='Fullscreen' i], [aria-label*='full screen' i], button:has-text('Fullscreen')").first
    - locator resolved to <button type="button" draggable="false" aria-pressed="false"…
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc073_submit_all_empty`
  - AssertionError: assert (False or False or 0 > 0)
 +  where False = is_title_error_visible(timeout=4000)
 +    where is_title_error_visible = <pages.marketplace_post_page_ae.MarketplacePostPage object at 0x103131be0>.is_title_error_visible
 +  and   False = is_description_error_visible(timeout=2000)
…
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc074_double_click_post`
  - TimeoutError: 未找到配送选项文案: No delivery required
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc075_only_images_submit`
  - assert (False or False)
 +  where False = is_title_error_visible(timeout=5000)
 +    where is_title_error_visible = <pages.marketplace_post_page_ae.MarketplacePostPage object at 0x1035e1280>.is_title_error_visible
 +  and   False = is_description_error_visible(timeout=3000)
 +    where is_descriptio…
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc076_no_image_submit`
  - TimeoutError: 未找到配送选项文案: No delivery required
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc077_save_empty_draft`
  - AssertionError: 空草稿保存应有成功反馈或 Draft 入口
assert False
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc078_save_partial_draft`
  - assert (False or 0 > 0)
 +  where False = is_draft_saved_alert_visible(timeout=10000)
 +    where is_draft_saved_alert_visible = <pages.marketplace_post_page_ae.MarketplacePostPage object at 0x10323dca0>.is_draft_saved_alert_visible
 +  and   0 = count()
 +    where count = <Locator frame=<Frame nam…
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc079_repeat_save_draft_overwrite`
  - AssertionError: assert (False or 0 > 0)
 +  where False = is_draft_saved_alert_visible(timeout=8000)
 +    where is_draft_saved_alert_visible = <pages.marketplace_post_page_ae.MarketplacePostPage object at 0x103538a30>.is_draft_saved_alert_visible
 +  and   0 = count()
 +    where count = <Locator f…
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc086_invalid_token_submit`
  - TimeoutError: 未找到配送选项文案: No delivery required
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc088_submit_network_timeout`
  - TimeoutError: 未找到配送选项文案: No delivery required
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc089_server_5xx_on_submit`
  - TimeoutError: 未找到配送选项文案: No delivery required
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc094_switch_language_while_filling`
  - playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("[data-testid*='language'], [aria-label*='language' i], button:has-text('EN'), a:has-text('العربية')").first
    - locator resolved to <button type="button" draggable="false" class="gm-s…
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc108_tab_order`
  - playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded.
Call log:
  - waiting for locator("#title")
    - locator resolved to <input value="" id="title" placeholder="" maxlength="200" autocomplete="off" class="limited-textarea-input form-control"/>
  - attempting click action…
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
  - waiting for locator("button.draft-entry") to be visible
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

（首条为 **xfail 预期失败**，其余为 `pytest.skip` 类跳过。）

- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc011_set_non_first_as_main`
  - **[xfail]** Bug: Set as Main操作未持久化到缩略图列表
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc014_oversized_image`
  - 当前构建未在前端拦截约15MB图片（计数器已增长），与 MD「应拒绝」不一致；已探测行为
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc018_corrupted_image`
  - 当前构建接受损坏图片文件（计数器已增长且无错误文案），与 MD 预期不一致；已探测行为
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc063_delivery_options_empty_validation`
  - 当前类别未显示Delivery Options，无法验证必填
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc036_polish_with_ai`
  - 当前环境未提供可点击的 Write with AI：未找到 Write with AI 按钮
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc015_upload_video_file`
  - 未检测到 ffmpeg，无法生成最小 MP4
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc016_upload_oversized_video`
  - 跳过 200MB+ 视频：设置 RUN_HEAVY_VIDEO=1 可在本地生成稀疏大文件跑测
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc017_upload_image_and_video`
  - 未检测到 ffmpeg，无法生成最小 MP4
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc067_locate_me_grant[geolocation_page0]`
  - Locate me 后 location 仍未变化（地图/地理服务或测试环境限制），跳过 TC067
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc100_safari_compatibility`
  - 设置 PLAYWRIGHT_WEBKIT_TC100=1 启用；需已执行 playwright install webkit
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc103_close_page_during_ai`
  - 当前环境无 Write with AI
- `test_cases/marketplace_post/test_ok_ae_marketplace_post_20260325.py` :: `test_tc105_modal_prev_next_boundary`
  - Modal 导航按钮选择器未匹配到
