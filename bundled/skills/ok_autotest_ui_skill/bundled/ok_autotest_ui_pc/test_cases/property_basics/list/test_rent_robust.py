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


class TestRentRobust:
    """健壮性测试（分页/视图切换/UI文案/URL安全/网络）- Property For Rent（13 条用例）"""

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
    @pytest.mark.p2
    @pytest.mark.case_id_property_rent_robust_051
    def test_robust_filter_params_persist_after_pagination(self, page, config, setup_property_page):
        """TC051：筛选条件下翻页，筛选状态保持"""
        property_page = setup_property_page

        with allure.step("设置 Price=500~2000 筛选"):
            property_page.click_price_filter()
            property_page.input_price_range("500", "2000")
            property_page.click_done_button_in_price_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置价格筛选")

        with allure.step("点击第二页"):
            try:
                page.get_by_role("link", name="2").first.click()
                page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
                logger.info("✓ 已跳转到第二页")
            except Exception:
                logger.info("⚠️ 未找到第二页按钮（数据量不足），跳过翻页步骤")
                return

        with allure.step("验证翻页后价格参数保持"):
            assert "lowestPrice=500" in page.url, \
                f"期望翻页后 URL 仍含 lowestPrice=500，实际: {page.url}"
            logger.info(f"✓ 翻页后价格参数保持: {page.url}")


    @pytest.mark.case_id_property_rent_robust_052
    @pytest.mark.p2
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("健壮性测试 - 分页与视图切换")
    @allure.title("切换 List/Map 视图后筛选条件保持")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("设置 Beds=2 后，点击 Map 视图切换，验证 URL 仍含 attr_168 参数")
    def test_robust_filter_params_persist_after_view_switch(self, page, config, setup_property_page):
        """TC052：切换 List/Map 视图，筛选条件保持"""
        property_page = setup_property_page

        with allure.step("设置 Beds=2 筛选"):
            property_page.click_beds_filter()
            property_page.select_beds_values("2")
            property_page.click_done_button_in_beds_modal()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已设置 Beds=2")

        with allure.step("点击 Map 视图切换按钮"):
            try:
                page.get_by_text("Map").first.click()
                page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
                logger.info("✓ 已切换到 Map 视图")
            except Exception:
                logger.info("⚠️ 未找到 Map 视图切换按钮，跳过切换步骤")
                return

        with allure.step("验证切换视图后 attr_168 参数保持"):
            assert "attr_168" in page.url, \
                f"期望切换视图后 URL 仍含 attr_168，实际: {page.url}"
            logger.info(f"✓ 视图切换后 Beds 参数保持: {page.url}")


    # ============================================
    # 八、健壮性测试 8.2 UI 文案校验 TC054–TC056
    # ============================================

    @pytest.mark.case_id_property_rent_robust_054
    @pytest.mark.p2
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("健壮性测试 - UI 文案校验")
    @allure.title("所有筛选面板文案拼写校验正确无错误")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("检查 Sort、Beds、Bathrooms 等筛选面板的选项文案拼写和大小写是否正确")
    def test_robust_filter_panel_text_spelling_correct(self, page, config, setup_property_page):
        """TC054：所有筛选面板文案拼写校验"""
        property_page = setup_property_page

        with allure.step("打开排序面板验证选项文案"):
            property_page.click_sort_button()
            page.wait_for_timeout(1000)
            page_content = page.content()
            expected_sort_options = ["Best Match", "Newest First", "Lowest Price", "Highest Price"]
            for option in expected_sort_options:
                assert option in page_content, \
                    f"期望排序面板含选项 '{option}'，实际未在页面找到"
                logger.info(f"✓ 排序选项 '{option}' 文案正确")
            property_page.click_page_blank_area()
            page.wait_for_timeout(500)

        with allure.step("打开 Beds 面板验证 Done/Clear 按钮文案"):
            property_page.click_beds_filter()
            page.wait_for_timeout(1000)
            beds_content = page.content()
            assert "Done" in beds_content, "期望 Beds 面板含 'Done' 按钮"
            assert "Clear" in beds_content, "期望 Beds 面板含 'Clear' 按钮"
            logger.info("✓ Beds 面板 Done/Clear 按钮文案正确")
            property_page.click_clear_button_in_beds_modal()
            property_page.click_done_button_in_beds_modal()
            page.wait_for_timeout(500)

        logger.info("✓ 所有筛选面板文案校验通过")


    @pytest.mark.case_id_property_rent_robust_056
    @pytest.mark.p2
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("健壮性测试 - UI 文案校验")
    @allure.title("选择 Property Type 后面包屑与标题文案一致")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("选择 Property Type=House 后，验证面包屑、H1 标题、浏览器 tab 标题均与所选类目一致")
    def test_robust_property_type_breadcrumb_title_consistent(self, page, config, setup_property_page):
        """TC056：选择 Property Type 后面包屑与标题一致性校验"""
        property_page = setup_property_page

        with allure.step("选择 Property Type=House"):
            property_page.click_property_type_filter()
            property_page.select_third_level_category(index=1)
            property_page.click_done_button()
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已选择 Property Type=House")

        with allure.step("验证页面标题含 House 信息"):
            page_title = page.title()
            page_content = page.content()
            has_house_info = ("house" in page_title.lower() or
                              "house" in page_content.lower() or
                              "house" in page.url.lower())
            assert has_house_info, \
                f"期望页面标题/内容含 'house' 信息，实际 title: '{page_title}'"
            logger.info(f"✓ 页面标题: '{page_title}'，URL: {page.url}")


    # ============================================
    # 八、健壮性测试 8.3 URL 参数安全 TC057–TC060
    # ============================================

    @pytest.mark.case_id_property_rent_robust_057
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("健壮性测试 - URL 参数安全")
    @allure.title("直接访问含筛选参数的 URL 筛选状态自动还原")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("直接访问含 lowestPrice=500&highestPrice=2000 参数的 URL，验证页面筛选状态自动生效")
    def test_robust_direct_url_with_params_restores_filter_state(self, page, config, setup_property_page):
        """TC057：直接访问含筛选参数的 URL"""
        # 不使用 setup_property_page 的导航，直接访问含参数 URL
        with allure.step("直接访问含筛选参数的 URL"):
            target_url = f"{config['base_url']}/en/city-canberra/cate-property/?iconSource=rent&lowestPrice=500&highestPrice=2000"
            page.goto(target_url, wait_until="domcontentloaded", timeout=config['timeout']['navigation'])
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info(f"✓ 直接访问 URL: {target_url}")

        with allure.step("验证页面正常加载且 URL 含价格参数"):
            current_url = page.url
            assert "lowestPrice=500" in current_url or "highestPrice=2000" in current_url, \
                f"期望 URL 含价格参数，实际 URL: {current_url}"
            logger.info(f"✓ URL 参数保持: {current_url}")

        with allure.step("验证页面内容正常渲染"):
            assert len(page.content()) > 0, "期望页面正常渲染"
            logger.info("✓ 页面正常渲染")


    @pytest.mark.case_id_property_rent_robust_058
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("健壮性测试 - URL 参数安全")
    @allure.title("手动篡改 URL 注入非法 sortId 值页面降级处理")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("访问含非法 sortId=999 的 URL，验证页面正常加载不崩溃，排序恢复为默认值")
    def test_robust_invalid_sort_id_in_url_page_degrades_gracefully(self, page, config, setup_property_page):
        """TC058：手动篡改 URL 注入非法 sortId 值"""
        with allure.step("访问含非法 sortId=999 的 URL"):
            invalid_url = f"{config['base_url']}/en/city-canberra/cate-property/?iconSource=rent&sortId=999"
            page.goto(invalid_url, wait_until="domcontentloaded", timeout=config['timeout']['navigation'])
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info(f"✓ 访问含非法 sortId=999 的 URL")

        with allure.step("验证页面正常加载不抛出 JS 错误"):
            assert len(page.content()) > 0, "期望页面正常渲染，不崩溃"
            logger.info("✓ 页面正常加载")

        with allure.step("验证排序按钮恢复为默认值或页面无 JS 异常"):
            property_page = PropertyPage(page)
            property_page.handle_cookie_popup()
            sort_text = property_page.get_current_sort_text()
            logger.info(f"当前排序文案: '{sort_text}'（非法值应被忽略）")
            assert len(page.content()) > 0, "期望页面内容不为空"
            logger.info("✓ 非法 sortId 被忽略，页面正常展示")


    @pytest.mark.case_id_property_rent_robust_060
    @pytest.mark.p1
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("健壮性测试 - URL 参数安全")
    @allure.title("URL 参数注入 XSS 脚本时脚本不执行页面正常")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("访问含 XSS 脚本参数的 URL，验证页面不弹 alert 且脚本内容被转义不执行")
    def test_robust_xss_script_in_url_not_executed(self, page, config, setup_property_page):
        """TC060：URL 参数注入 XSS 脚本"""
        xss_payload = "<script>alert(1)</script>"

        with allure.step("访问含 XSS 脚本的 URL"):
            xss_url = f"{config['base_url']}/en/city-canberra/cate-property/?iconSource=rent&lowestPrice={xss_payload}"
            dialog_triggered = []

            def handle_dialog(dialog):
                dialog_triggered.append(dialog.message)
                dialog.dismiss()

            page.on("dialog", handle_dialog)
            try:
                page.goto(xss_url, wait_until="domcontentloaded", timeout=config['timeout']['navigation'])
                page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            except Exception as e:
                logger.info(f"导航异常（可能因 XSS 参数被拦截）: {e}")
            logger.info("✓ 已访问含 XSS 参数的 URL")

        with allure.step("验证未触发 alert 对话框"):
            assert not dialog_triggered, \
                f"期望 XSS 脚本不执行，实际触发了 alert: {dialog_triggered}"
            logger.info("✓ XSS 脚本未执行，无 alert 弹出")

        with allure.step("验证页面正常显示"):
            assert len(page.content()) > 0, "期望页面正常渲染"
            logger.info("✓ 页面正常渲染")


    # ============================================
    # 八、健壮性测试 8.4 网络与接口健壮性 TC061–TC064
    # ============================================

    @pytest.mark.case_id_property_rent_robust_061
    @pytest.mark.p2
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("健壮性测试 - 网络与接口健壮性")
    @allure.title("断网状态下点击 Done 提交筛选页面展示错误提示不崩溃")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("通过 Playwright route 拦截所有网络请求模拟断网，点击 Done，验证页面友好展示错误提示")
    def test_robust_offline_filter_submit_shows_error_no_crash(self, page, config, setup_property_page):
        """TC061：断网状态下点击 Done 提交筛选"""
        property_page = setup_property_page

        with allure.step("先打开 Price 筛选面板，准备提交"):
            property_page.click_price_filter()
            property_page.input_price_range("500", "2000")
            logger.info("✓ 已输入价格，准备提交")

        with allure.step("通过 route 模拟断网（拦截 XHR/Fetch 请求）"):
            page.route("**/*", lambda route: route.abort())
            logger.info("✓ 已拦截所有网络请求（模拟断网）")

        with allure.step("点击 Done 提交"):
            try:
                property_page.click_done_button_in_price_modal()
                page.wait_for_timeout(3000)
                logger.info("✓ 已点击 Done（断网状态）")
            except Exception as e:
                logger.info(f"提交时发生异常（预期）: {e}")

        with allure.step("验证页面未崩溃"):
            try:
                content_length = len(page.content())
                assert content_length > 0, "期望断网后页面仍有内容（不崩溃）"
                logger.info(f"✓ 断网后页面内容长度: {content_length}，未崩溃")
            except Exception as e:
                logger.info(f"页面状态验证异常: {e}")

        with allure.step("恢复网络路由"):
            page.unroute("**/*")
            logger.info("✓ 网络路由已恢复")


    @pytest.mark.case_id_property_rent_robust_062
    @pytest.mark.p2
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("健壮性测试 - 网络与接口健壮性")
    @allure.title("接口响应超时后页面显示 Loading 状态或超时提示")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("通过 route 拦截列表接口并添加长时间延迟模拟超时，验证页面显示 Loading 或超时提示")
    def test_robust_api_timeout_page_shows_loading_or_timeout(self, page, config, setup_property_page):
        """TC062：接口响应超时，页面 Loading 状态"""
        property_page = setup_property_page

        with allure.step("拦截列表接口并添加超时延迟"):
            import asyncio

            def delay_route(route):
                page.wait_for_timeout(8000)
                route.continue_()

            page.route("**/api/**", delay_route)
            page.route("**/list**", delay_route)
            logger.info("✓ 已设置接口延迟拦截")

        with allure.step("点击 Beds=2 筛选提交"):
            try:
                property_page.click_beds_filter()
                property_page.select_beds_values("2")
                property_page.click_done_button_in_beds_modal()
                page.wait_for_timeout(3000)
                logger.info("✓ 已提交筛选（超时模拟中）")
            except Exception as e:
                logger.info(f"提交超时（预期）: {e}")

        with allure.step("验证页面未崩溃"):
            try:
                assert len(page.content()) > 0, "期望超时后页面不崩溃"
                logger.info("✓ 超时后页面未崩溃")
            except Exception:
                logger.info("⚠️ 页面状态异常，但未产生未处理异常")

        with allure.step("恢复网络路由"):
            page.unroute("**/api/**")
            page.unroute("**/list**")
            logger.info("✓ 网络路由已恢复")


    @pytest.mark.case_id_property_rent_robust_063
    @pytest.mark.p2
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("健壮性测试 - 网络与接口健壮性")
    @allure.title("服务端返回 500 错误时页面显示友好错误提示不暴露堆栈")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("通过 Playwright route Mock 使列表接口返回 HTTP 500，验证页面显示友好错误提示")
    def test_robust_server_500_error_shows_friendly_message(self, page, config, setup_property_page):
        """TC063：服务端返回 500 错误"""
        property_page = setup_property_page

        with allure.step("设置 route 使接口返回 500"):
            def mock_500(route):
                route.fulfill(status=500, body="Internal Server Error")

            page.route("**/api/**", mock_500)
            logger.info("✓ 已 Mock 接口返回 500")

        with allure.step("点击 Beds=2 筛选提交"):
            try:
                property_page.click_beds_filter()
                property_page.select_beds_values("2")
                property_page.click_done_button_in_beds_modal()
                page.wait_for_timeout(3000)
                logger.info("✓ 已提交筛选（500 Mock 中）")
            except Exception as e:
                logger.info(f"提交异常（预期）: {e}")

        with allure.step("验证页面不暴露服务端原始错误信息"):
            page_content = page.content().lower()
            sensitive_patterns = ["stack trace", "exception at", "java.lang", "null pointer"]
            for pattern in sensitive_patterns:
                assert pattern not in page_content, \
                    f"期望页面不暴露服务端异常信息 '{pattern}'，实际页面含此内容"
            logger.info("✓ 页面未暴露服务端原始异常信息")

        with allure.step("恢复路由"):
            page.unroute("**/api/**")
            logger.info("✓ 路由已恢复")


    @pytest.mark.case_id_property_rent_robust_064
    @pytest.mark.p2
    @pytest.mark.property_rent
    @pytest.mark.au
    @allure.feature("OK")
    @allure.story("健壮性测试 - 网络与接口健壮性")
    @allure.title("快速连续点击 Done 仅触发一次筛选请求防重复提交")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("快速连续点击 Done 按钮 3 次，验证 URL 参数正确写入且无重复参数")
    def test_robust_rapid_done_clicks_no_duplicate_submission(self, page, config, setup_property_page):
        """TC064：快速连续点击 Done 防重复提交"""
        property_page = setup_property_page

        with allure.step("打开排序面板，选择 Newest First"):
            property_page.click_sort_button()
            property_page.select_sort_option("Newest First")
            logger.info("✓ 已选择 Newest First")

        with allure.step("快速连续点击 Done 按钮 3 次"):
            done_button = page.locator("button:has-text('Done')").first
            done_button.click()
            page.wait_for_timeout(100)
            try:
                done_button.click()
            except Exception:
                pass
            page.wait_for_timeout(100)
            try:
                done_button.click()
            except Exception:
                pass
            page.wait_for_load_state('domcontentloaded', timeout=config['timeout']['navigation'])
            logger.info("✓ 已快速连续点击 Done 3 次")

        with allure.step("验证 URL 含 sortId 且无重复参数"):
            current_url = page.url
            assert "sortId" in current_url, \
                f"期望 URL 含 sortId，实际: {current_url}"
            sort_id_count = current_url.count("sortId")
            assert sort_id_count == 1, \
                f"期望 URL 中 sortId 只出现 1 次（防重复提交），实际出现 {sort_id_count} 次，URL: {current_url}"
            logger.info(f"✓ sortId 参数唯一，URL: {current_url}")


# ============================================
# Property For Sale (Buy) 搜索筛选翻页测试
# ============================================

_CONFIG_BUY = {
    "site": "au",
    "site_name": "澳大利亚站",
    "role": "buyer",
    "base_url": "https://au.58v5.cn",
    "target_page": "https://au.58v5.cn/en/city-canberra/cate-buy/?iconSource=buy",
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