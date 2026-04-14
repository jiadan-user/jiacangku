"""
AU站 Property 地图视图 - 地理位置权限专项测试

本文件专门存放需要 geolocation_page fixture 的测试用例（TC004/TC005）。
独立成文件的原因：geolocation_page 使用独立 Playwright 实例，与共享
module-scope Playwright 实例的测试混合运行时会产生 asyncio loop 冲突。

TC004：授权地理位置后地图中心移动到当前位置
TC005：拒绝授权后地图保持原始中心点
"""
import pytest
import allure
from pages.property_map_page import PropertyMapPage
from utils.logger import setup_logger

logger = setup_logger()

# ============================================
# 测试环境配置
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
        "viewport": {"width": 1920, "height": 1080},
    },
    "timeout": {
        "default": 90000,
        "wait": 30000,
        "navigation": 90000,
    },
}

_GEO_GRANTED = {
    "grant_permission": True,
    "geolocation": {"latitude": -33.8688, "longitude": 151.2093},
}
_GEO_DENIED = {
    "grant_permission": False,
    "geolocation": None,
}


@pytest.fixture(scope="module")
def config():
    return _CONFIG


class TestPropertyMapGeolocationPermission:
    """地理位置权限相关测试（独立 module，无共享 Playwright 实例干扰）"""

    @pytest.mark.case_id_map_geolocation04
    @pytest.mark.regression
    @pytest.mark.p1
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("授权定位后地图中心移动 - 正向场景")
    @allure.title("授权地理位置后点击定位按钮应使地图中心移动到当前位置")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("预设悉尼坐标并授权 geolocation 权限，点击定位按钮后验证地图 viewport 更新为新坐标")
    @pytest.mark.parametrize("geolocation_page", [_GEO_GRANTED], indirect=True)
    def test_map_center_moves_after_geolocation_granted(self, geolocation_page, config):
        """TC004：授权定位后地图中心移动到当前位置"""

        geo_config, run_in_browser = geolocation_page
        target_url = config["target_url"]
        sydney = geo_config["geolocation"]

        logger.info("=" * 80)
        logger.info("TC004 - 授权定位后地图中心移动")
        logger.info("=" * 80)
        logger.info(f"预设坐标（悉尼）: lat={sydney['latitude']}, lng={sydney['longitude']}")
        logger.info("地理位置权限：已授权 ✓")

        # 所有 page 操作通过 run_in_browser(lambda page: ...) 在子线程中执行
        with allure.step("步骤1：打开地图视图页面"):
            run_in_browser(lambda page: PropertyMapPage(page).navigate_to_map_page(target_url))
            logger.info("✓ 页面导航完成")

        with allure.step("步骤2：处理 Cookie 弹窗"):
            run_in_browser(lambda page: PropertyMapPage(page).handle_cookie_popup())
            logger.info("✓ Cookie 弹窗已处理")

        with allure.step("步骤3：等待地图渲染"):
            rendered = run_in_browser(lambda page: PropertyMapPage(page).is_map_rendered())
            if not rendered:
                pytest.skip("地图容器(.gm-style)未在 60s 内完成渲染，可能是 Google Maps API 加载超时")
            logger.info("✓ 地图渲染完成")

        viewport_before = run_in_browser(lambda page: PropertyMapPage(page).get_current_viewport_param())
        logger.info(f"点击前 viewport: {viewport_before}")

        with allure.step("步骤4：点击定位按钮"):
            visible = run_in_browser(lambda page: PropertyMapPage(page).is_location_button_visible())
            assert visible, "定位按钮不可见"
            run_in_browser(lambda page: PropertyMapPage(page).click_location_button())
            run_in_browser(lambda page: page.wait_for_timeout(3000))
            logger.info("✓ 已点击定位按钮")

        viewport_after = run_in_browser(lambda page: PropertyMapPage(page).get_current_viewport_param())
        logger.info(f"点击后 viewport: {viewport_after}")

        with allure.step("验证：地图 viewport 已更新"):
            assert viewport_after != viewport_before, (
                f"地图 viewport 未发生变化，授权后地图中心未移动。\n"
                f"点击前: {viewport_before}\n点击后: {viewport_after}"
            )
            logger.info("✓ viewport 参数已更新，地图中心已移动")

        logger.info("✅ TC004 通过！授权定位后地图中心成功移动到悉尼坐标")

    @pytest.mark.case_id_map_geolocation05
    @pytest.mark.regression
    @pytest.mark.p2
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("拒绝授权后地图保持原始中心点 - 异常场景")
    @allure.title("拒绝地理位置授权后地图中心应保持不变")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("不授予 geolocation 权限（模拟拒绝），点击定位按钮后验证地图 viewport 保持不变")
    @pytest.mark.parametrize("geolocation_page", [_GEO_DENIED], indirect=True)
    def test_map_center_unchanged_after_geolocation_denied(self, geolocation_page, config):
        """TC005：拒绝授权后地图保持原始中心点"""

        geo_config, run_in_browser = geolocation_page
        target_url = config["target_url"]

        logger.info("=" * 80)
        logger.info("TC005 - 拒绝授权后地图保持原始中心点")
        logger.info("=" * 80)
        logger.info("地理位置权限：未授权（模拟拒绝）")

        with allure.step("步骤1：打开地图视图页面（未授予 geolocation 权限）"):
            run_in_browser(lambda page: PropertyMapPage(page).navigate_to_map_page(target_url))
            logger.info("✓ 页面导航完成")

        with allure.step("步骤2：处理 Cookie 弹窗"):
            run_in_browser(lambda page: PropertyMapPage(page).handle_cookie_popup())
            logger.info("✓ Cookie 弹窗已处理")

        with allure.step("步骤3：等待地图渲染"):
            rendered = run_in_browser(lambda page: PropertyMapPage(page).is_map_rendered())
            if not rendered:
                pytest.skip("地图容器(.gm-style)未在 60s 内完成渲染，可能是 Google Maps API 加载超时")
            logger.info("✓ 地图渲染完成")

        viewport_before = run_in_browser(lambda page: PropertyMapPage(page).get_current_viewport_param())
        logger.info(f"点击前 viewport: {viewport_before}")

        with allure.step("步骤4：点击定位按钮"):
            visible = run_in_browser(lambda page: PropertyMapPage(page).is_location_button_visible())
            assert visible, "定位按钮不可见"
            run_in_browser(lambda page: PropertyMapPage(page).click_location_button())
            run_in_browser(lambda page: page.wait_for_timeout(3000))
            logger.info("✓ 已点击定位按钮")

        viewport_after = run_in_browser(lambda page: PropertyMapPage(page).get_current_viewport_param())
        logger.info(f"点击后 viewport: {viewport_after}")

        with allure.step("验证：地图 viewport 未变化"):
            assert viewport_after == viewport_before, (
                f"地图 viewport 发生了变化，但权限被拒绝后不应移动。\n"
                f"点击前: {viewport_before}\n点击后: {viewport_after}"
            )
            logger.info("✓ viewport 参数未变化，地图中心保持原位")

        logger.info("✅ TC005 通过！拒绝授权后地图中心保持不变")
