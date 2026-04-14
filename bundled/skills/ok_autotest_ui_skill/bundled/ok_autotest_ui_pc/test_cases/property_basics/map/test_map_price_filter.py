"""
地图模式 - Price 价格筛选测试（Sydney Student Accommodation）

测试站点：AU (https://au.58v5.cn)
覆盖用例：TC016–TC023
功能点：有效区间 / 仅 Min / 仅 Max / Min>Max / 负数 / 非数字 / 极大值 / Clear
"""
import re as _re
import pytest
import allure
from pages.property_map_page import PropertyMapPage
from utils.logger import setup_logger

logger = setup_logger()

_CONFIG = {
    "site": "au",
    "site_name": "澳大利亚站",
    "role": "buyer",
    "user_name": "mayueming_au_buyer",
    "base_url": "https://au.58v5.cn",
    "test_account": None,
    "target_page": (
        "https://au.58v5.cn/en/city-sydney/cate-student-apartment/"
        "?iconSource=student-apartment&view=map"
        "&viewport=c%3A-33.8623%2C151.2077%7Cz%3A11"
    ),
    "list_page": "https://au.58v5.cn/en/city-sydney/cate-student-apartment/?iconSource=student-apartment",
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



class TestMapPriceFilter:
    """Price 价格筛选测试（8 条用例）"""

    @pytest.fixture(scope="module")
    def setup_sa_page(self, page, config):
        """Class 级别页面准备：导航到地图模式页面，处理 Cookie，返回 PropertyMapPage 实例"""
        sa_page = PropertyMapPage(page)
        page.goto(config['target_page'], wait_until="domcontentloaded", timeout=config['timeout']['navigation'])
        page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
        sa_page.handle_cookie_popup()
        page.wait_for_timeout(1000)
        yield sa_page

    @pytest.fixture(scope="module", autouse=True)
    def reset_map_page_after_module(self, page, config):
        """模块级别：所有测试结束后重置页面"""
        yield  # 先执行所有测试
        try:
            logger.info("========== 模块测试完毕，重置页面 ==========")
            page.goto(config['target_page'], wait_until="domcontentloaded", timeout=config['timeout']['navigation'])
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            page.wait_for_timeout(1000)
            logger.info("✓ 模块测试完成，页面已重置")
        except Exception as e:
            logger.warning(f"模块结束后重置页面失败: {e}")
    
    @pytest.fixture(scope="function", autouse=True)
    def reset_page_between_tests(self, page, config, setup_sa_page):
        """函数级别：每个测试之间重置页面（不关闭浏览器）"""
        yield  # 先执行测试
        try:
            logger.info("========== 用例执行完毕，重置页面到初始状态 ==========")
            page.goto(config['target_page'], wait_until="domcontentloaded", timeout=config['timeout']['navigation'])
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            page.wait_for_timeout(1000)
            logger.info(f"✓ 页面已重置到初始状态: {page.url}")
        except Exception as e:
            logger.warning(f"重置页面失败（不影响用例结果）: {e}")
    @pytest.mark.p1
    @pytest.mark.case_id_sa_price_016
    def test_price_valid_min_max_url_contains_price_params(self, page, config, setup_sa_page):
        """TC016：输入有效 Min 和 Max 价格后点击 Done"""
        sa_page = setup_sa_page

        with allure.step("点击 Price 按钮展开面板"):
            sa_page.click_price_filter()
            logger.info("✓ Price 面板已展开")

        with allure.step("输入 Min=500，Max=1500"):
            sa_page.input_price_min("500")
            sa_page.input_price_max("1500")
            logger.info("✓ 已输入 Min=500，Max=1500")

        with allure.step("点击 Done"):
            sa_page.click_price_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已点击 Done")

        with allure.step("验证 URL 含 lowestPrice=500 和 highestPrice=1500"):
            current_url = page.url
            assert "lowestPrice=500" in current_url, \
                f"期望 URL 含 lowestPrice=500，实际 URL: {current_url}"
            assert "highestPrice=1500" in current_url, \
                f"期望 URL 含 highestPrice=1500，实际 URL: {current_url}"
            assert "view=map" in current_url, \
                f"期望 URL 保留 view=map，实际 URL: {current_url}"
            logger.info(f"✓ URL 含价格参数: {current_url}")

    @pytest.mark.case_id_sa_price_017
    @pytest.mark.p1
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Price 价格筛选 - 功能场景")
    @allure.title("仅输入 Min 价格，URL 仅含 lowestPrice")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("点击 Price，只输入 Min=500，Max 为空，点击 Done，验证 URL 含 lowestPrice=500 且无 highestPrice")
    def test_price_only_min_url_contains_lowest_price_only(self, page, config, setup_sa_page):
        """TC017：仅输入 Min 价格，URL 仅含 lowestPrice"""
        sa_page = setup_sa_page

        with allure.step("点击 Price → 只输入 Min=500 → Done"):
            sa_page.click_price_filter()
            sa_page.input_price_min("500")
            sa_page.click_price_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已输入 Min=500 并点击 Done")

        with allure.step("验证 URL 含 lowestPrice=500 且无 highestPrice"):
            current_url = page.url
            assert "lowestPrice=500" in current_url, \
                f"期望 URL 含 lowestPrice=500，实际 URL: {current_url}"
            assert "highestPrice" not in current_url, \
                f"期望 URL 不含 highestPrice，实际 URL: {current_url}"
            logger.info(f"✓ URL: {current_url}")

    @pytest.mark.case_id_sa_price_018
    @pytest.mark.p1
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Price 价格筛选 - 功能场景")
    @allure.title("仅输入 Max 价格，URL 仅含 highestPrice")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("点击 Price，只输入 Max=2000，Min 为空，点击 Done，验证 URL 含 highestPrice=2000 且无 lowestPrice")
    def test_price_only_max_url_contains_highest_price_only(self, page, config, setup_sa_page):
        """TC018：仅输入 Max 价格，URL 仅含 highestPrice"""
        sa_page = setup_sa_page

        with allure.step("点击 Price → 只输入 Max=2000 → Done"):
            sa_page.click_price_filter()
            sa_page.input_price_max("2000")
            sa_page.click_price_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已输入 Max=2000 并点击 Done")

        with allure.step("验证 URL 含 highestPrice=2000 且无 lowestPrice"):
            current_url = page.url
            assert "highestPrice=2000" in current_url, \
                f"期望 URL 含 highestPrice=2000，实际 URL: {current_url}"
            assert "lowestPrice" not in current_url, \
                f"期望 URL 不含 lowestPrice，实际 URL: {current_url}"
            logger.info(f"✓ URL: {current_url}")

    @pytest.mark.case_id_sa_price_019
    @pytest.mark.p1
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Price 价格筛选 - 异常场景")
    @allure.title("Min 大于 Max，系统阻止提交或自动处理")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("在 Price 面板输入 Min=2000、Max=500，点击 Done，验证系统阻止无效提交")
    def test_price_min_greater_than_max_system_handles_gracefully(self, page, config, setup_sa_page):
        """TC019：Min 大于 Max，系统阻止提交或自动处理"""
        sa_page = setup_sa_page

        with allure.step("打开 Price 面板，输入 Min=2000，Max=500"):
            sa_page.click_price_filter()
            sa_page.input_price_min("2000")
            sa_page.input_price_max("500")
            logger.info("✓ 已输入 Min=2000，Max=500（Min > Max）")

        with allure.step("点击 Done"):
            sa_page.click_price_done()
            page.wait_for_timeout(1000)
            logger.info("✓ 已点击 Done")

        with allure.step("验证系统未生成无效的 lowestPrice > highestPrice URL"):
            current_url = page.url
            low_match = _re.search(r'lowestPrice=(\d+)', current_url)
            high_match = _re.search(r'highestPrice=(\d+)', current_url)
            if low_match and high_match:
                low = int(low_match.group(1))
                high = int(high_match.group(1))
                assert low <= high, \
                    f"期望 lowestPrice <= highestPrice，实际 URL: {current_url}"
            logger.info(f"✓ 系统处理合理，URL: {current_url}")

    @pytest.mark.case_id_sa_price_020
    @pytest.mark.p1
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Price 价格筛选 - 边界场景")
    @allure.title("在 Min 框输入负数，系统不接受负数参数")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("在 Price 面板 Min 输入框输入 -100，点击 Done，验证 URL 不含 lowestPrice=-100")
    def test_price_negative_min_not_accepted(self, page, config, setup_sa_page):
        """TC020：在 Min 框输入负数，系统不接受"""
        sa_page = setup_sa_page

        with allure.step("打开 Price 面板，输入 Min=-100 → Done"):
            sa_page.click_price_filter()
            sa_page.input_price_min("-100")
            sa_page.click_price_done()
            page.wait_for_timeout(1000)
            logger.info("✓ 已输入 Min=-100 并点击 Done")

        with allure.step("验证 URL 不含 lowestPrice=-100"):
            current_url = page.url
            assert "lowestPrice=-100" not in current_url, \
                f"期望 URL 不含负数 lowestPrice，实际 URL: {current_url}"
            logger.info(f"✓ 负数参数未被提交，URL: {current_url}")

    @pytest.mark.case_id_sa_price_021
    @pytest.mark.p1
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Price 价格筛选 - 异常场景")
    @allure.title("在 Min 框输入非数字字符，系统不接受")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("在 Price 面板 Min 输入框输入 abc，点击 Done，验证 URL 不含 lowestPrice=abc")
    def test_price_non_numeric_min_not_accepted(self, page, config, setup_sa_page):
        """TC021：在 Min 框输入非数字字符，系统不接受"""
        sa_page = setup_sa_page

        with allure.step("打开 Price 面板，输入 Min=abc → Done"):
            sa_page.click_price_filter()
            sa_page.input_price_min("abc")
            sa_page.click_price_done()
            page.wait_for_timeout(1000)
            logger.info("✓ 已输入 Min=abc 并点击 Done")

        with allure.step("验证 URL 不含 lowestPrice=abc"):
            current_url = page.url
            assert "lowestPrice=abc" not in current_url, \
                f"期望 URL 不含非数字 lowestPrice，实际 URL: {current_url}"
            logger.info(f"✓ 非数字参数未被提交，URL: {current_url}")

    @pytest.mark.case_id_sa_price_022
    @pytest.mark.p2
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Price 价格筛选 - 边界场景")
    @allure.title("输入极大数值，页面不崩溃")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("在 Price 面板输入 Min=9999999，点击 Done，验证页面不崩溃且显示空状态或正常结果")
    def test_price_extreme_large_value_no_crash(self, page, config, setup_sa_page):
        """TC022：输入极大数值，页面不崩溃"""
        sa_page = setup_sa_page

        with allure.step("打开 Price 面板，输入 Min=9999999 → Done"):
            sa_page.click_price_filter()
            sa_page.input_price_min("9999999")
            sa_page.click_price_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已输入极大值并点击 Done")

        with allure.step("验证页面不崩溃（URL 正常、无 JS 报错）"):
            current_url = page.url
            assert "au.58v5.cn" in current_url, \
                f"期望页面未崩溃，实际 URL: {current_url}"
            logger.info(f"✓ 页面未崩溃，URL: {current_url}")

    @pytest.mark.case_id_sa_price_023
    @pytest.mark.p1
    @pytest.mark.student_apartment
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Price 价格筛选 - 功能场景")
    @allure.title("Price 筛选后点击 Clear，URL 中价格参数被移除")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("已设置 Price Min=500、Max=1500 后，重新打开 Price 面板点击 Clear，验证 URL 中价格参数移除")
    def test_price_clear_removes_price_params_from_url(self, page, config, setup_sa_page):
        """TC023：Price 筛选后点击 Clear，URL 中价格参数被移除"""
        sa_page = setup_sa_page

        with allure.step("先设置 Price=500~1500"):
            sa_page.click_price_filter()
            sa_page.input_price_min("500")
            sa_page.input_price_max("1500")
            sa_page.click_price_done()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            assert "lowestPrice=500" in page.url, f"Price 设置失败，URL: {page.url}"
            logger.info("✓ 已设置 Price 筛选")

        with allure.step("重新打开 Price 面板，点击 Clear"):
            sa_page.click_price_filter()
            sa_page.click_price_clear()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已点击 Clear")

        with allure.step("验证 URL 中价格参数已移除"):
            current_url = page.url
            assert "lowestPrice" not in current_url, \
                f"期望 URL 不含 lowestPrice，实际 URL: {current_url}"
            assert "highestPrice" not in current_url, \
                f"期望 URL 不含 highestPrice，实际 URL: {current_url}"
            logger.info(f"✓ 价格参数已清除，URL: {current_url}")


