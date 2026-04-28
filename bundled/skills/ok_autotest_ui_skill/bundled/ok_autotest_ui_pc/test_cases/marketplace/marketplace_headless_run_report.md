# marketplace 无头跑测汇总报告

- 生成时间: 2026-04-20 16:06:40 +0800
- **范围**: `test_cases/marketplace/` 下全部脚本（3 个文件，114 条用例）
- **无头开关**: `HEADLESS=true`（由 `test_cases/conftest.py` 中 `config` 覆盖 `browser.headless`）
- JUnit 输入: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/marketplace/marketplace_headless_junit.xml`
- 控制台日志: `/Users/wangyongli/Documents/okIdeaProject/qa-agent/bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc/test_cases/marketplace/marketplace_headless_console.log`

## 总耗时

- **pytest 汇总**: 27 failed, 85 passed, 2 skipped in 1478.52s
- **墙钟（time real）**: **1479.49 s**（约 24.66 min）

## 备注（跑测后代码修复）

- `test_tc039`～`test_tc060` 曾因 **docstring 内误写 `page = marketplace_list_session`** 导致 `NameError`，已在仓库中改为在 docstring **闭合后**赋值。若需与本报告数字完全一致，请在拉取修复后重新执行无头全量。
- 用例总数（JUnit 条目）: 114

## 各测试脚本耗时（按 JUnit 单条 time 汇总到文件）

| 脚本 | 耗时 (s) |
| --- | ---: |
| `test_cases/marketplace/test_ae_marketplace_sell_similar_v2.py` | 575.894 |
| `test_cases/marketplace/test_ae_marketplace_detail_online_offline.py` | 451.739 |
| `test_cases/marketplace/test_ae_marketplace_list_page.py` | 445.806 |

## 统计摘要（按文件）

| 脚本 | passed | failed | skipped | error |
| --- | ---: | ---: | ---: | ---: |
| `test_cases/marketplace/test_ae_marketplace_detail_online_offline.py` | 45 | 0 | 0 | 0 |
| `test_cases/marketplace/test_ae_marketplace_list_page.py` | 31 | 27 | 2 | 0 |
| `test_cases/marketplace/test_ae_marketplace_sell_similar_v2.py` | 9 | 0 | 0 | 0 |

## 失败用例

- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc009_price_range_filter`
  - AssertionError: 价格筛选后列表为空
assert 0 > 0
- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc010_multiple_filters_combination`
  - playwright._impl._errors.TimeoutError: Locator.fill: Timeout 30000ms exceeded.
Call log:
waiting for get_by_placeholder("Min")
- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc014_sort_with_filter_combination`
  - playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded.
Call log:
waiting for locator("button:has-text(\"确认\"), button:has-text(\"Confirm\")").first
- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc017_click_card_to_detail`
  - playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded.
Call log:
waiting for locator("[class*=\"list-components-item-card\"]").first
- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc018_favorite_item_when_logged_in`
  - AssertionError: 收藏后应停留在列表页，当前URL: https://ae.58v5.cn/en/city-abu-dhabi/cate-electronics/?keyword=%3Cscript%3Ealert%28%27xss%27%29%3C%2Fscript%3E&sortId=3
assert 'marketplace' in 'https://ae.58v5.cn/en/city-abu-dhabi/cate-electronics/?keyword=%3cscript%3ealert%28%27xss%27%29%3c%2fscript%3e&sortid=3'
…
- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc039_price_input_boundary`
  - NameError: name 'page' is not defined
- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc040_location_filter_cascade`
  - NameError: name 'page' is not defined
- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc041_filter_reset`
  - NameError: name 'page' is not defined
- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc042_filter_category_count`
  - NameError: name 'page' is not defined
- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc043_transaction_filter`
  - NameError: name 'page' is not defined
- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc044_filter_animation`
  - NameError: name 'page' is not defined
- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc045_sort_highest_price`
  - NameError: name 'page' is not defined
- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc046_sort_persistence_url`
  - NameError: name 'page' is not defined
- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc047_title_truncation`
  - NameError: name 'page' is not defined
- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc048_price_format`
  - NameError: name 'page' is not defined
- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc049_condition_labels`
  - NameError: name 'page' is not defined
- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc050_right_click_context_menu`
  - NameError: name 'page' is not defined
- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc051_skeleton_screen`
  - NameError: name 'page' is not defined
- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc052_pagination_strategy`
  - NameError: name 'page' is not defined
- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc053_pagination_boundary`
  - NameError: name 'page' is not defined
- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc054_error_handling_retry`
  - NameError: name 'page' is not defined
- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc055_image_lazy_loading`
  - NameError: name 'page' is not defined
- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc056_image_fallback`
  - NameError: name 'page' is not defined
- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc057_image_format_support`
  - NameError: name 'page' is not defined
- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc058_image_responsive`
  - NameError: name 'page' is not defined
- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc059_mobile_responsive`
  - NameError: name 'page' is not defined
- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc060_keyboard_navigation_accessibility`
  - NameError: name 'page' is not defined

## 错误（setup/teardown 等）

（无）

## 跳过用例

- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc015_item_card_information_check`
  - 商品列表为空，跳过此用例
- `test_cases/marketplace/test_ae_marketplace_list_page.py` :: `test_tc016_item_card_hover_effect`
  - 商品列表为空，跳过此用例
