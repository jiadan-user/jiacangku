# Marketplace 目录全量执行报告

## 执行说明

- **目录**: `test_cases/marketplace/`（含 `test_ae_marketplace_detail_online_offline.py`、`test_ae_marketplace_list_page.py`、`test_ae_marketplace_sell_similar_v2.py`）
- **命令**: `pytest test_cases/marketplace/ -v --tb=short -r fEs --junit-xml=...`
- **环境**: `HEADLESS=true`
- **工作目录**: `bundled/skills/ok_autotest_ui_skill/bundled/ok_autotest_ui_pc`
- **生成时间**: 2026-04-20（以本机 pytest 输出为准）

## 整体结果与时长

| 指标 | 数值 |
|------|------|
| 用例总数 | 114 |
| 通过 | 110 |
| 失败 | 4 |
| 跳过 | 0 |
| 错误 | 0 |
| **pytest 汇总耗时** | **1370.04 s（约 22 分 50 秒）** |

说明：耗时取自 JUnit `testsuite` 的 `time` 属性，与控制台 `110 passed in 1370.04s` 一致。

**产物路径**

- JUnit: `test_cases/marketplace/marketplace_folder_run_junit.xml`
- 控制台日志: `test_cases/marketplace/marketplace_folder_run_console.log`
- 耗时摘要: `test_cases/marketplace/marketplace_folder_run_duration_sec.txt`

## 失败用例及原因

### 1. `test_ae_marketplace_detail_online_offline.py::test_tc013_online_detail_seller_verified_listings`

- **现象**: `AssertionError: 应展示卖家 listings 数量文案`
- **原因**: `detail_page.has_any_listings_count_visible()` 返回 `False`，页面上未检测到卖家 listings 数量相关文案（或选择器/展示与预期不一致）。

### 2. `test_ae_marketplace_detail_online_offline.py::test_tc024_offline_detail_seller_listings`

- **现象**: `AssertionError: 应展示卖家 listings 数量文案`
- **原因**: 同 TC013，`has_any_listings_count_visible()` 为 `False`（offline 详情场景）。

### 3. `test_ae_marketplace_sell_similar_v2.py::test_tc009_publish_page_inherits_product_attributes`

- **现象**: `AssertionError: 应该成功跳转到发布页（含新标签场景）`
- **原因**: `sell_similar_page.is_publish_page_loaded(timeout=15000)` 为 `False`，在超时时间内未判定进入发布页（可能为新标签页/路由检测与 headless 实际行为不一致）。

### 4. `test_ae_marketplace_sell_similar_v2.py::test_tc010_publish_page_inherits_description`

- **现象**: `AssertionError: 应该成功跳转到发布页（含新标签场景）`
- **原因**: 同 TC009，`is_publish_page_loaded` 未通过。

## 跳过用例及原因

本次运行 **无跳过用例**（JUnit `skipped="0"`）。若后续出现 `pytest.skip` / `@pytest.mark.skip`，可从 JUnit 中 `<skipped message="..."/>` 或控制台 `-r s` 汇总中查看原因。

## 结论

- 全目录 **114** 条用例在约 **22 分 50 秒** 内执行完毕；**110** 通过，**4** 失败，**0** 跳过。
- 失败集中在：详情页卖家 listings 数量展示（2 条）、Sell Similar 跳转发布页判定（2 条）。建议结合当时页面 DOM/文案变更或 `HEADLESS` 下新标签行为排查。
