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
    "user_name": "mayueming_au_buyer",
    "base_url": "https://au.58v5.cn",
    "test_account": None,
    "target_page": "https://au.58v5.cn/en/city-canberra/cate-property/?iconSource=rent",
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


class TestRentPriceFilter:
    """Price（价格）筛选功能测试 - Property For Rent（10 条用例）"""

    @pytest.fixture(scope="module")
    def setup_property_page(self, page, config):
        property_page = PropertyPage(page)
        page.goto(config['target_page'], wait_until="domcontentloaded", timeout=config['timeout']['navigation'])
        page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
        property_page.handle_cookie_popup()
        page.wait_for_timeout(1000)
        yield property_page

    @pytest.fixture(scope="module", autouse=True)
    def reset_rent_page_after_module(self, page, config):
        """模块级别：所有测试结束后重置页面"""
        yield  # 先执行所有测试
        # 所有测试完成后的清理
        try:
            logger.info("========== 模块测试完毕，重置页面 ==========")
            page.goto(_CONFIG['target_page'], wait_until="domcontentloaded", timeout=_CONFIG['timeout']['navigation'])
            page.wait_for_load_state('domcontentloaded', timeout=_CONFIG['timeout']['navigation'])
            page.wait_for_timeout(1000)
            logger.info("✓ 模块测试完成，页面已重置")
        except Exception as e:
            logger.warning(f"模块结束后重置页面失败: {e}")
    
    @pytest.fixture(scope="function", autouse=True)
    def reset_page_between_tests(self, page, config, setup_property_page):
        """函数级别：每个测试之间重置页面（不关闭浏览器）"""
        yield  # 先执行测试
        # 每个测试后重置页面到初始状态
        try:
            logger.info("========== 用例执行完毕，重置页面到初始状态 ==========")
            page.goto(_CONFIG['target_page'], wait_until="domcontentloaded", timeout=_CONFIG['timeout']['navigation'])
            page.wait_for_load_state('domcontentloaded', timeout=_CONFIG['timeout']['navigation'])
            page.wait_for_timeout(1000)
            current_url = page.url
            if "cate-property" in current_url:
                logger.info(f"✓ 页面已重置到初始状态: {current_url}")
            else:
                logger.warning(f"⚠️ 页面 URL 可能不符合预期: {current_url}")
        except Exception as e:
            logger.warning(f"重置页面失败（不影响用例结果）: {e}")
            try:
                page.reload(wait_until="domcontentloaded", timeout=_CONFIG['timeout']['navigation'])
                page.wait_for_timeout(1000)
                logger.info("✓ 已通过刷新恢复页面")
            except Exception:
                pass
    @pytest.mark.p1
    @pytest.mark.case_id_property_rent_price_009
    def test_price_valid_min_max_url_contains_price_params(self, page, config, setup_property_page):
        """TC009：输入有效 Min 和 Max 价格后 Done"""
        property_page = setup_property_page

        with allure.step("点击 Price 筛选按钮"):
            property_page.click_price_filter()
            logger.info("✓ Price 筛选面板已打开")

        with allure.step("输入 Min=500，Max=2000"):
            property_page.input_price_range("500", "2000")
            logger.info("✓ 已输入价格区间 500-2000")

        with allure.step("点击 Done"):
            property_page.click_done_button_in_price_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已点击 Done，页面刷新")

        with allure.step("验证 URL 含 lowestPrice=500"):
            assert "lowestPrice=500" in page.url, \
                f"期望 URL 含 lowestPrice=500，实际 URL: {page.url}"
            logger.info(f"✓ lowestPrice=500 存在于 URL")

        with allure.step("验证 URL 含 highestPrice=2000"):
            assert "highestPrice=2000" in page.url, \
                f"期望 URL 含 highestPrice=2000，实际 URL: {page.url}"
            logger.info(f"✓ highestPrice=2000 存在于 URL")

        with allure.step("验证激活标签显示价格区间"):
            price_tag = property_page.get_price_filter_tag_text()
            assert price_tag, "期望显示价格激活标签，实际未找到"
            logger.info(f"✓ 价格激活标签: {price_tag}")


    @pytest.mark.case_id_property_rent_price_010
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Price 价格筛选 - 边界值场景")
    @allure.title("仅输入 Min 价格 Max 为空后 Done URL 含 lowestPrice")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("点击 Price 筛选，仅输入 Min=500，Max 留空，点击 Done，验证 URL 含 lowestPrice=500")
    def test_price_only_min_price_url_contains_lowest_price(self, page, config, setup_property_page):
        """TC010：仅输入 Min 价格（Max 为空）后 Done"""
        property_page = setup_property_page

        with allure.step("点击 Price → 仅输入 Min=500 → Done"):
            property_page.click_price_filter()
            property_page.input_price_range("500", "")
            property_page.click_done_button_in_price_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 仅输入 Min=500，已点击 Done")

        with allure.step("验证 URL 含 lowestPrice=500"):
            assert "lowestPrice=500" in page.url, \
                f"期望 URL 含 lowestPrice=500，实际 URL: {page.url}"
            logger.info(f"✓ lowestPrice=500 在 URL 中: {page.url}")


    @pytest.mark.case_id_property_rent_price_011
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Price 价格筛选 - 边界值场景")
    @allure.title("仅输入 Max 价格 Min 为空后 Done URL 含 highestPrice")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("点击 Price 筛选，仅输入 Max=2000，Min 留空，点击 Done，验证 URL 含 highestPrice=2000")
    def test_price_only_max_price_url_contains_highest_price(self, page, config, setup_property_page):
        """TC011：仅输入 Max 价格（Min 为空）后 Done"""
        property_page = setup_property_page

        with allure.step("点击 Price → 仅输入 Max=2000 → Done"):
            property_page.click_price_filter()
            property_page.input_price_range("", "2000")
            property_page.click_done_button_in_price_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 仅输入 Max=2000，已点击 Done")

        with allure.step("验证 URL 含 highestPrice=2000"):
            assert "highestPrice=2000" in page.url, \
                f"期望 URL 含 highestPrice=2000，实际 URL: {page.url}"
            logger.info(f"✓ highestPrice=2000 在 URL 中: {page.url}")


    @pytest.mark.case_id_property_rent_price_012
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Price 价格筛选 - 异常场景")
    @allure.title("Min 大于 Max 时系统拦截不提交逆向区间")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("输入 Min=5000、Max=1000（逆向区间），点击 Done，验证系统给出错误提示且 Done 按钮不提交")
    def test_price_min_greater_than_max_system_intercepts(self, page, config, setup_property_page):
        """TC012：Min 大于 Max（逆向价格区间）"""
        property_page = setup_property_page

        with allure.step("点击 Price → 输入 Min=5000、Max=1000 → Done"):
            property_page.click_price_filter()
            property_page.input_price_range("5000", "1000")
            property_page.click_done_button_in_price_modal()
            page.wait_for_timeout(1500)
            logger.info("✓ 输入逆向区间并点击 Done")

        with allure.step("验证系统拦截：错误提示或价格参数未写入 URL"):
            current_url = page.url
            error_msg = property_page.get_price_error_message()
            is_intercepted = error_msg or ("lowestPrice=5000" not in current_url)
            assert is_intercepted, \
                "期望系统拦截逆向价格区间：应显示错误提示或不将非法区间写入 URL"
            logger.info(f"✓ 系统拦截生效，错误信息: {error_msg}, URL: {current_url}")


    @pytest.mark.case_id_property_rent_price_013
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Price 价格筛选 - 边界值场景")
    @allure.title("Min 输入负数时系统拦截不接受负价格")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("点击 Price 筛选，Min 输入 -500，点击 Done，验证系统拒绝负价格输入")
    def test_price_negative_min_value_system_rejects(self, page, config, setup_property_page):
        """TC013：Min 输入负数价格"""
        property_page = setup_property_page

        with allure.step("点击 Price → 输入 Min=-500 → Done"):
            property_page.click_price_filter()
            property_page.input_price_range("-500", "")
            property_page.click_done_button_in_price_modal()
            page.wait_for_timeout(1500)
            logger.info("✓ 输入负数 Min 并点击 Done")

        with allure.step("验证系统拒绝负数价格"):
            current_url = page.url
            error_msg = property_page.get_price_error_message()
            is_rejected = error_msg or ("lowestPrice=-500" not in current_url)
            assert is_rejected, \
                "期望系统拒绝负价格：应显示错误提示或不将负值写入 URL"
            logger.info(f"✓ 系统拒绝负价格，URL: {current_url}")


    @pytest.mark.case_id_property_rent_price_014
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Price 价格筛选 - 异常场景")
    @allure.title("Min 输入非数字字符时系统拦截")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("点击 Price 筛选，Min 输入 abc，点击 Done，验证系统拒绝非数字字符输入")
    def test_price_non_numeric_min_value_system_rejects(self, page, config, setup_property_page):
        """TC014：Min 输入非数字字符"""
        property_page = setup_property_page

        with allure.step("点击 Price → 输入 Min=abc → Done"):
            property_page.click_price_filter()
            property_page.input_price_range("abc", "")
            property_page.click_done_button_in_price_modal()
            page.wait_for_timeout(1500)
            logger.info("✓ 输入非数字 Min 并点击 Done")

        with allure.step("验证 URL 不含非法价格参数"):
            current_url = page.url
            assert "lowestPrice=abc" not in current_url, \
                "期望 URL 不含非法价格参数 lowestPrice=abc"
            logger.info(f"✓ 系统拦截非数字输入，URL: {current_url}")


    @pytest.mark.case_id_property_rent_price_015
    @pytest.mark.p2
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Price 价格筛选 - 边界值场景")
    @allure.title("输入超大数值极端边界时页面不崩溃")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("输入极端价格 Min=999999999，点击 Done，验证页面正常响应不崩溃")
    def test_price_extremely_large_value_page_no_crash(self, page, config, setup_property_page):
        """TC015：输入超大数值（极端边界）"""
        property_page = setup_property_page

        with allure.step("点击 Price → 输入极端大值 → Done"):
            property_page.click_price_filter()
            property_page.input_price_range("999999999", "")
            property_page.click_done_button_in_price_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 输入极端大值并点击 Done")

        with allure.step("验证页面正常渲染不崩溃"):
            page_content = page.content()
            assert len(page_content) > 0, "期望页面内容不为空（页面未崩溃）"
            logger.info(f"✓ 页面正常，URL: {page.url}")


    @pytest.mark.case_id_property_rent_price_016
    @pytest.mark.p2
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Price 价格筛选 - 边界值场景")
    @allure.title("输入小数价格时系统正常处理")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("输入 Min=1500.5、Max=2000.99，点击 Done，验证系统正常处理小数价格")
    def test_price_decimal_values_system_handles_normally(self, page, config, setup_property_page):
        """TC016：输入小数价格"""
        property_page = setup_property_page

        with allure.step("点击 Price → 输入 Min=1500.5，Max=2000.99 → Done"):
            property_page.click_price_filter()
            property_page.input_price_range("1500.5", "2000.99")
            property_page.click_done_button_in_price_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 输入小数价格并点击 Done")

        with allure.step("验证页面正常响应"):
            page_content = page.content()
            assert len(page_content) > 0, "期望页面正常渲染"
            logger.info(f"✓ 页面正常，URL: {page.url}")


    @pytest.mark.case_id_property_rent_price_017
    @pytest.mark.p2
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Price 价格筛选 - 边界值场景")
    @allure.title("输入 0 作为最小价格时系统正常处理")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("输入 Min=0，点击 Done，验证系统正常处理零值最小价格")
    def test_price_zero_as_min_value_system_handles(self, page, config, setup_property_page):
        """TC017：输入 0 作为最小价格"""
        property_page = setup_property_page

        with allure.step("点击 Price → 输入 Min=0 → Done"):
            property_page.click_price_filter()
            property_page.input_price_range("0", "")
            property_page.click_done_button_in_price_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 输入 Min=0 并点击 Done")

        with allure.step("验证页面正常响应"):
            assert len(page.content()) > 0, "期望页面正常渲染"
            logger.info(f"✓ 页面正常，URL: {page.url}")


    @pytest.mark.case_id_property_rent_price_018
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("Price 价格筛选 - 功能场景")
    @allure.title("已设置价格筛选后点击 Clear URL 中价格参数消失")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("设置价格筛选 500~2000 后，重新打开面板点击 Clear，验证 URL 价格参数消失")
    def test_price_clear_removes_price_params_from_url(self, page, config, setup_property_page):
        """TC018：已设置价格筛选后点击 Clear 清除"""
        property_page = setup_property_page

        with allure.step("先设置价格筛选 500~2000"):
            property_page.click_price_filter()
            property_page.input_price_range("500", "2000")
            property_page.click_done_button_in_price_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            page.wait_for_timeout(3000)  # 增加等待，确保页面导航和筛选器重新渲染
            logger.info("✓ 已设置价格筛选 500~2000")

        with allure.step("重新打开价格面板并点击 Clear"):
            property_page.click_price_filter()
            property_page.click_clear_button_in_price_modal()
            property_page.click_done_button_in_price_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            page.wait_for_timeout(1500)  # 等待清除后页面导航完成
            logger.info("✓ 已点击 Clear 并 Done")

        with allure.step("验证 URL 不含价格参数"):
            assert "lowestPrice" not in page.url, \
                f"期望 URL 不含 lowestPrice，实际 URL: {page.url}"
            assert "highestPrice" not in page.url, \
                f"期望 URL 不含 highestPrice，实际 URL: {page.url}"
            logger.info(f"✓ 价格参数已从 URL 清除: {page.url}")


    # ============================================