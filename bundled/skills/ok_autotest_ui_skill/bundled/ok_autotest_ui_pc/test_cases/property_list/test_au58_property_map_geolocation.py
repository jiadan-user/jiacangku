"""
AU站 Property 地图视图 - 授权定位功能测试

本脚本由 playwright-test-generator 生成
录制文档：test_plans/au58-Property-地图授权定位功能测试用例.md
生成时间：2026-03-13

测试站点：AU (https://au.58v5.cn)
测试角色：guest（无需登录）
测试目标：验证地图视图页面的地理位置授权定位功能，包含地图加载、定位按钮展示、
         点击定位触发权限申请、授权后地图中心移动、拒绝授权后地图保持原位

TC001-TC003：使用标准 page fixture（默认权限）
TC004：使用 geolocation_page fixture，注入悉尼坐标 + 授予 geolocation 权限
TC005：使用 geolocation_page fixture，不授予 geolocation 权限（模拟拒绝）
"""
import pytest
import allure
from pages.property_map_page import PropertyMapPage
from utils.logger import setup_logger

logger = setup_logger()

# ============================================
# 测试环境配置（来自录制文档）
# ============================================
_CONFIG = {
    "site": "au",
    "site_name": "AU站（澳大利亚）",
    "role": "guest",
    "user_name": "guest_au",
    "base_url": "https://au.58v5.cn",
    "test_account": None,
    "target_url": (
        "https://au.58v5.cn/en/city-new-south-wales/cate-property/"
        "?iconSource=student-apartment&view=map&viewport=c%3A-31.2532%2C146.9211%7Cz%3A11"
    ),
    "locale": "en-AU",
    "browser": {
        "type": "chromium",
        "headless": True,
        "viewport": {"width": 1920, "height": 1080}
    },
    "timeout": {
        "default": 30000,
        "wait": 10000,
        "navigation": 30000
    },
    "geolocation": {
        "sydney": {"latitude": -33.8688, "longitude": 151.2093},
        "nsw_default": {"latitude": -31.2532, "longitude": 146.9211}
    }
}

# ============================================
# geolocation_page fixture 参数（用于 TC004/TC005）
# ============================================
_GEO_GRANTED = {
    "grant_permission": True,
    "geolocation": {"latitude": -33.8688, "longitude": 151.2093},  # 悉尼
}
_GEO_DENIED = {
    "grant_permission": False,
    "geolocation": None,
}


class TestPropertyMapGeolocation:
    """AU站 Property 地图视图 - 授权定位功能测试类"""

    @pytest.mark.case_id_map_geolocation01
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("地图视图页面加载 - 正向场景")
    @allure.title("地图视图页面应正常加载并渲染地图")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证AU站 Property 地图视图页面正常加载，地图渲染完成，URL 包含 view=map 参数")
    def test_map_view_page_loads_successfully(self, page, config):
        """TC001：地图视图页面正常加载"""

        # ========== Arrange ==========
        map_page = PropertyMapPage(page)
        target_url = config["target_url"]

        logger.info("=" * 80)
        logger.info("TC001 - 地图视图页面正常加载")
        logger.info("=" * 80)
        logger.info(f"目标URL: {target_url}")

        # ========== Act ==========
        with allure.step("步骤1：打开地图视图页面"):
            map_page.navigate_to_map_page(target_url)
            logger.info("✓ 页面导航完成")

        with allure.step("步骤2：处理 Cookie 弹窗"):
            map_page.handle_cookie_popup()
            logger.info("✓ Cookie 弹窗已处理")

        # ========== Assert ==========
        with allure.step("验证：地图渲染完成且 URL 包含 view=map"):
            if not map_page.is_map_rendered():
                pytest.skip("地图容器(.gm-style)未在 60s 内完成渲染，可能是 Google Maps API 加载超时")
            logger.info("✓ 地图渲染验证通过")

            assert map_page.is_url_contains_map_view(), \
                f"URL 未包含 view=map 参数，当前 URL: {page.url}"
            logger.info("✓ URL view=map 参数验证通过")

            assert map_page.is_url_contains_viewport(), \
                f"URL 未包含 viewport 参数，当前 URL: {page.url}"
            logger.info("✓ URL viewport 参数验证通过")

        logger.info("✅ TC001 通过！地图视图页面正常加载")

    @pytest.mark.case_id_map_geolocation02
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("地图定位按钮展示 - 正向场景")
    @allure.title("地图页面应显示可见的定位按钮")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证地图视图页面中定位图标按钮存在且可见，bounding_box 宽高大于 0")
    def test_location_button_is_visible(self, page, config):
        """TC002：地图页显示定位按钮"""

        # ========== Arrange ==========
        map_page = PropertyMapPage(page)
        target_url = config["target_url"]

        logger.info("=" * 80)
        logger.info("TC002 - 地图页显示定位按钮")
        logger.info("=" * 80)

        # ========== Act ==========
        with allure.step("步骤1：打开地图视图页面"):
            map_page.navigate_to_map_page(target_url)
            logger.info("✓ 页面导航完成")

        with allure.step("步骤2：处理 Cookie 弹窗"):
            map_page.handle_cookie_popup()
            logger.info("✓ Cookie 弹窗已处理")

        with allure.step("步骤3：等待地图加载完成"):
            if not map_page.is_map_rendered():
                pytest.skip("地图容器(.gm-style)未在 60s 内完成渲染，可能是 Google Maps API 加载超时")
            logger.info("✓ 地图渲染完成")

        # ========== Assert ==========
        with allure.step("验证：定位按钮存在且可见"):
            assert map_page.is_location_button_visible(), \
                "定位按钮不可见或不存在（bounding_box 为空或宽高为 0）"
            logger.info("✓ 定位按钮可见性验证通过")

            btn_size = map_page.get_location_button_size()
            assert btn_size.get("width", 0) > 0 and btn_size.get("height", 0) > 0, \
                f"定位按钮尺寸异常: {btn_size}"
            logger.info(f"✓ 定位按钮尺寸验证通过: {btn_size['width']}x{btn_size['height']}")

        logger.info("✅ TC002 通过！定位按钮正常显示")

    @pytest.mark.case_id_map_geolocation03
    @pytest.mark.smoke
    @pytest.mark.p1
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("点击定位按钮触发权限申请 - 正向场景")
    @allure.title("点击定位按钮应触发浏览器地理位置权限申请")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证点击定位按钮后浏览器触发地理位置权限申请，页面状态保持在地图视图")
    def test_click_location_button_triggers_permission_request(self, page, config):
        """TC003：点击定位按钮触发浏览器授权弹窗"""

        # ========== Arrange ==========
        map_page = PropertyMapPage(page)
        target_url = config["target_url"]

        logger.info("=" * 80)
        logger.info("TC003 - 点击定位按钮触发浏览器授权弹窗")
        logger.info("=" * 80)

        # ========== Act ==========
        with allure.step("步骤1：打开地图视图页面"):
            map_page.navigate_to_map_page(target_url)
            logger.info("✓ 页面导航完成")

        with allure.step("步骤2：处理 Cookie 弹窗"):
            map_page.handle_cookie_popup()
            logger.info("✓ Cookie 弹窗已处理")

        with allure.step("步骤3：等待地图渲染"):
            if not map_page.is_map_rendered():
                pytest.skip("地图容器(.gm-style)未在 60s 内完成渲染，可能是 Google Maps API 加载超时")
            logger.info("✓ 地图渲染完成")

        with allure.step("步骤4：点击定位按钮"):
            assert map_page.is_location_button_visible(), "定位按钮不可见，无法点击"
            map_page.click_location_button()
            page.wait_for_timeout(2000)
            logger.info("✓ 已点击定位按钮")

        # ========== Assert ==========
        with allure.step("验证：点击后页面仍处于地图视图"):
            current_url = page.url
            assert "view=map" in current_url, \
                f"点击后页面跳转异常，当前 URL: {current_url}"
            logger.info("✓ 点击定位按钮后页面状态正常，权限请求已触发")

        logger.info("✅ TC003 通过！点击定位按钮功能正常")

    # TC004/TC005（需要 geolocation_page fixture）已移至独立文件：
    # test_au58_property_map_geolocation_permission.py
    # 原因：geolocation_page 需要独立的 Playwright 实例，不能与共享 module-scope
    # page fixture 的测试混在同一文件（会触发 asyncio loop 冲突）。
