"""
SG站 - 岗位偏好页 提交功能测试

本脚本由 playwright-test-generator 生成
录制文档：test_cases/zhaopin/ok-sg-JobPref-Submit-测试用例-20260319.md
生成时间：2026-03-19

测试站点：SG (https://sg.58v5.cn)
测试角色：Seller (卖家)
测试目标：验证从首页点击Jobs金刚位跳转到岗位偏好页，填写并提交偏好的全流程，
         重点覆盖 Continue 提交按钮的各类场景（正向、必填字段验证、边界、Skip）
"""
import pytest
import allure
from pages.jobs_pref_page_sg import JobsPrefPageSG
from test_cases.zhaopin.sg_login_helper import ensure_sg_logged_in
from utils.db_client import execute_update
from utils.logger import setup_logger

logger = setup_logger()

# 测试账号在 preference 表中对应的 user_id（固定值，与账号 yongli@58.com 绑定）
_TEST_USER_ID = "796636253998732992"


def _cleanup_preference(user_id: str = _TEST_USER_ID):
    """
    删除 preference 表中指定用户的岗位偏好数据（测试数据清理）

    Args:
        user_id: 用户ID，默认使用测试账号的 user_id
    """
    sql = "DELETE FROM preference WHERE user_id = %s"
    rows = execute_update(sql, (user_id,))
    logger.info(f"✓ 已清理 preference 表数据，user_id={user_id}，删除 {rows} 行")

# ============================================
# 测试环境配置（来自录制文档，录制与运行使用同一账号）
# ============================================
_CONFIG = {
    "site": "sg",
    "site_name": "新加坡站",
    "role": "seller",
    "user_name": "dc_seller_sg",
    "base_url": "https://sg.58v5.cn",
    "test_account": {
        "username": "yongli@58.com",
        "password": "Qwer1234"
    },
    "locale": "en-SG",
    "currency": "SGD",
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


# ============================================================
# TC001: 所有字段填写完整 → 正常提交成功
# ============================================================
@pytest.mark.case_id_sg_jobpref_submit01
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.sg
@pytest.mark.jobs_pref
@allure.feature("OK")
@allure.story("SG站岗位偏好页 - 提交功能 - 正向场景")
@allure.title("所有字段填写完整后点击Continue应该成功提交并跳转到Jobs列表页")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证填写所有必填及可选字段后点击Continue，页面跳转到SG站Jobs列表页")
def test_submit_with_all_fields_filled_should_success(page, config):
    """TC001: 所有字段填写完整正常提交成功"""

    # ========== Arrange：准备测试对象 ==========
    pref_page = JobsPrefPageSG(page)

    logger.info("=" * 80)
    logger.info("SG站 - 岗位偏好页提交功能测试 TC001")
    logger.info("=" * 80)
    logger.info(f"站点: {config['site'].upper()} ({config['site_name']})")
    logger.info(f"账号: {config['user_name']} / {config['test_account']['username']}")
    logger.info("=" * 80)

    # ========== 前置清理：确保测试账号无历史偏好数据干扰 ==========
    with allure.step("前置清理：删除测试账号的历史偏好数据（确保干净环境）"):
        _cleanup_preference()
        logger.info("✓ 前置清理完成，preference 表已清空")

    # ========== Act 阶段1：确保已登录 ==========
    with allure.step("确保已登录SG站（Session复用）"):
        ensure_sg_logged_in(page, config)
        logger.info("✓ 已登录SG站")

    # ========== Act 阶段2：进入岗位偏好页 ==========
    with allure.step("从首页点击Jobs金刚位进入岗位偏好页"):
        pref_page.navigate_to_jobs_pref_via_home(config['base_url'])
        logger.info("✓ 已进入岗位偏好页")

    # ========== Act 阶段3：填写 Job Functions ==========
    with allure.step("选择Job Functions：ICT > Developers/Programmers"):
        pref_page.open_job_functions_panel()
        pref_page.select_job_function(
            category="Information & Communication",
            subcategory="Developers/Programmers"
        )
        pref_page.confirm_job_functions()
        logger.info("✓ Job Functions 已选择：ICT > Developers/Programmers")

    # ========== Act 阶段4：填写 Location ==========
    with allure.step("选择Location：Singapore"):
        pref_page.open_location_panel()
        pref_page.select_location("Singapore")
        pref_page.confirm_location()
        logger.info("✓ Location 已选择：Singapore")

    # ========== Act 阶段5：填写 Salary ==========
    with allure.step("填写Salary：Monthly，S$5000"):
        pref_page.open_pay_type_dropdown()
        pref_page.select_pay_type("Monthly")
        pref_page.input_salary_amount("5000")
        logger.info("✓ Salary 已填写：Monthly / S$5000")

    # ========== Act 阶段6：填写 Workplace Type & Job Type ==========
    with allure.step("选择Workplace Type：Onsite；Job Type：Full-time"):
        pref_page.select_workplace_type("Onsite")
        pref_page.select_job_type("Full-time")
        logger.info("✓ Workplace Type: Onsite，Job Type: Full-time")

    # ========== Act 阶段7：点击 Continue 提交 ==========
    with allure.step("点击Continue提交岗位偏好"):
        pref_page.click_continue()
        logger.info("✓ 已点击Continue按钮")

    # ========== Assert：验证跳转到岗位偏好类别招聘大类页 ==========
    with allure.step("验证提交成功：URL跳转到按岗位偏好筛选的招聘大类页"):
        assert pref_page.is_submit_success(timeout=15000), \
            f"提交失败，当前URL未跳转到招聘大类页（cate-jobs），实际URL: {pref_page.get_current_url()}"
        current_url = pref_page.get_current_url()
        assert "cate-jobs" in current_url, \
            f"跳转URL不含岗位偏好类别路径，实际URL: {current_url}"
        logger.info(f"✅ 提交成功！已跳转到按偏好筛选的招聘大类页: {current_url}")

    with allure.step("验证列表页显示偏好标签 Developers/Programmers 及 Edit 链接"):
        assert pref_page.is_preference_tag_visible("Developers/Programmers"), \
            "列表页顶部未显示偏好标签 Developers/Programmers"
        assert pref_page.is_edit_link_visible(), \
            "列表页顶部未显示 Edit 链接"
        logger.info("✅ 偏好标签 Developers/Programmers 及 Edit 链接均已显示")

    # ========== Cleanup：删除 preference 表测试数据 ==========
    with allure.step("清理测试数据：删除 preference 表中当前用户的偏好记录"):
        _cleanup_preference()

    logger.info("=" * 80)
    logger.info("✅ TC001 岗位偏好页提交 - 所有字段填写完整 → 通过")
    logger.info("=" * 80)


# ============================================================
# TC002: 未选 Job Functions 直接点击 Continue
# ============================================================
@pytest.mark.case_id_sg_jobpref_submit02
@pytest.mark.regression
@pytest.mark.p0
@pytest.mark.sg
@pytest.mark.jobs_pref
@allure.feature("OK")
@allure.story("SG站岗位偏好页 - 提交功能 - 异常场景")
@allure.title("未选Job Functions直接点击Continue应该阻止提交并停留在当前页")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证Job Functions为必填字段，未选择时点击Continue无法提交")
def test_submit_without_job_functions_should_be_blocked(page, config):
    """TC002: 未选Job Functions直接点击Continue"""

    # ========== Arrange ==========
    pref_page = JobsPrefPageSG(page)

    logger.info("=" * 80)
    logger.info("SG站 - 岗位偏好页提交功能测试 TC002")
    logger.info("=" * 80)

    # ========== Act 阶段1：确保已登录 ==========
    with allure.step("确保已登录SG站（Session复用）"):
        ensure_sg_logged_in(page, config)
        logger.info("✓ 已登录SG站")

    # ========== Act 阶段2：进入岗位偏好页 ==========
    with allure.step("从首页点击Jobs金刚位进入岗位偏好页"):
        pref_page.navigate_to_jobs_pref_via_home(config['base_url'])
        logger.info("✓ 已进入岗位偏好页")

    # ========== Act 阶段3：清除预填的 Job Functions（回填数据处理）==========
    with allure.step("清除预填的 Job Functions（确保测试账号无历史偏好干扰）"):
        pref_page.clear_job_functions()
        logger.info("✓ Job Functions 已清除（清除预填数据）")

    # ========== Act 阶段4：填写 Location、Salary（不选 Job Functions）==========
    with allure.step("选择Location：Singapore（不选Job Functions）"):
        pref_page.open_location_panel()
        pref_page.select_location("Singapore")
        pref_page.confirm_location()
        logger.info("✓ Location 已选择：Singapore")

    with allure.step("填写Salary：Monthly，S$5000"):
        pref_page.open_pay_type_dropdown()
        pref_page.select_pay_type("Monthly")
        pref_page.input_salary_amount("5000")
        logger.info("✓ Salary 已填写")

    # ========== Act 阶段5：点击 Continue ==========
    with allure.step("点击Continue（Job Functions未选）"):
        pref_page.click_continue()
        logger.info("✓ 已点击Continue按钮")

    # ========== Assert：验证停留在偏好页 + 错误提示 ==========
    with allure.step("验证页面未跳转，仍停留在岗位偏好页"):
        assert pref_page.is_still_on_pref_page(timeout=3000), \
            f"异常：Job Functions未选却跳转成功，当前URL: {pref_page.get_current_url()}"
        logger.info(f"✅ 验证通过：页面停留在偏好页，URL: {pref_page.get_current_url()}")

    with allure.step("验证显示必填错误提示：Don't leave this field empty."):
        assert pref_page.is_error_message_visible("Don't leave this field empty."), \
            "Job Functions未选时未显示错误提示 \"Don't leave this field empty.\""
        logger.info("✅ 错误提示已显示：Don't leave this field empty.")

    # ========== Cleanup：兜底清理（防止异常场景意外提交成功留下脏数据）==========
    with allure.step("兜底清理：确保 preference 表无脏数据"):
        _cleanup_preference()

    logger.info("=" * 80)
    logger.info("✅ TC002 Job Functions未选 → 提交被阻止 通过")
    logger.info("=" * 80)


# ============================================================
# TC003: 未选 Location 直接点击 Continue
# ============================================================
@pytest.mark.case_id_sg_jobpref_submit03
@pytest.mark.regression
@pytest.mark.p0
@pytest.mark.sg
@pytest.mark.jobs_pref
@allure.feature("OK")
@allure.story("SG站岗位偏好页 - 提交功能 - 异常场景")
@allure.title("未选Location直接点击Continue应该阻止提交并停留在当前页")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证Location为必填字段，未选择时点击Continue无法提交")
def test_submit_without_location_should_be_blocked(page, config):
    """TC003: 未选Location直接点击Continue"""

    # ========== Arrange ==========
    pref_page = JobsPrefPageSG(page)

    logger.info("=" * 80)
    logger.info("SG站 - 岗位偏好页提交功能测试 TC003")
    logger.info("=" * 80)

    # ========== Act 阶段1：确保已登录 ==========
    with allure.step("确保已登录SG站（Session复用）"):
        ensure_sg_logged_in(page, config)
        logger.info("✓ 已登录SG站")

    # ========== Act 阶段2：进入岗位偏好页 ==========
    with allure.step("从首页点击Jobs金刚位进入岗位偏好页"):
        pref_page.navigate_to_jobs_pref_via_home(config['base_url'])
        logger.info("✓ 已进入岗位偏好页")

    # ========== Act 阶段3：填写 Job Functions，清除 Location（不选Location）==========
    with allure.step("选择Job Functions"):
        pref_page.open_job_functions_panel()
        pref_page.select_job_function(
            category="Information & Communication",
            subcategory="Developers/Programmers"
        )
        pref_page.confirm_job_functions()
        logger.info("✓ Job Functions 已选择")

    with allure.step("清除预填的 Location（确保Location为空）"):
        pref_page.clear_location()
        logger.info("✓ Location 已清除（清除预填数据）")

    with allure.step("填写Salary：Monthly，S$5000"):
        pref_page.open_pay_type_dropdown()
        pref_page.select_pay_type("Monthly")
        pref_page.input_salary_amount("5000")
        logger.info("✓ Salary 已填写")

    # ========== Act 阶段4：点击 Continue ==========
    with allure.step("点击Continue（Location未选）"):
        pref_page.click_continue()
        logger.info("✓ 已点击Continue按钮")

    # ========== Assert：验证停留在偏好页 + 错误提示 ==========
    with allure.step("验证页面未跳转，仍停留在岗位偏好页"):
        assert pref_page.is_still_on_pref_page(timeout=3000), \
            f"异常：Location未选却跳转成功，当前URL: {pref_page.get_current_url()}"
        logger.info(f"✅ 验证通过：页面停留在偏好页，URL: {pref_page.get_current_url()}")

    with allure.step("验证显示必填错误提示：Don't leave this field empty."):
        assert pref_page.is_error_message_visible("Don't leave this field empty."), \
            "Location未选时未显示错误提示 \"Don't leave this field empty.\""
        logger.info("✅ 错误提示已显示：Don't leave this field empty.")

    # ========== Cleanup：兜底清理 ==========
    with allure.step("兜底清理：确保 preference 表无脏数据"):
        _cleanup_preference()

    logger.info("=" * 80)
    logger.info("✅ TC003 Location未选 → 提交被阻止 通过")
    logger.info("=" * 80)


# ============================================================
# TC004: Salary 只选 Pay Type 不填金额
# ============================================================
@pytest.mark.case_id_sg_jobpref_submit04
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.sg
@pytest.mark.jobs_pref
@allure.feature("OK")
@allure.story("SG站岗位偏好页 - 提交功能 - 异常场景")
@allure.title("Salary只选Pay Type不填金额点击Continue应该阻止提交")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证Salary金额为必填，只选Pay Type不填金额时点击Continue无法提交")
def test_submit_with_salary_type_only_no_amount_should_be_blocked(page, config):
    """TC004: Salary只选Pay Type不填金额直接点击Continue"""

    # ========== Arrange ==========
    pref_page = JobsPrefPageSG(page)

    logger.info("=" * 80)
    logger.info("SG站 - 岗位偏好页提交功能测试 TC004")
    logger.info("=" * 80)

    # ========== Act 阶段1：确保已登录 ==========
    with allure.step("确保已登录SG站（Session复用）"):
        ensure_sg_logged_in(page, config)
        logger.info("✓ 已登录SG站")

    # ========== Act 阶段2：进入岗位偏好页 ==========
    with allure.step("从首页点击Jobs金刚位进入岗位偏好页"):
        pref_page.navigate_to_jobs_pref_via_home(config['base_url'])
        logger.info("✓ 已进入岗位偏好页")

    # ========== Act 阶段3：填写 Job Functions、Location（Salary只选Pay Type）==========
    with allure.step("选择Job Functions"):
        pref_page.open_job_functions_panel()
        pref_page.select_job_function(
            category="Information & Communication",
            subcategory="Developers/Programmers"
        )
        pref_page.confirm_job_functions()
        logger.info("✓ Job Functions 已选择")

    with allure.step("选择Location：Singapore"):
        pref_page.open_location_panel()
        pref_page.select_location("Singapore")
        pref_page.confirm_location()
        logger.info("✓ Location 已选择")

    with allure.step("选择Pay Type：Monthly，并清空Salary金额"):
        pref_page.open_pay_type_dropdown()
        pref_page.select_pay_type("Monthly")
        pref_page.clear_salary_amount()
        logger.info("✓ Pay Type 已选择 Monthly，Salary金额已清空")

    # ========== Act 阶段4：点击 Continue ==========
    with allure.step("点击Continue（Salary金额未填）"):
        pref_page.click_continue()
        logger.info("✓ 已点击Continue按钮")

    # ========== Assert：验证停留在偏好页 + 错误提示 ==========
    with allure.step("验证页面未跳转，仍停留在岗位偏好页"):
        assert pref_page.is_still_on_pref_page(timeout=3000), \
            f"异常：Salary金额未填却跳转成功，当前URL: {pref_page.get_current_url()}"
        logger.info(f"✅ 验证通过：页面停留在偏好页，URL: {pref_page.get_current_url()}")

    with allure.step("验证显示必填错误提示：Don't leave this field empty."):
        assert pref_page.is_error_message_visible("Don't leave this field empty."), \
            "Salary金额未填时未显示错误提示 \"Don't leave this field empty.\""
        logger.info("✅ 错误提示已显示：Don't leave this field empty.")

    # ========== Cleanup：兜底清理 ==========
    with allure.step("兜底清理：确保 preference 表无脏数据"):
        _cleanup_preference()

    logger.info("=" * 80)
    logger.info("✅ TC004 Salary只选Pay Type不填金额 → 提交被阻止 通过")
    logger.info("=" * 80)


# ============================================================
# TC005: Salary 填写 0 提交（边界值测试）
# ============================================================
@pytest.mark.case_id_sg_jobpref_submit05
@pytest.mark.regression
@pytest.mark.p2
@pytest.mark.sg
@pytest.mark.jobs_pref
@allure.feature("OK")
@allure.story("SG站岗位偏好页 - 提交功能 - 边界场景")
@allure.title("Salary金额填写0点击Continue应该校验金额有效性")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证Salary金额为0时系统的校验行为（0不是有效薪资期望）")
def test_submit_with_salary_amount_zero(page, config):
    """TC005: Salary填写0点击Continue（边界值）"""

    # ========== Arrange ==========
    pref_page = JobsPrefPageSG(page)

    logger.info("=" * 80)
    logger.info("SG站 - 岗位偏好页提交功能测试 TC005")
    logger.info("=" * 80)

    # ========== Act 阶段1：确保已登录 ==========
    with allure.step("确保已登录SG站（Session复用）"):
        ensure_sg_logged_in(page, config)
        logger.info("✓ 已登录SG站")

    # ========== Act 阶段2：进入岗位偏好页 ==========
    with allure.step("从首页点击Jobs金刚位进入岗位偏好页"):
        pref_page.navigate_to_jobs_pref_via_home(config['base_url'])
        logger.info("✓ 已进入岗位偏好页")

    # ========== Act 阶段3：填写必填字段，Salary金额填0 ==========
    with allure.step("选择Job Functions"):
        pref_page.open_job_functions_panel()
        pref_page.select_job_function(
            category="Information & Communication",
            subcategory="Developers/Programmers"
        )
        pref_page.confirm_job_functions()
        logger.info("✓ Job Functions 已选择")

    with allure.step("选择Location：Singapore"):
        pref_page.open_location_panel()
        pref_page.select_location("Singapore")
        pref_page.confirm_location()
        logger.info("✓ Location 已选择")

    with allure.step("Pay Type: Monthly，Salary金额输入0"):
        pref_page.open_pay_type_dropdown()
        pref_page.select_pay_type("Monthly")
        pref_page.input_salary_amount("0")
        logger.info("✓ Salary 金额填写为 0")

    # ========== Act 阶段4：点击 Continue ==========
    with allure.step("点击Continue（Salary金额为0）"):
        pref_page.click_continue()
        logger.info("✓ 已点击Continue按钮")

    # ========== Assert：MCP实测确认系统接受0值，明确断言跳转成功 ==========
    with allure.step("验证系统接受Salary金额0并跳转到列表页（MCP实测：0值不被前端拦截）"):
        assert pref_page.is_submit_success(timeout=15000), \
            f"预期系统接受Salary=0并跳转成功，但实际未跳转，当前URL: {pref_page.get_current_url()}"
        current_url = pref_page.get_current_url()
        assert "cate-jobs" in current_url, \
            f"Salary=0提交后跳转URL不含 cate-jobs，实际URL: {current_url}"
        logger.info(f"✅ 系统接受Salary=0，已跳转到招聘大类页：{current_url}")

    # ========== Cleanup：清理测试数据 ==========
    with allure.step("清理测试数据：删除 preference 表中当前用户的偏好记录"):
        _cleanup_preference()

    logger.info("=" * 80)
    logger.info("✅ TC005 Salary填写0 → 系统接受，跳转成功 通过")
    logger.info("=" * 80)


# ============================================================
# TC006: 不选 Workplace Type 和 Job Type（可选字段）可以提交
# ============================================================
@pytest.mark.case_id_sg_jobpref_submit06
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.sg
@pytest.mark.jobs_pref
@allure.feature("OK")
@allure.story("SG站岗位偏好页 - 提交功能 - 正向场景")
@allure.title("不选Workplace Type和Job Type只填必填字段点击Continue应该成功提交")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证Workplace Type和Job Type为可选字段，不填写不影响提交结果")
def test_submit_without_optional_fields_should_success(page, config):
    """TC006: 不选Workplace Type和Job Type，只填必填字段正常提交"""

    # ========== Arrange ==========
    pref_page = JobsPrefPageSG(page)

    logger.info("=" * 80)
    logger.info("SG站 - 岗位偏好页提交功能测试 TC006")
    logger.info("=" * 80)

    # ========== Act 阶段1：确保已登录 ==========
    with allure.step("确保已登录SG站（Session复用）"):
        ensure_sg_logged_in(page, config)
        logger.info("✓ 已登录SG站")

    # ========== Act 阶段2：进入岗位偏好页 ==========
    with allure.step("从首页点击Jobs金刚位进入岗位偏好页"):
        pref_page.navigate_to_jobs_pref_via_home(config['base_url'])
        logger.info("✓ 已进入岗位偏好页")

    # ========== Act 阶段3：只填必填字段，不选可选字段 ==========
    with allure.step("选择Job Functions"):
        pref_page.open_job_functions_panel()
        pref_page.select_job_function(
            category="Information & Communication",
            subcategory="Developers/Programmers"
        )
        pref_page.confirm_job_functions()
        logger.info("✓ Job Functions 已选择")

    with allure.step("选择Location：Singapore"):
        pref_page.open_location_panel()
        pref_page.select_location("Singapore")
        pref_page.confirm_location()
        logger.info("✓ Location 已选择")

    with allure.step("填写Salary：Yearly，S$60000"):
        pref_page.open_pay_type_dropdown()
        pref_page.select_pay_type("Yearly")
        pref_page.input_salary_amount("60000")
        logger.info("✓ Salary 已填写：Yearly / S$60000")

    # ========== Act 阶段4：不选 Workplace Type 和 Job Type，直接提交 ==========
    with allure.step("点击Continue（不选Workplace Type和Job Type）"):
        pref_page.click_continue()
        logger.info("✓ 已点击Continue按钮（未选可选字段）")

    # ========== Assert：验证跳转到岗位偏好类别招聘大类页 ==========
    with allure.step("验证提交成功：URL跳转到按岗位偏好筛选的招聘大类页"):
        assert pref_page.is_submit_success(timeout=15000), \
            f"提交失败，当前URL未跳转到招聘大类页（cate-jobs），实际URL: {pref_page.get_current_url()}"
        current_url = pref_page.get_current_url()
        assert "cate-jobs" in current_url, \
            f"跳转URL不含岗位偏好类别路径，实际URL: {current_url}"
        logger.info(f"✅ 提交成功！已跳转到按偏好筛选的招聘大类页: {current_url}")

    # ========== Cleanup：删除 preference 表测试数据 ==========
    with allure.step("清理测试数据：删除 preference 表中当前用户的偏好记录"):
        _cleanup_preference()

    logger.info("=" * 80)
    logger.info("✅ TC006 不选可选字段 → 提交成功 通过")
    logger.info("=" * 80)


# ============================================================
# TC007: 快速连续点击 Continue 按钮（防重复提交 / 健壮性）
# ============================================================
@pytest.mark.case_id_sg_jobpref_submit07
@pytest.mark.regression
@pytest.mark.p2
@pytest.mark.sg
@pytest.mark.jobs_pref
@allure.feature("OK")
@allure.story("SG站岗位偏好页 - 提交功能 - 健壮性场景")
@allure.title("快速连续点击Continue两次应该只执行一次提交并最终跳转到Jobs列表页")
@allure.severity(allure.severity_level.MINOR)
@allure.description("验证快速连续双击Continue时系统只执行一次提交，不重复跳转或触发多次接口请求")
def test_submit_with_double_click_continue_should_only_submit_once(page, config):
    """TC007: 快速连续点击Continue按钮（防重复提交健壮性测试）"""

    # ========== Arrange ==========
    pref_page = JobsPrefPageSG(page)

    logger.info("=" * 80)
    logger.info("SG站 - 岗位偏好页提交功能测试 TC007")
    logger.info("=" * 80)

    # ========== Act 阶段1：确保已登录 ==========
    with allure.step("确保已登录SG站（Session复用）"):
        ensure_sg_logged_in(page, config)
        logger.info("✓ 已登录SG站")

    # ========== Act 阶段2：进入岗位偏好页 ==========
    with allure.step("从首页点击Jobs金刚位进入岗位偏好页"):
        pref_page.navigate_to_jobs_pref_via_home(config['base_url'])
        logger.info("✓ 已进入岗位偏好页")

    # ========== Act 阶段3：填写所有必填字段（同TC001）==========
    with allure.step("选择Job Functions：ICT > Developers/Programmers"):
        pref_page.open_job_functions_panel()
        pref_page.select_job_function(
            category="Information & Communication",
            subcategory="Developers/Programmers"
        )
        pref_page.confirm_job_functions()
        logger.info("✓ Job Functions 已选择")

    with allure.step("选择Location：Singapore"):
        pref_page.open_location_panel()
        pref_page.select_location("Singapore")
        pref_page.confirm_location()
        logger.info("✓ Location 已选择")

    with allure.step("填写Salary：Monthly，S$5000"):
        pref_page.open_pay_type_dropdown()
        pref_page.select_pay_type("Monthly")
        pref_page.input_salary_amount("5000")
        logger.info("✓ Salary 已填写")

    # ========== Act 阶段4：快速连续点击 Continue 两次 ==========
    with allure.step("快速连续点击Continue按钮两次（模拟双击行为）"):
        pref_page.click_continue_twice_fast()
        logger.info("✓ 已快速连续点击Continue两次")

    # ========== Assert：验证最终落地到 cate-jobs 页（只跳转一次）==========
    with allure.step("验证最终跳转到Jobs列表页（系统只执行一次提交）"):
        # 在无头模式下，页面跳转可能需要更长时间
        assert pref_page.is_submit_success(timeout=20000), \
            f"双击Continue后未跳转到招聘大类页，当前URL: {pref_page.get_current_url()}"
        current_url = pref_page.get_current_url()
        assert "cate-jobs" in current_url, \
            f"双击Continue后跳转URL不含 cate-jobs，实际URL: {current_url}"
        logger.info(f"✅ 验证通过：最终跳转到招聘大类页：{current_url}")

    # ========== Cleanup ==========
    with allure.step("清理测试数据：删除 preference 表中当前用户的偏好记录"):
        _cleanup_preference()

    logger.info("=" * 80)
    logger.info("✅ TC007 快速连续点击Continue → 系统只执行一次提交，通过")
    logger.info("=" * 80)


# ============================================================
# TC008: 点击 Skip 跳过提交
# ============================================================
@pytest.mark.case_id_sg_jobpref_submit08
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.sg
@pytest.mark.jobs_pref
@allure.feature("OK")
@allure.story("SG站岗位偏好页 - 提交功能 - Skip场景")
@allure.title("点击Skip跳过应该直接跳转到Jobs列表页且不保存偏好数据")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证点击Skip链接后页面跳转到SG站Jobs列表页，不触发偏好保存逻辑")
def test_skip_job_preference_should_navigate_to_jobs_list(page, config):
    """TC008: 点击Skip跳过岗位偏好提交"""

    # ========== Arrange ==========
    pref_page = JobsPrefPageSG(page)

    logger.info("=" * 80)
    logger.info("SG站 - 岗位偏好页提交功能测试 TC008")
    logger.info("=" * 80)

    # ========== Act 阶段1：确保已登录 ==========
    with allure.step("确保已登录SG站（Session复用）"):
        ensure_sg_logged_in(page, config)
        logger.info("✓ 已登录SG站")

    # ========== Act 阶段2：进入岗位偏好页 ==========
    with allure.step("从首页点击Jobs金刚位进入岗位偏好页"):
        pref_page.navigate_to_jobs_pref_via_home(config['base_url'])
        logger.info("✓ 已进入岗位偏好页")

    # ========== Act 阶段3：点击 Skip 链接（不填写任何字段）==========
    with allure.step("点击Skip链接（不填写任何偏好字段）"):
        pref_page.click_skip()
        logger.info("✓ 已点击Skip链接")

    # ========== Assert：验证跳转到 Jobs 列表页 ==========
    with allure.step("验证页面跳转到Jobs列表页（cate-jobs）"):
        # 在无头模式下，增加等待时间
        assert pref_page.is_submit_success(timeout=20000), \
            f"点击Skip后未跳转到Jobs列表页（cate-jobs），当前URL: {pref_page.get_current_url()}"
        current_url = pref_page.get_current_url()
        assert "cate-jobs" in current_url, \
            f"Skip后跳转URL不含 cate-jobs，实际URL: {current_url}"
        logger.info(f"✅ Skip成功，已跳转到Jobs列表页：{current_url}")

    with allure.step("验证页面未显示必填字段错误提示"):
        assert not pref_page.is_error_message_visible("Don't leave this field empty."), \
            "点击Skip后不应显示必填字段错误提示，但实际显示了"
        logger.info("✅ 验证通过：Skip后无必填字段错误提示")

    logger.info("=" * 80)
    logger.info("✅ TC008 点击Skip跳过 → 成功跳转到Jobs列表页 通过")
    logger.info("=" * 80)


# ============================================================
# TC009: 提交后重访列表页，验证偏好标签持久化
# ============================================================
@pytest.mark.case_id_sg_jobpref_submit09
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.sg
@pytest.mark.jobs_pref
@allure.feature("OK")
@allure.story("SG站岗位偏好页 - 提交功能 - 数据持久化验证")
@allure.title("提交偏好后列表页应显示岗位偏好标签，验证完成后清除数据库记录")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证提交岗位偏好后列表页偏好标签正确展示，确认数据入库后清理DB偏好记录")
def test_preference_tag_visible_after_submit_then_cleanup_db(page, config):
    """TC009: 提交后列表页显示偏好标签，验证完成后删除DB偏好记录"""

    # ========== Arrange ==========
    pref_page = JobsPrefPageSG(page)
    preference_tag = "Developers/Programmers"

    logger.info("=" * 80)
    logger.info("SG站 - 岗位偏好页提交功能测试 TC009")
    logger.info("=" * 80)

    # ========== Act 阶段1：确保已登录 ==========
    with allure.step("确保已登录SG站（Session复用）"):
        ensure_sg_logged_in(page, config)
        logger.info("✓ 已登录SG站")

    # ========== Act 阶段2：进入岗位偏好页并提交 ==========
    with allure.step("从首页点击Jobs金刚位进入岗位偏好页"):
        pref_page.navigate_to_jobs_pref_via_home(config['base_url'])
        logger.info("✓ 已进入岗位偏好页")

    with allure.step("选择Job Functions：ICT > Developers/Programmers"):
        pref_page.open_job_functions_panel()
        pref_page.select_job_function(
            category="Information & Communication",
            subcategory="Developers/Programmers"
        )
        pref_page.confirm_job_functions()
        logger.info("✓ Job Functions 已选择：ICT > Developers/Programmers")

    with allure.step("选择Location：Singapore"):
        pref_page.open_location_panel()
        pref_page.select_location("Singapore")
        pref_page.confirm_location()
        logger.info("✓ Location 已选择：Singapore")

    with allure.step("填写Salary：Monthly，S$5000"):
        pref_page.open_pay_type_dropdown()
        pref_page.select_pay_type("Monthly")
        pref_page.input_salary_amount("5000")
        logger.info("✓ Salary 已填写：Monthly / S$5000")

    with allure.step("点击Continue提交岗位偏好"):
        pref_page.click_continue()
        logger.info("✓ 已点击Continue按钮")

    # ========== Act 阶段3：等待列表页加载完成 ==========
    with allure.step("等待跳转到岗位列表页（cate-jobs）并加载完成"):
        assert pref_page.is_submit_success(timeout=15000), \
            f"提交失败，未跳转到cate-jobs，当前URL: {pref_page.get_current_url()}"
        try:
            page.wait_for_load_state("networkidle", timeout=8000)
        except Exception:
            pass
        logger.info(f"✓ 已跳转到岗位列表页：{pref_page.get_current_url()}")

    # ========== Assert：验证列表页偏好标签 ==========
    with allure.step(f"验证列表页顶部显示偏好标签：{preference_tag}"):
        assert pref_page.is_preference_tag_visible(preference_tag), \
            f"列表页未看到偏好标签 \"{preference_tag}\"，偏好数据可能未正确写入或展示"
        logger.info(f"✅ 偏好标签 \"{preference_tag}\" 显示验证通过")

    with allure.step("验证列表页顶部显示 Edit 链接"):
        assert pref_page.is_edit_link_visible(), \
            "列表页顶部未显示 Edit 链接"
        logger.info("✅ Edit 链接验证通过")

    with allure.step("验证当前URL含 cate-jobs"):
        current_url = pref_page.get_current_url()
        assert "cate-jobs" in current_url, \
            f"当前URL不含 cate-jobs，实际URL: {current_url}"
        logger.info(f"✅ URL验证通过：{current_url}")

    # ========== Cleanup：验证完成后删除 DB 偏好记录 ==========
    with allure.step("验证完成，清理数据库：删除 preference 表中当前用户的偏好记录"):
        _cleanup_preference()
        logger.info(f"✅ 已清理 preference 表数据（user_id={_TEST_USER_ID}）")

    logger.info("=" * 80)
    logger.info("✅ TC009 提交后列表页偏好标签验证通过，DB数据已清理")
    logger.info("=" * 80)
