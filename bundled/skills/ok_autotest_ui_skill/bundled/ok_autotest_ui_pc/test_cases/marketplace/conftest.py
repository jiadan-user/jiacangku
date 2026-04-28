# test_cases/marketplace/conftest.py
"""Marketplace 目录专用 fixture：同一测试模块内只执行一次「登录 + 直达 Marketplace 列表」。"""
import pytest

from pages.marketplace_list_page_ae import MarketplaceListPageAe
from test_cases.zhaopin.ae_login_helper import ensure_ae_logged_in


@pytest.fixture(scope="module")
def marketplace_list_session(page, config):
    """
    模块级复用：首次被任意用例请求时执行一次 ensure_ae_logged_in + navigate_to_marketplace_directly，
    后续同模块用例共享同一 Page 与当前列表页起点（仍可按用例再 goto / 筛选）。

    注意：
    - `test_ae_marketplace_list_page.py` 中 **TC001**（首页金刚位进入）仍使用裸 `page`，不依赖本 fixture。
    - **TC020**（未登录收藏）等需先清 Cookie 的用例仍使用裸 `page`，并在用例末尾自行 `ensure_ae_logged_in` 恢复。
    - 其他需特殊入口的用例请继续使用裸 `page`。
    """
    ensure_ae_logged_in(page, config)
    list_page = MarketplaceListPageAe(page)
    list_page.navigate_to_marketplace_directly(config["base_url"])
    yield page
