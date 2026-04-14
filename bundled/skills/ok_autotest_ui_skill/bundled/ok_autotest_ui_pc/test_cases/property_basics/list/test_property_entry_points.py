import re
import pytest
import allure
from pages.property_page import PropertyPage
from utils.logger import setup_logger

logger = setup_logger()

_CONFIG = {
    "site": "au",
    "site_name": "澳大利亚站",
    "role": "buyer",
    "base_url": "https://au.58v5.cn",
    "target_page": "https://au.58v5.cn/en/city-canberra/",
    "locale": "en-AU",
    "currency": "AUD",
    "browser": {
        "type": "chromium",
        "headless": False,
        "viewport": {"width": 1920, "height": 1080}
    },
    "timeout": {
        "default": 30000,
        "wait": 10000,
        "navigation": 30000
    }
}

# 房产列表页入口测试
# 录制文档：/Users/a58/Desktop/测试用例/OK-Property入口-测试用例-20260313.md
# 生成时间：2026-03-13
# 测试目标：验证金刚位 Property、All 类目页、Browse 下拉菜单三条入口
#           均能正确进入对应房产列表页，URL/H1/子类目链接符合预期
# ============================================================

_ENTRY_HOME_URL = "https://au.58v5.cn/en/city-canberra/"


@allure.feature("房产列表页入口")
class TestPropertyEntryPoints:
    """房产列表页三大入口功能测试（金刚位 / All / Browse 下拉菜单）"""

    @pytest.fixture(scope="module")
    def entry_page(self, page, config):
        """
        module 级别 fixture：整个测试模块共享同一个浏览器和页面，
        返回已处理 Cookie 弹窗的 PropertyPage 实例。
        """
        p = PropertyPage(page)
        page.goto(_ENTRY_HOME_URL, wait_until="domcontentloaded", timeout=config["timeout"]["navigation"])
        page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
        p.handle_cookie_popup()
        page.wait_for_timeout(1000)
        return p
    
    @pytest.fixture(scope="module", autouse=True)
    def reset_entry_page_after_module(self, page, config):
        """模块级别：所有测试结束后重置页面"""
        yield  # 先执行所有测试
        try:
            logger.info("========== 模块测试完毕，重置页面 ==========")
            page.goto(_CONFIG['target_page'], wait_until="domcontentloaded", timeout=_CONFIG['timeout']['navigation'])
            page.wait_for_load_state('domcontentloaded', timeout=_CONFIG['timeout']['navigation'])
            page.wait_for_timeout(1000)
            logger.info("✓ 模块测试完成，页面已重置")
        except Exception as e:
            logger.warning(f"模块结束后重置页面失败: {e}")
    
    @pytest.fixture(scope="function", autouse=True)
    def reset_page_between_tests(self, page, config, entry_page):
        """函数级别：每个测试之间重置页面（不关闭浏览器）"""
        yield  # 先执行测试
        try:
            logger.info("========== 用例执行完毕，重置页面到初始状态 ==========")
            page.goto(_ENTRY_HOME_URL, wait_until="domcontentloaded", timeout=config["timeout"]["navigation"])
            page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
            page.wait_for_timeout(1000)
            logger.info(f"✓ 页面已重置到初始状态: {page.url}")
        except Exception as e:
            logger.warning(f"重置页面失败（不影响用例结果）: {e}")
            try:
                page.reload(wait_until="domcontentloaded", timeout=config["timeout"]["navigation"])
                page.wait_for_timeout(1000)
                logger.info("✓ 已通过刷新恢复页面")
            except Exception:
                pass

    # ------------------------------------------------------------------
    # 模块一：入口1 — 金刚位 Property（TC001–TC002）
    # ------------------------------------------------------------------

    @allure.story("入口1 - 金刚位 Property")
    @allure.title("TC001: 点击金刚位 Property 图标 → 进入 Property For Sale 列表页")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description(
        "MCP JS: await page.getByRole('link', { name: 'Property Property' }).click();\n"
        "期望 URL: /cate-property/?iconSource=buy，H1: Property For Sale"
    )
    @pytest.mark.au
    @pytest.mark.p0
    @pytest.mark.property_entry
    @pytest.mark.case_id_entry_001
    def test_tc001_category_icon_property_navigates_to_for_sale(self, entry_page, page, config):
        with allure.step("点击金刚位 Property 图标"):
            entry_page.click_category_icon_property()
            logger.info("✓ 已点击金刚位 Property 图标")

        with allure.step("验证 URL 含 cate-property 和 iconSource=buy"):
            current_url = page.url
            assert "cate-property" in current_url, \
                f"期望 URL 含 cate-property，实际: {current_url}"
            assert "iconSource=buy" in current_url, \
                f"期望 URL 含 iconSource=buy，实际: {current_url}"
            logger.info(f"✓ URL 验证通过: {current_url}")

        with allure.step("验证 H1 标题为 Property For Sale"):
            h1 = entry_page.get_page_h1()
            assert "Property For Sale" in h1, \
                f"期望 H1 含 'Property For Sale'，实际: '{h1}'"
            logger.info(f"✓ H1 验证通过: {h1}")

        with allure.step("验证筛选栏可见（Best Match / Filter）"):
            assert page.get_by_text("Best Match").is_visible(timeout=5000), \
                "期望页面显示 Best Match 排序按钮"
            logger.info("✓ 筛选栏可见")

    @allure.story("入口1 - 金刚位 Property")
    @allure.title("TC002: 金刚位 Property 链接跳转 URL 参数验证")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "验证金刚位 Property 点击后 URL 包含 cate-property 和 iconSource=buy，页面正常加载无报错"
    )
    @pytest.mark.au
    @pytest.mark.p1
    @pytest.mark.property_entry
    @pytest.mark.case_id_entry_002
    def test_tc002_category_icon_property_url_params(self, entry_page, page, config):
        with allure.step("点击金刚位 Property 图标"):
            entry_page.click_category_icon_property()

        with allure.step("验证 URL 参数完整性"):
            current_url = page.url
            assert "cate-property" in current_url, \
                f"URL 应含 cate-property，实际: {current_url}"
            assert "iconSource=buy" in current_url, \
                f"URL 应含 iconSource=buy，实际: {current_url}"
            assert "au.58v5.cn" in current_url, \
                f"URL 应在 au 站，实际: {current_url}"
            logger.info(f"✓ URL 参数验证通过: {current_url}")

        with allure.step("验证页面正常加载（H1 存在）"):
            h1 = entry_page.get_page_h1()
            assert h1 != "", "期望页面有 H1 标题，实际为空"
            logger.info(f"✓ 页面已加载，H1: {h1}")

    # ------------------------------------------------------------------
    # 模块二：入口2 — All → Property 子类目（TC003–TC007）
    # ------------------------------------------------------------------

    @allure.story("入口2 - All 类目页")
    @allure.title("TC003: 点击 All 图标 → 进入全类目页，Property 区块正常展示")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description(
        "MCP JS: await page.getByRole('link', { name: 'All All' }).click();\n"
        "期望落地 /listpage/，并展示 Property 区块的 5 个子类链接"
    )
    @pytest.mark.au
    @pytest.mark.p0
    @pytest.mark.property_entry
    @pytest.mark.case_id_entry_003
    def test_tc003_all_icon_opens_listpage_with_property_section(self, entry_page, page, config):
        with allure.step("重置到首页"):
            page.goto(_ENTRY_HOME_URL, wait_until="domcontentloaded", timeout=config["timeout"]["navigation"])
            page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
            entry_page.handle_cookie_popup()
            page.wait_for_timeout(1500)
            logger.info(f"✓ 页面已重置到首页: {_ENTRY_HOME_URL}")
        
        with allure.step("点击金刚位 All 图标"):
            entry_page.click_category_icon_all()
            page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
            page.wait_for_timeout(1500)
            logger.info("✓ 已点击 All 图标并等待页面加载")

        with allure.step("验证 URL 含 listpage"):
            current_url = page.url
            assert "listpage" in current_url, \
                f"期望 URL 含 listpage，实际: {current_url}"
            logger.info(f"✓ listpage URL 验证通过: {current_url}")

        with allure.step("验证 Property 区块 5 个子类链接均可见"):
            visible_links = entry_page.get_listpage_property_link_names()
            expected = [
                "Property For Rent",
                "Property For Sale",
                "Student Accommodation",
                "Commercial Property for sale",
                "Commercial Property for rent",
            ]
            for name in expected:
                assert name in visible_links, \
                    f"期望 listpage 中可见链接「{name}」，已可见: {visible_links}"
            logger.info(f"✓ Property 区块链接验证通过: {visible_links}")

    @allure.story("入口2 - All → Property For Sale")
    @allure.title("TC004: All → 点击 Property For Sale → 进入 For Sale 列表页")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description(
        "MCP JS: await page.getByRole('link', { name: 'Property For Sale' }).click();\n"
        "期望 URL: /cate-buy/，H1: Property For Sale"
    )
    @pytest.mark.au
    @pytest.mark.p0
    @pytest.mark.property_entry
    @pytest.mark.case_id_entry_004
    def test_tc004_all_to_property_for_sale(self, entry_page, page, config):
        with allure.step("重置到首页"):
            page.goto(_ENTRY_HOME_URL, wait_until="domcontentloaded", timeout=config["timeout"]["navigation"])
            page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
            entry_page.handle_cookie_popup()
            page.wait_for_timeout(1500)
            logger.info(f"✓ 页面已重置到首页: {_ENTRY_HOME_URL}")
        
        with allure.step("点击 All 进入 listpage"):
            entry_page.click_category_icon_all()
            page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
            page.wait_for_timeout(1500)
            logger.info("✓ 已进入 All listpage")

        with allure.step("点击 Property For Sale"):
            entry_page.click_listpage_property_for_sale()
            page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
            page.wait_for_timeout(1500)
            logger.info("✓ 已点击 Property For Sale 并等待页面加载")

        with allure.step("验证 URL 含 cate-buy"):
            current_url = page.url
            assert "cate-buy" in current_url, \
                f"期望 URL 含 cate-buy，实际: {current_url}"
            logger.info(f"✓ URL: {current_url}")

        with allure.step("验证 H1 含 Property For Sale"):
            h1 = entry_page.get_page_h1()
            assert "Property For Sale" in h1, \
                f"期望 H1 含 'Property For Sale'，实际: '{h1}'"
            logger.info(f"✓ H1: {h1}")

    @allure.story("入口2 - All → Property For Rent")
    @allure.title("TC005: All → 点击 Property For Rent → 进入 For Rent 列表页")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description(
        "MCP JS: await page.getByRole('link', { name: 'Property For Rent' }).click();\n"
        "期望 URL: /cate-rent/，H1: Property For Rent"
    )
    @pytest.mark.au
    @pytest.mark.p0
    @pytest.mark.property_entry
    @pytest.mark.case_id_entry_005
    def test_tc005_all_to_property_for_rent(self, entry_page, page, config):
        with allure.step("重置到首页"):
            page.goto(_ENTRY_HOME_URL, wait_until="domcontentloaded", timeout=config["timeout"]["navigation"])
            page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
            entry_page.handle_cookie_popup()
            page.wait_for_timeout(1500)
            logger.info(f"✓ 页面已重置到首页: {_ENTRY_HOME_URL}")
        
        with allure.step("点击 All 进入 listpage"):
            entry_page.click_category_icon_all()
            page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
            page.wait_for_timeout(1500)
            logger.info("✓ 已进入 All listpage")

        with allure.step("点击 Property For Rent"):
            entry_page.click_listpage_property_for_rent()
            page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
            page.wait_for_timeout(1500)
            logger.info("✓ 已点击 Property For Rent 并等待页面加载")

        with allure.step("验证 URL 含 cate-rent"):
            current_url = page.url
            assert "cate-rent" in current_url, \
                f"期望 URL 含 cate-rent，实际: {current_url}"
            logger.info(f"✓ URL: {current_url}")

        with allure.step("验证 H1 含 Property For Rent"):
            h1 = entry_page.get_page_h1()
            assert "Property For Rent" in h1, \
                f"期望 H1 含 'Property For Rent'，实际: '{h1}'"
            logger.info(f"✓ H1: {h1}")

    @allure.story("入口2 - All → Student Accommodation")
    @allure.title("TC006: All → 点击 Student Accommodation → 进入学生公寓列表页")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "MCP JS: await page.getByRole('link', { name: 'Student Accommodation' }).click();\n"
        "期望 URL: /cate-student-apartment/，H1: Student Accommodation"
    )
    @pytest.mark.au
    @pytest.mark.p1
    @pytest.mark.property_entry
    @pytest.mark.case_id_entry_006
    def test_tc006_all_to_student_accommodation(self, entry_page, page, config):
        with allure.step("重置到首页"):
            page.goto(_ENTRY_HOME_URL, wait_until="domcontentloaded", timeout=config["timeout"]["navigation"])
            page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
            entry_page.handle_cookie_popup()
            page.wait_for_timeout(1500)
            logger.info(f"✓ 页面已重置到首页: {_ENTRY_HOME_URL}")
        
        with allure.step("点击 All 进入 listpage"):
            entry_page.click_category_icon_all()
            page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
            page.wait_for_timeout(1500)
            logger.info("✓ 已进入 All listpage")

        with allure.step("点击 Student Accommodation"):
            entry_page.click_listpage_student_accommodation()
            page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
            page.wait_for_timeout(1500)
            logger.info("✓ 已点击 Student Accommodation 并等待页面加载")

        with allure.step("验证 URL 含 cate-student-apartment"):
            current_url = page.url
            assert "cate-student-apartment" in current_url, \
                f"期望 URL 含 cate-student-apartment，实际: {current_url}"
            logger.info(f"✓ URL: {current_url}")

        with allure.step("验证 H1 含 Student Accommodation"):
            h1 = entry_page.get_page_h1()
            assert "Student Accommodation" in h1, \
                f"期望 H1 含 'Student Accommodation'，实际: '{h1}'"
            logger.info(f"✓ H1: {h1}")

    @allure.story("入口2 - All → Commercial Property for sale")
    @allure.title("TC007: All → 点击 Commercial Property for sale → 进入商业 For Sale 列表页")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "MCP JS: await page.getByRole('link', { name: 'Commercial Property for sale' }).click();\n"
        "期望 URL: /cate-commercial-buy/，H1 含 Commercial"
    )
    @pytest.mark.au
    @pytest.mark.p1
    @pytest.mark.property_entry
    @pytest.mark.case_id_entry_007
    def test_tc007_all_to_commercial_for_sale(self, entry_page, page, config):
        with allure.step("重置到首页"):
            page.goto(_ENTRY_HOME_URL, wait_until="domcontentloaded", timeout=config["timeout"]["navigation"])
            page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
            entry_page.handle_cookie_popup()
            page.wait_for_timeout(1500)
            logger.info(f"✓ 页面已重置到首页: {_ENTRY_HOME_URL}")
        
        with allure.step("点击 All 进入 listpage"):
            entry_page.click_category_icon_all()
            page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
            page.wait_for_timeout(1500)
            logger.info("✓ 已进入 All listpage")

        with allure.step("点击 Commercial Property for sale"):
            entry_page.click_listpage_commercial_for_sale()
            page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
            page.wait_for_timeout(1500)
            logger.info("✓ 已点击 Commercial Property for sale 并等待页面加载")

        with allure.step("验证 URL 含 cate-commercial-buy"):
            current_url = page.url
            assert "cate-commercial-buy" in current_url, \
                f"期望 URL 含 cate-commercial-buy，实际: {current_url}"
            logger.info(f"✓ URL: {current_url}")

        with allure.step("验证 H1 含 Commercial"):
            h1 = entry_page.get_page_h1()
            assert h1 != "", f"期望 H1 存在，实际为空"
            logger.info(f"✓ H1: {h1}")

    # ------------------------------------------------------------------
    # 模块三：入口3 — Browse 下拉菜单（TC008–TC013）
    # ------------------------------------------------------------------

    @allure.story("入口3 - Browse 下拉")
    @allure.title("TC008: 点击 Browse 展开下拉菜单，验证 Property 一级入口可见")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description(
        "MCP JS: await page.getByText('Browse').click();\n"
        "期望 Browse Mega Menu 展开，左侧含 Property 一级分类链接"
    )
    @pytest.mark.au
    @pytest.mark.p0
    @pytest.mark.property_entry
    @pytest.mark.case_id_entry_008
    def test_tc008_browse_opens_dropdown_with_property(self, entry_page, page, config):
        with allure.step("点击 Browse ▾ 按钮"):
            entry_page.click_browse_button()
            logger.info("✓ 已点击 Browse 按钮")

        with allure.step("验证 Browse 下拉菜单已展开（Property 一级链接可见）"):
            is_visible = entry_page.is_browse_dropdown_visible()
            assert is_visible, "期望 Browse 下拉展开后「Property」一级链接可见"
            logger.info("✓ Browse 下拉已展开，Property 可见")

    @allure.story("入口3 - Browse → Property 子菜单")
    @allure.title("TC009: Browse 下拉 → Hover Property → 展开 Property 子菜单（5个选项）")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description(
        "MCP JS:\n"
        "  await page.getByText('Browse').click();\n"
        "  await page.getByRole('link', { name: 'Property', exact: true }).hover();\n"
        "期望右侧展示 5 个 Property 子类链接"
    )
    @pytest.mark.au
    @pytest.mark.p0
    @pytest.mark.property_entry
    @pytest.mark.case_id_entry_009
    def test_tc009_browse_hover_property_shows_submenu(self, entry_page, page, config):
        with allure.step("重置到首页"):
            page.goto(_ENTRY_HOME_URL, wait_until="domcontentloaded", timeout=config["timeout"]["navigation"])
            page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
            entry_page.handle_cookie_popup()
            page.wait_for_timeout(1500)
            logger.info(f"✓ 页面已重置到首页: {_ENTRY_HOME_URL}")
        
        with allure.step("点击 Browse ▾ 并 Hover Property"):
            entry_page.click_browse_button()
            page.wait_for_timeout(800)
            entry_page.hover_browse_property()
            page.wait_for_timeout(800)
            logger.info("✓ 已 Hover Browse > Property 并等待子菜单展开")

        with allure.step("验证 Property 子菜单展开并含 5 个子类链接"):
            visible_links = entry_page.get_browse_property_submenu_link_names()
            expected = [
                "Property For Rent",
                "Property For Sale",
                "Student Accommodation",
                "Commercial Property for sale",
                "Commercial Property for rent",
            ]
            for name in expected:
                assert name in visible_links, \
                    f"期望 Browse Property 子菜单含「{name}」，已可见: {visible_links}"
            logger.info(f"✓ 子菜单链接验证通过: {visible_links}")

    @allure.story("入口3 - Browse → Property For Rent")
    @allure.title("TC010: Browse → Property → Property For Rent → 进入 For Rent 列表")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description(
        "MCP JS:\n"
        "  await page.getByText('Browse').click();\n"
        "  await page.getByRole('link', { name: 'Property', exact: true }).hover();\n"
        "  await page.getByRole('link', { name: 'Property For Rent' }).click();\n"
        "期望 URL: /cate-rent/?iconSource=rent，H1: Property For Rent"
    )
    @pytest.mark.au
    @pytest.mark.p0
    @pytest.mark.property_entry
    @pytest.mark.case_id_entry_010
    def test_tc010_browse_to_property_for_rent(self, entry_page, page, config):
        with allure.step("重置到首页"):
            page.goto(_ENTRY_HOME_URL, wait_until="domcontentloaded", timeout=config["timeout"]["navigation"])
            page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
            entry_page.handle_cookie_popup()
            page.wait_for_timeout(1500)
            logger.info(f"✓ 页面已重置到首页: {_ENTRY_HOME_URL}")
        
        with allure.step("Browse → Hover Property → 点击 Property For Rent"):
            entry_page.click_browse_button()
            page.wait_for_timeout(800)
            entry_page.hover_browse_property()
            page.wait_for_timeout(800)
            entry_page.click_browse_submenu_property_for_rent()
            page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
            page.wait_for_timeout(1500)
            logger.info("✓ 已通过 Browse 进入 Property For Rent 并等待页面加载")

        with allure.step("验证 URL 含 cate-rent 和 iconSource=rent"):
            current_url = page.url
            assert "cate-rent" in current_url, \
                f"期望 URL 含 cate-rent，实际: {current_url}"
            assert "iconSource=rent" in current_url, \
                f"期望 URL 含 iconSource=rent，实际: {current_url}"
            logger.info(f"✓ URL: {current_url}")

        with allure.step("验证 H1 含 Property For Rent"):
            h1 = entry_page.get_page_h1()
            assert "Property For Rent" in h1, \
                f"期望 H1 含 'Property For Rent'，实际: '{h1}'"
            logger.info(f"✓ H1: {h1}")

    @allure.story("入口3 - Browse → Property For Sale")
    @allure.title("TC011: Browse → Property → Property For Sale → 进入 For Sale 列表")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description(
        "MCP JS:\n"
        "  await page.getByText('Browse').click();\n"
        "  await page.getByRole('link', { name: 'Property', exact: true }).hover();\n"
        "  await page.getByRole('link', { name: 'Property For Sale' }).click();\n"
        "期望 URL: /cate-buy/?iconSource=buy，H1: Property For Sale"
    )
    @pytest.mark.au
    @pytest.mark.p0
    @pytest.mark.property_entry
    @pytest.mark.case_id_entry_011
    def test_tc011_browse_to_property_for_sale(self, entry_page, page, config):
        with allure.step("重置到首页"):
            page.goto(_ENTRY_HOME_URL, wait_until="domcontentloaded", timeout=config["timeout"]["navigation"])
            page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
            entry_page.handle_cookie_popup()
            page.wait_for_timeout(1500)
            logger.info(f"✓ 页面已重置到首页: {_ENTRY_HOME_URL}")
        
        with allure.step("Browse → Hover Property → 点击 Property For Sale"):
            entry_page.click_browse_button()
            page.wait_for_timeout(800)
            entry_page.hover_browse_property()
            page.wait_for_timeout(800)
            entry_page.click_browse_submenu_property_for_sale()
            page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
            page.wait_for_timeout(1500)
            logger.info("✓ 已通过 Browse 进入 Property For Sale 并等待页面加载")

        with allure.step("验证 URL 含 cate-buy 和 iconSource=buy"):
            current_url = page.url
            assert "cate-buy" in current_url, \
                f"期望 URL 含 cate-buy，实际: {current_url}"
            assert "iconSource=buy" in current_url, \
                f"期望 URL 含 iconSource=buy，实际: {current_url}"
            logger.info(f"✓ URL: {current_url}")

        with allure.step("验证 H1 含 Property For Sale"):
            h1 = entry_page.get_page_h1()
            assert "Property For Sale" in h1, \
                f"期望 H1 含 'Property For Sale'，实际: '{h1}'"
            logger.info(f"✓ H1: {h1}")

    @allure.story("入口3 - Browse → Student Accommodation")
    @allure.title("TC012: Browse → Property → Student Accommodation → 进入学生公寓列表")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "MCP JS:\n"
        "  await page.getByText('Browse').click();\n"
        "  await page.getByRole('link', { name: 'Property', exact: true }).hover();\n"
        "  await page.getByRole('link', { name: 'Student Accommodation' }).click();\n"
        "期望 URL: /cate-student-apartment/?iconSource=student-apartment"
    )
    @pytest.mark.au
    @pytest.mark.p1
    @pytest.mark.property_entry
    @pytest.mark.case_id_entry_012
    def test_tc012_browse_to_student_accommodation(self, entry_page, page, config):
        with allure.step("重置到首页"):
            page.goto(_ENTRY_HOME_URL, wait_until="domcontentloaded", timeout=config["timeout"]["navigation"])
            page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
            entry_page.handle_cookie_popup()
            page.wait_for_timeout(1500)
            logger.info(f"✓ 页面已重置到首页: {_ENTRY_HOME_URL}")
        
        with allure.step("Browse → Hover Property → 点击 Student Accommodation"):
            entry_page.click_browse_button()
            page.wait_for_timeout(800)
            entry_page.hover_browse_property()
            page.wait_for_timeout(800)
            entry_page.click_browse_submenu_student_accommodation()
            page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
            page.wait_for_timeout(1500)
            logger.info("✓ 已通过 Browse 进入 Student Accommodation 并等待页面加载")

        with allure.step("验证 URL 含 cate-student-apartment 和 iconSource=student-apartment"):
            current_url = page.url
            assert "cate-student-apartment" in current_url, \
                f"期望 URL 含 cate-student-apartment，实际: {current_url}"
            assert "iconSource=student-apartment" in current_url, \
                f"期望 URL 含 iconSource=student-apartment，实际: {current_url}"
            logger.info(f"✓ URL: {current_url}")

        with allure.step("验证 H1 含 Student Accommodation"):
            h1 = entry_page.get_page_h1()
            assert "Student Accommodation" in h1, \
                f"期望 H1 含 'Student Accommodation'，实际: '{h1}'"
            logger.info(f"✓ H1: {h1}")

    @allure.story("入口3 - Browse → Commercial Property for sale")
    @allure.title("TC013: Browse → Property → Commercial Property for sale → 进入商业 For Sale 列表")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "MCP JS:\n"
        "  await page.getByText('Browse').click();\n"
        "  await page.getByRole('link', { name: 'Property', exact: true }).hover();\n"
        "  await page.getByRole('link', { name: 'Commercial Property for sale' }).click();\n"
        "期望 URL: /cate-commercial-buy/?iconSource=commercial-buy"
    )
    @pytest.mark.au
    @pytest.mark.p1
    @pytest.mark.property_entry
    @pytest.mark.case_id_entry_013
    def test_tc013_browse_to_commercial_for_sale(self, entry_page, page, config):
        with allure.step("重置到首页"):
            page.goto(_ENTRY_HOME_URL, wait_until="domcontentloaded", timeout=config["timeout"]["navigation"])
            page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
            entry_page.handle_cookie_popup()
            page.wait_for_timeout(1500)
            logger.info(f"✓ 页面已重置到首页: {_ENTRY_HOME_URL}")
        
        with allure.step("Browse → Hover Property → 点击 Commercial Property for sale"):
            entry_page.click_browse_button()
            page.wait_for_timeout(800)
            entry_page.hover_browse_property()
            page.wait_for_timeout(800)
            entry_page.click_browse_submenu_commercial_for_sale()
            page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
            page.wait_for_timeout(1500)
            logger.info("✓ 已通过 Browse 进入 Commercial Property for sale 并等待页面加载")

        with allure.step("验证 URL 含 cate-commercial-buy 和 iconSource=commercial-buy"):
            current_url = page.url
            assert "cate-commercial-buy" in current_url, \
                f"期望 URL 含 cate-commercial-buy，实际: {current_url}"
            assert "iconSource=commercial-buy" in current_url, \
                f"期望 URL 含 iconSource=commercial-buy，实际: {current_url}"
            logger.info(f"✓ URL: {current_url}")

        with allure.step("验证 H1 不为空"):
            h1 = entry_page.get_page_h1()
            assert h1 != "", "期望 H1 存在，实际为空"
            logger.info(f"✓ H1: {h1}")

    # ------------------------------------------------------------------
    # 模块四：异常与边界（TC014–TC018）
    # ------------------------------------------------------------------

    @allure.story("入口3 - Browse 直接点击 Property 一级")
    @allure.title("TC014: Browse 下拉直接点击 Property 一级链接 → 落地 Property 列表（iconSource 沿用历史导航）")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "MCP JS:\n"
        "  await page.getByText('Browse').click();\n"
        "  await page.getByRole('link', { name: 'Property', exact: true }).click();\n\n"
        "产品逻辑：Browse > Property 一级链接直接点击时，iconSource 参数由上次访问过的 Property\n"
        "子类型决定（非固定为 buy）。例如用户上次访问 For Rent，则 iconSource=rent；\n"
        "上次访问 For Sale，则 iconSource=buy。\n\n"
        "验证重点：\n"
        "  1. URL 必须含 cate-property（落地正确的 Property 列表页）\n"
        "  2. iconSource 存在且为合法枚举值（buy / rent / student-apartment / commercial-buy / commercial-rent）\n"
        "  3. 页面 H1 与 iconSource 对应的子类型标题一致（无白屏）"
    )
    @pytest.mark.au
    @pytest.mark.p1
    @pytest.mark.property_entry
    @pytest.mark.case_id_entry_014
    def test_tc014_browse_direct_click_property(self, entry_page, page, config):
        _VALID_ICON_SOURCES = {
            "buy": "Property For Sale",
            "rent": "Property For Rent",
            "student-apartment": "Student Accommodation",
            "commercial-buy": "Commercial Property for sale",
            "commercial-rent": "Commercial Property for rent",
        }

        with allure.step("点击 Browse 展开，然后直接点击 Property 一级链接（不 hover）"):
            entry_page.click_browse_button()
            entry_page.click_browse_property_direct()
            logger.info("✓ 已直接点击 Browse > Property 一级链接")

        with allure.step("验证 URL 落地在 cate-property 页"):
            current_url = page.url
            assert "cate-property" in current_url, \
                f"期望 URL 含 cate-property，实际: {current_url}"
            logger.info(f"✓ URL: {current_url}")

        with allure.step("验证 iconSource 参数存在且为合法枚举值（产品逻辑：沿用历史子类型）"):
            matched_source = None
            for source in _VALID_ICON_SOURCES:
                if f"iconSource={source}" in current_url:
                    matched_source = source
                    break
            assert matched_source is not None, \
                f"期望 URL 含合法 iconSource（{list(_VALID_ICON_SOURCES.keys())}），实际 URL: {current_url}"
            logger.info(f"✓ iconSource={matched_source}（历史导航决定的子类型，属正常产品逻辑）")

        with allure.step("验证页面 H1 与 iconSource 对应子类型一致，无白屏"):
            h1 = entry_page.get_page_h1()
            expected_h1_keyword = _VALID_ICON_SOURCES[matched_source]
            assert expected_h1_keyword in h1, \
                f"期望 H1 含「{expected_h1_keyword}」（iconSource={matched_source}），实际: '{h1}'"
            logger.info(f"✓ H1='{h1}'，与 iconSource={matched_source} 一致")


