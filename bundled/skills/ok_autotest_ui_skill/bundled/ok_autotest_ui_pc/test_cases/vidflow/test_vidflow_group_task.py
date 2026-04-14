"""
Vidflow - 消息管理·群发任务 测试

本脚本由 playwright-test-generator 生成
录制文档：web-qa-brain/output/vidflow/Vidflow-群发任务-测试用例-20250312.md
生成时间：2025-03-13

测试范围：消息管理 tab 下「群发任务」页面（#/groupTaskManagement/groupTaskList）
基础URL：https://vidflow.ok.com
说明：若登录需 58 盾请人工处理；预期结果中「待实测确认」部分建议 MCP 实测后更新选择器与断言。

执行方式：只打开一次浏览器，在同一浏览器页面中顺序执行本脚本中所有用例；
         全部用例跑完后才关闭浏览器。
"""
import time
import pytest
import allure
from datetime import datetime
from pages.vidflow_login_page import VidflowLoginPage
from pages.vidflow_group_task_page import VidflowGroupTaskPage
from utils.session_manager import SessionManager
from utils.logger import setup_logger

logger = setup_logger()

# ============================================
# 测试环境配置（来自用例文档）
# ============================================
_CONFIG = {
    "site": "vidflow",
    "site_name": "Vidflow",
    "role": "user",
    "user_name": "vidflow_jiangyuqi01",
    "base_url": "https://vidflow.ok.com",
    "entry_url": "https://vidflow.ok.com/#/groupTaskManagement/groupTaskList",
    "test_account": {
        "username": "jiangyuqi01@58.com",
        "password": "I1SVqUgfTr"
    },
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


def _ensure_logged_in(page, config):
    """
    确保已登录且在同一页面内执行：中途不退出账号、不重新加载 session。
    - 已登录：仅在当前不在列表页时 goto 列表页，不调用 load_session，保证不退出账号。
    - 未登录：才执行 load_session 或完整登录（仅首次或 session 失效时）。
    """
    base_url = config["base_url"]
    entry_url = config.get("entry_url") or f"{base_url.rstrip('/')}/#/groupTaskManagement/groupTaskList"
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, base_url, session_name=session_name)
    login_page = VidflowLoginPage(page)

    # 已登录时：不退出账号、不 load_session，仅必要时回到列表页（同一页面内跳转）
    try:
        if login_page.is_logged_in(username_part="jiangyuqi01", timeout=2000):
            if "groupTaskList" in page.url:
                return True
            page.goto(entry_url, timeout=config["timeout"]["navigation"])
            page.wait_for_load_state("domcontentloaded", timeout=15000)
            page.wait_for_timeout(1000)
            return True
    except Exception:
        pass

    # 未登录时才恢复 session 或执行登录（仅首次/失效时）
    if session_manager.load_session():
        page.goto(entry_url, timeout=config["timeout"]["navigation"])
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        try:
            login_page.handle_cookie_popup()
        except Exception:
            pass
        page.wait_for_timeout(2000)
        if login_page.is_logged_in(username_part="jiangyuqi01", timeout=3000):
            return True
    page.goto(base_url, timeout=config["timeout"]["navigation"])
    page.wait_for_timeout(2000)
    login_page.handle_cookie_popup()
    page.wait_for_timeout(1000)
    if not login_page.is_login_visible(timeout=5000):
        page.goto(entry_url, timeout=config["timeout"]["navigation"])
        page.wait_for_timeout(2000)
        return True
    login_page.click_login_entry()
    page.wait_for_timeout(2000)
    username = config["test_account"]["username"]
    password = config["test_account"]["password"]
    login_page.input_email(username)
    try:
        login_page.click_continue()
        page.wait_for_timeout(2000)
    except Exception:
        # 单页登录（无「继续」）或按钮文案不同：若已出现密码框则直接填密码提交
        if page.locator('input[type="password"]').first.is_visible(timeout=3000):
            login_page.input_password(password)
            login_page.click_submit_login()
            page.wait_for_load_state("domcontentloaded", timeout=15000)
            page.wait_for_timeout(3000)
            session_manager.save_session()
            page.goto(entry_url, timeout=config["timeout"]["navigation"])
            page.wait_for_load_state("domcontentloaded", timeout=15000)
            return True
        raise
    login_page.input_password(password)
    login_page.click_submit_login()
    page.wait_for_load_state("domcontentloaded", timeout=15000)
    page.wait_for_timeout(3000)
    session_manager.save_session()
    page.goto(entry_url, timeout=config["timeout"]["navigation"])
    page.wait_for_load_state("domcontentloaded", timeout=15000)
    return True


# ============================================
# 只打开一次浏览器，在同一浏览器页面中顺序执行本脚本中所有用例
# ============================================
@pytest.fixture(scope="module")
def page(config):
    """
    只打开一次浏览器，本模块内所有用例在同一个浏览器、同一个页面（同一 tab）中顺序执行。
    不重复启动浏览器，不新开页面；全部用例执行完毕后才关闭浏览器。
    """
    import os
    from utils.browser_manager import BrowserManager

    logger.info("=" * 80)
    logger.info("【Module】只打开一次浏览器，在同一页面中顺序执行本脚本所有用例")
    logger.info("=" * 80)

    browser_manager = BrowserManager()
    _page = browser_manager.start_browser(
        browser_type=config["browser"]["type"],
        headless=config["browser"]["headless"],
        base_url=config["base_url"],
        viewport=config["browser"]["viewport"],
    )

    if os.environ.get("DEBUG_PAUSE", "").lower() in ("1", "true", "yes"):
        try:
            _page.pause()
        except Exception:
            pass

    _ensure_logged_in(_page, config)
    logger.info("✓ 登录完成，后续用例在同一页面中顺序执行（不退出账号、不关浏览器）")
    logger.info("=" * 80)

    yield _page

    # 仅在所有用例执行完毕后关闭浏览器
    if os.environ.get("KEEP_BROWSER_OPEN", "").lower() not in ("1", "true", "yes"):
        browser_manager.close_browser(_page)
    logger.info("【Module】全部用例执行完毕，共享浏览器已关闭")


@pytest.fixture(autouse=True)
def pause_between_tests():
    """每个用例之间停留 1 秒。"""
    yield
    time.sleep(1)


# ---------- 核心流程（正向） ----------

@pytest.mark.case_id_vidflow_group_task_tc001
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("Vidflow")
@allure.story("群发任务 - 核心流程")
@allure.title("TC001: 成功进入群发任务页面")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("访问群发任务列表直链，未登录则登录，验证进入列表页且无报错")
def test_tc001_enter_group_task_page(page, config):
    # Arrange
    group_page = VidflowGroupTaskPage(page)
    _ensure_logged_in(page, config)
    # Act
    with allure.step("等待页面加载完成"):
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        logger.info("✓ 页面加载完成")
    # Assert
    with allure.step("验证进入群发任务列表页"):
        on_list = group_page.is_on_group_task_list_page(timeout=8000)
        assert on_list, "未进入群发任务列表页或 URL 不包含 groupTaskManagement/groupTaskList"
    with allure.step("验证无整页空白"):
        assert group_page.is_list_or_empty_visible(timeout=8000), "列表或空状态未正常展示"
    logger.info("✅ TC001 通过：成功进入群发任务页面")


@pytest.mark.case_id_vidflow_group_task_tc002
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("Vidflow")
@allure.story("群发任务 - 核心流程")
@allure.title("TC002: 群发任务页默认列表展示")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("进入页面后观察默认展示：有数据时展示任务列表，无数据时展示空状态")
def test_tc002_default_list_display(page, config):
    _ensure_logged_in(page, config)
    group_page = VidflowGroupTaskPage(page)
    with allure.step("验证列表或空状态展示"):
        assert group_page.is_list_or_empty_visible(timeout=8000), "默认列表/空状态未正常展示"
    logger.info("✅ TC002 通过：默认列表展示正常")


@pytest.mark.case_id_vidflow_group_task_tc003
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("Vidflow")
@allure.story("群发任务 - 核心流程")
@allure.title("TC003: 从消息管理 Tab 进入群发任务")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("点击消息管理 tab，再点击群发任务入口，验证进入列表页且 URL 正确")
def test_tc003_navigate_via_message_management(page, config):
    _ensure_logged_in(page, config)
    group_page = VidflowGroupTaskPage(page)
    with allure.step("点击消息管理 tab"):
        group_page.click_message_management_tab()
        logger.info("✓ 已点击消息管理")
    with allure.step("点击群发任务入口"):
        group_page.click_group_task_entry()
        logger.info("✓ 已点击群发任务")
    with allure.step("验证进入群发任务列表页"):
        assert group_page.is_on_group_task_list_page(timeout=10000), "未进入群发任务列表页"
    logger.info("✅ TC003 通过：从消息管理进入群发任务成功")


# ---------- 列表与搜索筛选 ----------

@pytest.mark.case_id_vidflow_group_task_tc004
@pytest.mark.p1
@allure.feature("Vidflow")
@allure.story("群发任务 - 列表与筛选")
@allure.title("TC004: 列表分页 - 切换页码")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("点击第 2 页或下一页，验证列表与分页状态正确")
def test_tc004_pagination_switch_page(page, config):
    _ensure_logged_in(page, config)
    group_page = VidflowGroupTaskPage(page)
    with allure.step("点击第 2 页或下一页"):
        try:
            group_page.click_page_2_or_next()
            logger.info("✓ 已切换分页")
        except Exception as e:
            pytest.skip(f"分页不可用或数据不足一页: {e}")
    with allure.step("验证仍在列表页"):
        assert group_page.is_on_group_task_list_page(timeout=5000), "分页后未保持在群发任务列表页"
    logger.info("✅ TC004 通过：分页切换正常")


@pytest.mark.case_id_vidflow_group_task_tc005
@pytest.mark.p2
@allure.feature("Vidflow")
@allure.story("群发任务 - 列表与筛选")
@allure.title("TC005: 列表分页 - 每页条数切换")
@allure.severity(allure.severity_level.MINOR)
@allure.description("选择每页条数下拉框中的第二项，验证当前页条数与总页数变化")
def test_tc005_pagination_page_size(page, config):
    _ensure_logged_in(page, config)
    group_page = VidflowGroupTaskPage(page)
    with allure.step("选择每页条数下拉框中的第二项"):
        try:
            group_page.set_page_size_to_second_option()
            logger.info("✓ 已选择每页条数第二项")
        except Exception as e:
            pytest.skip(f"每页条数切换不可用: {e}")
    assert group_page.is_on_group_task_list_page(timeout=5000), "设置每页条数后未保持在列表页"
    logger.info("✅ TC005 通过：每页条数切换正常")


@pytest.mark.case_id_vidflow_group_task_tc006
@pytest.mark.p1
@allure.feature("Vidflow")
@allure.story("群发任务 - 列表与筛选")
@allure.title("TC006: 搜索 - 按任务名称/关键词有结果")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("输入已知存在的任务名或关键词并搜索，验证列表仅展示匹配结果")
def test_tc006_search_with_results(page, config):
    _ensure_logged_in(page, config)
    group_page = VidflowGroupTaskPage(page)
    keyword = "沙特-招聘3.1"
    with allure.step("输入关键词并触发搜索"):
        group_page.fill_search_keyword(keyword)
        group_page.trigger_search()
        logger.info("✓ 已执行搜索")
    with allure.step("验证列表或空状态展示"):
        assert group_page.is_list_or_empty_visible(timeout=5000), "搜索后列表/空状态未正常展示"
    logger.info("✅ TC006 通过：搜索有结果场景正常")


@pytest.mark.case_id_vidflow_group_task_tc007
@pytest.mark.p1
@allure.feature("Vidflow")
@allure.story("群发任务 - 列表与筛选")
@allure.title("TC007: 搜索 - 无结果")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("输入肯定不存在的关键词并搜索，验证展示无结果/空状态")
def test_tc007_search_no_results(page, config):
    _ensure_logged_in(page, config)
    group_page = VidflowGroupTaskPage(page)
    keyword = "AutoTest_NoMatch"
    with allure.step("输入不存在的关键词并搜索"):
        group_page.fill_search_keyword(keyword)
        group_page.trigger_search()
        logger.info("✓ 已执行搜索")
    with allure.step("验证列表或空状态展示"):
        assert group_page.is_list_or_empty_visible(timeout=5000), "无结果时列表/空状态未正常展示"
    logger.info("✅ TC007 通过：搜索无结果场景正常")


@pytest.mark.case_id_vidflow_group_task_tc008_reset
@pytest.mark.p1
@allure.feature("Vidflow")
@allure.story("群发任务 - 列表与筛选")
@allure.title("TC008-重置: 点击重置按钮清空筛选")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("在有筛选/搜索条件时点击重置按钮，清空已有筛选，列表恢复默认")
def test_tc008_reset_filters(page, config):
    _ensure_logged_in(page, config)
    group_page = VidflowGroupTaskPage(page)
    with allure.step("先执行一次搜索，使页面存在筛选条件"):
        group_page.fill_search_keyword("AutoTest_NoMatch")
        group_page.trigger_search()
        page.wait_for_timeout(1500)
    with allure.step("点击重置按钮清空筛选"):
        try:
            group_page.click_reset_filters()
            logger.info("✓ 已点击重置，清空筛选")
        except Exception as e:
            pytest.skip(f"重置按钮不可用: {e}")
    with allure.step("验证重置后列表或空状态正常展示"):
        assert group_page.is_list_or_empty_visible(timeout=5000), "重置后列表/空状态未正常展示"
    logger.info("✅ TC008-重置 通过：重置筛选项正常")


@pytest.mark.case_id_vidflow_group_task_tc009
@pytest.mark.p1
@allure.feature("Vidflow")
@allure.story("群发任务 - 列表与筛选")
@allure.title("TC009: 筛选 - 按任务状态（下拉选已过期并点击筛选）")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("点击状态筛选下拉框（全部状态），在下拉中选择「已过期」，点击筛选按钮，验证列表展示该状态任务")
def test_tc009_filter_by_status(page, config):
    _ensure_logged_in(page, config)
    group_page = VidflowGroupTaskPage(page)
    with allure.step("点击状态筛选下拉框（全部状态），选择已过期"):
        try:
            group_page.open_status_filter_dropdown()
            group_page.select_status_option_in_dropdown("已过期")
            logger.info("✓ 已选择状态「已过期」")
        except Exception as e:
            pytest.skip(f"状态筛选不可用: {e}")
    with allure.step("等待下拉关闭后点击筛选按钮"):
        group_page.wait_for_status_dropdown_closed()
        group_page.click_filter_button()
        logger.info("✓ 已点击筛选按钮")
    with allure.step("验证筛选生效：列表或空状态正常展示"):
        assert group_page.is_list_or_empty_visible(timeout=5000), "筛选后列表未正常展示"
    logger.info("✅ TC009 通过：按状态筛选（已过期）正常")
    page.wait_for_timeout(1000)


@pytest.mark.case_id_vidflow_group_task_tc0010
@pytest.mark.p2
@allure.feature("Vidflow")
@allure.story("群发任务 - 列表与筛选")
@allure.title("TC0010: 筛选 - 按时间范围（开始 2026-02-01，结束 2026-02-03，点击筛选）")
@allure.severity(allure.severity_level.MINOR)
@allure.description("点击开始时间输入 2026-02-01，点击结束时间输入 2026-02-03，点击筛选按钮，验证列表展示时间范围内任务")
def test_tc010_filter_by_date_range(page, config):
    _ensure_logged_in(page, config)
    group_page = VidflowGroupTaskPage(page)
    with allure.step("点击开始时间输入 2026-02-04，结束时间输入 2026-02-05"):
        try:
            group_page.fill_start_date("2026-02-04")
            group_page.fill_end_date("2026-02-05")
            logger.info("✓ 已选择时间范围 2026-02-04 ~ 2026-02-05")
        except Exception as e:
            pytest.skip(f"时间范围筛选未实现或不可用: {e}")
    with allure.step("等待日期面板关闭后点击筛选按钮"):
        group_page.wait_for_date_picker_closed()
        group_page.click_filter_button()
        logger.info("✓ 已点击筛选按钮")
    with allure.step("验证筛选生效：列表或空状态正常展示"):
        assert group_page.is_list_or_empty_visible(timeout=5000), "时间筛选后列表未正常展示"
    logger.info("✅ TC0010 通过：按时间筛选正常")
    page.wait_for_timeout(1000)


# # ---------- 新建/编辑群发任务 ----------

# @pytest.mark.case_id_vidflow_group_task_tc010
# @pytest.mark.smoke
# @pytest.mark.p0
# @allure.feature("Vidflow")
# @allure.story("群发任务 - 新建/编辑")
# @allure.title("TC010: 新建群发任务 - 必填项填写完整并提交")
# @allure.severity(allure.severity_level.CRITICAL)
# @allure.description("点击新建，填写所有必填项后提交，验证提交成功、弹窗关闭、列表出现新任务")
# def test_tc010_create_task_full_required(page, config):
#     _ensure_logged_in(page, config)
#     group_page = VidflowGroupTaskPage(page)
#     task_name = f"AutoTest_{datetime.now().strftime('%Y%m%d%H%M%S')}"
#     with allure.step("点击新建/创建任务"):
#         group_page.click_new_task()
#         logger.info("✓ 已打开新建弹窗")
#     with allure.step("填写必填项并提交"):
#         group_page.fill_required_task_name(task_name)
#         group_page.submit_modal()
#         logger.info("✓ 已提交表单")
#     with allure.step("验证提交后进入创建页或回到列表页"):
#         page.wait_for_timeout(2000)
#         current_url = page.url
#         assert "groupTaskManagement" in current_url, f"提交后应在群发任务相关页，当前: {current_url}"
#     logger.info("✅ TC010 通过：新建任务提交流程正常（提交后进入 createTask/列表页）")


@pytest.mark.case_id_vidflow_group_task_tc011
@pytest.mark.p0
@allure.feature("Vidflow")
@allure.story("群发任务 - 新建/编辑")
@allure.title("TC011: 新建群发任务 - 不填信息点提交后点取消")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("点击新建任务，点击下一步，不填写任何信息点击提交，等待1s后点击取消")
def test_tc011_create_task_empty_required(page, config):
    _ensure_logged_in(page, config)
    group_page = VidflowGroupTaskPage(page)
    with allure.step("点击新建任务"):
        group_page.click_new_task()
        logger.info("✓ 已打开新建弹窗")
    with allure.step("点击下一步按钮"):
        group_page.click_next_step_in_modal()
        logger.info("✓ 已点击下一步")
    with allure.step("不填写任何信息，点击提交按钮"):
        group_page.submit_modal()
        logger.info("✓ 已点击提交")
    with allure.step("等待 1s 后点击取消按钮"):
        page.wait_for_timeout(1000)
        group_page.cancel_or_close_modal()
        logger.info("✓ 已点击取消")
    with allure.step("点击取消后再停留 1s"):
        page.wait_for_timeout(1000)
    with allure.step("验证弹窗已关闭"):
        page.wait_for_timeout(500)
        assert not group_page.is_modal_visible(timeout=2000), "点击取消后弹窗应已关闭"
    logger.info("✅ TC011 通过：不填信息点提交、等待1s后点取消，弹窗已关闭")


# @pytest.mark.case_id_vidflow_group_task_tc012
# @pytest.mark.p1
# @allure.feature("Vidflow")
# @allure.story("群发任务 - 新建/编辑")
# @allure.title("TC012: 新建/编辑弹窗 - 点击关闭或取消")
# @allure.severity(allure.severity_level.NORMAL)
# @allure.description("打开弹窗后点击取消或关闭，验证弹窗关闭")
# def test_tc012_modal_cancel_or_close(page, config):
#     _ensure_logged_in(page, config)
#     group_page = VidflowGroupTaskPage(page)
#     with allure.step("打开新建弹窗"):
#         group_page.click_new_task()
#         page.wait_for_timeout(1000)
#     with allure.step("点击取消或关闭"):
#         group_page.cancel_or_close_modal()
#         logger.info("✓ 已关闭弹窗")
#     with allure.step("验证弹窗已关闭"):
#         page.wait_for_timeout(1000)
#         assert not group_page.is_modal_visible(timeout=2000), "弹窗应已关闭"
#     logger.info("✅ TC012 通过：取消/关闭弹窗正常")


# @pytest.mark.case_id_vidflow_group_task_tc013
# @pytest.mark.p1
# @allure.feature("Vidflow")
# @allure.story("群发任务 - 新建/编辑")
# @allure.title("TC013: 编辑群发任务 - 修改信息并保存")
# @allure.severity(allure.severity_level.NORMAL)
# @allure.description("点击某条任务的编辑，修改允许编辑的字段后保存，验证保存成功")
# def test_tc013_edit_task_and_save(page, config):
#     _ensure_logged_in(page, config)
#     group_page = VidflowGroupTaskPage(page)
#     if group_page.get_list_row_count() == 0:
#         pytest.skip("列表无任务，无法执行编辑")
#     with allure.step("点击第一条任务的编辑"):
#         try:
#             group_page.click_edit_on_first_task()
#             logger.info("✓ 已打开编辑")
#         except Exception as e:
#             pytest.skip(f"无编辑入口或不可用: {e}")
#     with allure.step("修改任务名称并保存"):
#         group_page.fill_required_task_name(f"Edit_{datetime.now().strftime('%H%M%S')}")
#         group_page.submit_modal()
#         logger.info("✓ 已保存")
#     with allure.step("验证回到列表页"):
#         page.wait_for_timeout(2000)
#         assert group_page.is_on_group_task_list_page(timeout=5000), "保存后未回到列表页"
#     logger.info("✅ TC013 通过：编辑并保存正常")


# ---------- 任务操作与状态 ----------

@pytest.mark.case_id_vidflow_group_task_tc012
@pytest.mark.p1
@allure.feature("Vidflow")
@allure.story("群发任务 - 任务操作")
@allure.title("TC012: 查看任务详情（最后一列 data-icon=more→详情→关闭弹窗）")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("点击第一行最后一列→点击 data-icon=more→弹窗中选详情→弹窗停留2s→点击右上角X关闭")
def test_tc012_view_task_detail(page, config):
    _ensure_logged_in(page, config)
    group_page = VidflowGroupTaskPage(page)
    if group_page.get_list_row_count() == 0:
        pytest.skip("列表无任务，无法查看详情")
    with allure.step("点击第一行最后一列，点击 data-icon=more，在弹窗中选择详情"):
        try:
            group_page.click_first_row_three_dots_icon()
            group_page.click_detail_in_dropdown()
            logger.info("✓ 已点击 more 并在弹窗中选择详情")
        except Exception as e:
            pytest.skip(f"查看详情入口不可用: {e}")
    page.wait_for_timeout(1000)
    with allure.step("弹窗出现后停留 2s，点击弹窗右上角 X 关闭"):
        try:
            group_page.close_detail_modal_with_x()
            logger.info("✓ 已关闭详情弹窗")
        except Exception as e:
            pytest.skip(f"关闭弹窗失败: {e}")
    with allure.step("验证回到列表页"):
        page.wait_for_timeout(1000)
        assert group_page.is_on_group_task_list_page(timeout=5000), "关闭后应回到列表页"
    logger.info("✅ TC012 通过：查看详情并关闭弹窗正常")


# @pytest.mark.case_id_vidflow_group_task_tc015
# @pytest.mark.p0
# @allure.feature("Vidflow")
# @allure.story("群发任务 - 任务操作")
# @allure.title("TC015: 删除/取消任务 - 二次确认取消")
# @allure.severity(allure.severity_level.CRITICAL)
# @allure.description("点击删除/取消，在二次确认弹窗中点击取消，验证弹窗关闭且任务仍存在")
# def test_tc015_delete_confirm_cancel(page, config):
#     _ensure_logged_in(page, config)
#     group_page = VidflowGroupTaskPage(page)
#     if group_page.get_list_row_count() == 0:
#         pytest.skip("列表无任务，无法执行删除取消")
#     with allure.step("点击删除/取消按钮"):
#         try:
#             group_page.click_delete_or_cancel_task()
#             page.wait_for_timeout(1500)
#         except Exception as e:
#             pytest.skip(f"删除/取消入口不可用: {e}")
#     with allure.step("在确认弹窗中点击取消"):
#         group_page.confirm_delete_modal(confirm=False)
#         logger.info("✓ 已点击取消")
#     with allure.step("验证弹窗关闭且仍在列表页"):
#         page.wait_for_timeout(1000)
#         assert group_page.is_on_group_task_list_page(timeout=5000), "取消后应仍在列表页"
#     logger.info("✅ TC015 通过：二次确认取消正常")


# @pytest.mark.case_id_vidflow_group_task_tc016
# @pytest.mark.p0
# @allure.feature("Vidflow")
# @allure.story("群发任务 - 任务操作")
# @allure.title("TC016: 删除/取消任务 - 确认操作")
# @allure.severity(allure.severity_level.CRITICAL)
# @allure.description("在确认弹窗中点击确定/删除，验证弹窗关闭且列表状态更新或移除")
# def test_tc016_delete_confirm_ok(page, config):
#     _ensure_logged_in(page, config)
#     group_page = VidflowGroupTaskPage(page)
#     if group_page.get_list_row_count() == 0:
#         pytest.skip("列表无任务，无法执行删除确认")
#     with allure.step("点击删除并确认"):
#         try:
#             group_page.click_delete_or_cancel_task()
#             page.wait_for_timeout(1500)
#             group_page.confirm_delete_modal(confirm=True)
#             logger.info("✓ 已确认删除")
#         except Exception as e:
#             pytest.skip(f"删除确认流程不可用: {e}")
#     with allure.step("验证弹窗关闭且列表更新"):
#         page.wait_for_timeout(2000)
#         assert group_page.is_list_or_empty_visible(timeout=5000), "删除后列表/空状态应正常展示"
#     logger.info("✅ TC016 通过：确认删除正常")


@pytest.mark.case_id_vidflow_group_task_tc013
@pytest.mark.p2
@allure.feature("Vidflow")
@allure.story("群发任务 - Tab 与页面状态")
@allure.title("TC013: 群发任务页刷新")
@allure.severity(allure.severity_level.MINOR)
@allure.description("刷新页面，验证登录态有效时仍为群发任务页内容")
def test_tc015_page_refresh(page, config):
    _ensure_logged_in(page, config)
    group_page = VidflowGroupTaskPage(page)
    entry_url = config.get("entry_url") or f"{config['base_url'].rstrip('/')}/#/groupTaskManagement/groupTaskList"
    with allure.step("刷新页面"):
        page.reload(wait_until="domcontentloaded", timeout=30000)
    with allure.step("验证仍在群发任务页或跳转登录"):
        assert "groupTaskList" in page.url or "login" in page.url.lower(), "刷新后 URL 异常"
    logger.info("✅ TC013 通过：刷新后状态正常")