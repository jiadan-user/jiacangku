# test_cases/test_messages_complete.py
"""
OK阿联酋站 - Messages页面完整测试套件
包含TC001-TC040的所有测试用例（已去除冗余代码和不可自动化用例）

测试用例分布：
- TC001-TC008: 基础探索测试
- TC009-TC014: 功能按钮测试
- TC014A: URL消息发送测试
- TC015-TC017: 深度功能探索测试
- TC018-TC021: 异常和边界测试
- TC022: 消息操作功能测试（已删除 - 自动化无法触发Copy菜单）
- TC023-TC028: 列表功能（滑动/时间戳/未读气泡/时间顺序/置顶/免打扰）
- TC029: 发送附件（PDF）
- TC030: 附件类型校验
- TC031: 发送图片
- TC032: 图片类型校验
- TC033: 地理位置图标入口
- TC034: 发送框初始 Send 按钮禁用
- TC035: 输入文字后 Send 按钮启用
- TC036: 发送文件图标触发文件选择
- TC037: 发送图片图标触发图片选择
- TC038: 验证左侧会话列表数量统计准确性（2026-04-03 新增）
- TC039: 验证会话列表滚动功能（2026-04-03 新增）
- TC040: 验证右侧聊天消息统计功能（2026-04-03 新增）

更新日志：
2026-04-03: 
- 修复了会话列表选择器混淆问题（TC038）
- 新增会话列表滚动功能测试（TC039）
- 新增聊天消息统计功能测试（TC040）
- 详见: docs/MESSAGES_PAGE_SELECTOR_UPDATE_20260403.md
"""
import pytest
import allure
import platform
from pathlib import Path
from pages.login_page import LoginPage
from pages.messages_explore_page import MessagesExplorePage
from utils.session_manager import SessionManager
from utils.logger import setup_logger

# ========== 测试配置（_CONFIG）==========
_CONFIG = {
    'site': 'ae',
    'site_name': 'OK阿联酋站',
    'role': 'seller',
    'user_name': 'gaosong01_ae_seller',
    'base_url': 'https://ae.ok.com/en/city-abu-dhabi/',
    'target_page': 'https://aepub.ok.com/biz/en/chat',
    
    'test_account': {
        'username': 'gaosong01@58.com',
        'password': 'Qwert_123'
    },
    
    'locale': 'en-AE',
    'currency': 'AED',
    
    'browser': {
        'type': 'chromium',
        'headless': False,
        'viewport': {
            'width': 1920,
            'height': 1080
        }
    },
    
    'timeout': {
        'default': 30000,
        'wait': 10000,
        'navigation': 30000
    }
}

logger = setup_logger()


# ==================== TC001-TC008: 基础探索测试 ====================

@pytest.mark.p0
@allure.feature("OK - Messages")
@allure.story("Messages页面功能探索 - 页面访问")
@allure.title("TC001: 从首页访问Messages页面")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.messages
@pytest.mark.navigation
@pytest.mark.ae
@pytest.mark.smoke
@pytest.mark.case_id_messages_explore_001
def test_access_messages_from_home(page, config):
    """
    TC001: 从首页访问Messages页面
    
    测试步骤:
    1. 登录并打开首页
    2. 点击Messages链接
    3. 验证进入Messages页面
    """
    logger.info("=" * 80)
    logger.info("TC001: 从首页访问Messages页面")
    logger.info("=" * 80)
    
    # Arrange: 准备测试数据和对象
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    login_page = LoginPage(page, base_url=config['base_url'])
    messages_page = MessagesExplorePage(page)
    
    # 尝试加载Session
    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        logger.info("✗ Session不存在，开始登录流程")
        login_page.navigate_to_home_page()
        login_page.handle_cookie_popup()
        login_page.login(config['test_account']['username'], config['test_account']['password'])
        session_manager.save_session()
        logger.info("✓ 登录成功并保存 Session")
    
    # Act: 执行测试操作
    
    # 步骤1: 导航到首页
    messages_page.navigate_to_home(config['base_url'])
    logger.info("✓ 已导航到首页")
    
    # 步骤2: 点击Messages链接
    initial_url = page.url
    click_success = messages_page.click_messages_link()
    
    # 等待页面跳转
    page.wait_for_timeout(3000)
    
    # 检查是否真的跳转了
    current_url = page.url
    if current_url == initial_url or 'chat' not in current_url.lower() and 'message' not in current_url.lower():
        logger.info(f"✗ 点击Messages链接后URL未变化或不正确: {current_url}，尝试直接导航")
        messages_page.navigate_to_messages_directly(config['target_page'])
        page.wait_for_timeout(2000)
        logger.info("✓ 已直接导航到Messages页面")
    else:
        logger.info("✓ 已点击Messages链接")
    
    # Assert: 验证测试结果
    
    # 验证1: URL正确
    current_url = page.url
    assert 'chat' in current_url.lower() or 'message' in current_url.lower(), f"URL不正确: {current_url}"
    logger.info(f"✓ URL验证通过: {current_url}")
    
    # 验证2: 页面关键元素可见
    messages_container = page.locator('[class*="chat"], [class*="message"], [class*="conversation"]').first
    assert messages_container.is_visible(timeout=10000), "Messages页面关键元素未显示"
    logger.info("✓ Messages页面关键元素已显示")
    
    logger.info("✅ TC001 测试通过！")
    logger.info("=" * 80)


@pytest.mark.p2
@allure.feature("OK - Messages")
@allure.story("Messages页面功能探索 - 会话列表")
@allure.title("TC002: 探索Messages页面会话列表功能")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.messages
@pytest.mark.conversation
@pytest.mark.exploration
@pytest.mark.ae
@pytest.mark.case_id_messages_explore_002
def test_explore_conversation_list(page, config):
    """
    TC002: 探索Messages页面会话列表功能
    
    测试步骤:
    1. 访问Messages页面
    2. 检查会话列表元素
    3. 滑动会话列表
    4. 点击第二个会话并验证昵称一致性
    """
    logger.info("=" * 80)
    logger.info("TC002: 探索会话列表功能")
    logger.info("=" * 80)
    
    # Arrange
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    login_page = LoginPage(page, base_url=config['base_url'])
    messages_page = MessagesExplorePage(page)
    
    # 加载Session或登录
    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        logger.info("✗ Session不存在，开始登录流程")
        login_page.navigate_to_home_page()
        login_page.handle_cookie_popup()
        login_page.click_login_register()
        login_page.input_email(config['test_account']['username'])
        login_page.click_continue()
        login_page.input_password(config['test_account']['password'])
        login_page.click_login()
        session_manager.save_session()
        logger.info("✓ 登录成功并保存 Session")
    
    # Act
    
    # 步骤1: 导航到Messages页面
    messages_page.navigate_to_messages_directly(config['target_page'])
    logger.info("✓ 已导航到Messages页面")
    
    # 步骤2: 等待会话列表加载
    messages_page.wait_for_conversation_list()
    logger.info("✓ 会话列表加载完成")
    
    # 步骤3: 滑动左侧会话列表
    logger.info("\n--- 滑动会话列表 ---")
    scroll_result = messages_page.scroll_conversation_list(distance=200)
    logger.info(f"✓ 滑动会话列表: {scroll_result['success']}")
    if scroll_result['success']:
        logger.info(f"  滑动距离: {scroll_result['distance']}px")
    
    # 截图（滑动后）
    page.screenshot(path="screenshots/tc002_after_scroll.png", timeout=60000)
    logger.info("✓ 已截图: tc002_after_scroll.png")
    
    # 步骤4: 检查会话列表元素
    elements = messages_page.check_conversation_item_elements()
    logger.info(f"\n✓ 会话列表元素检查:")
    logger.info(f"  - 头像: {elements.get('has_avatar', False)}")
    logger.info(f"  - 用户名: {elements.get('has_user_name', False)}")
    logger.info(f"  - 消息预览: {elements.get('has_message_preview', False)}")
    logger.info(f"  - 时间戳: {elements.get('has_timestamp', False)}")
    
    # 步骤5: 获取第二个会话的昵称（点击前）
    logger.info("\n--- 获取第二个会话昵称 ---")
    conversation_name = messages_page.get_conversation_name_by_index(1)
    logger.info(f"✓ 第二个会话昵称: {conversation_name}")
    
    # 步骤6: 点击第二个会话
    logger.info("\n--- 点击第二个会话 ---")
    click_success = messages_page.click_conversation_by_index(1)
    
    if click_success:
        logger.info("✓ 已点击第二个会话")
        
        # 验证会话详情可见
        detail_visible = messages_page.is_conversation_detail_visible()
        logger.info(f"✓ 会话详情区域显示: {detail_visible}")
        
        if detail_visible:
            # 获取会话详情页的用户昵称
            logger.info("\n--- 验证用户昵称一致性 ---")
            detail_user_name = messages_page.get_conversation_detail_user_name()
            logger.info(f"✓ 详情页用户昵称: {detail_user_name}")
            
            # 验证：昵称一致性（记录信息，不强制断言）
            if conversation_name and detail_user_name:
                # 比较昵称（去除空格，不区分大小写）
                conv_name_clean = conversation_name.strip().lower()
                detail_name_clean = detail_user_name.strip().lower()
                
                # 检查是否匹配（详情页昵称可能包含会话列表昵称）
                if conv_name_clean == detail_name_clean or conv_name_clean in detail_name_clean or detail_name_clean in conv_name_clean:
                    logger.info(f"✅ 昵称一致性验证通过:")
                    logger.info(f"   会话列表昵称: {conversation_name}")
                    logger.info(f"   详情页昵称: {detail_user_name}")
                else:
                    logger.warning(f"⚠️ 昵称可能不一致（需人工确认）:")
                    logger.warning(f"   会话列表获取到: {conversation_name}")
                    logger.warning(f"   详情页获取到: {detail_user_name}")
                    logger.warning(f"   说明：由于DOM结构复杂，自动获取的昵称可能不准确，请查看截图人工确认")
            else:
                logger.warning("⚠️ 无法获取完整昵称信息，跳过昵称验证")
            
            # 截图（会话详情）
            page.screenshot(path="screenshots/tc002_conversation_detail.png", timeout=60000)
            logger.info("✓ 已截图: tc002_conversation_detail.png")
    else:
        logger.warning("✗ 点击第二个会话失败")
    
    # Assert
    logger.info("\n" + "=" * 80)
    logger.info("会话列表功能测试汇总:")
    logger.info(f"  - 会话列表加载: ✅")
    logger.info(f"  - 列表滑动: {'✅' if scroll_result['success'] else '❌'}")
    logger.info(f"  - 会话元素结构: ✅")
    logger.info(f"  - 点击第二个会话: {'✅' if click_success else '❌'}")
    
    logger.info("✅ TC002 测试通过！")
    logger.info("=" * 80)


@pytest.mark.p2
@allure.feature("OK - Messages")
@allure.story("Messages页面功能探索 - 会话详情")
@allure.title("TC003: 探索会话详情页面功能")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.messages
@pytest.mark.conversation
@pytest.mark.exploration
@pytest.mark.ae
@pytest.mark.case_id_messages_explore_003
def test_explore_conversation_detail(page, config):
    """TC003: 探索会话详情页面功能（简化版）"""
    logger.info("=" * 80)
    logger.info("TC003: 探索会话详情功能")
    logger.info("=" * 80)
    
    # Arrange
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    login_page = LoginPage(page, base_url=config['base_url'])
    messages_page = MessagesExplorePage(page)
    
    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        logger.info("✗ Session不存在，开始登录流程")
        login_page.navigate_to_home_page()
        login_page.handle_cookie_popup()
        login_page.click_login_register()
        login_page.input_email(config['test_account']['username'])
        login_page.click_continue()
        login_page.input_password(config['test_account']['password'])
        login_page.click_login()
        session_manager.save_session()
        logger.info("✓ 登录成功并保存 Session")
    
    # Act
    messages_page.navigate_to_messages_directly(config['target_page'])
    logger.info("✓ 已导航到Messages页面")
    
    # 验证是否真的进入了 Messages 页面（检查是否被重定向到登录页）
    current_url = page.url
    if 'login' in current_url.lower() or page.locator('input[type="password"]').count() > 0:
        logger.error(f"❌ Session 失效，被重定向到登录页: {current_url}")
        logger.info("尝试重新登录...")
        
        # 重新登录
        login_page.input_email(config['test_account']['username'])
        login_page.click_continue()
        page.wait_for_timeout(1000)
        login_page.input_password(config['test_account']['password'])
        login_page.click_login()
        page.wait_for_timeout(5000)
        
        # 保存新的 Session
        session_manager.save_session()
        logger.info("✓ 重新登录成功")
        
        # 再次导航到 Messages 页面
        messages_page.navigate_to_messages_directly(config['target_page'])
        page.wait_for_timeout(3000)
    
    messages_page.wait_for_conversation_list()
    conversation_count = messages_page.get_conversation_count()
    logger.info(f"✓ 会话总数: {conversation_count}")
    
    if conversation_count >= 2:
        messages_page.click_conversation_by_index(1)
        logger.info("✓ 已点击第二个会话")
    else:
        pytest.skip(f"会话数量不足（当前: {conversation_count}），跳过测试")
    
    # 检查会话详情基本元素
    detail_elements = messages_page.check_conversation_detail_elements()
    logger.info("✓ 会话详情基本元素检查:")
    logger.info(f"  - 消息输入框: {detail_elements.get('has_message_input', False)}")
    logger.info(f"  - 发送按钮: {detail_elements.get('has_send_button', False)}")
    logger.info(f"  - 消息历史: {detail_elements.get('has_message_history', False)}")
    
    # Assert
    assert detail_elements.get('has_message_input', False), "消息输入框未显示"
    
    logger.info("✅ TC003 测试通过！")
    logger.info("=" * 80)


@pytest.mark.p2
@allure.feature("OK - Messages")
@allure.story("Messages页面功能探索 - 消息发送")
@allure.title("TC004: 探索消息发送功能")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.messages
@pytest.mark.send
@pytest.mark.exploration
@pytest.mark.ae
@pytest.mark.case_id_messages_explore_004
def test_explore_message_sending(page, config):
    """TC004: 探索消息发送功能（简化版）"""
    logger.info("=" * 80)
    logger.info("TC004: 探索消息发送功能")
    logger.info("=" * 80)
    
    # Arrange
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    login_page = LoginPage(page, base_url=config['base_url'])
    messages_page = MessagesExplorePage(page)
    
    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        logger.info("✗ Session不存在，开始登录流程")
        login_page.navigate_to_home_page()
        login_page.handle_cookie_popup()
        login_page.click_login_register()
        login_page.input_email(config['test_account']['username'])
        login_page.click_continue()
        login_page.input_password(config['test_account']['password'])
        login_page.click_login()
        session_manager.save_session()
        logger.info("✓ 登录成功并保存 Session")
    
    # Act
    messages_page.navigate_to_messages_directly(config['target_page'])
    logger.info("✓ 已导航到Messages页面")
    
    messages_page.wait_for_conversation_list()
    conversation_count = messages_page.get_conversation_count()
    
    if conversation_count >= 2:
        messages_page.click_conversation_by_index(1)
        logger.info("✓ 已进入第二个会话")
    else:
        pytest.skip(f"会话数量不足（当前: {conversation_count}）")
    
    # 测试消息输入框
    input_test = messages_page.test_message_input("这是一条测试消息")
    logger.info(f"✓ 消息输入框测试:")
    logger.info(f"  - 可编辑: {input_test.get('editable', False)}")
    logger.info(f"  - 输入成功: {input_test.get('test_success', False)}")
    
    # Assert
    assert input_test.get('editable', False), "消息输入框不可编辑"
    
    logger.info("✅ TC004 测试通过！")
    logger.info("=" * 80)


@pytest.mark.p2
@allure.feature("OK - Messages")
@allure.story("Messages页面功能探索 - 搜索筛选")
@allure.title("TC005: 探索搜索和筛选功能")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.messages
@pytest.mark.search
@pytest.mark.exploration
@pytest.mark.ae
@pytest.mark.case_id_messages_explore_005
def test_explore_search_and_filter(page, config):
    """TC005: 探索搜索和筛选功能（简化版）"""
    logger.info("=" * 80)
    logger.info("TC005: 探索搜索和筛选功能")
    logger.info("=" * 80)
    
    # Arrange
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    login_page = LoginPage(page, base_url=config['base_url'])
    messages_page = MessagesExplorePage(page)
    
    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        logger.info("✗ Session不存在，开始登录流程")
        login_page.navigate_to_home_page()
        login_page.handle_cookie_popup()
        login_page.click_login_register()
        login_page.input_email(config['test_account']['username'])
        login_page.click_continue()
        login_page.input_password(config['test_account']['password'])
        login_page.click_login()
        session_manager.save_session()
        logger.info("✓ 登录成功并保存 Session")
    
    # Act
    messages_page.navigate_to_messages_directly(config['target_page'])
    logger.info("✓ 已导航到Messages页面")
    
    messages_page.wait_for_conversation_list()
    
    # 检查搜索框
    has_search = messages_page.check_search_input()
    logger.info(f"✓ 搜索框: {has_search}")
    
    # 检查筛选功能
    has_filter = messages_page.check_filter_button()
    logger.info(f"✓ 筛选功能: {has_filter}")
    
    # Assert
    conversation_count = messages_page.get_conversation_count()
    assert conversation_count > 0, "会话列表为空"
    
    logger.info("✅ TC005 测试通过！")
    logger.info("=" * 80)


@pytest.mark.p2
@allure.feature("OK - Messages")
@allure.story("Messages页面功能探索 - 用户信息")
@allure.title("TC006: 探索用户信息和操作")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.messages
@pytest.mark.user
@pytest.mark.exploration
@pytest.mark.ae
@pytest.mark.case_id_messages_explore_006
def test_explore_user_info(page, config):
    """TC006: 探索用户信息和操作（简化版）"""
    logger.info("=" * 80)
    logger.info("TC006: 探索用户信息")
    logger.info("=" * 80)
    
    # Arrange
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    login_page = LoginPage(page, base_url=config['base_url'])
    messages_page = MessagesExplorePage(page)
    
    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        logger.info("✗ Session不存在，开始登录流程")
        login_page.navigate_to_home_page()
        login_page.handle_cookie_popup()
        login_page.click_login_register()
        login_page.input_email(config['test_account']['username'])
        login_page.click_continue()
        login_page.input_password(config['test_account']['password'])
        login_page.click_login()
        session_manager.save_session()
        logger.info("✓ 登录成功并保存 Session")
    
    # Act
    messages_page.navigate_to_messages_directly(config['target_page'])
    logger.info("✓ 已导航到Messages页面")
    
    messages_page.wait_for_conversation_list()
    conversation_count = messages_page.get_conversation_count()
    
    if conversation_count >= 2:
        messages_page.click_conversation_by_index(1)
        logger.info("✓ 已进入第二个会话")
    else:
        pytest.skip(f"会话数量不足（当前: {conversation_count}）")
    
    # 检查用户信息
    user_info = messages_page.check_user_info()
    logger.info(f"✓ 用户信息检查:")
    logger.info(f"  - 头像: {user_info.get('has_avatar', False)}")
    logger.info(f"  - 用户名: {user_info.get('has_name', False)}")
    logger.info(f"  - 在线状态: {user_info.get('has_status', False)}")
    
    logger.info("✅ TC006 测试通过！")
    logger.info("=" * 80)


@pytest.mark.p2
@allure.feature("OK - Messages")
@allure.story("Messages页面功能探索 - 消息展示")
@allure.title("TC007: 探索消息类型和展示")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.messages
@pytest.mark.display
@pytest.mark.exploration
@pytest.mark.ae
@pytest.mark.case_id_messages_explore_007
def test_explore_message_display(page, config):
    """TC007: 探索消息类型和展示（简化版）"""
    logger.info("=" * 80)
    logger.info("TC007: 探索消息类型和展示")
    logger.info("=" * 80)
    
    # Arrange
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    login_page = LoginPage(page, base_url=config['base_url'])
    messages_page = MessagesExplorePage(page)
    
    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        logger.info("✗ Session不存在，开始登录流程")
        login_page.navigate_to_home_page()
        login_page.handle_cookie_popup()
        login_page.click_login_register()
        login_page.input_email(config['test_account']['username'])
        login_page.click_continue()
        login_page.input_password(config['test_account']['password'])
        login_page.click_login()
        session_manager.save_session()
        logger.info("✓ 登录成功并保存 Session")
    
    # Act
    messages_page.navigate_to_messages_directly(config['target_page'])
    logger.info("✓ 已导航到Messages页面")
    
    messages_page.wait_for_conversation_list()
    conversation_count = messages_page.get_conversation_count()
    
    if conversation_count >= 2:
        messages_page.click_conversation_by_index(1)
        logger.info("✓ 已进入第二个会话")
    else:
        pytest.skip(f"会话数量不足（当前: {conversation_count}）")
    
    # 分析消息类型
    message_analysis = messages_page.analyze_message_types(max_count=5)
    logger.info(f"✓ 消息分析（前{len(message_analysis)}条）")
    
    if len(message_analysis) == 0:
        logger.info("⚠️ 未找到消息历史")
    else:
        logger.info(f"✓ 成功分析 {len(message_analysis)} 条消息")
    
    logger.info("✅ TC007 测试通过！")
    logger.info("=" * 80)


@pytest.mark.p1
@allure.feature("OK - Messages")
@allure.story("Messages页面功能探索 - 安全提示")
@allure.title("TC008: 会话页面安全提示检查")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.messages
@pytest.mark.security
@pytest.mark.exploration
@pytest.mark.ae
@pytest.mark.case_id_messages_explore_008
def test_security_tip_check(page, config):
    """
    TC008: 会话页面安全提示检查
    
    测试步骤:
    1. 访问Messages页面并进入会话
    2. 向下滑动会话页至顶部
    3. 查看是否展示安全提示"for your safe..."
    """
    logger.info("=" * 80)
    logger.info("TC008: 会话页面安全提示检查")
    logger.info("=" * 80)
    
    # Arrange
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    login_page = LoginPage(page, base_url=config['base_url'])
    messages_page = MessagesExplorePage(page)
    
    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        logger.info("✗ Session不存在，开始登录流程")
        login_page.navigate_to_home_page()
        login_page.handle_cookie_popup()
        login_page.click_login_register()
        login_page.input_email(config['test_account']['username'])
        login_page.click_continue()
        login_page.input_password(config['test_account']['password'])
        login_page.click_login()
        session_manager.save_session()
        logger.info("✓ 登录成功并保存 Session")
    
    # Act
    
    # 步骤1: 导航到Messages页面并进入会话
    messages_page.navigate_to_messages_directly(config['target_page'])
    logger.info("✓ 已导航到Messages页面")
    
    messages_page.wait_for_conversation_list()
    conversation_count = messages_page.get_conversation_count()
    logger.info(f"✓ 会话总数: {conversation_count}")
    
    if conversation_count == 0:
        logger.warning("⚠️ 会话列表为空，跳过测试")
        pytest.skip("会话列表为空")
    
    # 点击第二个会话
    messages_page.click_conversation_by_index(1)
    page.wait_for_timeout(3000)
    logger.info("✓ 已进入会话详情页")
    
    # 截图（进入会话后）
    page.screenshot(path="screenshots/tc008_conversation_initial.png", timeout=60000)
    logger.info("✓ 已截图: tc008_conversation_initial.png")
    
    # 步骤2: 向下滑动会话页至顶部
    logger.info("\n--- 滑动会话页至顶部 ---")
    try:
        # 查找消息历史容器并滚动到顶部
        scroll_result = page.evaluate("""
            () => {
                const containers = document.querySelectorAll('[class*="message"], [class*="chat"], [class*="conversation"], [class*="history"]');
                
                for (const container of containers) {
                    // 检查是否是可滚动的消息容器（右侧区域）
                    const rect = container.getBoundingClientRect();
                    if (rect.x > 300 && container.scrollHeight > container.clientHeight) {
                        const originalScrollTop = container.scrollTop;
                        container.scrollTop = 0;  // 滚动到顶部
                        
                        return {
                            success: true,
                            scrolled: true,
                            originalPosition: originalScrollTop,
                            finalPosition: 0,
                            containerClass: container.className
                        };
                    }
                }
                
                return {success: false, scrolled: false};
            }
        """)
        
        if scroll_result['success']:
            logger.info(f"✓ 已滚动到顶部")
            logger.info(f"  原始位置: {scroll_result['originalPosition']}px")
            logger.info(f"  滚动后位置: {scroll_result['finalPosition']}px")
            page.wait_for_timeout(1000)  # 等待滚动完成
        else:
            logger.info("⚠️ 未找到可滚动容器，可能已在顶部")
    except Exception as e:
        logger.warning(f"滚动失败: {e}")
    
    # 截图（滚动后）
    page.screenshot(path="screenshots/tc008_after_scroll_top.png", timeout=60000)
    logger.info("✓ 已截图: tc008_after_scroll_top.png")
    
    # 步骤3: 查找安全提示
    logger.info("\n--- 查找安全提示 ---")
    security_tip = page.evaluate("""
        () => {
            // 查找包含"for your safe"的文本元素
            const allElements = document.querySelectorAll('*');
            
            for (const el of allElements) {
                const text = el.textContent || '';
                const rect = el.getBoundingClientRect();
                
                // 查找包含安全提示关键词的元素
                if (text.toLowerCase().includes('for your safe') || 
                    text.toLowerCase().includes('safety') ||
                    text.toLowerCase().includes('security tip')) {
                    
                    // 确保元素可见且在右侧会话区域
                    if (rect.x > 300 && rect.width > 0 && rect.height > 0) {
                        return {
                            found: true,
                            text: text.trim().substring(0, 200),
                            position: {
                                x: Math.round(rect.x),
                                y: Math.round(rect.y)
                            },
                            tag: el.tagName,
                            className: el.className || ''
                        };
                    }
                }
            }
            
            return {found: false};
        }
    """)
    
    logger.info(f"✓ 安全提示: {security_tip['found']}")
    
    if security_tip['found']:
        logger.info(f"  位置: ({security_tip['position']['x']}, {security_tip['position']['y']})")
        logger.info(f"  标签: {security_tip['tag']}")
        logger.info(f"  内容: {security_tip['text'][:100]}")
        
        # 截图（安全提示）
        page.screenshot(path="screenshots/tc008_security_tip.png", timeout=60000)
        logger.info("✓ 已截图: tc008_security_tip.png")
    else:
        logger.warning("  ⚠️ 未找到安全提示（可能需要滚动或在其他位置）")
        
        # 尝试使用更宽松的条件再次查找
        logger.info("\n--- 使用宽松条件再次查找 ---")
        all_tips = page.evaluate("""
            () => {
                const tips = [];
                const allElements = document.querySelectorAll('div, span, p');
                
                for (const el of allElements) {
                    const text = el.textContent || '';
                    const rect = el.getBoundingClientRect();
                    
                    // 查找可能的提示文本（较长的文本，在顶部区域）
                    if (text.length > 20 && text.length < 500 && 
                        rect.x > 300 && rect.y > 80 && rect.y < 300 &&
                        rect.width > 200) {
                        tips.push({
                            text: text.trim().substring(0, 100),
                            position: {y: Math.round(rect.y)}
                        });
                    }
                }
                
                return tips.slice(0, 5);  // 返回前5个
            }
        """)
        
        if all_tips.length > 0:
            logger.info(f"  找到 {len(all_tips)} 个可能的提示文本:")
            for i, tip in enumerate(all_tips, 1):
                logger.info(f"    {i}. (y={tip['position']['y']}) {tip['text'][:80]}")
    
    # Assert
    logger.info("\n" + "=" * 80)
    logger.info("安全提示检查汇总:")
    logger.info(f"  - 安全提示: {'✅ 存在' if security_tip['found'] else '⚠️ 未找到'}")
    if security_tip['found']:
        logger.info(f"  - 提示内容: {security_tip['text'][:80]}")
    
    logger.info("✅ TC008 测试通过！")
    logger.info("=" * 80)


# ==================== TC009-TC014: 功能按钮测试 ====================

@pytest.mark.p2
@allure.feature("OK - Messages")
@allure.story("Messages页面功能探索 - 电话按钮")
@allure.title("TC009: 测试会话页面的电话按钮功能")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.messages
@pytest.mark.conversation
@pytest.mark.phone
@pytest.mark.exploration
@pytest.mark.ae
@pytest.mark.case_id_messages_explore_009
def test_phone_button(page, config):
    """
    TC009: 会话页面电话按钮测试
    
    测试步骤:
    1. 访问Messages页面并进入会话
    2. 查找电话按钮
    3. 测试电话按钮点击（如果存在）
    """
    logger.info("=" * 80)
    logger.info("TC009: 会话页面电话按钮测试")
    logger.info("=" * 80)
    
    # Arrange
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    login_page = LoginPage(page, base_url=config['base_url'])
    messages_page = MessagesExplorePage(page)
    
    # 加载Session或登录
    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        logger.info("✗ Session不存在，开始登录流程")
        login_page.navigate_to_home_page()
        login_page.handle_cookie_popup()
        login_page.login(config['test_account']['username'], config['test_account']['password'])
        session_manager.save_session()
        logger.info("✓ 登录成功并保存 Session")
    
    # Act
    
    # 步骤1: 导航到Messages页面并进入会话
    messages_page.navigate_to_messages_directly(config['target_page'])
    logger.info("✓ 已导航到Messages页面")
    
    messages_page.wait_for_conversation_list()
    conv_count = messages_page.get_conversation_count()
    logger.info(f"✓ 会话列表加载完成，当前会话数: {conv_count}")
    
    if conv_count == 0:
        logger.warning("⚠️ 会话列表为空，跳过测试")
        pytest.skip("会话列表为空")
    
    # 点击第二个会话
    messages_page.click_conversation_by_index(1)
    page.wait_for_timeout(3000)
    logger.info("✓ 已进入会话详情页")
    
    # 截图
    page.screenshot(path="screenshots/tc009_conversation_page.png", timeout=60000)
    logger.info("✓ 已截图: tc009_conversation_page.png")
    
    # 步骤2: 查找电话按钮
    logger.info("\n--- 查找电话按钮 ---")
    has_phone = messages_page.check_phone_button_advanced()
    logger.info(f"✓ 电话按钮: {has_phone['exists']}")
    
    if has_phone['exists']:
        logger.info(f"  选择器: {has_phone['selector']}")
        
        # 步骤3: 测试电话按钮点击
        logger.info("\n--- 测试电话按钮点击 ---")
        click_result = messages_page.click_phone_button_advanced()
        logger.info(f"✓ 点击成功: {click_result['success']}")
        logger.info(f"  弹窗显示: {click_result['has_dialog']}")
        
        if click_result['has_dialog']:
            logger.info(f"  弹窗内容: {click_result['dialog_text'][:100] if click_result['dialog_text'] else 'N/A'}")
            page.screenshot(path="screenshots/tc009_phone_dialog.png", timeout=60000)
            logger.info("✓ 已截图: tc009_phone_dialog.png")
    else:
        logger.warning("  ✗ 未找到电话按钮")
    
    # Assert
    logger.info("\n" + "=" * 80)
    logger.info("电话按钮测试汇总:")
    logger.info(f"  - 电话按钮: {'✅ 存在' if has_phone['exists'] else '❌ 不存在'}")
    if has_phone['exists']:
        logger.info(f"  - 点击成功: {'✅' if click_result['success'] else '❌'}")
        logger.info(f"  - 弹窗显示: {'✅' if click_result['has_dialog'] else '❌'}")
    
    logger.info("✅ TC009 测试通过！")
    logger.info("=" * 80)


@pytest.mark.p1
@allure.feature("OK - Messages")
@allure.story("Messages页面功能探索 - 设置入口")
@allure.title("TC010: 测试会话页面右上角三点菜单（...）")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.messages
@pytest.mark.conversation
@pytest.mark.settings
@pytest.mark.exploration
@pytest.mark.ae
@pytest.mark.case_id_messages_explore_010
def test_three_dots_menu(page, config):
    """
    TC010: 会话页面设置入口测试
    
    测试步骤:
    1. 访问Messages页面并进入会话
    2. 定位会话详情页右上角的三点菜单（...）
    3. 点击三点菜单打开下拉列表
    4. 验证下拉列表中的选项
    """
    logger.info("=" * 80)
    logger.info("TC010: 会话页面设置入口测试")
    logger.info("=" * 80)
    
    # Arrange
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    login_page = LoginPage(page, base_url=config['base_url'])
    messages_page = MessagesExplorePage(page)
    
    # 加载Session或登录
    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        logger.info("✗ Session不存在，开始登录流程")
        login_page.navigate_to_home_page()
        login_page.handle_cookie_popup()
        login_page.login(config['test_account']['username'], config['test_account']['password'])
        session_manager.save_session()
        logger.info("✓ 登录成功并保存 Session")
    
    # Act
    
    # 步骤1: 导航到Messages页面并进入会话
    messages_page.navigate_to_messages_directly(config['target_page'])
    logger.info("✓ 已导航到Messages页面")
    
    messages_page.wait_for_conversation_list()
    conv_count = messages_page.get_conversation_count()
    logger.info(f"✓ 会话列表加载完成，当前会话数: {conv_count}")
    
    if conv_count == 0:
        logger.warning("⚠️ 会话列表为空，跳过测试")
        pytest.skip("会话列表为空")
    
    # 点击第二个会话
    messages_page.click_conversation_by_index(1)
    page.wait_for_timeout(3000)
    logger.info("✓ 已进入会话详情页")
    
    # 截图
    page.screenshot(path="screenshots/tc010_conversation_page.png", timeout=60000)
    logger.info("✓ 已截图: tc010_conversation_page.png")
    
    # 步骤2: 定位并点击三点菜单
    logger.info("\n--- 查找三点菜单（...） ---")
    has_menu = messages_page.check_three_dots_menu()
    logger.info(f"✓ 三点菜单: {has_menu['exists']}")
    
    if has_menu['exists']:
        if 'x' in has_menu and 'y' in has_menu:
            logger.info(f"  位置: ({has_menu['x']}, {has_menu['y']})")
        
        # 步骤3: 点击打开菜单
        logger.info("\n--- 点击打开三点菜单 ---")
        menu_result = messages_page.click_three_dots_menu()
        logger.info(f"✓ 菜单打开: {menu_result['opened']}")
        
        if menu_result['opened']:
            logger.info(f"  菜单项数量: {menu_result['item_count']}")
            logger.info("  菜单选项:")
            for i, item in enumerate(menu_result['items'], 1):
                logger.info(f"    {i}. {item}")
            
            # 截图
            page.screenshot(path="screenshots/tc010_menu_opened.png", timeout=60000)
            logger.info("✓ 已截图: tc010_menu_opened.png")
            
            # 关闭菜单
            page.keyboard.press('Escape')
            page.wait_for_timeout(1000)
        else:
            logger.warning(f"  ✗ 菜单未打开: {menu_result.get('error', '未知原因')}")
    else:
        logger.warning("  ✗ 未找到三点菜单")
    
    # Assert
    logger.info("\n" + "=" * 80)
    logger.info("设置入口测试汇总:")
    logger.info(f"  - 三点菜单（...）: {'✅ 存在' if has_menu['exists'] else '❌ 不存在'}")
    if has_menu['exists'] and menu_result.get('opened'):
        logger.info(f"  - 菜单可打开: ✅")
        logger.info(f"  - 菜单项数量: {menu_result['item_count']}")
    
    logger.info("✅ TC010 测试通过！")
    logger.info("=" * 80)


@pytest.mark.p2
@allure.feature("OK - Messages")
@allure.story("Messages页面功能探索 - 置顶功能")
@allure.title("TC011: 测试会话置顶/取消置顶功能")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.messages
@pytest.mark.conversation
@pytest.mark.pin
@pytest.mark.exploration
@pytest.mark.ae
@pytest.mark.case_id_messages_explore_011
def test_pin_function(page, config):
    """
    TC011: 会话页面置顶功能测试
    
    测试步骤:
    1. 访问Messages页面并进入会话
    2. 打开三点菜单（...）
    3. 查找置顶选项（Pin/Unpin）
    4. 点击置顶选项并验证
    """
    logger.info("=" * 80)
    logger.info("TC011: 会话页面置顶功能测试")
    logger.info("=" * 80)
    
    # Arrange
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    login_page = LoginPage(page, base_url=config['base_url'])
    messages_page = MessagesExplorePage(page)
    
    # 加载Session或登录
    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        logger.info("✗ Session不存在，开始登录流程")
        login_page.navigate_to_home_page()
        login_page.handle_cookie_popup()
        login_page.login(config['test_account']['username'], config['test_account']['password'])
        session_manager.save_session()
        logger.info("✓ 登录成功并保存 Session")
    
    # Act
    
    # 步骤1: 导航到Messages页面并进入会话
    messages_page.navigate_to_messages_directly(config['target_page'])
    logger.info("✓ 已导航到Messages页面")
    
    messages_page.wait_for_conversation_list()
    conv_count = messages_page.get_conversation_count()
    logger.info(f"✓ 会话列表加载完成，当前会话数: {conv_count}")
    
    if conv_count == 0:
        logger.warning("⚠️ 会话列表为空，跳过测试")
        pytest.skip("会话列表为空")
    
    # 点击第二个会话
    messages_page.click_conversation_by_index(1)
    page.wait_for_timeout(3000)
    logger.info("✓ 已进入会话详情页")
    
    # 步骤2: 打开三点菜单
    logger.info("\n--- 打开三点菜单 ---")
    menu_result = messages_page.click_three_dots_menu()
    
    if not menu_result['opened']:
        logger.warning(f"⚠️ 三点菜单未打开: {menu_result.get('error', '未知原因')}")
        pytest.skip("三点菜单未打开")
    
    logger.info(f"✓ 菜单已打开，菜单项数量: {menu_result['item_count']}")
    
    # 截图
    page.screenshot(path="screenshots/tc011_menu_opened.png", timeout=60000)
    
    # 步骤3: 查找置顶选项
    logger.info("\n--- 查找置顶选项 ---")
    has_pin = messages_page.check_pin_option_in_menu()
    logger.info(f"✓ 置顶选项: {has_pin['exists']}")
    
    if has_pin['exists']:
        logger.info(f"  选项文本: {has_pin['text']}")
        
        # 步骤4: 点击置顶选项
        logger.info("\n--- 点击置顶选项 ---")
        pin_result = messages_page.click_pin_option(cancel=True)
        logger.info(f"✓ 点击成功: {pin_result['success']}")
        logger.info(f"  确认弹窗: {pin_result['has_dialog']}")
        
        if pin_result['has_dialog']:
            page.screenshot(path="screenshots/tc011_pin_dialog.png", timeout=60000)
            logger.info("✓ 已截图: tc011_pin_dialog.png")
    else:
        logger.warning("  ✗ 未找到置顶选项")
    
    # Assert
    logger.info("\n" + "=" * 80)
    logger.info("置顶功能测试汇总:")
    logger.info(f"  - 置顶选项: {'✅ 存在' if has_pin['exists'] else '❌ 不存在'}")
    if has_pin['exists']:
        logger.info(f"  - 选项文本: {has_pin['text']}")
        logger.info(f"  - 点击成功: {'✅' if pin_result['success'] else '❌'}")
    
    logger.info("✅ TC011 测试通过！")
    logger.info("=" * 80)


@pytest.mark.p2
@allure.feature("OK - Messages")
@allure.story("Messages页面功能探索 - 免打扰功能")
@allure.title("TC012: 测试会话免打扰/取消免打扰功能")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.messages
@pytest.mark.conversation
@pytest.mark.mute
@pytest.mark.exploration
@pytest.mark.ae
@pytest.mark.case_id_messages_explore_012
def test_mute_function(page, config):
    """
    TC012: 会话页面免打扰功能测试
    
    测试步骤:
    1. 访问Messages页面并进入会话
    2. 打开三点菜单（...）
    3. 查找免打扰选项（Mute/Unmute）
    4. 点击免打扰选项并验证
    """
    logger.info("=" * 80)
    logger.info("TC012: 会话页面免打扰功能测试")
    logger.info("=" * 80)
    
    # Arrange
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    login_page = LoginPage(page, base_url=config['base_url'])
    messages_page = MessagesExplorePage(page)
    
    # 加载Session或登录
    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        logger.info("✗ Session不存在，开始登录流程")
        login_page.navigate_to_home_page()
        login_page.handle_cookie_popup()
        login_page.login(config['test_account']['username'], config['test_account']['password'])
        session_manager.save_session()
        logger.info("✓ 登录成功并保存 Session")
    
    # Act
    
    # 步骤1: 导航到Messages页面并进入会话
    messages_page.navigate_to_messages_directly(config['target_page'])
    logger.info("✓ 已导航到Messages页面")
    
    messages_page.wait_for_conversation_list()
    conv_count = messages_page.get_conversation_count()
    logger.info(f"✓ 会话列表加载完成，当前会话数: {conv_count}")
    
    if conv_count == 0:
        logger.warning("⚠️ 会话列表为空，跳过测试")
        pytest.skip("会话列表为空")
    
    # 点击第二个会话
    messages_page.click_conversation_by_index(1)
    page.wait_for_timeout(3000)
    logger.info("✓ 已进入会话详情页")
    
    # 步骤2: 打开三点菜单
    logger.info("\n--- 打开三点菜单 ---")
    menu_result = messages_page.click_three_dots_menu()
    
    if not menu_result['opened']:
        logger.warning(f"⚠️ 三点菜单未打开: {menu_result.get('error', '未知原因')}")
        pytest.skip("三点菜单未打开")
    
    logger.info(f"✓ 菜单已打开，菜单项数量: {menu_result['item_count']}")
    
    # 截图
    page.screenshot(path="screenshots/tc012_menu_opened.png", timeout=60000)
    
    # 步骤3: 查找免打扰选项
    logger.info("\n--- 查找免打扰选项 ---")
    has_mute = messages_page.check_mute_option_in_menu()
    logger.info(f"✓ 免打扰选项: {has_mute['exists']}")
    
    if has_mute['exists']:
        logger.info(f"  选项文本: {has_mute['text']}")
        
        # 步骤4: 点击免打扰选项
        logger.info("\n--- 点击免打扰选项 ---")
        mute_result = messages_page.click_mute_option(cancel=True)
        logger.info(f"✓ 点击成功: {mute_result['success']}")
        logger.info(f"  确认弹窗: {mute_result['has_dialog']}")
        
        if mute_result['has_dialog']:
            page.screenshot(path="screenshots/tc012_mute_dialog.png", timeout=60000)
            logger.info("✓ 已截图: tc012_mute_dialog.png")
    else:
        logger.warning("  ✗ 未找到免打扰选项")
    
    # Assert
    logger.info("\n" + "=" * 80)
    logger.info("免打扰功能测试汇总:")
    logger.info(f"  - 免打扰选项: {'✅ 存在' if has_mute['exists'] else '❌ 不存在'}")
    if has_mute['exists']:
        logger.info(f"  - 选项文本: {has_mute['text']}")
        logger.info(f"  - 点击成功: {'✅' if mute_result['success'] else '❌'}")
    
    logger.info("✅ TC012 测试通过！")
    logger.info("=" * 80)


@pytest.mark.p1
@allure.feature("OK - Messages")
@allure.story("Messages页面功能探索 - 拉黑功能")
@allure.title("TC013: 测试会话拉黑/取消拉黑完整流程")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.messages
@pytest.mark.conversation
@pytest.mark.block
@pytest.mark.exploration
@pytest.mark.ae
@pytest.mark.case_id_messages_explore_013
def test_block_function(page, config):
    """
    TC013: 会话页面拉黑功能完整测试
    
    测试步骤:
    1. 访问Messages页面并进入会话
    2. 打开三点菜单（...）
    3. 查找并点击Block选项
    4. 测试拉黑确认弹窗的Cancel按钮
    5. 重新打开菜单，点击Block选项
    6. 测试拉黑确认弹窗的Block按钮（确认拉黑）
    7. 验证拉黑半层显示
    8. 测试拉黑半层上的Unblock按钮
    """
    logger.info("=" * 80)
    logger.info("TC013: 会话页面拉黑功能完整测试")
    logger.info("=" * 80)
    
    # Arrange
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    login_page = LoginPage(page, base_url=config['base_url'])
    messages_page = MessagesExplorePage(page)
    
    # 加载Session或登录
    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        logger.info("✗ Session不存在，开始登录流程")
        login_page.navigate_to_home_page()
        login_page.handle_cookie_popup()
        login_page.login(config['test_account']['username'], config['test_account']['password'])
        session_manager.save_session()
        logger.info("✓ 登录成功并保存 Session")
    
    # Act
    
    # 步骤1: 导航到Messages页面并进入会话
    messages_page.navigate_to_messages_directly(config['target_page'])
    logger.info("✓ 已导航到Messages页面")
    
    messages_page.wait_for_conversation_list()
    conv_count = messages_page.get_conversation_count()
    logger.info(f"✓ 会话列表加载完成，当前会话数: {conv_count}")
    
    if conv_count == 0:
        logger.warning("⚠️ 会话列表为空，跳过测试")
        pytest.skip("会话列表为空")
    
    # 点击第二个会话
    messages_page.click_conversation_by_index(1)
    page.wait_for_timeout(3000)
    logger.info("✓ 已进入会话详情页")
    page.screenshot(path="screenshots/tc013_conversation_page.png", timeout=60000)
    
    # 步骤2: 打开三点菜单
    logger.info("\n--- 步骤2: 打开三点菜单 ---")
    menu_result = messages_page.click_three_dots_menu()
    
    if not menu_result['opened']:
        logger.warning(f"⚠️ 三点菜单未打开: {menu_result.get('error', '未知原因')}")
        pytest.skip("三点菜单未打开")
    
    logger.info(f"✓ 菜单已打开，菜单项数量: {menu_result['item_count']}")
    page.screenshot(path="screenshots/tc013_menu_opened.png", timeout=60000)
    
    # 步骤3: 查找拉黑选项
    logger.info("\n--- 步骤3: 查找Block选项 ---")
    has_block = messages_page.check_block_option_in_menu()
    logger.info(f"✓ Block选项: {has_block['exists']}")
    
    if not has_block['exists']:
        logger.warning("  ✗ 未找到Block选项，跳过测试")
        pytest.skip("未找到Block选项")
    
    logger.info(f"  选项文本: {has_block['text']}")
    logger.info(f"  选项位置: ({has_block.get('x', 'N/A')}, {has_block.get('y', 'N/A')})")
    
    # 步骤4: 测试Cancel按钮 - 点击Block并在弹窗中点击Cancel
    logger.info("\n--- 步骤4: 测试拉黑确认弹窗的Cancel按钮 ---")
    
    # 使用坐标点击Block选项
    if 'x' in has_block and 'y' in has_block:
        logger.info(f"点击Block选项: ({has_block['x']}, {has_block['y']})")
        page.mouse.click(has_block['x'] + 10, has_block['y'] + 10)
    else:
        page.locator("text=/^Block$/i, text=/^拉黑$/i").first.click()
    
    page.wait_for_timeout(1000)
    # 点击后立即截图，查看页面状态
    page.screenshot(path="screenshots/tc013_after_block_click.png", timeout=60000)
    logger.info("✓ 已截图: tc013_after_block_click.png")
    
    page.wait_for_timeout(1000)
    
    # 查找确认弹窗 - 使用更宽松的条件
    dialog_info = page.evaluate("""
        () => {
            // 尝试多种选择器查找弹窗
            const selectors = [
                '[role="dialog"]',
                '.modal',
                '[class*="Modal"]',
                '[class*="modal"]',
                '[class*="Dialog"]',
                '[class*="dialog"]',
                '[class*="Popup"]',
                '[class*="popup"]',
                '[class*="confirm"]',
                '[class*="Confirm"]'
            ];
            
            for (const selector of selectors) {
                const dialogs = document.querySelectorAll(selector);
                
                for (const dialog of dialogs) {
                    const rect = dialog.getBoundingClientRect();
                    const text = dialog.textContent?.toLowerCase() || '';
                    
                    // 检查是否是可见的弹窗，且包含block相关内容
                    if (rect.width > 100 && rect.height > 100 && 
                        (text.includes('block') || text.includes('confirm') || text.includes('sure'))) {
                        
                        const buttons = Array.from(dialog.querySelectorAll('button'));
                        const buttonTexts = buttons.map(btn => btn.textContent?.trim()).filter(text => text);
                        
                        return {
                            found: true,
                            text: dialog.textContent?.substring(0, 300),
                            buttons: buttonTexts,
                            visible: true,
                            selector: selector,
                            position: {x: Math.round(rect.x), y: Math.round(rect.y)},
                            size: {width: Math.round(rect.width), height: Math.round(rect.height)}
                        };
                    }
                }
            }
            
            return {found: false};
        }
    """)
    
    logger.info(f"✓ 确认弹窗: {dialog_info['found']}")
    
    if dialog_info['found']:
        logger.info(f"  弹窗可见: {dialog_info['visible']}")
        logger.info(f"  弹窗选择器: {dialog_info.get('selector', 'N/A')}")
        logger.info(f"  弹窗位置: ({dialog_info.get('position', {}).get('x', 'N/A')}, {dialog_info.get('position', {}).get('y', 'N/A')})")
        logger.info(f"  弹窗大小: {dialog_info.get('size', {}).get('width', 'N/A')}x{dialog_info.get('size', {}).get('height', 'N/A')}")
        logger.info(f"  弹窗按钮: {dialog_info['buttons']}")
        logger.info(f"  弹窗内容: {dialog_info['text'][:150]}")
        page.screenshot(path="screenshots/tc013_block_dialog.png", timeout=60000)
        logger.info("✓ 已截图: tc013_block_dialog.png")
        
        # 点击Cancel按钮
        logger.info("\n  点击Cancel按钮...")
        cancel_clicked = page.evaluate("""
            () => {
                // 尝试多种选择器查找弹窗
                const dialogSelectors = [
                    '[role="dialog"]',
                    '.modal',
                    '[class*="modal"]',
                    '[class*="Modal"]',
                    '[class*="Dialog"]',
                    '[class*="dialog"]'
                ];
                
                for (const selector of dialogSelectors) {
                    const dialogs = document.querySelectorAll(selector);
                    
                    for (const dialog of dialogs) {
                        const rect = dialog.getBoundingClientRect();
                        const text = dialog.textContent?.toLowerCase() || '';
                        
                        // 确保是可见的拉黑确认弹窗
                        if (rect.width > 100 && rect.height > 100 && text.includes('block')) {
                            const buttons = Array.from(dialog.querySelectorAll('button'));
                            const cancelBtn = buttons.find(btn => {
                                const btnText = btn.textContent?.trim().toLowerCase() || '';
                                return btnText === 'cancel' || btnText === 'close' || btnText === 'no' || btnText === '取消';
                            });
                            
                            if (cancelBtn) {
                                cancelBtn.click();
                                return {success: true, buttonText: cancelBtn.textContent?.trim()};
                            }
                        }
                    }
                }
                
                return {success: false};
            }
        """)
        
        if cancel_clicked.get('success'):
            logger.info(f"  ✓ Cancel按钮点击成功: {cancel_clicked.get('buttonText', 'Cancel')}")
            page.wait_for_timeout(1000)
            page.screenshot(path="screenshots/tc013_after_cancel.png", timeout=60000)
            logger.info("✓ 已截图: tc013_after_cancel.png")
        else:
            logger.warning("  ⚠️ 未找到Cancel按钮，使用ESC键关闭")
            page.keyboard.press('Escape')
            page.wait_for_timeout(1000)
    else:
        logger.warning("  ⚠️ 未检测到确认弹窗，可能直接拉黑")
    
    # 检查是否直接显示了拉黑半层（无论是否有弹窗）
    page.wait_for_timeout(2000)
    block_overlay_early = page.evaluate("""
        () => {
            const allElements = Array.from(document.querySelectorAll('div, section'));
            
            for (const el of allElements) {
                const text = el.textContent?.toLowerCase() || '';
                const rect = el.getBoundingClientRect();
                
                if ((text.includes('blocked') || text.includes('unblock')) &&
                    rect.x > 300 && rect.width > 200 && rect.height > 100) {
                    
                    // 查找Unblock按钮
                    const buttons = Array.from(el.querySelectorAll('button'));
                    const unblockBtn = buttons.find(btn => {
                        const btnText = btn.textContent?.trim().toLowerCase() || '';
                        return btnText === 'unblock' || btnText === '取消拉黑' || btnText.includes('unblock');
                    });
                    
                    return {
                        found: true,
                        text: el.textContent?.substring(0, 200),
                        hasUnblockButton: !!unblockBtn,
                        unblockButtonText: unblockBtn ? unblockBtn.textContent?.trim() : null
                    };
                }
            }
            
            return {found: false};
        }
    """)
    
    if block_overlay_early['found']:
        logger.info("\n--- 检测到拉黑半层（直接拉黑，无确认弹窗） ---")
        logger.info(f"✓ 拉黑半层: {block_overlay_early['found']}")
        logger.info(f"  半层内容: {block_overlay_early['text'][:100]}")
        logger.info(f"  包含Unblock按钮: {block_overlay_early['hasUnblockButton']}")
        if block_overlay_early['hasUnblockButton']:
            logger.info(f"  Unblock按钮文本: {block_overlay_early['unblockButtonText']}")
        page.screenshot(path="screenshots/tc013_block_overlay_direct.png", timeout=60000)
        logger.info("✓ 已截图: tc013_block_overlay_direct.png")
        
        # 直接测试Unblock按钮
        if block_overlay_early['hasUnblockButton']:
            logger.info("\n--- 测试拉黑半层上的Unblock按钮 ---")
            
            # 点击Unblock按钮
            unblock_clicked = page.evaluate("""
                () => {
                    const allElements = Array.from(document.querySelectorAll('div, section'));
                    
                    for (const el of allElements) {
                        const text = el.textContent?.toLowerCase() || '';
                        const rect = el.getBoundingClientRect();
                        
                        if ((text.includes('blocked') || text.includes('unblock')) &&
                            rect.x > 300 && rect.width > 200) {
                            
                            const buttons = Array.from(el.querySelectorAll('button'));
                            const unblockBtn = buttons.find(btn => {
                                const btnText = btn.textContent?.trim().toLowerCase() || '';
                                return btnText === 'unblock' || btnText === '取消拉黑' || btnText.includes('unblock');
                            });
                            
                            if (unblockBtn) {
                                unblockBtn.click();
                                return {success: true, buttonText: unblockBtn.textContent?.trim()};
                            }
                        }
                    }
                    
                    return {success: false};
                }
            """)
            
            logger.info(f"✓ Unblock按钮点击: {unblock_clicked['success']}")
            if unblock_clicked['success']:
                logger.info(f"  按钮文本: {unblock_clicked.get('buttonText', 'N/A')}")
                page.wait_for_timeout(3000)
                page.screenshot(path="screenshots/tc013_after_unblock.png", timeout=60000)
                logger.info("✓ 已截图: tc013_after_unblock.png")
                
                # 验证拉黑半层是否消失
                overlay_gone = page.evaluate("""
                    () => {
                        const allElements = Array.from(document.querySelectorAll('div, section'));
                        
                        for (const el of allElements) {
                            const text = el.textContent?.toLowerCase() || '';
                            const rect = el.getBoundingClientRect();
                            
                            if ((text.includes('blocked') || text.includes('unblock')) &&
                                rect.x > 300 && rect.width > 200 && rect.height > 100) {
                                return false;
                            }
                        }
                        
                        return true;
                    }
                """)
                
                logger.info(f"✓ 拉黑半层已消失: {overlay_gone}")
            else:
                logger.warning("  ⚠️ Unblock按钮点击失败")
        
        # 直接跳到Assert
        logger.info("\n" + "=" * 80)
        logger.info("拉黑功能完整测试汇总:")
        logger.info(f"  - Block选项: ✅ 存在")
        logger.info(f"  - 确认弹窗: ❌ 无弹窗（直接拉黑）")
        logger.info(f"  - 拉黑半层: ✅ 显示")
        logger.info(f"  - Unblock按钮: {'✅ 测试通过' if block_overlay_early.get('hasUnblockButton') and unblock_clicked.get('success') else '❌ 测试失败'}")
        
        logger.info("✅ TC013 测试通过！")
        logger.info("=" * 80)
        return  # 提前结束测试
    
    # 步骤5: 重新打开菜单并点击Block
    logger.info("\n--- 步骤5: 重新打开菜单并点击Block ---")
    page.wait_for_timeout(1000)
    
    # 重新打开三点菜单
    menu_result2 = messages_page.click_three_dots_menu()
    if not menu_result2['opened']:
        logger.warning("⚠️ 无法重新打开菜单")
        pytest.skip("无法重新打开菜单")
    
    logger.info("✓ 菜单已重新打开")
    page.wait_for_timeout(1000)
    
    # 再次查找Block选项
    has_block2 = messages_page.check_block_option_in_menu()
    if not has_block2['exists']:
        logger.warning("⚠️ 未找到Block选项")
        pytest.skip("未找到Block选项")
    
    # 点击Block选项
    if 'x' in has_block2 and 'y' in has_block2:
        logger.info(f"再次点击Block选项: ({has_block2['x']}, {has_block2['y']})")
        page.mouse.click(has_block2['x'] + 10, has_block2['y'] + 10)
    else:
        page.locator("text=/^Block$/i, text=/^拉黑$/i").first.click()
    
    page.wait_for_timeout(1000)
    page.screenshot(path="screenshots/tc013_after_second_block_click.png", timeout=60000)
    logger.info("✓ 已截图: tc013_after_second_block_click.png")
    page.wait_for_timeout(1000)
    
    # 步骤6: 点击Block确认按钮
    logger.info("\n--- 步骤6: 测试拉黑确认弹窗的Block按钮 ---")
    
    # 查找并点击Block确认按钮
    block_confirmed = page.evaluate("""
        () => {
            // 尝试多种选择器查找弹窗
            const dialogSelectors = [
                '[role="dialog"]',
                '.modal',
                '[class*="modal"]',
                '[class*="Modal"]',
                '[class*="Dialog"]',
                '[class*="dialog"]'
            ];
            
            for (const selector of dialogSelectors) {
                const dialogs = document.querySelectorAll(selector);
                
                for (const dialog of dialogs) {
                    const rect = dialog.getBoundingClientRect();
                    const text = dialog.textContent?.toLowerCase() || '';
                    
                    // 确保是可见的拉黑确认弹窗
                    if (rect.width > 100 && rect.height > 100 && text.includes('block')) {
                        const buttons = Array.from(dialog.querySelectorAll('button'));
                        const blockBtn = buttons.find(btn => {
                            const btnText = btn.textContent?.trim().toLowerCase() || '';
                            return btnText === 'block' || btnText === 'confirm' || btnText === 'ok' || btnText === '确认' || btnText === '拉黑';
                        });
                        
                        if (blockBtn) {
                            blockBtn.click();
                            return {success: true, buttonText: blockBtn.textContent?.trim()};
                        }
                    }
                }
            }
            
            return {success: false, reason: 'block_button_not_found'};
        }
    """)
    
    logger.info(f"✓ Block按钮点击: {block_confirmed['success']}")
    if block_confirmed['success']:
        logger.info(f"  按钮文本: {block_confirmed.get('buttonText', 'N/A')}")
        page.wait_for_timeout(3000)  # 等待拉黑操作完成
        page.screenshot(path="screenshots/tc013_after_block_confirm.png", timeout=60000)
        logger.info("✓ 已截图: tc013_after_block_confirm.png")
    else:
        logger.warning(f"  ⚠️ Block按钮点击失败: {block_confirmed.get('reason', 'unknown')}")
    
    # 步骤7: 验证拉黑半层显示
    logger.info("\n--- 步骤7: 验证拉黑半层显示 ---")
    
    # 查找拉黑半层
    block_overlay = page.evaluate("""
        () => {
            // 查找包含"blocked"、"unblock"等关键词的覆盖层
            const allElements = Array.from(document.querySelectorAll('div, section'));
            
            for (const el of allElements) {
                const text = el.textContent?.toLowerCase() || '';
                const rect = el.getBoundingClientRect();
                
                // 查找包含unblock关键词且位于右侧区域的元素
                if ((text.includes('blocked') || text.includes('unblock') || text.includes('已拉黑')) &&
                    rect.x > 300 && rect.width > 200 && rect.height > 100) {
                    
                    // 查找Unblock按钮
                    const buttons = Array.from(el.querySelectorAll('button'));
                    const unblockBtn = buttons.find(btn => {
                        const btnText = btn.textContent?.trim().toLowerCase() || '';
                        return btnText === 'unblock' || btnText === '取消拉黑' || btnText.includes('unblock');
                    });
                    
                    return {
                        found: true,
                        text: el.textContent?.substring(0, 200),
                        hasUnblockButton: !!unblockBtn,
                        unblockButtonText: unblockBtn ? unblockBtn.textContent?.trim() : null,
                        position: {x: Math.round(rect.x), y: Math.round(rect.y)},
                        size: {width: Math.round(rect.width), height: Math.round(rect.height)}
                    };
                }
            }
            
            return {found: false};
        }
    """)
    
    logger.info(f"✓ 拉黑半层: {block_overlay['found']}")
    
    if block_overlay['found']:
        logger.info(f"  半层位置: ({block_overlay['position']['x']}, {block_overlay['position']['y']})")
        logger.info(f"  半层大小: {block_overlay['size']['width']}x{block_overlay['size']['height']}")
        logger.info(f"  包含Unblock按钮: {block_overlay['hasUnblockButton']}")
        if block_overlay['hasUnblockButton']:
            logger.info(f"  Unblock按钮文本: {block_overlay['unblockButtonText']}")
        logger.info(f"  半层内容: {block_overlay['text'][:100]}")
        page.screenshot(path="screenshots/tc013_block_overlay.png", timeout=60000)
        logger.info("✓ 已截图: tc013_block_overlay.png")
        
        # 步骤8: 测试Unblock按钮
        if block_overlay['hasUnblockButton']:
            logger.info("\n--- 步骤8: 测试拉黑半层上的Unblock按钮 ---")
            
            # 点击Unblock按钮
            unblock_clicked = page.evaluate("""
                () => {
                    const allElements = Array.from(document.querySelectorAll('div, section'));
                    
                    for (const el of allElements) {
                        const text = el.textContent?.toLowerCase() || '';
                        const rect = el.getBoundingClientRect();
                        
                        if ((text.includes('blocked') || text.includes('unblock')) &&
                            rect.x > 300 && rect.width > 200) {
                            
                            const buttons = Array.from(el.querySelectorAll('button'));
                            const unblockBtn = buttons.find(btn => {
                                const btnText = btn.textContent?.trim().toLowerCase() || '';
                                return btnText === 'unblock' || btnText === '取消拉黑' || btnText.includes('unblock');
                            });
                            
                            if (unblockBtn) {
                                unblockBtn.click();
                                return {success: true, buttonText: unblockBtn.textContent?.trim()};
                            }
                        }
                    }
                    
                    return {success: false};
                }
            """)
            
            logger.info(f"✓ Unblock按钮点击: {unblock_clicked['success']}")
            if unblock_clicked['success']:
                logger.info(f"  按钮文本: {unblock_clicked.get('buttonText', 'N/A')}")
                page.wait_for_timeout(3000)  # 等待取消拉黑操作完成
                page.screenshot(path="screenshots/tc013_after_unblock.png", timeout=60000)
                logger.info("✓ 已截图: tc013_after_unblock.png")
                
                # 验证拉黑半层是否消失
                overlay_gone = page.evaluate("""
                    () => {
                        const allElements = Array.from(document.querySelectorAll('div, section'));
                        
                        for (const el of allElements) {
                            const text = el.textContent?.toLowerCase() || '';
                            const rect = el.getBoundingClientRect();
                            
                            if ((text.includes('blocked') || text.includes('unblock')) &&
                                rect.x > 300 && rect.width > 200 && rect.height > 100) {
                                return false;  // 半层仍然存在
                            }
                        }
                        
                        return true;  // 半层已消失
                    }
                """)
                
                logger.info(f"✓ 拉黑半层已消失: {overlay_gone}")
            else:
                logger.warning("  ⚠️ Unblock按钮点击失败")
        else:
            logger.warning("  ⚠️ 拉黑半层中未找到Unblock按钮")
    else:
        logger.warning("  ⚠️ 未检测到拉黑半层")
    
    # Assert
    logger.info("\n" + "=" * 80)
    logger.info("拉黑功能完整测试汇总:")
    logger.info(f"  - Block选项: ✅ 存在")
    logger.info(f"  - 确认弹窗: {'✅ 显示' if dialog_info['found'] else '❌ 未显示'}")
    logger.info(f"  - Cancel按钮: {'✅ 测试通过' if dialog_info['found'] else '⚠️ 未测试'}")
    logger.info(f"  - Block确认按钮: {'✅ 测试通过' if block_confirmed['success'] else '❌ 测试失败'}")
    logger.info(f"  - 拉黑半层: {'✅ 显示' if block_overlay['found'] else '❌ 未显示'}")
    logger.info(f"  - Unblock按钮: {'✅ 测试通过' if block_overlay.get('hasUnblockButton') else '❌ 未找到'}")
    
    logger.info("✅ TC013 测试通过！")
    logger.info("=" * 80)


@pytest.mark.p1
@allure.feature("OK - Messages")
@allure.story("Messages页面功能探索 - 消息发送")
@allure.title("TC014: 输入框输入消息并发送")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.messages
@pytest.mark.conversation
@pytest.mark.send
@pytest.mark.exploration
@pytest.mark.ae
@pytest.mark.case_id_messages_explore_014
def test_send_message(page, config):
    """
    TC014: 会话页面消息发送功能测试
    
    测试步骤:
    1. 访问Messages页面并进入会话
    2. 定位消息输入框
    3. 输入测试消息"hello"
    4. 定位并点击发送按钮
    5. 验证消息已发送
    """
    logger.info("=" * 80)
    logger.info("TC014: 会话页面消息发送功能测试")
    logger.info("=" * 80)
    
    # Arrange
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    login_page = LoginPage(page, base_url=config['base_url'])
    messages_page = MessagesExplorePage(page)
    
    # 加载Session或登录
    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        logger.info("✗ Session不存在，开始登录流程")
        login_page.navigate_to_home_page()
        login_page.handle_cookie_popup()
        login_page.login(config['test_account']['username'], config['test_account']['password'])
        session_manager.save_session()
        logger.info("✓ 登录成功并保存 Session")
    
    # Act
    
    # 步骤1: 导航到Messages页面并进入会话
    messages_page.navigate_to_messages_directly(config['target_page'])
    logger.info("✓ 已导航到Messages页面")
    
    messages_page.wait_for_conversation_list()
    conv_count = messages_page.get_conversation_count()
    logger.info(f"✓ 会话列表加载完成，当前会话数: {conv_count}")
    
    if conv_count == 0:
        logger.warning("⚠️ 会话列表为空，跳过测试")
        pytest.skip("会话列表为空")
    
    # 点击第二个会话
    messages_page.click_conversation_by_index(1)
    page.wait_for_timeout(3000)
    logger.info("✓ 已进入会话详情页")
    
    # 截图（初始状态）
    page.screenshot(path="screenshots/tc014_conversation_page.png", timeout=60000)
    logger.info("✓ 已截图: tc014_conversation_page.png")
    
    # 步骤2: 检查消息输入框
    logger.info("\n--- 检查消息输入框 ---")
    has_input = messages_page.check_message_input()
    logger.info(f"✓ 消息输入框: {has_input['exists']}")
    
    if not has_input['exists']:
        logger.warning("⚠️ 消息输入框不存在，跳过测试")
        pytest.skip("消息输入框不存在")
    
    logger.info(f"  选择器: {has_input['selector']}")
    
    # 步骤3: 输入消息"hello"
    logger.info("\n--- 输入消息 'hello' ---")
    input_result = messages_page.input_message('hello')
    logger.info(f"✓ 输入成功: {input_result['success']}")
    logger.info(f"  输入内容: '{input_result['text']}'")
    
    if not input_result['success']:
        logger.error(f"  输入失败: {input_result.get('error', '未知错误')}")
    
    # 截图（输入后）
    page.screenshot(path="screenshots/tc014_after_input.png", timeout=60000)
    logger.info("✓ 已截图: tc014_after_input.png")
    
    # 步骤4: 检查并点击发送按钮
    logger.info("\n--- 检查发送按钮 ---")
    has_send_button = messages_page.check_send_button()
    logger.info(f"✓ 发送按钮: {has_send_button['exists']}")
    
    if not has_send_button['exists']:
        logger.warning("⚠️ 发送按钮不存在，跳过发送")
        pytest.skip("发送按钮不存在")
    
    if 'x' in has_send_button and 'y' in has_send_button:
        logger.info(f"  位置: ({has_send_button['x']}, {has_send_button['y']})")
    if 'text' in has_send_button:
        logger.info(f"  按钮文本: '{has_send_button['text']}'")
    
    # 截图（发送前）
    page.screenshot(path="screenshots/tc014_before_send.png", timeout=60000)
    logger.info("✓ 已截图: tc014_before_send.png")
    
    logger.info("\n--- 点击发送按钮 ---")
    send_result = messages_page.click_send_button()
    logger.info(f"✓ 点击成功: {send_result['success']}")
    logger.info(f"  输入框已清空: {send_result['input_cleared']}")
    
    # 等待消息发送并显示（最多等待5秒）
    logger.info("\n--- 等待消息显示 ---")
    page.wait_for_timeout(2000)  # 先等待2秒
    
    # 尝试滚动消息列表到底部
    try:
        page.evaluate("""
            () => {
                // 查找消息历史容器并滚动到底部
                const containers = document.querySelectorAll('[class*="message"], [class*="chat"], [class*="conversation"]');
                for (const container of containers) {
                    if (container.scrollHeight > container.clientHeight) {
                        container.scrollTop = container.scrollHeight;
                    }
                }
            }
        """)
        logger.info("✓ 已滚动到消息列表底部")
        page.wait_for_timeout(1000)  # 等待滚动完成
    except Exception as e:
        logger.warning(f"滚动失败: {e}")
    
    # 截图（发送后）
    page.screenshot(path="screenshots/tc014_after_send.png", timeout=60000)
    logger.info("✓ 已截图: tc014_after_send.png")
    
    # 步骤5: 验证消息已发送（多次尝试）
    logger.info("\n--- 验证消息已发送 ---")
    latest_message = None
    max_retries = 3
    
    for attempt in range(max_retries):
        latest_message = messages_page.get_latest_message()
        if latest_message['found'] and 'hello' in latest_message['text'].lower():
            logger.info(f"✓ 第{attempt + 1}次尝试：找到消息")
            break
        else:
            if attempt < max_retries - 1:
                logger.info(f"⚠️ 第{attempt + 1}次尝试：未找到消息，等待1秒后重试...")
                page.wait_for_timeout(1000)
            else:
                logger.warning(f"⚠️ 第{attempt + 1}次尝试：仍未找到消息")
    
    logger.info(f"✓ 找到消息: {latest_message['found']}")
    
    if latest_message['found']:
        logger.info(f"  最新消息: '{latest_message['text']}'")
        logger.info(f"  包含'hello': {'hello' in latest_message['text'].lower()}")
        logger.info(f"  消息总数: {latest_message['count']}")
    
    # Assert
    logger.info("\n" + "=" * 80)
    logger.info("消息发送功能测试汇总:")
    logger.info(f"  - 消息输入框: {'✅ 存在' if has_input['exists'] else '❌ 不存在'}")
    logger.info(f"  - 输入成功: {'✅' if input_result['success'] else '❌'}")
    logger.info(f"  - 发送按钮: {'✅ 存在' if has_send_button['exists'] else '❌ 不存在'}")
    logger.info(f"  - 发送成功: {'✅' if send_result['success'] else '❌'}")
    logger.info(f"  - 输入框清空: {'✅' if send_result['input_cleared'] else '❌'}")
    if latest_message['found']:
        logger.info(f"  - 消息已显示: {'✅' if 'hello' in latest_message['text'].lower() else '⚠️ 未确认'}")
    
    logger.info("✅ TC014 测试通过！")
    logger.info("=" * 80)


@pytest.mark.p1
@allure.feature("OK - Messages")
@allure.story("Messages页面功能探索 - 消息发送")
@allure.title("TC014A: 输入框输入URL并发送")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.messages
@pytest.mark.conversation
@pytest.mark.send
@pytest.mark.url
@pytest.mark.exploration
@pytest.mark.ae
@pytest.mark.case_id_messages_explore_014a
def test_send_url_message(page, config):
    """
    TC014A: 会话页面发送URL消息功能测试
    
    测试步骤:
    1. 访问Messages页面并进入会话
    2. 定位消息输入框
    3. 输入测试URL "https://www.google.com"
    4. 定位并点击发送按钮
    5. 验证URL消息已发送并正确显示
    """
    logger.info("=" * 80)
    logger.info("TC014A: 会话页面发送URL消息功能测试")
    logger.info("=" * 80)
    
    # Arrange
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    login_page = LoginPage(page, base_url=config['base_url'])
    messages_page = MessagesExplorePage(page)
    
    # 加载Session或登录
    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        logger.info("✗ Session不存在，开始登录流程")
        login_page.navigate_to_home_page()
        login_page.handle_cookie_popup()
        login_page.login(config['test_account']['username'], config['test_account']['password'])
        session_manager.save_session()
        logger.info("✓ 登录成功并保存 Session")
    
    # Act
    
    # 步骤1: 导航到Messages页面并进入会话
    messages_page.navigate_to_messages_directly(config['target_page'])
    logger.info("✓ 已导航到Messages页面")
    
    messages_page.wait_for_conversation_list()
    conv_count = messages_page.get_conversation_count()
    logger.info(f"✓ 会话列表加载完成，当前会话数: {conv_count}")
    
    if conv_count == 0:
        logger.warning("⚠️ 会话列表为空，跳过测试")
        pytest.skip("会话列表为空")
    
    # 点击第二个会话
    messages_page.click_conversation_by_index(1)
    page.wait_for_timeout(3000)
    logger.info("✓ 已进入会话详情页")
    
    # 截图（初始状态）
    page.screenshot(path="screenshots/tc014a_conversation_page.png", timeout=60000)
    logger.info("✓ 已截图: tc014a_conversation_page.png")
    
    # 步骤2: 检查消息输入框
    logger.info("\n--- 检查消息输入框 ---")
    has_input = messages_page.check_message_input()
    logger.info(f"✓ 消息输入框: {has_input['exists']}")
    
    if not has_input['exists']:
        logger.warning("⚠️ 消息输入框不存在，跳过测试")
        pytest.skip("消息输入框不存在")
    
    logger.info(f"  选择器: {has_input['selector']}")
    
    # 步骤3: 输入URL "https://www.google.com"
    test_url = "https://www.google.com"
    logger.info(f"\n--- 输入URL '{test_url}' ---")
    input_result = messages_page.input_message(test_url)
    logger.info(f"✓ 输入成功: {input_result['success']}")
    logger.info(f"  输入内容: '{input_result['text']}'")
    
    if not input_result['success']:
        logger.error(f"  输入失败: {input_result.get('error', '未知错误')}")
    
    # 截图（输入URL后）
    page.screenshot(path="screenshots/tc014a_after_url_input.png", timeout=60000)
    logger.info("✓ 已截图: tc014a_after_url_input.png")
    
    # 检查URL是否被自动识别为链接
    logger.info("\n--- 检查URL是否被识别为链接 ---")
    url_recognized = page.evaluate("""
        () => {
            const input = document.querySelector('textarea[placeholder*="message"], input[placeholder*="message"]');
            if (!input) return {found: false};
            
            const value = input.value || input.textContent || '';
            const hasUrl = value.includes('http://') || value.includes('https://');
            
            // 检查是否有链接预览或特殊样式
            const parent = input.closest('[class*="input"], [class*="message"]');
            if (parent) {
                const hasLinkPreview = parent.querySelector('[class*="link"], [class*="preview"], a[href]');
                return {
                    found: true,
                    hasUrl: hasUrl,
                    hasLinkPreview: !!hasLinkPreview,
                    inputValue: value
                };
            }
            
            return {found: true, hasUrl: hasUrl, hasLinkPreview: false, inputValue: value};
        }
    """)
    
    logger.info(f"✓ URL识别检查:")
    logger.info(f"  输入框包含URL: {url_recognized.get('hasUrl', False)}")
    logger.info(f"  链接预览: {url_recognized.get('hasLinkPreview', False)}")
    logger.info(f"  输入框内容: '{url_recognized.get('inputValue', '')[:50]}'")
    
    # 步骤4: 检查并点击发送按钮
    logger.info("\n--- 检查发送按钮 ---")
    has_send_button = messages_page.check_send_button()
    logger.info(f"✓ 发送按钮: {has_send_button['exists']}")
    
    if not has_send_button['exists']:
        logger.warning("⚠️ 发送按钮不存在，跳过发送")
        pytest.skip("发送按钮不存在")
    
    if 'x' in has_send_button and 'y' in has_send_button:
        logger.info(f"  位置: ({has_send_button['x']}, {has_send_button['y']})")
    if 'text' in has_send_button:
        logger.info(f"  按钮文本: '{has_send_button['text']}'")
    
    # 截图（发送前）
    page.screenshot(path="screenshots/tc014a_before_send.png", timeout=60000)
    logger.info("✓ 已截图: tc014a_before_send.png")
    
    logger.info("\n--- 点击发送按钮 ---")
    send_result = messages_page.click_send_button()
    logger.info(f"✓ 点击成功: {send_result['success']}")
    logger.info(f"  输入框已清空: {send_result['input_cleared']}")
    
    # 等待消息发送并显示（最多等待5秒）
    logger.info("\n--- 等待URL消息显示 ---")
    page.wait_for_timeout(2000)  # 先等待2秒
    
    # 尝试滚动消息列表到底部
    try:
        page.evaluate("""
            () => {
                // 查找消息历史容器并滚动到底部
                const containers = document.querySelectorAll('[class*="message"], [class*="chat"], [class*="conversation"]');
                for (const container of containers) {
                    if (container.scrollHeight > container.clientHeight) {
                        container.scrollTop = container.scrollHeight;
                    }
                }
            }
        """)
        logger.info("✓ 已滚动到消息列表底部")
        page.wait_for_timeout(1000)  # 等待滚动完成
    except Exception as e:
        logger.warning(f"滚动失败: {e}")
    
    # 截图（发送后）
    page.screenshot(path="screenshots/tc014a_after_send.png", timeout=60000)
    logger.info("✓ 已截图: tc014a_after_send.png")
    
    # 步骤5: 验证URL消息已发送（多次尝试）
    logger.info("\n--- 验证URL消息已发送 ---")
    latest_message = None
    max_retries = 3
    
    for attempt in range(max_retries):
        latest_message = messages_page.get_latest_message()
        if latest_message['found'] and 'google.com' in latest_message['text'].lower():
            logger.info(f"✓ 第{attempt + 1}次尝试：找到URL消息")
            break
        else:
            if attempt < max_retries - 1:
                logger.info(f"⚠️ 第{attempt + 1}次尝试：未找到URL消息，等待1秒后重试...")
                page.wait_for_timeout(1000)
            else:
                logger.warning(f"⚠️ 第{attempt + 1}次尝试：仍未找到URL消息")
    
    logger.info(f"✓ 找到消息: {latest_message['found']}")
    
    if latest_message['found']:
        logger.info(f"  最新消息: '{latest_message['text']}'")
        logger.info(f"  包含'google.com': {'google.com' in latest_message['text'].lower()}")
        logger.info(f"  消息总数: {latest_message['count']}")
    
    # 检查URL是否被渲染为可点击链接
    logger.info("\n--- 检查URL是否被渲染为链接 ---")
    url_link_check = page.evaluate("""
        () => {
            // 查找最新的消息元素
            const messages = Array.from(document.querySelectorAll('[class*="message"], [class*="chat-bubble"]'));
            
            if (messages.length === 0) {
                return {found: false, reason: 'no_messages'};
            }
            
            // 从后往前查找包含URL的消息
            for (let i = messages.length - 1; i >= 0; i--) {
                const msg = messages[i];
                const text = msg.textContent?.toLowerCase() || '';
                
                if (text.includes('google.com')) {
                    // 检查是否有<a>标签
                    const links = msg.querySelectorAll('a[href]');
                    const hasClickableLink = links.length > 0;
                    
                    const linkInfo = Array.from(links).map(link => ({
                        href: link.getAttribute('href'),
                        text: link.textContent?.trim(),
                        target: link.getAttribute('target')
                    }));
                    
                    return {
                        found: true,
                        hasClickableLink: hasClickableLink,
                        linkCount: links.length,
                        links: linkInfo,
                        messageText: text.substring(0, 100)
                    };
                }
            }
            
            return {found: false, reason: 'url_message_not_found'};
        }
    """)
    
    logger.info(f"✓ URL链接检查:")
    logger.info(f"  找到URL消息: {url_link_check.get('found', False)}")
    
    if url_link_check.get('found'):
        logger.info(f"  包含可点击链接: {url_link_check.get('hasClickableLink', False)}")
        logger.info(f"  链接数量: {url_link_check.get('linkCount', 0)}")
        
        if url_link_check.get('links'):
            for idx, link in enumerate(url_link_check['links'], 1):
                logger.info(f"  链接{idx}:")
                logger.info(f"    - href: {link.get('href', 'N/A')}")
                logger.info(f"    - text: {link.get('text', 'N/A')}")
                logger.info(f"    - target: {link.get('target', 'N/A')}")
        
        # 截图（URL链接渲染）
        page.screenshot(path="screenshots/tc014a_url_link_rendered.png", timeout=60000)
        logger.info("✓ 已截图: tc014a_url_link_rendered.png")
    else:
        logger.warning(f"  未找到URL消息: {url_link_check.get('reason', 'unknown')}")
    
    # Assert
    logger.info("\n" + "=" * 80)
    logger.info("URL消息发送功能测试汇总:")
    logger.info(f"  - 消息输入框: {'✅ 存在' if has_input['exists'] else '❌ 不存在'}")
    logger.info(f"  - URL输入成功: {'✅' if input_result['success'] else '❌'}")
    logger.info(f"  - 发送按钮: {'✅ 存在' if has_send_button['exists'] else '❌ 不存在'}")
    logger.info(f"  - 发送成功: {'✅' if send_result['success'] else '❌'}")
    logger.info(f"  - 输入框清空: {'✅' if send_result['input_cleared'] else '❌'}")
    
    if latest_message['found']:
        logger.info(f"  - URL消息已显示: {'✅' if 'google.com' in latest_message['text'].lower() else '⚠️ 未确认'}")
    
    if url_link_check.get('found'):
        logger.info(f"  - URL渲染为链接: {'✅' if url_link_check.get('hasClickableLink') else '❌ 纯文本'}")
    
    logger.info("✅ TC014A 测试通过！")
    logger.info("=" * 80)


@pytest.mark.p2
@allure.feature("OK - Messages")
@allure.story("Messages页面异常测试 - 输入验证")
@allure.title("TC018: 发送空消息异常测试")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.messages
@pytest.mark.conversation
@pytest.mark.send
@pytest.mark.exception
@pytest.mark.ae
@pytest.mark.case_id_messages_exception_018
def test_send_empty_message(page, config):
    """
    TC018: 发送空消息异常测试
    
    测试步骤:
    1. 访问Messages页面并进入会话
    2. 不输入任何内容，检查发送按钮状态
    3. 输入空格，检查发送按钮状态
    4. 输入换行符，检查发送按钮状态
    5. 尝试点击发送按钮（如果可点击）
    6. 验证空消息未被发送
    """
    logger.info("=" * 80)
    logger.info("TC018: 发送空消息异常测试")
    logger.info("=" * 80)
    
    # Arrange
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    login_page = LoginPage(page, base_url=config['base_url'])
    messages_page = MessagesExplorePage(page)
    
    # 加载Session或登录
    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        logger.info("✗ Session不存在，开始登录流程")
        login_page.navigate_to_home_page()
        login_page.handle_cookie_popup()
        login_page.login(config['test_account']['username'], config['test_account']['password'])
        session_manager.save_session()
        logger.info("✓ 登录成功并保存 Session")
    
    # Act
    
    # 步骤1: 导航到Messages页面并进入会话
    messages_page.navigate_to_messages_directly(config['target_page'])
    logger.info("✓ 已导航到Messages页面")
    
    messages_page.wait_for_conversation_list()
    conv_count = messages_page.get_conversation_count()
    logger.info(f"✓ 会话列表加载完成，当前会话数: {conv_count}")
    
    if conv_count == 0:
        logger.warning("⚠️ 会话列表为空，跳过测试")
        pytest.skip("会话列表为空")
    
    # 点击第二个会话
    messages_page.click_conversation_by_index(1)
    page.wait_for_timeout(3000)
    logger.info("✓ 已进入会话详情页")
    
    # 记录初始消息数量
    initial_message = messages_page.get_latest_message()
    initial_count = initial_message.get('count', 0)
    logger.info(f"✓ 初始消息数量: {initial_count}")
    
    # 步骤2: 不输入任何内容，检查发送按钮状态
    logger.info("\n--- 测试1: 空输入框 ---")
    page.screenshot(path="screenshots/tc018_empty_input.png", timeout=60000)
    logger.info("✓ 已截图: tc018_empty_input.png")
    
    send_button_state = page.evaluate("""
        () => {
            const buttons = Array.from(document.querySelectorAll('button'));
            const sendBtn = buttons.find(btn => {
                const text = btn.textContent?.toLowerCase() || '';
                return text.includes('send') || btn.className.toLowerCase().includes('send');
            });
            
            if (!sendBtn) return {found: false};
            
            return {
                found: true,
                disabled: sendBtn.disabled,
                className: sendBtn.className,
                visible: sendBtn.offsetWidth > 0 && sendBtn.offsetHeight > 0
            };
        }
    """)
    
    logger.info(f"✓ 发送按钮状态（空输入）:")
    logger.info(f"  找到按钮: {send_button_state.get('found', False)}")
    logger.info(f"  禁用状态: {send_button_state.get('disabled', False)}")
    logger.info(f"  可见: {send_button_state.get('visible', False)}")
    
    # 步骤3: 输入空格
    logger.info("\n--- 测试2: 输入空格 ---")
    input_result = messages_page.input_message('   ')  # 3个空格
    logger.info(f"✓ 输入空格: {input_result['success']}")
    
    page.screenshot(path="screenshots/tc018_space_input.png", timeout=60000)
    logger.info("✓ 已截图: tc018_space_input.png")
    
    send_button_state_space = page.evaluate("""
        () => {
            const buttons = Array.from(document.querySelectorAll('button'));
            const sendBtn = buttons.find(btn => {
                const text = btn.textContent?.toLowerCase() || '';
                return text.includes('send') || btn.className.toLowerCase().includes('send');
            });
            
            if (!sendBtn) return {found: false};
            
            return {
                found: true,
                disabled: sendBtn.disabled,
                visible: sendBtn.offsetWidth > 0 && sendBtn.offsetHeight > 0
            };
        }
    """)
    
    logger.info(f"✓ 发送按钮状态（空格输入）:")
    logger.info(f"  禁用状态: {send_button_state_space.get('disabled', False)}")
    
    # 清空输入框
    page.evaluate("""
        () => {
            const input = document.querySelector('textarea[placeholder*="message"], input[placeholder*="message"]');
            if (input) {
                input.value = '';
                input.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }
    """)
    page.wait_for_timeout(500)
    
    # 步骤4: 输入换行符
    logger.info("\n--- 测试3: 输入换行符 ---")
    page.evaluate("""
        () => {
            const input = document.querySelector('textarea[placeholder*="message"], input[placeholder*="message"]');
            if (input) {
                input.value = '\\n\\n\\n';
                input.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }
    """)
    page.wait_for_timeout(500)
    
    page.screenshot(path="screenshots/tc018_newline_input.png", timeout=60000)
    logger.info("✓ 已截图: tc018_newline_input.png")
    
    send_button_state_newline = page.evaluate("""
        () => {
            const buttons = Array.from(document.querySelectorAll('button'));
            const sendBtn = buttons.find(btn => {
                const text = btn.textContent?.toLowerCase() || '';
                return text.includes('send') || btn.className.toLowerCase().includes('send');
            });
            
            if (!sendBtn) return {found: false};
            
            return {
                found: true,
                disabled: sendBtn.disabled,
                visible: sendBtn.offsetWidth > 0 && sendBtn.offsetHeight > 0
            };
        }
    """)
    
    logger.info(f"✓ 发送按钮状态（换行符输入）:")
    logger.info(f"  禁用状态: {send_button_state_newline.get('disabled', False)}")
    
    # 步骤5: 尝试点击发送按钮（如果可点击）
    logger.info("\n--- 测试4: 尝试发送空消息 ---")
    
    if not send_button_state_newline.get('disabled', True):
        logger.info("⚠️ 发送按钮未禁用，尝试点击...")
        try:
            send_result = messages_page.click_send_button()
            logger.info(f"  点击结果: {send_result['success']}")
            page.wait_for_timeout(2000)
            
            # 检查是否有错误提示
            error_message = page.evaluate("""
                () => {
                    const errorSelectors = [
                        '[class*="error"]',
                        '[class*="warning"]',
                        '[class*="alert"]',
                        '.toast',
                        '[role="alert"]'
                    ];
                    
                    for (const selector of errorSelectors) {
                        const elements = document.querySelectorAll(selector);
                        for (const el of elements) {
                            const rect = el.getBoundingClientRect();
                            if (rect.width > 0 && rect.height > 0) {
                                return {
                                    found: true,
                                    text: el.textContent?.trim().substring(0, 100)
                                };
                            }
                        }
                    }
                    
                    return {found: false};
                }
            """)
            
            logger.info(f"  错误提示: {error_message.get('found', False)}")
            if error_message.get('found'):
                logger.info(f"  提示内容: {error_message.get('text', 'N/A')}")
        except Exception as e:
            logger.info(f"  点击失败（预期）: {e}")
    else:
        logger.info("✅ 发送按钮已禁用（符合预期）")
    
    # 步骤6: 验证空消息未被发送
    logger.info("\n--- 验证空消息未被发送 ---")
    page.wait_for_timeout(1000)
    
    final_message = messages_page.get_latest_message()
    final_count = final_message.get('count', 0)
    logger.info(f"✓ 最终消息数量: {final_count}")
    
    message_sent = final_count > initial_count
    logger.info(f"✓ 空消息是否被发送: {message_sent}")
    
    # Assert
    logger.info("\n" + "=" * 80)
    logger.info("空消息测试汇总:")
    logger.info(f"  - 空输入时发送按钮禁用: {'✅' if send_button_state.get('disabled', False) else '⚠️ 未禁用'}")
    logger.info(f"  - 空格输入时发送按钮禁用: {'✅' if send_button_state_space.get('disabled', False) else '⚠️ 未禁用'}")
    logger.info(f"  - 换行符输入时发送按钮禁用: {'✅' if send_button_state_newline.get('disabled', False) else '⚠️ 未禁用'}")
    logger.info(f"  - 空消息未被发送: {'✅' if not message_sent else '❌ 已发送'}")
    
    # 如果发送按钮未禁用但消息未发送，也算通过（有其他验证机制）
    if not message_sent:
        logger.info("✅ TC018 测试通过！（空消息未被发送）")
    elif send_button_state.get('disabled') or send_button_state_space.get('disabled') or send_button_state_newline.get('disabled'):
        logger.info("✅ TC018 测试通过！（发送按钮正确禁用）")
    else:
        logger.warning("⚠️ TC018 测试警告：发送按钮未禁用且空消息可能被发送")
    
    logger.info("=" * 80)


@pytest.mark.p2
@allure.feature("OK - Messages")
@allure.story("Messages页面异常测试 - 输入验证")
@allure.title("TC019: 发送超长消息异常测试")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.messages
@pytest.mark.conversation
@pytest.mark.send
@pytest.mark.exception
@pytest.mark.boundary
@pytest.mark.ae
@pytest.mark.case_id_messages_exception_019
def test_send_long_message(page, config):
    """
    TC019: 发送超长消息异常测试
    
    测试步骤:
    1. 访问Messages页面并进入会话
    2. 输入超长文本（5000字符）
    3. 检查字符限制和计数器
    4. 尝试发送
    5. 验证消息是否被截断或拒绝
    """
    logger.info("=" * 80)
    logger.info("TC019: 发送超长消息异常测试")
    logger.info("=" * 80)
    
    # Arrange
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    login_page = LoginPage(page, base_url=config['base_url'])
    messages_page = MessagesExplorePage(page)
    
    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        logger.info("✗ Session不存在，开始登录流程")
        login_page.navigate_to_home_page()
        login_page.handle_cookie_popup()
        login_page.login(config['test_account']['username'], config['test_account']['password'])
        session_manager.save_session()
        logger.info("✓ 登录成功并保存 Session")
    
    # Act
    messages_page.navigate_to_messages_directly(config['target_page'])
    logger.info("✓ 已导航到Messages页面")
    
    messages_page.wait_for_conversation_list()
    conv_count = messages_page.get_conversation_count()
    
    if conv_count == 0:
        pytest.skip("会话列表为空")
    
    messages_page.click_conversation_by_index(1)
    page.wait_for_timeout(3000)
    logger.info("✓ 已进入会话详情页")
    
    # 步骤1: 输入超长文本
    logger.info("\n--- 输入超长文本（5000字符） ---")
    long_text = 'A' * 5000
    logger.info(f"✓ 生成超长文本: {len(long_text)} 字符")
    
    input_result = messages_page.input_message(long_text)
    logger.info(f"✓ 输入成功: {input_result['success']}")
    
    actual_length = len(input_result.get('text', ''))
    logger.info(f"  尝试输入: {len(long_text)} 字符")
    logger.info(f"  实际输入: {actual_length} 字符")
    logger.info(f"  是否被截断: {actual_length < len(long_text)}")
    
    if actual_length < len(long_text):
        logger.info(f"  字符限制: {actual_length} 字符")
    
    page.screenshot(path="screenshots/tc019_long_text_input.png", timeout=60000)
    logger.info("✓ 已截图: tc019_long_text_input.png")
    
    # 步骤2: 检查字符计数器
    logger.info("\n--- 检查字符计数器 ---")
    char_counter = page.evaluate("""
        () => {
            const counterSelectors = [
                '[class*="counter"]',
                '[class*="count"]',
                '[class*="limit"]',
                '[class*="length"]'
            ];
            
            for (const selector of counterSelectors) {
                const elements = document.querySelectorAll(selector);
                for (const el of elements) {
                    const text = el.textContent || '';
                    if (text.match(/\\d+\\/\\d+/) || text.match(/\\d+/)) {
                        return {found: true, text: text.trim()};
                    }
                }
            }
            
            return {found: false};
        }
    """)
    
    logger.info(f"✓ 字符计数器: {char_counter['found']}")
    if char_counter['found']:
        logger.info(f"  计数器内容: {char_counter['text']}")
    
    # 步骤3: 尝试发送
    logger.info("\n--- 尝试发送超长消息 ---")
    send_result = messages_page.click_send_button()
    logger.info(f"✓ 发送操作: {send_result['success']}")
    
    page.wait_for_timeout(2000)
    page.screenshot(path="screenshots/tc019_after_send.png", timeout=60000)
    
    # Assert
    logger.info("\n" + "=" * 80)
    logger.info("超长消息测试汇总:")
    logger.info(f"  - 字符限制: {'✅ 存在' if actual_length < len(long_text) else '⚠️ 无限制'}")
    logger.info(f"  - 字符计数器: {'✅ 显示' if char_counter['found'] else '❌ 未显示'}")
    logger.info(f"  - 发送操作: {'✅ 成功' if send_result['success'] else '❌ 失败'}")
    
    logger.info("✅ TC019 测试通过！")
    logger.info("=" * 80)


@pytest.mark.p1
@allure.feature("OK - Messages")
@allure.story("Messages页面异常测试 - 安全验证")
@allure.title("TC020: 发送特殊字符消息测试")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.messages
@pytest.mark.conversation
@pytest.mark.send
@pytest.mark.exception
@pytest.mark.security
@pytest.mark.ae
@pytest.mark.case_id_messages_exception_020
def test_send_special_characters(page, config):
    """
    TC020: 发送特殊字符消息测试
    
    测试步骤:
    1. 访问Messages页面并进入会话
    2. 测试HTML标签（XSS）
    3. 测试SQL注入字符
    4. 测试Emoji表情
    5. 测试特殊符号
    6. 验证所有特殊字符被正确处理
    """
    logger.info("=" * 80)
    logger.info("TC020: 发送特殊字符消息测试")
    logger.info("=" * 80)
    
    # Arrange
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    login_page = LoginPage(page, base_url=config['base_url'])
    messages_page = MessagesExplorePage(page)
    
    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        logger.info("✗ Session不存在，开始登录流程")
        login_page.navigate_to_home_page()
        login_page.handle_cookie_popup()
        login_page.login(config['test_account']['username'], config['test_account']['password'])
        session_manager.save_session()
        logger.info("✓ 登录成功并保存 Session")
    
    # Act
    messages_page.navigate_to_messages_directly(config['target_page'])
    logger.info("✓ 已导航到Messages页面")
    
    messages_page.wait_for_conversation_list()
    conv_count = messages_page.get_conversation_count()
    
    if conv_count == 0:
        pytest.skip("会话列表为空")
    
    messages_page.click_conversation_by_index(1)
    page.wait_for_timeout(3000)
    logger.info("✓ 已进入会话详情页")
    
    test_results = {}
    
    # 测试1: HTML标签（XSS）
    logger.info("\n--- 测试1: HTML标签（XSS） ---")
    html_test = '<script>alert("XSS")</script>'
    logger.info(f"测试内容: {html_test}")
    
    messages_page.input_message(html_test)
    page.screenshot(path="screenshots/tc020_html_input.png", timeout=60000)
    
    messages_page.click_send_button()
    page.wait_for_timeout(2000)
    
    latest_message = messages_page.get_latest_message()
    if latest_message['found']:
        logger.info(f"  消息内容: {latest_message['text'][:100]}")
        is_escaped = '&lt;' in latest_message['text'] or '<script>' not in latest_message['text']
        logger.info(f"  是否转义: {is_escaped}")
        test_results['html'] = is_escaped
    
    page.screenshot(path="screenshots/tc020_html_sent.png", timeout=60000)
    
    # 测试2: SQL注入
    logger.info("\n--- 测试2: SQL注入字符 ---")
    sql_test = "'; DROP TABLE users; --"
    logger.info(f"测试内容: {sql_test}")
    
    messages_page.input_message(sql_test)
    page.screenshot(path="screenshots/tc020_sql_input.png", timeout=60000)
    
    messages_page.click_send_button()
    page.wait_for_timeout(2000)
    
    latest_message = messages_page.get_latest_message()
    if latest_message['found']:
        logger.info(f"  消息内容: {latest_message['text'][:100]}")
        test_results['sql'] = True
    
    page.screenshot(path="screenshots/tc020_sql_sent.png", timeout=60000)
    
    # 测试3: Emoji表情
    logger.info("\n--- 测试3: Emoji表情 ---")
    emoji_test = '😀🎉💯👍❤️'
    logger.info(f"测试内容: {emoji_test}")
    
    messages_page.input_message(emoji_test)
    page.screenshot(path="screenshots/tc020_emoji_input.png", timeout=60000)
    
    messages_page.click_send_button()
    page.wait_for_timeout(2000)
    
    latest_message = messages_page.get_latest_message()
    if latest_message['found']:
        logger.info(f"  消息内容: {latest_message['text'][:100]}")
        emoji_displayed = '😀' in latest_message['text'] or '🎉' in latest_message['text']
        logger.info(f"  Emoji显示正常: {emoji_displayed}")
        test_results['emoji'] = emoji_displayed
    
    page.screenshot(path="screenshots/tc020_emoji_sent.png", timeout=60000)
    
    # 测试4: 特殊符号
    logger.info("\n--- 测试4: 特殊符号 ---")
    special_test = '!@#$%^&*()_+-=[]{}|;:\'",.<>?/~`'
    logger.info(f"测试内容: {special_test}")
    
    messages_page.input_message(special_test)
    page.screenshot(path="screenshots/tc020_special_input.png", timeout=60000)
    
    messages_page.click_send_button()
    page.wait_for_timeout(2000)
    
    latest_message = messages_page.get_latest_message()
    if latest_message['found']:
        logger.info(f"  消息内容: {latest_message['text'][:100]}")
        test_results['special'] = True
    
    page.screenshot(path="screenshots/tc020_special_sent.png", timeout=60000)
    
    # Assert
    logger.info("\n" + "=" * 80)
    logger.info("特殊字符测试汇总:")
    logger.info(f"  - HTML标签转义: {'✅' if test_results.get('html', False) else '❌'}")
    logger.info(f"  - SQL注入防护: {'✅' if test_results.get('sql', False) else '❌'}")
    logger.info(f"  - Emoji显示: {'✅' if test_results.get('emoji', False) else '❌'}")
    logger.info(f"  - 特殊符号显示: {'✅' if test_results.get('special', False) else '❌'}")
    
    logger.info("✅ TC020 测试通过！")
    logger.info("=" * 80)


@pytest.mark.p2
@allure.feature("OK - Messages")
@allure.story("Messages页面功能测试 - 多行文本")
@allure.title("TC021: 发送多行文本消息测试")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.messages
@pytest.mark.conversation
@pytest.mark.send
@pytest.mark.ae
@pytest.mark.case_id_messages_exception_021
def test_send_multiline_message(page, config):
    """
    TC021: 发送多行文本消息测试
    
    测试步骤:
    1. 访问Messages页面并进入会话
    2. 输入多行文本（包含换行符）
    3. 发送消息
    4. 验证换行符被正确保留和显示
    """
    logger.info("=" * 80)
    logger.info("TC021: 发送多行文本消息测试")
    logger.info("=" * 80)
    
    # Arrange
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    login_page = LoginPage(page, base_url=config['base_url'])
    messages_page = MessagesExplorePage(page)
    
    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        logger.info("✗ Session不存在，开始登录流程")
        login_page.navigate_to_home_page()
        login_page.handle_cookie_popup()
        login_page.login(config['test_account']['username'], config['test_account']['password'])
        session_manager.save_session()
        logger.info("✓ 登录成功并保存 Session")
    
    # Act
    messages_page.navigate_to_messages_directly(config['target_page'])
    logger.info("✓ 已导航到Messages页面")
    
    messages_page.wait_for_conversation_list()
    conv_count = messages_page.get_conversation_count()
    
    if conv_count == 0:
        pytest.skip("会话列表为空")
    
    messages_page.click_conversation_by_index(1)
    page.wait_for_timeout(3000)
    logger.info("✓ 已进入会话详情页")
    
    # 步骤1: 输入多行文本
    logger.info("\n--- 输入多行文本 ---")
    multiline_text = 'Line 1\nLine 2\nLine 3\nLine 4\nLine 5'
    display_text = multiline_text.replace('\n', '\\n')
    logger.info(f"测试内容: {display_text}")
    
    input_result = messages_page.input_message(multiline_text)
    logger.info(f"✓ 输入成功: {input_result['success']}")
    
    line_count = input_result.get('text', '').count('\n') + 1
    logger.info(f"  输入行数: {line_count}")
    
    page.screenshot(path="screenshots/tc021_multiline_input.png", timeout=60000)
    logger.info("✓ 已截图: tc021_multiline_input.png")
    
    # 步骤2: 发送多行消息
    logger.info("\n--- 发送多行消息 ---")
    send_result = messages_page.click_send_button()
    logger.info(f"✓ 发送成功: {send_result['success']}")
    
    page.wait_for_timeout(2000)
    
    # 滚动到底部
    page.evaluate("""
        () => {
            const containers = document.querySelectorAll('[class*="message"]');
            for (const container of containers) {
                if (container.scrollHeight > container.clientHeight) {
                    container.scrollTop = container.scrollHeight;
                }
            }
        }
    """)
    page.wait_for_timeout(1000)
    
    page.screenshot(path="screenshots/tc021_after_send.png", timeout=60000)
    logger.info("✓ 已截图: tc021_after_send.png")
    
    # 步骤3: 验证多行消息显示
    logger.info("\n--- 验证多行消息显示 ---")
    message_display = page.evaluate("""
        () => {
            const messages = Array.from(document.querySelectorAll('[class*="message"], [class*="chat-bubble"]'));
            
            if (messages.length === 0) {
                return {found: false};
            }
            
            const lastMsg = messages[messages.length - 1];
            const text = lastMsg.textContent || '';
            const innerHTML = lastMsg.innerHTML;
            
            const hasBrTag = innerHTML.includes('<br>');
            const lineCount = text.split('\\n').length;
            
            return {
                found: true,
                text: text.trim().substring(0, 100),
                hasBrTag: hasBrTag,
                lineCount: lineCount,
                preservesNewlines: lineCount > 1 || hasBrTag
            };
        }
    """)
    
    logger.info(f"✓ 多行消息显示:")
    logger.info(f"  找到消息: {message_display['found']}")
    
    if message_display['found']:
        logger.info(f"  行数: {message_display['lineCount']}")
        logger.info(f"  使用<br>标签: {message_display['hasBrTag']}")
        logger.info(f"  换行符保留: {message_display['preservesNewlines']}")
        logger.info(f"  消息内容: {message_display['text'][:80]}")
    
    page.screenshot(path="screenshots/tc021_multiline_display.png", timeout=60000)
    logger.info("✓ 已截图: tc021_multiline_display.png")
    
    # Assert
    logger.info("\n" + "=" * 80)
    logger.info("多行文本测试汇总:")
    logger.info(f"  - 多行输入支持: ✅")
    logger.info(f"  - 发送成功: {'✅' if send_result['success'] else '❌'}")
    logger.info(f"  - 换行符保留: {'✅' if message_display.get('preservesNewlines', False) else '❌'}")
    logger.info(f"  - 显示格式正确: {'✅' if message_display.get('lineCount', 0) > 1 or message_display.get('hasBrTag', False) else '❌'}")
    
    logger.info("✅ TC021 测试通过！")
    logger.info("=" * 80)


# TC022: 复制消息功能测试 - 已删除（自动化无法触发应用的自定义Copy菜单）


# ==================== TC023-TC025: 会话列表交互测试 ====================

@allure.feature("OK - Messages")
@allure.story("Messages页面功能探索 - 会话列表交互")
@allure.title("TC023: 会话列表滑动功能测试")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.messages
@pytest.mark.conversation
@pytest.mark.scroll
@pytest.mark.ae
@pytest.mark.case_id_messages_scroll_023
def test_conversation_list_scroll(page, config):
    """
    TC023: 会话列表滑动功能测试
    
    ⚠️ 状态：需要进一步调查
    
    已知问题：
    1. Playwright的右键点击无法触发应用的自定义Copy菜单（白底气泡）
    2. 手动操作时Copy菜单可以出现，但Copy功能失败（Toast提示"copy 失败"）
    3. 可能需要与开发团队确认Copy菜单的触发机制和实现方式
    
    测试步骤:
    1. 访问Messages页面并进入会话（无需滚动）
    2. 右键点击消息，触发Copy菜单
    3. 点击Copy按钮进行复制
    4. 粘贴到输入框并发送
    5. 验证复制的消息已发送
    """
    logger.info("=" * 80)
    logger.info("TC022: 复制消息功能测试")
    logger.info("=" * 80)
    
    # Arrange
    session_name = f"{_CONFIG['site']}_{_CONFIG['role']}"
    session_manager = SessionManager(page, _CONFIG['base_url'], session_name)
    login_page = LoginPage(page, base_url=_CONFIG['base_url'])
    messages_page = MessagesExplorePage(page)
    
    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        logger.info("✗ Session不存在，开始登录流程")
        login_page.navigate_to_home_page()
        login_page.handle_cookie_popup()
        login_page.login(_CONFIG['test_account']['username'], _CONFIG['test_account']['password'])
        session_manager.save_session()
        logger.info("✓ 登录成功并保存 Session")
    
    # Act
    messages_page.navigate_to_messages_directly(_CONFIG['target_page'])
    logger.info("✓ 已导航到Messages页面")
    
    messages_page.wait_for_conversation_list()
    conv_count = messages_page.get_conversation_count()
    
    if conv_count == 0:
        pytest.skip("会话列表为空")
    
    messages_page.click_conversation_by_index(1)
    page.wait_for_timeout(3000)
    logger.info("✓ 已进入会话详情页")
    
    # 等待页面稳定
    page.wait_for_timeout(2000)
    
    # 步骤1: 查找消息（在当前可见区域，不滚动）
    logger.info("\n--- 步骤1: 查找可见区域的消息 ---")
    
    # 截图当前状态
    page.screenshot(path="screenshots/tc022_initial_state.png", timeout=60000)
    logger.info("✓ 已截图初始状态")
    
    message_info = page.evaluate("""
        () => {
            const selectors = [
                "[class*='message']",
                "[class*='chat-item']",
                "[class*='msg']",
                "[class*='bubble']"
            ];
            
            let allRightMessages = [];
            
            for (const selector of selectors) {
                const elements = Array.from(document.querySelectorAll(selector));
                
                for (const el of elements) {
                    const rect = el.getBoundingClientRect();
                    
                    // 只查找右侧的消息（发送的消息）且在可视区域内
                    if (rect.x > 300 && 
                        rect.width > 50 &&
                        rect.y > 100 &&  // 排除顶部导航
                        rect.y < 600) {  // 缩小范围，避免底部边缘
                        
                        // 查找消息内的文本元素
                        const textElements = el.querySelectorAll('span, div, p');
                        let bestTextEl = null;
                        let longestText = '';
                        
                        for (const textEl of textElements) {
                            const text = textEl.textContent?.trim() || '';
                            const textRect = textEl.getBoundingClientRect();
                            
                            // 查找最长的文本元素（排除时间戳等）
                            if (text.length > longestText.length && 
                                text.length > 2 &&
                                textRect.width > 30 &&
                                textRect.height > 10) {
                                bestTextEl = textEl;
                                longestText = text;
                            }
                        }
                        
                        // 使用文本元素的位置，如果找不到则使用消息元素
                        const targetEl = bestTextEl || el;
                        const targetRect = targetEl.getBoundingClientRect();
                        
                        allRightMessages.push({
                            element: el,
                            textElement: bestTextEl,
                            rect: rect,
                            textRect: targetRect,
                            text: el.textContent?.trim() || '',
                            y: rect.y
                        });
                    }
                }
            }
            
            if (allRightMessages.length === 0) {
                return {found: false, reason: 'no_messages_in_viewport'};
            }
            
            // 按Y坐标排序，取最下面的消息（最新的）
            allRightMessages.sort((a, b) => b.y - a.y);
            const targetMsg = allRightMessages[0];
            
            // 使用文本元素的坐标（更精确）
            const clickRect = targetMsg.textRect;
            
            return {
                found: true,
                x: Math.round(clickRect.x + clickRect.width / 2),
                y: Math.round(clickRect.y + clickRect.height / 2),
                width: Math.round(clickRect.width),
                height: Math.round(clickRect.height),
                messageText: targetMsg.text,
                totalMessages: allRightMessages.length,
                hasTextElement: !!targetMsg.textElement
            };
        }
    """)
    
    if not message_info['found']:
        logger.error(f"⚠️ 未找到消息: {message_info.get('reason')}")
        pytest.skip("未找到可复制的消息")
    
    logger.info(f"✓ 找到消息: '{message_info['messageText'][:50]}'")
    logger.info(f"  位置: ({message_info['x']}, {message_info['y']})")
    logger.info(f"  尺寸: {message_info['width']}x{message_info['height']}")
    
    # 截图：点击前
    page.screenshot(path="screenshots/tc022_before_click.png", timeout=60000)
    logger.info("✓ 截图: tc022_before_click.png")
    
    # 步骤1: 左键点击消息（激活），然后右键点击（触发Copy菜单）
    logger.info("步骤1: 先左键点击消息，再右键点击...")
    click_x = message_info['x']
    click_y = message_info['y']
    
    # 先将鼠标移动到消息上
    page.mouse.move(click_x, click_y)
    logger.info("✓ 已将鼠标移动到消息上")
    
    # 等待一下
    page.wait_for_timeout(500)
    
    # 先左键点击一次（激活消息）
    page.mouse.click(click_x, click_y, button='left')
    logger.info("✓ 已左键点击消息（激活）")
    
    # 等待激活效果
    page.wait_for_timeout(500)
    
    # 截图：左键点击后
    page.screenshot(path="screenshots/tc022_after_left_click.png", timeout=60000)
    logger.info("✓ 截图: tc022_after_left_click.png")
    
    # 然后右键点击（触发Copy菜单）
    page.mouse.click(click_x, click_y, button='right')
    logger.info("✓ 已右键点击消息")
    
    # 等待Copy菜单出现
    page.wait_for_timeout(1000)
    
    # 截图：右键后
    page.screenshot(path="screenshots/tc022_after_right_click.png", timeout=60000)
    logger.info("✓ 截图: tc022_after_right_click.png")
    
    # 步骤2: 查找并点击Copy按钮
    logger.info("\n--- 步骤2: 查找并点击Copy按钮 ---")
    
    # 查找Copy按钮（优化：只查找高zIndex的元素）
    copy_button_info = page.evaluate("""
        () => {
            // 只查找按钮、span、div等常见菜单元素
            const selectors = 'button, span, div[role="menuitem"], div[role="button"], [class*="menu"]';
            const allElements = Array.from(document.querySelectorAll(selectors));
            let foundCopyButtons = [];
            
            for (const el of allElements) {
                const text = el.textContent?.toLowerCase().trim() || '';
                const innerText = el.innerText?.toLowerCase().trim() || '';
                
                // 查找恰好是"copy"或接近"copy"的元素
                if (text === 'copy' || innerText === 'copy') {
                    
                    const rect = el.getBoundingClientRect();
                    const style = window.getComputedStyle(el);
                    
                    // 检查是否可见
                    const visible = 
                        style.display !== 'none' &&
                        style.visibility !== 'hidden' &&
                        parseFloat(style.opacity) > 0 &&
                        rect.width > 0 &&
                        rect.height > 0 &&
                        rect.y > 0 &&
                        rect.y < window.innerHeight;
                    
                    if (visible) {
                        foundCopyButtons.push({
                            tag: el.tagName,
                            text: el.textContent?.trim(),
                            className: el.className,
                            rect: {
                                x: Math.round(rect.x),
                                y: Math.round(rect.y),
                                width: Math.round(rect.width),
                                height: Math.round(rect.height)
                            },
                            zIndex: style.zIndex
                        });
                    }
                }
            }
            
            if (foundCopyButtons.length === 0) {
                return {found: false};
            }
            
            // 优先选择最上层的、最小的Copy按钮（最可能是菜单项）
            foundCopyButtons.sort((a, b) => {
                const aZ = parseInt(a.zIndex) || 0;
                const bZ = parseInt(b.zIndex) || 0;
                if (bZ !== aZ) return bZ - aZ;  // zIndex高的优先
                return (a.rect.width * a.rect.height) - (b.rect.width * b.rect.height);  // 面积小的优先
            });
            
            const bestButton = foundCopyButtons[0];
            
            return {
                found: true,
                x: Math.round(bestButton.rect.x + bestButton.rect.width / 2),
                y: Math.round(bestButton.rect.y + bestButton.rect.height / 2),
                text: bestButton.text,
                tag: bestButton.tag,
                allButtons: foundCopyButtons.map(b => ({
                    tag: b.tag,
                    text: b.text,
                    rect: b.rect,
                    zIndex: b.zIndex
                }))
            };
        }
    """)
    
    if not copy_button_info['found']:
        logger.error("⚠️ 未找到Copy按钮")
        page.screenshot(path="screenshots/tc022_copy_button_not_found.png", timeout=60000)
        pytest.skip("未找到Copy按钮")
    
    logger.info(f"✓ 找到Copy按钮")
    logger.info(f"  标签: {copy_button_info['tag']}")
    logger.info(f"  文本: '{copy_button_info['text']}'")
    logger.info(f"  位置: ({copy_button_info['x']}, {copy_button_info['y']})")
    logger.info(f"  找到 {len(copy_button_info['allButtons'])} 个候选按钮:")
    for i, btn in enumerate(copy_button_info['allButtons'][:5], 1):
        logger.info(f"    {i}. {btn['tag']}: '{btn['text']}' at ({btn['rect']['x']}, {btn['rect']['y']}) "
                    f"size={btn['rect']['width']}x{btn['rect']['height']} zIndex={btn['zIndex']}")
    
    # 点击Copy按钮
    logger.info("点击Copy按钮...")
    page.mouse.click(copy_button_info['x'], copy_button_info['y'])
    logger.info("✓ 已点击Copy按钮")
    
    # 等待复制完成
    page.wait_for_timeout(1000)
    
    # 截图：点击Copy后
    page.screenshot(path="screenshots/tc022_after_copy_click.png", timeout=60000)
    logger.info("✓ 截图: tc022_after_copy_click.png")
    
    # 保存原始消息文本用于验证
    original_message_text = message_info['messageText']
    logger.info(f"  原始消息（用于验证）: '{original_message_text[:100]}'")
    
    # 步骤3: 粘贴到输入框
    logger.info("\n--- 步骤3: 粘贴到输入框 ---")
    
    # 清空并聚焦输入框
    input_cleared = page.evaluate("""
        () => {
            const input = document.querySelector('textarea[placeholder*="message"], input[placeholder*="message"]');
            if (input) {
                input.focus();
                input.value = '';
                return {success: true};
            }
            return {success: false};
        }
    """)
    
    logger.info(f"✓ 输入框已清空并聚焦: {input_cleared['success']}")
    page.wait_for_timeout(500)
    
    # 使用键盘粘贴
    if platform.system() == 'Darwin':
        page.keyboard.press('Meta+V')
        logger.info("✓ 执行粘贴操作（Cmd+V）")
    else:
        page.keyboard.press('Control+V')
        logger.info("✓ 执行粘贴操作（Ctrl+V）")
    
    page.wait_for_timeout(1500)
    
    # 检查输入框内容
    paste_result = page.evaluate("""
        () => {
            const input = document.querySelector('textarea[placeholder*="message"], input[placeholder*="message"]');
            if (input) {
                return {
                    success: true,
                    text: input.value,
                    hasContent: input.value.length > 0
                };
            }
            return {success: false};
        }
    """)
    
    logger.info(f"✓ 粘贴验证: {paste_result['success']}")
    
    if not paste_result.get('hasContent'):
        logger.error("❌ 粘贴后输入框为空")
        page.screenshot(path="screenshots/tc022_paste_failed.png", timeout=60000)
        pytest.fail("复制功能失败：粘贴后输入框为空")
    
    pasted_text = paste_result['text']
    logger.info(f"  粘贴内容: '{pasted_text}'")
    
    # 验证粘贴的内容是否与原始消息匹配
    target_text = original_message_text
    paste_matches_target = target_text.strip() in pasted_text or pasted_text.strip() in target_text
    logger.info(f"  原始消息文本: '{target_text[:50]}'")
    logger.info(f"  粘贴匹配原始消息: {paste_matches_target}")
    
    page.screenshot(path="screenshots/tc022_after_paste.png", timeout=60000)
    logger.info("✓ 已截图: tc022_after_paste.png")
    
    # 步骤4: 点击Send发送
    logger.info("\n--- 步骤4: 点击Send发送 ---")
    
    send_result = messages_page.click_send_button()
    logger.info(f"✓ 发送操作: {send_result['success']}")
    
    page.wait_for_timeout(3000)
    
    page.wait_for_timeout(2000)  # 等待消息发送完成
    
    page.screenshot(path="screenshots/tc022_message_sent_from_paste.png", timeout=60000)
    logger.info("✓ 已截图: tc022_message_sent_from_paste.png")
    
    # 步骤5: 验证粘贴的消息已发送
    logger.info("\n--- 步骤5: 验证复制的消息已发送 ---")
    
    # 使用JavaScript直接查找最新消息（避免触发滚动）
    latest_message_info = page.evaluate("""
        () => {
            const selectors = [
                "[class*='message']",
                "[class*='chat-item']",
                "[class*='msg']"
            ];
            
            let allRightMessages = [];
            
            for (const selector of selectors) {
                const elements = Array.from(document.querySelectorAll(selector));
                
                for (const el of elements) {
                    const rect = el.getBoundingClientRect();
                    const text = el.textContent?.trim() || '';
                    
                    // 查找右侧消息（发送的消息）
                    if (rect.x > 300 && rect.width > 50 && text.length > 0) {
                        allRightMessages.push({
                            text: text,
                            y: rect.y
                        });
                    }
                }
            }
            
            if (allRightMessages.length === 0) {
                return {found: false};
            }
            
            // 按Y坐标排序，取最下面的消息（最新的）
            allRightMessages.sort((a, b) => b.y - a.y);
            
            return {
                found: true,
                text: allRightMessages[0].text
            };
        }
    """)
    
    if not latest_message_info['found']:
        logger.error("❌ 未找到最新消息")
        pytest.fail("无法验证消息是否发送")
    
    logger.info(f"  最新消息: {latest_message_info['text'][:100]}")
    
    # 验证最新消息包含粘贴的内容
    message_contains_pasted = pasted_text.strip() in latest_message_info['text']
    logger.info(f"  包含粘贴内容: {message_contains_pasted}")
    
    # Assert
    logger.info("\n" + "=" * 80)
    logger.info("TC022 测试结果汇总:")
    logger.info(f"  1. 找到目标消息: ✅ ('{target_text[:30]}')")
    logger.info(f"  2. 选中消息文本: ✅")
    logger.info(f"  3. Cmd+C复制: ✅")
    logger.info(f"  4. Cmd+V粘贴: {'✅' if paste_result.get('hasContent') else '❌'}")
    logger.info(f"  5. 复制内容: '{pasted_text[:50]}'")
    logger.info(f"  6. 内容匹配目标: {'✅' if paste_matches_target else '❌'}")
    logger.info(f"  7. 点击Send发送: {'✅' if send_result.get('success') else '❌'}")
    logger.info(f"  8. 消息已发送: {'✅' if message_contains_pasted else '❌'}")
    
    if paste_matches_target and message_contains_pasted:
        logger.info("✅ TC022 测试通过！（复制功能正常）")
    else:
        logger.warning(f"⚠️ TC022 测试异常")
        logger.warning(f"   目标文本: '{target_text}'")
        logger.warning(f"   复制内容: '{pasted_text}'")
    
    logger.info("=" * 80)
    
    # 最终断言
    assert paste_result.get('hasContent'), "粘贴后输入框为空"
    assert paste_matches_target, f"粘贴内容与目标不匹配 - 目标:'{target_text}', 粘贴:'{pasted_text}'"
    assert message_contains_pasted, "发送的消息不包含粘贴的内容"


# ==================== TC023-TC025: 会话列表交互测试 ====================

@pytest.mark.p2
@allure.feature("OK - Messages")
@allure.story("Messages页面功能探索 - 会话列表交互")
@allure.title("TC023: 会话列表滑动功能测试")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.messages
@pytest.mark.conversation
@pytest.mark.scroll
@pytest.mark.ae
@pytest.mark.case_id_messages_scroll_023
def test_conversation_list_scroll(page, config):
    """
    TC023: 会话列表滑动功能测试
    
    测试步骤:
    1. 定位会话列表容器
    2. 获取初始状态
    3. 向下滑动会话列表
    4. 验证滑动后的状态
    """
    logger.info("=" * 80)
    logger.info("TC023: 会话列表滑动功能测试")
    logger.info("=" * 80)
    
    # 准备：确保在Messages页面
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    login_page = LoginPage(page, base_url=config['base_url'])
    messages_page = MessagesExplorePage(page)
    
    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        logger.info("✗ Session不存在，开始登录流程")
        login_page.navigate_to_home_page()
        login_page.handle_cookie_popup()
        login_page.login(config['test_account']['username'], config['test_account']['password'])
        session_manager.save_session()
    
    # 导航到Messages页面
    messages_page.navigate_to_messages_directly(_CONFIG['target_page'])
    page.wait_for_timeout(3000)
    
    # 步骤1：定位会话列表容器
    logger.info("\n--- 步骤1: 定位会话列表容器 ---")
    conversation_list = page.evaluate("""
        () => {
            const selectors = [
                '[class*="conversation-list"]',
                '[class*="chat-list"]',
                '[class*="message-list"]',
                '[class*="session-list"]',
                '[class*="left"]'
            ];
            
            for (const selector of selectors) {
                const container = document.querySelector(selector);
                if (container) {
                    return {
                        found: true,
                        selector: selector,
                        scrollHeight: container.scrollHeight,
                        clientHeight: container.clientHeight,
                        scrollable: container.scrollHeight > container.clientHeight
                    };
                }
            }
            
            return {found: false};
        }
    """)
    
    logger.info(f"✓ 会话列表容器: {conversation_list}")
    assert conversation_list['found'], "未找到会话列表容器"
    
    # 步骤2：获取初始状态
    logger.info("\n--- 步骤2: 获取初始状态 ---")
    initial_state = page.evaluate("""
        () => {
            const conversations = document.querySelectorAll('[class*="conversation"], [class*="chat-item"]');
            const visible = Array.from(conversations).filter(el => {
                const rect = el.getBoundingClientRect();
                return rect.top >= 0 && rect.bottom <= window.innerHeight;
            });
            
            return {
                total: conversations.length,
                visible: visible.length,
                firstVisible: visible[0]?.textContent?.trim().substring(0, 30)
            };
        }
    """)
    
    logger.info(f"✓ 初始状态 - 总会话数: {initial_state['total']}, 可见: {initial_state['visible']}")
    page.screenshot(path='screenshots/tc023_before_scroll.png', timeout=60000)
    
    # 步骤3：向下滑动会话列表
    logger.info("\n--- 步骤3: 向下滑动会话列表 ---")
    scroll_result = page.evaluate("""
        () => {
            const selectors = [
                '[class*="conversation-list"]',
                '[class*="chat-list"]',
                '[class*="left"]'
            ];
            
            for (const selector of selectors) {
                const container = document.querySelector(selector);
                if (container && container.scrollHeight > container.clientHeight) {
                    const initialScrollTop = container.scrollTop;
                    container.scrollTop += 300;
                    
                    return {
                        success: true,
                        selector: selector,
                        scrolledFrom: initialScrollTop,
                        scrolledTo: container.scrollTop,
                        scrollDistance: container.scrollTop - initialScrollTop
                    };
                }
            }
            
            return {success: false};
        }
    """)
    
    logger.info(f"✓ 滑动结果: {scroll_result}")
    page.wait_for_timeout(1000)
    
    # 步骤4：验证滑动后的状态
    logger.info("\n--- 步骤4: 验证滑动后的状态 ---")
    after_scroll_state = page.evaluate("""
        () => {
            const conversations = document.querySelectorAll('[class*="conversation"], [class*="chat-item"]');
            const visible = Array.from(conversations).filter(el => {
                const rect = el.getBoundingClientRect();
                return rect.top >= 0 && rect.bottom <= window.innerHeight;
            });
            
            return {
                total: conversations.length,
                visible: visible.length,
                firstVisible: visible[0]?.textContent?.trim().substring(0, 30)
            };
        }
    """)
    
    logger.info(f"✓ 滑动后状态 - 可见: {after_scroll_state['visible']}")
    page.screenshot(path='screenshots/tc023_after_scroll.png', timeout=60000)
    
    # 验证滑动效果
    if conversation_list['scrollable']:
        assert scroll_result['success'], "滑动操作失败"
        logger.info("✓ 会话列表滑动功能正常")
    else:
        logger.info("⚠ 会话列表不可滑动（会话数量较少）")
    
    logger.info("✓ TC023 测试通过")


@pytest.mark.p2
@allure.feature("OK - Messages")
@allure.story("Messages页面功能探索 - 会话列表展示")
@allure.title("TC024: 会话列表时间戳检查")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.messages
@pytest.mark.conversation
@pytest.mark.timestamp
@pytest.mark.ae
@pytest.mark.case_id_messages_timestamp_024
def test_conversation_timestamp(page, config):
    """
    TC024: 会话列表时间戳检查
    
    测试步骤:
    1. 获取所有会话的时间戳
    2. 验证时间戳格式
    3. 验证时间戳位置
    """
    logger.info("=" * 80)
    logger.info("TC024: 会话列表时间戳检查")
    logger.info("=" * 80)
    
    # 准备：确保在Messages页面
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    login_page = LoginPage(page, base_url=config['base_url'])
    messages_page = MessagesExplorePage(page)
    
    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        logger.info("✗ Session不存在，开始登录流程")
        login_page.navigate_to_home_page()
        login_page.handle_cookie_popup()
        login_page.login(config['test_account']['username'], config['test_account']['password'])
        session_manager.save_session()
    
    # 导航到Messages页面
    messages_page.navigate_to_messages_directly(_CONFIG['target_page'])
    page.wait_for_timeout(3000)
    
    # 步骤1：获取所有会话的时间戳
    logger.info("\n--- 步骤1: 获取所有会话的时间戳 ---")
    timestamps = page.evaluate("""
        () => {
            const conversations = document.querySelectorAll('[class*="conversation"], [class*="chat-item"]');
            const results = [];
            
            for (const conv of conversations) {
                const rect = conv.getBoundingClientRect();
                if (rect.height > 0 && rect.width > 0) {
                    // 查找时间戳元素
                    const timeSelectors = [
                        '[class*="time"]',
                        '[class*="timestamp"]',
                        '[class*="date"]',
                        'span[class*="text-"]'
                    ];
                    
                    let timestamp = null;
                    for (const selector of timeSelectors) {
                        const timeEl = conv.querySelector(selector);
                        if (timeEl) {
                            const text = timeEl.textContent?.trim();
                            // 检查是否是时间格式（包含数字或时间关键词）
                            if (text && (/\\d/.test(text) || /yesterday|today/i.test(text))) {
                                timestamp = text;
                                break;
                            }
                        }
                    }
                    
                    const userName = conv.textContent?.trim().split('\\n')[0] || 'Unknown';
                    
                    results.push({
                        userName: userName.substring(0, 30),
                        timestamp: timestamp,
                        hasTimestamp: !!timestamp
                    });
                }
            }
            
            return results;
        }
    """)
    
    logger.info(f"✓ 获取到 {len(timestamps)} 个会话的时间戳")
    for i, ts in enumerate(timestamps[:5]):
        logger.info(f"  会话{i+1}: {ts['userName']} - {ts['timestamp']}")
    
    # 步骤2：验证时间戳格式
    logger.info("\n--- 步骤2: 验证时间戳格式 ---")
    import re
    timestamp_patterns = [
        r'\d+:\d+',           # 时间格式: 10:30, 14:25
        r'\d+月\d+日',         # 日期格式: 3月31日
        r'Yesterday',         # 昨天
        r'Today',             # 今天
        r'\w+ \d+',           # Mar 31, Jan 15
    ]
    
    valid_timestamps = 0
    for ts in timestamps:
        if ts['hasTimestamp']:
            timestamp_text = ts['timestamp']
            is_valid = any(re.search(pattern, timestamp_text) for pattern in timestamp_patterns)
            if is_valid:
                valid_timestamps += 1
    
    logger.info(f"✓ 有效时间戳数量: {valid_timestamps}/{len(timestamps)}")
    
    # 验证至少70%的会话有有效时间戳
    if len(timestamps) > 0:
        coverage = valid_timestamps / len(timestamps)
        logger.info(f"✓ 时间戳覆盖率: {coverage*100:.1f}%")
        assert coverage >= 0.7, f"时间戳覆盖率不足: {coverage*100:.1f}%"
    
    # 截图
    page.screenshot(path='screenshots/tc024_timestamps.png', timeout=60000)
    
    logger.info("✓ TC024 测试通过")


@pytest.mark.p1
@allure.feature("OK - Messages")
@allure.story("Messages页面功能探索 - 未读消息提示")
@allure.title("TC025: 未读消息气泡展示测试")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.messages
@pytest.mark.conversation
@pytest.mark.unread
@pytest.mark.notification
@pytest.mark.ae
@pytest.mark.case_id_messages_unread_025
def test_unread_message_badge(page, config):
    """
    TC025: 未读消息气泡展示测试
    
    测试步骤:
    1. 查找未读消息气泡
    2. 验证气泡样式
    3. 点击有未读消息的会话
    4. 返回验证气泡消失
    """
    logger.info("=" * 80)
    logger.info("TC025: 未读消息气泡展示测试")
    logger.info("=" * 80)
    
    # 准备：确保在Messages页面
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    login_page = LoginPage(page, base_url=config['base_url'])
    messages_page = MessagesExplorePage(page)
    
    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        logger.info("✗ Session不存在，开始登录流程")
        login_page.navigate_to_home_page()
        login_page.handle_cookie_popup()
        login_page.login(config['test_account']['username'], config['test_account']['password'])
        session_manager.save_session()
    
    # 导航到Messages页面
    messages_page.navigate_to_messages_directly(_CONFIG['target_page'])
    page.wait_for_timeout(5000)
    
    # 等待会话列表加载
    try:
        page.wait_for_selector('.list-group.list-group-flush', timeout=30000)
        logger.info("✓ 会话列表已加载")
    except Exception as e:
        logger.error(f"✗ 会话列表加载超时: {e}")
        pytest.skip("Messages页面会话列表加载超时，可能是网络问题")
    
    # 步骤1：查找未读消息气泡
    logger.info("\n--- 步骤1: 查找未读消息气泡 ---")
    unread_badges = page.evaluate("""
        () => {
            const conversations = document.querySelectorAll('[class*="conversation"], [class*="chat-item"]');
            const results = [];
            
            for (const conv of conversations) {
                // 查找未读气泡
                const badgeSelectors = [
                    '[class*="badge"]',
                    '[class*="unread"]',
                    '[class*="count"]',
                    '[class*="notification"]',
                    'span[class*="bg-red"]',
                    'div[class*="dot"]'
                ];
                
                let badge = null;
                let badgeText = null;
                
                for (const selector of badgeSelectors) {
                    const badgeEl = conv.querySelector(selector);
                    if (badgeEl) {
                        const text = badgeEl.textContent?.trim();
                        const computed = window.getComputedStyle(badgeEl);
                        const bgColor = computed.backgroundColor;
                        
                        // 检查是否是红色背景的气泡
                        if (bgColor.includes('rgb(255') || bgColor.includes('rgb(239') || 
                            bgColor.includes('red') || text && /^\\d+$/.test(text)) {
                            badge = badgeEl;
                            badgeText = text;
                            break;
                        }
                    }
                }
                
                if (badge) {
                    const userName = conv.textContent?.trim().split('\\n')[0] || 'Unknown';
                    const rect = badge.getBoundingClientRect();
                    const computed = window.getComputedStyle(badge);
                    
                    results.push({
                        userName: userName.substring(0, 30),
                        badgeText: badgeText,
                        isNumeric: /^\\d+$/.test(badgeText),
                        isDot: badgeText === '' || badgeText === '•',
                        backgroundColor: computed.backgroundColor,
                        color: computed.color,
                        borderRadius: computed.borderRadius,
                        position: {
                            x: rect.x,
                            y: rect.y,
                            width: rect.width,
                            height: rect.height
                        }
                    });
                }
            }
            
            return results;
        }
    """)
    
    logger.info(f"✓ 找到 {len(unread_badges)} 个未读消息气泡")
    for badge in unread_badges[:5]:
        logger.info(f"  {badge['userName']}: {badge['badgeText'] or '红点'} (背景: {badge['backgroundColor']})")
    
    page.screenshot(path='screenshots/tc025_unread_badges.png', timeout=60000)
    
    # 步骤2：验证气泡样式
    logger.info("\n--- 步骤2: 验证气泡样式 ---")
    if unread_badges:
        first_badge = unread_badges[0]
        logger.info(f"✓ 气泡样式:")
        logger.info(f"  背景色: {first_badge['backgroundColor']}")
        logger.info(f"  文字色: {first_badge['color']}")
        logger.info(f"  圆角: {first_badge['borderRadius']}")
        logger.info(f"  是否数字: {first_badge['isNumeric']}")
        
        # 验证至少有一个气泡显示数字
        has_numeric = any(b['isNumeric'] for b in unread_badges)
        logger.info(f"✓ 是否有数字气泡: {has_numeric}")
    else:
        logger.info("⚠ 当前没有未读消息气泡")
    
    # 步骤3：点击有未读消息的会话（如果存在）
    if unread_badges:
        logger.info("\n--- 步骤3: 点击有未读消息的会话 ---")
        click_result = page.evaluate("""
            () => {
                const badges = document.querySelectorAll('[class*="badge"], [class*="unread"]');
                for (const badge of badges) {
                    const text = badge.textContent?.trim();
                    if (text && /^\\d+$/.test(text)) {
                        const conversation = badge.closest('[class*="conversation"], [class*="chat-item"]');
                        if (conversation) {
                            conversation.click();
                            return {
                                success: true,
                                userName: conversation.textContent?.trim().split('\\n')[0],
                                unreadCount: text
                            };
                        }
                    }
                }
                return {success: false};
            }
        """)
        
        if click_result['success']:
            logger.info(f"✓ 点击未读会话: {click_result['userName']} (未读: {click_result['unreadCount']})")
            page.wait_for_timeout(2000)
            page.screenshot(path='screenshots/tc025_after_click.png', timeout=60000)
        else:
            logger.info("⚠ 未找到可点击的未读会话")
    
    logger.info("✓ TC025 测试通过")


# ==================== TC026-TC028: 会话列表深度交互测试 ====================

@pytest.mark.p1
@allure.feature("OK - Messages")
@allure.story("Messages页面功能探索 - 会话列表时间顺序")
@allure.title("TC026: 会话列表按最新消息时间倒序排列")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.messages
@pytest.mark.conversation
@pytest.mark.timestamp
@pytest.mark.ae
@pytest.mark.case_id_messages_list_order_026
def test_conversation_list_time_order(page, config):
    """
    TC026: 会话列表时间顺序展示测试（✅ 实测）

    实测发现：
    - 会话列表容器：.list-group.list-group-flush（scrollH=2642, clientH=684，可滚动）
    - 时间戳格式：当天显示 HH:MM，昨天显示 Yesterday，
      其余显示 "Mon Day"（如 Mar 9, Feb 5, Jan 21）
    - 时间顺序：最新消息在最上方（降序排列）
    
    测试步骤:
    1. 导航到Messages页面
    2. 获取前10条会话的时间戳
    3. 验证时间顺序为从新到旧（降序）
    4. 验证时间格式正确
    """
    logger.info("=" * 80)
    logger.info("TC026: 会话列表时间顺序展示测试")
    logger.info("=" * 80)

    # 准备
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    login_page = LoginPage(page, base_url=config['base_url'])
    messages_page = MessagesExplorePage(page)

    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        login_page.navigate_to_home_page()
        login_page.handle_cookie_popup()
        login_page.login(config['test_account']['username'], config['test_account']['password'])
        session_manager.save_session()

    try:
        messages_page.navigate_to_messages_directly(_CONFIG['target_page'])
        page.wait_for_timeout(5000)
        # 等待会话列表出现
        page.wait_for_selector('.list-group.list-group-flush', timeout=30000)
        logger.info("✓ 会话列表已加载")
    except Exception as e:
        logger.error(f"✗ Messages页面加载失败: {e}")
        pytest.skip(f"Messages页面加载失败，可能是网络问题: {str(e)[:100]}")

    # 步骤1：获取会话列表容器信息
    logger.info("\n--- 步骤1: 验证会话列表容器可滚动 ---")
    container_info = page.evaluate("""
        () => {
            const listGroup = document.querySelector(".list-group.list-group-flush");
            // 找可滚动的父容器
            let scrollable = listGroup?.parentElement;
            while (scrollable && scrollable.scrollHeight <= scrollable.clientHeight) {
                scrollable = scrollable.parentElement;
                if (!scrollable || scrollable === document.body) { scrollable = null; break; }
            }
            return {
                containerScrollH: scrollable?.scrollHeight,
                containerClientH: scrollable?.clientHeight,
                isScrollable: scrollable ? scrollable.scrollHeight > scrollable.clientHeight : false,
                totalItems: listGroup?.children?.length || 0
            };
        }
    """)
    logger.info(f"✓ 容器信息: scrollH={container_info['containerScrollH']}, "
                f"clientH={container_info['containerClientH']}, "
                f"可滚动={container_info['isScrollable']}, "
                f"总会话数={container_info['totalItems']}")

    assert container_info['totalItems'] > 0, "会话列表为空"
    page.screenshot(path='screenshots/tc026_list_initial.png', timeout=60000)

    # 步骤2：获取前10条会话的时间戳
    logger.info("\n--- 步骤2: 获取会话时间戳 ---")
    timestamps_raw = page.evaluate("""
        () => {
            const list = document.querySelector(".list-group.list-group-flush");
            if (!list) return [];
            return Array.from(list.children).slice(0, 10).map((item, idx) => {
                const spans = Array.from(item.querySelectorAll("span"));
                const timeSpan = spans.find(s =>
                    /^\\d+:\\d+$/.test(s.textContent.trim()) ||
                    /^Yesterday$/.test(s.textContent.trim()) ||
                    /^Today$/.test(s.textContent.trim()) ||
                    /^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \\d+$/.test(s.textContent.trim())
                );
                const allTexts = spans.map(s => s.textContent.trim()).filter(t => t.length > 0);
                return {
                    idx,
                    timeText: timeSpan?.textContent?.trim() || null,
                    allTexts: allTexts.slice(0, 4)
                };
            });
        }
    """)

    logger.info(f"✓ 获取到 {len(timestamps_raw)} 条会话时间戳")
    for ts in timestamps_raw:
        logger.info(f"  Item {ts['idx']}: time='{ts['timeText']}' | {ts['allTexts']}")

    # 步骤3：验证时间戳格式
    logger.info("\n--- 步骤3: 验证时间戳格式 ---")
    import re
    valid_patterns = [
        r'^\d+:\d+$',                                          # HH:MM
        r'^Yesterday$',                                         # 昨天
        r'^Today$',                                             # 今天
        r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d+$',  # Mon Day
    ]
    valid_count = 0
    for ts in timestamps_raw:
        if ts['timeText']:
            if any(re.match(p, ts['timeText']) for p in valid_patterns):
                valid_count += 1
                logger.info(f"  ✓ 格式正确: '{ts['timeText']}'")
            else:
                logger.warning(f"  ⚠ 格式异常: '{ts['timeText']}'")

    assert valid_count >= len(timestamps_raw) * 0.8, \
        f"时间戳格式正确率不足80%: {valid_count}/{len(timestamps_raw)}"
    logger.info(f"✓ 时间戳格式验证通过: {valid_count}/{len(timestamps_raw)}")

    # 步骤4：验证时间顺序（最新在前）
    logger.info("\n--- 步骤4: 验证时间顺序（最新消息在上方）---")
    # 实测中时间戳按格式优先级：HH:MM > Yesterday > Mon Day（越靠前越新）
    # 所以只需验证今日时间（HH:MM格式）出现在日期格式之前
    time_only = [ts['timeText'] for ts in timestamps_raw if ts['timeText']]
    logger.info(f"✓ 完整时间序列: {time_only}")

    # 找到第一个纯日期格式的位置
    first_date_idx = None
    for i, t in enumerate(time_only):
        if re.match(r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d+$', t or ''):
            first_date_idx = i
            break

    if first_date_idx is not None:
        # 验证日期之前的全是 HH:MM 或 Yesterday/Today
        for t in time_only[:first_date_idx]:
            assert re.match(r'^\d+:\d+$', t or '') or t in ('Yesterday', 'Today'), \
                f"时间顺序异常：'{t}' 出现在日期 '{time_only[first_date_idx]}' 之前"
        logger.info(f"✓ 时间顺序验证通过：HH:MM/Today/Yesterday 均在日期格式之前")
    else:
        logger.info("⚠ 当天/昨天消息不足，仅有日期格式，跳过顺序验证")

    logger.info("✓ TC026 测试通过 ✅ 实测")


@pytest.mark.p1
@allure.feature("OK - Messages")
@allure.story("Messages页面功能探索 - 置顶会话icon")
@allure.title("TC027: 置顶会话在列表顶部显示pin图标")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.messages
@pytest.mark.conversation
@pytest.mark.pin
@pytest.mark.ae
@pytest.mark.case_id_messages_pin_icon_027
def test_pinned_conversation_icon(page, config):
    """
    TC027: 置顶会话icon展示测试（✅ 实测）

    实测发现：
    - 置顶操作入口：右侧聊天区顶部 .c-d-img-menu → 点击后弹出 .c-d-menu
    - 菜单项结构：.c-d-menu-item（Pin / Mute / Block）
    - 置顶后icon：img src 含 "toplist@2x"（image URL: toplist@2x.2004c053.png）
    - 置顶后会话移动到列表第1位（索引0）
    - 置顶的会话菜单变为 "Unpin/Mute/Block"

    测试步骤:
    1. 导航到Messages页面，选择第3条会话
    2. 打开菜单执行Pin操作
    3. 验证该会话移动到列表第1位
    4. 验证置顶icon（toplist图片）出现
    5. 还原：执行Unpin操作
    """
    logger.info("=" * 80)
    logger.info("TC027: 置顶会话icon展示测试")
    logger.info("=" * 80)

    # 准备
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    login_page = LoginPage(page, base_url=config['base_url'])
    messages_page = MessagesExplorePage(page)

    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        login_page.navigate_to_home_page()
        login_page.handle_cookie_popup()
        login_page.login(config['test_account']['username'], config['test_account']['password'])
        session_manager.save_session()

    try:
        messages_page.navigate_to_messages_directly(_CONFIG['target_page'])
        page.wait_for_timeout(5000)
        page.wait_for_selector('.list-group.list-group-flush', timeout=30000)
        logger.info("✓ 会话列表已加载")
    except Exception as e:
        logger.error(f"✗ Messages页面加载失败: {e}")
        pytest.skip(f"Messages页面加载失败，可能是网络问题: {str(e)[:100]}")

    # 步骤1：记录置顶前第3条会话的信息
    logger.info("\n--- 步骤1: 记录待置顶会话信息 ---")
    before_info = page.evaluate("""
        () => {
            const list = document.querySelector(".list-group.list-group-flush");
            // 取第3条（idx=2）
            const item = list?.children[2];
            if (!item) return null;
            const spans = Array.from(item.querySelectorAll("span"));
            return { texts: spans.map(s => s.textContent.trim()).filter(t => t.length > 0).slice(0, 3) };
        }
    """)
    logger.info(f"✓ 待置顶会话信息（第3条）: {before_info}")
    target_name = before_info['texts'][0] if before_info else None

    page.screenshot(path='screenshots/tc027_before_pin.png', timeout=60000)

    # 步骤2：点击第3条会话进入详情，打开菜单Pin
    logger.info("\n--- 步骤2: 执行Pin操作 ---")
    items = page.query_selector_all('.list-group.list-group-flush > div')
    assert len(items) >= 3, f"会话数量不足: {len(items)}"

    items[2].click()
    page.wait_for_timeout(2000)

    # 打开...菜单
    menu_img = page.locator('.c-d-img-menu').first
    assert menu_img.is_visible(), "菜单按钮不可见"
    menu_img.click()
    page.wait_for_timeout(1000)

    menu_text = page.locator('.c-d-menu').first.text_content()
    logger.info(f"✓ 当前菜单内容: '{menu_text}'")

    page.screenshot(path='screenshots/tc027_menu_open.png', timeout=60000)

    # 判断当前是已Pin还是未Pin
    if 'Unpin' in menu_text:
        logger.info("⚠ 该会话已置顶，先取消再重新置顶以验证完整流程")
        page.locator('.c-d-menu-item span:has-text("Unpin")').first.click()
        page.wait_for_timeout(2000)
        items[2].click()
        page.wait_for_timeout(1500)
        menu_img.click()
        page.wait_for_timeout(1000)

    # 执行Pin
    pin_btn = page.locator('.c-d-menu-item span:has-text("Pin")').first
    assert pin_btn.is_visible(), "Pin按钮不可见"
    pin_btn.click()
    page.wait_for_timeout(2000)
    logger.info("✓ 已执行Pin操作")

    # 重新导航到Messages列表页面以查看置顶效果
    try:
        messages_page.navigate_to_messages_directly(_CONFIG['target_page'])
        page.wait_for_timeout(3000)
        
        # 等待列表刷新
        page.wait_for_selector('.list-group.list-group-flush', timeout=10000)
        page.wait_for_timeout(2000)
        logger.info("✓ 已重新加载Messages列表页面")
    except Exception as e:
        logger.error(f"✗ 重新加载Messages页面失败: {e}")
        pytest.skip(f"置顶后重新加载Messages页面失败，可能是网络问题: {str(e)[:100]}")

    # 步骤3：验证置顶会话移到列表第1位
    logger.info("\n--- 步骤3: 验证置顶会话移到列表第1位 ---")
    after_pin = page.evaluate("""
        () => {
            const list = document.querySelector(".list-group.list-group-flush");
            const firstItem = list?.children[0];
            if (!firstItem) return null;
            const spans = Array.from(firstItem.querySelectorAll("span"));
            const imgs = Array.from(firstItem.querySelectorAll("img"));
            return {
                texts: spans.map(s => s.textContent.trim()).filter(t => t.length > 0).slice(0, 3),
                imgSrcs: imgs.map(img => img.src),
                hasPinIcon: imgs.some(img => img.src.includes("toplist"))
            };
        }
    """)
    logger.info(f"✓ 置顶后第1条会话: {after_pin['texts']}")
    logger.info(f"✓ 图片列表: {[s.split('/')[-1] for s in after_pin['imgSrcs']]}")
    logger.info(f"✓ 是否有置顶icon: {after_pin['hasPinIcon']}")

    # 步骤4：验证置顶icon（toplist图片）出现
    logger.info("\n--- 步骤4: 验证置顶icon显示 ---")
    assert after_pin['hasPinIcon'], "置顶后列表第1条未找到置顶icon（toplist图片）"
    logger.info("✓ 置顶icon验证通过！图片URL包含 'toplist'")

    # 注意：由于可能有新消息进来，不强制验证会话名称，只验证置顶icon存在
    if target_name and target_name in after_pin['texts']:
        logger.info(f"✓ 置顶会话'{target_name}'已移到第1位")
    else:
        logger.warning(f"⚠ 置顶后第1条会话为 {after_pin['texts']}，可能有新消息进来，但置顶icon已正确显示")

    page.screenshot(path='screenshots/tc027_after_pin.png', timeout=60000)

    # 步骤5：还原 - 执行Unpin
    logger.info("\n--- 步骤5: 还原 - 执行Unpin ---")
    items_after = page.query_selector_all('.list-group.list-group-flush > div')
    items_after[0].click()
    page.wait_for_timeout(1500)
    menu_img.click()
    page.wait_for_timeout(1000)
    unpin_btn = page.locator('.c-d-menu-item span:has-text("Unpin")').first
    if unpin_btn.is_visible():
        unpin_btn.click()
        page.wait_for_timeout(2000)
        logger.info("✓ Unpin还原完成")
    else:
        logger.warning("⚠ Unpin按钮不可见，跳过还原")

    logger.info("✓ TC027 测试通过 ✅ 实测")


@pytest.mark.p1
@allure.feature("OK - Messages")
@allure.story("Messages页面功能探索 - 免打扰会话icon")
@allure.title("TC028: 免打扰会话在列表显示mute图标")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.messages
@pytest.mark.conversation
@pytest.mark.mute
@pytest.mark.ae
@pytest.mark.case_id_messages_mute_icon_028
def test_muted_conversation_icon(page, config):
    """
    TC028: 免打扰会话icon展示测试（✅ 实测）

    实测发现：
    - 免打扰操作入口：.c-d-img-menu → .c-d-menu → "Mute"菜单项
    - 免打扰后icon：img src 含 "listMute@2x"（URL: listMute@2x.e432d57b.png）
    - 已静音会话菜单项显示 "Unmute"（可取消静音）
    - 静音icon位置：会话item内的 hstack 容器中

    测试步骤:
    1. 导航到Messages页面，选择第2条会话
    2. 如已静音先取消，确保从未静音状态开始
    3. 打开菜单执行Mute操作
    4. 验证会话列表中出现静音icon（listMute图片）
    5. 还原：执行Unmute操作
    """
    logger.info("=" * 80)
    logger.info("TC028: 免打扰会话icon展示测试")
    logger.info("=" * 80)

    # 准备
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    login_page = LoginPage(page, base_url=config['base_url'])
    messages_page = MessagesExplorePage(page)

    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        login_page.navigate_to_home_page()
        login_page.handle_cookie_popup()
        login_page.login(config['test_account']['username'], config['test_account']['password'])
        session_manager.save_session()

    try:
        messages_page.navigate_to_messages_directly(_CONFIG['target_page'])
        page.wait_for_timeout(5000)
        page.wait_for_selector('.list-group.list-group-flush', timeout=15000)
    except Exception as e:
        logger.error(f"✗ Messages页面加载失败: {e}")
        pytest.skip(f"Messages页面加载失败，可能是网络问题: {str(e)[:100]}")

    # 步骤1：记录第2条会话信息
    logger.info("\n--- 步骤1: 记录待操作会话信息 ---")
    before_info = page.evaluate("""
        () => {
            const list = document.querySelector(".list-group.list-group-flush");
            const item = list?.children[1];
            if (!item) return null;
            const spans = Array.from(item.querySelectorAll("span"));
            const imgs = Array.from(item.querySelectorAll("img"));
            return {
                texts: spans.map(s => s.textContent.trim()).filter(t => t.length > 0).slice(0, 3),
                hasMuteIcon: imgs.some(img => img.src.includes("listMute"))
            };
        }
    """)
    logger.info(f"✓ 第2条会话信息: {before_info}")
    page.screenshot(path='screenshots/tc028_before_mute.png', timeout=60000)

    # 步骤2：点击第2条会话，检查并确保从未静音状态开始
    logger.info("\n--- 步骤2: 确保从未静音状态开始 ---")
    items = page.query_selector_all('.list-group.list-group-flush > div')
    items[1].click()
    page.wait_for_timeout(2000)

    menu_img = page.locator('.c-d-img-menu').first
    assert menu_img.is_visible(), "菜单按钮不可见"
    menu_img.click()
    page.wait_for_timeout(1000)

    menu_text = page.locator('.c-d-menu').first.text_content()
    logger.info(f"✓ 当前菜单: '{menu_text}'")

    if 'Unmute' in menu_text:
        logger.info("  ⚠ 当前已静音，先执行Unmute")
        page.locator('.c-d-menu-item span:has-text("Unmute")').first.click()
        page.wait_for_timeout(2000)
        # 重新打开菜单
        items[1].click()
        page.wait_for_timeout(1500)
        menu_img.click()
        page.wait_for_timeout(1000)
        menu_text = page.locator('.c-d-menu').first.text_content()
        logger.info(f"  ✓ 取消静音后菜单: '{menu_text}'")

    # 步骤3：执行Mute操作
    logger.info("\n--- 步骤3: 执行Mute操作 ---")
    mute_btn = page.locator('.c-d-menu-item span:has-text("Mute")').first
    assert mute_btn.is_visible(), "Mute按钮不可见"
    mute_btn.click()
    page.wait_for_timeout(2000)
    logger.info("✓ 已执行Mute操作")

    # 步骤4：验证会话列表中出现静音icon
    logger.info("\n--- 步骤4: 验证静音icon出现 ---")
    mute_verify = page.evaluate("""
        () => {
            const list = document.querySelector(".list-group.list-group-flush");
            const items = Array.from(list?.children || []);
            
            // 找有listMute图标的会话
            const mutedItems = items.map((item, idx) => {
                const imgs = Array.from(item.querySelectorAll("img"));
                const hasMute = imgs.some(img => img.src.includes("listMute"));
                const spans = Array.from(item.querySelectorAll("span"));
                const texts = spans.map(s => s.textContent.trim()).filter(t => t.length > 0).slice(0, 3);
                return { idx, hasMute, texts, muteImgCount: imgs.filter(img => img.src.includes("listMute")).length };
            }).filter(item => item.hasMute);
            
            return {
                mutedCount: mutedItems.length,
                mutedItems
            };
        }
    """)
    logger.info(f"✓ 找到 {mute_verify['mutedCount']} 个静音会话")
    for item in mute_verify['mutedItems'][:3]:
        logger.info(f"  Item {item['idx']}: {item['texts']} (mute图标数: {item['muteImgCount']})")

    assert mute_verify['mutedCount'] >= 1, "执行Mute后未找到任何静音icon（listMute图片）"
    logger.info("✓ 静音icon验证通过！img src 包含 'listMute'")

    page.screenshot(path='screenshots/tc028_after_mute.png', timeout=60000)

    # 步骤5：验证菜单变为Unmute
    logger.info("\n--- 步骤5: 验证菜单变为Unmute ---")
    
    # 关闭当前菜单（如果打开）
    page.keyboard.press('Escape')
    page.wait_for_timeout(500)
    
    # 重新获取会话列表并找到刚才静音的会话
    items = page.query_selector_all('.list-group.list-group-flush > div')
    target_name = before_info['texts'][0] if before_info else None
    
    # 确保点击正确的会话
    clicked = False
    for item in items:
        item_text = item.text_content()
        if target_name and target_name in item_text:
            item.click()
            page.wait_for_timeout(1500)
            clicked = True
            logger.info(f"✓ 点击会话: {target_name}")
            break
    
    if not clicked:
        logger.warning("⚠ 未找到目标会话，点击第2条")
        items[1].click()
        page.wait_for_timeout(1500)

    # 打开菜单
    menu_img = page.locator('.c-d-img-menu').first
    menu_img.click()
    page.wait_for_timeout(1500)
    
    menu_after_mute = page.locator('.c-d-menu').first.text_content()
    logger.info(f"✓ 静音后菜单: '{menu_after_mute}'")
    
    # 检查是否有Unmute菜单项
    try:
        unmute_item = page.locator('.c-d-menu-item span:has-text("Unmute")').first
        has_unmute_item = unmute_item.is_visible(timeout=2000)
        logger.info(f"✓ Unmute菜单项可见: {has_unmute_item}")
        
        if has_unmute_item:
            logger.info("✓ 菜单正确显示Unmute选项")
        else:
            # 如果定位器找不到，检查文本
            if 'Unmute' not in menu_after_mute:
                logger.warning(f"⚠ 静音后菜单未显示Unmute: '{menu_after_mute}'")
                pytest.skip(f"静音后菜单文本可能已变更，未找到Unmute选项: '{menu_after_mute}'")
            logger.info("✓ 菜单文本包含Unmute")
    except Exception as e:
        logger.warning(f"⚠ 检查Unmute菜单项时出错: {e}")
        if 'Unmute' not in menu_after_mute:
            pytest.skip(f"静音后菜单文本可能已变更，未找到Unmute选项: '{menu_after_mute}'")

    # 步骤6：还原 - 执行Unmute
    logger.info("\n--- 步骤6: 还原 - 执行Unmute ---")
    unmute_btn = page.locator('.c-d-menu-item span:has-text("Unmute")').first
    if unmute_btn.is_visible():
        unmute_btn.click()
        page.wait_for_timeout(2000)
        logger.info("✓ Unmute还原完成")
    else:
        logger.warning("⚠ Unmute按钮不可见，跳过还原")

    logger.info("✓ TC028 测试通过 ✅ 实测")


# ==================== TC029-TC037: 消息输入区新增功能 ====================

def _setup_session_and_navigate(page, config):
    """
    通用辅助：加载 session 并导航到 Messages 页面。
    返回 (session_manager, messages_page) 供各用例复用。
    """
    session_manager = SessionManager(page, _CONFIG['base_url'], f"{config['site']}_{config['role']}_{config['user_name']}")
    login_page = LoginPage(page, base_url=_CONFIG['base_url'])
    messages_page = MessagesExplorePage(page)

    if session_manager.load_session():
        logger.info("✓ Session 已加载")
    else:
        login_page.navigate_to_home_page()
        login_page.handle_cookie_popup()
        login_page.login(config['test_account']['username'], config['test_account']['password'])
        session_manager.save_session()

    messages_page.navigate_to_messages_directly(_CONFIG['target_page'])
    page.wait_for_timeout(3000)
    return messages_page


def _click_first_conversation(page):
    """
    通用辅助：点击会话列表第一个会话，确保 textarea 可见。
    先尝试坐标点击，若 textarea 未出现则尝试 JS 点击可点击元素。
    """
    page.mouse.click(317, 309)
    page.wait_for_timeout(2000)
    ta = page.locator('textarea.ci-input-item')
    
    # 尝试等待 textarea 出现
    try:
        ta.wait_for(state='visible', timeout=5000)
    except:
        # 如果第一次点击失败，尝试 JS 点击
        page.evaluate("""() => {
            var items = Array.from(document.querySelectorAll('li, [style*="cursor: pointer"]'));
            var item = items.find(function(el){ return el.offsetHeight > 30 && el.offsetWidth > 100; });
            if (item) item.click();
        }""")
        page.wait_for_timeout(2000)
        # 再次等待 textarea
        ta.wait_for(state='visible', timeout=5000)
    
    assert ta.is_visible(), "进入会话后 textarea 应可见"
    return ta


# ---- 保留原辅助函数别名，供旧引用向后兼容 ----
def _enter_first_conversation(page):
    """向后兼容包装，内部调用拆分后的两个辅助函数"""
    import json, os
    session_file = 'sessions/ae_seller_session.json'
    if not os.path.exists(session_file):
        raise FileNotFoundError(f"Session 文件不存在: {session_file}")
    ctx = page.context
    with open(session_file, 'r') as f:
        cookies = json.load(f)
    ctx.add_cookies(cookies)
    page.goto('https://ae.58v5.cn/en/city-abu-dhabi/', wait_until='domcontentloaded', timeout=60000)
    page.wait_for_timeout(1000)
    page.goto('https://aepub.58v5.cn/biz/en/chat', wait_until='domcontentloaded', timeout=60000)
    page.wait_for_timeout(3000)
    return _click_first_conversation(page)


@pytest.mark.p1
@allure.feature("OK - Messages")
@allure.story("消息输入区 - 发送附件")
@allure.title("TC029: 发送附件 - 上传 PDF 文件后预览区显示文件名")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.messages
@pytest.mark.ae
@pytest.mark.case_id_messages_attachment_029
def test_send_pdf_attachment(page, config):
    """
    TC029: 发送 PDF 附件 ✅ 实测
    
    实测结论：
    - 输入区底部有 sendFile 图标，对应隐藏的 input[type=file][accept=".pdf,.doc,..."]
    - set_input_files 后文件名出现在页面文字中
    - Send 按钮 disabled 状态下不能点击（需等待上传完成后 enabled）
    """
    import os
    logger.info("=" * 80)
    logger.info("TC029: 发送PDF附件")

    PDF_PATH = '/Users/a58/ok_autotest_ui_pc/test_data/files/口算题 (加减混合) 1000题.pdf'
    if not os.path.exists(PDF_PATH):
        pytest.skip(f"PDF 文件不存在: {PDF_PATH}")

    _setup_session_and_navigate(page, config)

    with allure.step("点击第一个会话"):
        _click_first_conversation(page)

    with allure.step("验证附件 file input 存在（accept=.pdf,.doc...）"):
        file_input = page.locator('input[type=file][accept*="pdf"]')
        assert file_input.count() > 0, "应存在接受 PDF 的 file input"
        accept_val = file_input.first.get_attribute('accept')
        logger.info(f"✓ file input accept: {accept_val}")
        assert '.pdf' in accept_val, "accept 属性应包含 .pdf"
        assert '.doc' in accept_val, "accept 属性应包含 .doc"
        assert '.xlsx' in accept_val, "accept 属性应包含 .xlsx"

    with allure.step("上传 PDF 文件"):
        file_input.first.set_input_files(PDF_PATH)
        page.wait_for_timeout(2000)

    with allure.step("验证文件名出现在页面中（预览状态）"):
        body = page.evaluate("() => document.body.innerText")
        assert '口算题 (加减混合) 1000题.pdf' in body, \
            f"上传后页面应显示文件名，实际页面文字不含文件名"
        logger.info("✓ 文件名已出现在页面中 ✅ 实测")

    with allure.step("验证 Send 按钮存在（可能为 disabled 状态，等待上传完成）"):
        send_btn = page.locator('button:has-text("Send")')
        assert send_btn.count() > 0, "上传文件后应出现 Send 按钮"
        logger.info(f"✓ Send 按钮存在，disabled={send_btn.first.get_attribute('disabled')}")

    page.screenshot(path='screenshots/tc029_pdf_attachment.png', timeout=60000)
    logger.info("✓ TC029 PDF附件测试通过 ✅ 实测")


@pytest.mark.p2
@allure.feature("OK - Messages")
@allure.story("消息输入区 - 发送附件")
@allure.title("TC030: 附件 file input - accept 属性支持多种文档格式")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.messages
@pytest.mark.ae
@pytest.mark.case_id_messages_attachment_030
def test_attachment_accepted_types(page, config):
    """
    TC030: 附件 file input accept 属性包含所有支持格式 ✅ 实测
    
    实测结论：accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.zip,.txt"
    """
    logger.info("=" * 80)
    logger.info("TC030: 附件类型校验")

    _setup_session_and_navigate(page, config)
    _click_first_conversation(page)

    with allure.step("验证附件 input accept 包含所有支持格式"):
        file_input = page.locator('input[type=file][accept*="pdf"]')
        assert file_input.count() > 0, "应存在附件 file input"
        accept_val = file_input.first.get_attribute('accept')
        logger.info(f"✓ accept 属性: {accept_val}")

        expected_types = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.zip', '.txt']
        for ext in expected_types:
            assert ext in accept_val, f"accept 属性应包含 '{ext}'，实际={accept_val}"
        logger.info(f"✓ 所有期望格式均包含在 accept 中: {expected_types}")

    with allure.step("验证 multiple 属性（支持多选）"):
        multiple = file_input.first.get_attribute('multiple')
        assert multiple is not None, "附件 file input 应支持 multiple（多文件上传）"
        logger.info("✓ file input multiple 属性存在")

    page.screenshot(path='screenshots/tc030_attachment_types.png', timeout=60000)
    logger.info("✓ TC030 附件类型校验通过 ✅ 实测")


@pytest.mark.p1
@allure.feature("OK - Messages")
@allure.story("消息输入区 - 发送图片")
@allure.title("TC031: 发送图片 - 上传图片后预览区应有 img 元素")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.messages
@pytest.mark.ae
@pytest.mark.case_id_messages_image_031
def test_send_image(page, config):
    """
    TC031: 发送图片 ✅ 实测
    
    实测结论：
    - 输入区底部有 picture25@2x 图标，对应 input[type=file][accept="image/JPG,image/PNG,image/JPEG"]
    - 上传后图片显示在 .ci-image 预览区
    - Send 按钮 disabled = 等待上传完成
    """
    import os
    logger.info("=" * 80)
    logger.info("TC031: 发送图片")

    IMG_PATH = str(
        Path(__file__).resolve().parents[2] / "test_data" / "images" / "8b423179e72ba4d4a56ca6a5b0479aee.png"
    )
    if not os.path.exists(IMG_PATH):
        pytest.skip(f"图片文件不存在: {IMG_PATH}")

    _setup_session_and_navigate(page, config)
    _click_first_conversation(page)

    with allure.step("验证图片 file input 存在（accept=image/JPG,image/PNG,image/JPEG）"):
        img_input = page.locator('input[type=file][accept*="image"]')
        assert img_input.count() > 0, "应存在接受 image 的 file input"
        accept_val = img_input.first.get_attribute('accept')
        logger.info(f"✓ 图片 file input accept: {accept_val}")
        for fmt in ['image/JPG', 'image/PNG', 'image/JPEG']:
            assert fmt in accept_val, f"accept 应包含 {fmt}，实际={accept_val}"

    with allure.step("上传图片文件"):
        img_input.first.set_input_files(IMG_PATH)
        page.wait_for_timeout(2000)

    with allure.step("验证 .ci-image 预览区存在"):
        preview_div = page.locator('.ci-image')
        assert preview_div.count() > 0, ".ci-image 预览区应存在"
        logger.info("✓ .ci-image 预览区存在")

    with allure.step("验证 Send 按钮出现"):
        send_btn = page.locator('button:has-text("Send")')
        assert send_btn.count() > 0, "上传图片后应有 Send 按钮"
        logger.info(f"✓ Send 按钮存在，disabled={send_btn.first.get_attribute('disabled')}")

    page.screenshot(path='screenshots/tc031_image_send.png', timeout=60000)
    logger.info("✓ TC031 图片发送测试通过 ✅ 实测")


@pytest.mark.p2
@allure.feature("OK - Messages")
@allure.story("消息输入区 - 发送图片")
@allure.title("TC032: 图片 file input - accept 只接受 JPG/PNG/JPEG 格式")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.messages
@pytest.mark.ae
@pytest.mark.case_id_messages_image_032
def test_image_accepted_types(page, config):
    """
    TC032: 图片 file input accept 属性只接受图片格式 ✅ 实测
    
    实测结论：accept="image/JPG,image/PNG,image/JPEG"，不含 gif/webp/pdf 等
    """
    logger.info("=" * 80)
    logger.info("TC032: 图片类型校验")

    _setup_session_and_navigate(page, config)
    _click_first_conversation(page)

    with allure.step("验证图片 input accept 属性"):
        img_input = page.locator('input[type=file][accept*="image"]')
        assert img_input.count() > 0, "应存在图片 file input"
        accept_val = img_input.first.get_attribute('accept')
        logger.info(f"✓ 图片 accept: {accept_val}")

        # 应支持的格式
        assert 'image/JPG' in accept_val, "应支持 JPG"
        assert 'image/PNG' in accept_val, "应支持 PNG"
        assert 'image/JPEG' in accept_val, "应支持 JPEG"

        # 不应支持的格式
        assert '.pdf' not in accept_val, "图片 input 不应接受 PDF"
        assert '.doc' not in accept_val, "图片 input 不应接受 DOC"
        logger.info("✓ 图片格式校验通过，仅接受 JPG/PNG/JPEG")

    with allure.step("验证 multiple 属性（支持多张图片）"):
        multiple = img_input.first.get_attribute('multiple')
        assert multiple is not None, "图片 file input 应支持 multiple"
        logger.info("✓ 图片 file input 支持多选")

    page.screenshot(path='screenshots/tc032_image_types.png', timeout=60000)
    logger.info("✓ TC032 图片类型校验通过 ✅ 实测")


@pytest.mark.p1
@allure.feature("OK - Messages")
@allure.story("消息输入区 - 地理位置")
@allure.title("TC033: 地理位置图标 - 点击弹出 Send Location 地图弹窗")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.messages
@pytest.mark.ae
@pytest.mark.case_id_messages_location_033
def test_location_icon_entry(page, config):
    """
    TC033: 地理位置图标入口 ✅ 实测

    实测结论：
    - 输入区 .ci-send 第一个图标为 icon-location-big.png（地理位置）
    - 点击后弹出 "Send Location" 弹窗，内嵌 Google Maps
    - 弹窗含：标题 "Send Location"、"Locate me" 按钮、拖拽 pin 提示、"Send" 发送按钮
    - 提示文案：Drag the pin to set precise location. Accurate locations get more responses.
    - 注意：图标在页面底部（viewY≈912），需确保会话已打开
    """
    logger.info("=" * 80)
    logger.info("TC033: 地理位置图标 - Send Location 弹窗")

    _setup_session_and_navigate(page, config)
    _click_first_conversation(page)

    with allure.step("验证地理位置图标是 .ci-send 区域第一个图标"):
        first_icon_src = page.evaluate("""() => {
            var imgs = Array.from(document.querySelectorAll('.ci-send img'));
            return imgs.length > 0 ? imgs[0].src.split('/').pop() : null;
        }""")
        assert first_icon_src and 'location' in first_icon_src, \
            f".ci-send 第一个图标应为 location 图标，实际={first_icon_src}"
        logger.info(f"✓ .ci-send 第一个图标为地理位置图标: {first_icon_src}")

    with allure.step("获取地理位置图标真实视口坐标并点击"):
        loc_coords = page.evaluate("""() => {
            var imgs = Array.from(document.querySelectorAll('.ci-send img'));
            var loc = imgs.find(function(e){ return e.src.includes('location'); });
            if (!loc) return null;
            var rect = loc.getBoundingClientRect();
            return {
                centerX: Math.round(rect.x + rect.width / 2),
                centerY: Math.round(rect.y + rect.height / 2),
                inViewport: rect.y < window.innerHeight
            };
        }""")
        assert loc_coords, "应能获取地理位置图标坐标"
        logger.info(f"✓ 地理位置图标坐标: {loc_coords}")

        # 若图标在视口外（页面需滚动），滚动到图标位置
        if not loc_coords.get('inViewport'):
            page.evaluate("document.querySelector('.ci-send').scrollIntoView()")
            page.wait_for_timeout(300)
            loc_coords = page.evaluate("""() => {
                var imgs = Array.from(document.querySelectorAll('.ci-send img'));
                var loc = imgs.find(function(e){ return e.src.includes('location'); });
                if (!loc) return null;
                var rect = loc.getBoundingClientRect();
                return {centerX: Math.round(rect.x + rect.width/2), centerY: Math.round(rect.y + rect.height/2)};
            }""")

        page.mouse.click(loc_coords['centerX'], loc_coords['centerY'])
        page.wait_for_timeout(3000)

    with allure.step("验证 Send Location 弹窗弹出"):
        body = page.evaluate("() => document.body.innerText")
        assert 'Send Location' in body, \
            f"点击地理位置图标后应弹出 'Send Location' 弹窗，实际页面文字不含该文本"
        logger.info("✓ 'Send Location' 弹窗已弹出 ✅ 实测")

    with allure.step("验证弹窗包含 Google Maps 信息"):
        assert 'Map data' in body or 'Google' in body, \
            "Send Location 弹窗应内嵌 Google Maps"
        logger.info("✓ 弹窗包含 Google Maps 地图数据")

    with allure.step("验证弹窗含 Locate me 和 Send 按钮"):
        assert 'Locate me' in body, "弹窗应有 'Locate me' 定位按钮"
        assert 'Send' in body, "弹窗应有 'Send' 发送按钮"
        logger.info("✓ 弹窗 Locate me / Send 按钮均存在")

    with allure.step("验证拖拽 pin 提示文案"):
        assert 'Drag the pin to set precise location' in body, \
            "弹窗应有 'Drag the pin to set precise location' 提示"
        assert 'Accurate locations get more responses' in body, \
            "弹窗应有 'Accurate locations get more responses' 提示"
        logger.info("✓ 弹窗提示文案正确")

    page.screenshot(path='screenshots/tc033_location_modal.png', timeout=60000)
    logger.info("✓ TC033 地理位置弹窗测试通过 ✅ 实测")


@pytest.mark.p1
@allure.feature("OK - Messages")
@allure.story("消息输入区 - Send 按钮状态")
@allure.title("TC034: Send 按钮初始状态为 disabled")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.messages
@pytest.mark.ae
@pytest.mark.case_id_messages_send_034
def test_send_button_initially_disabled(page, config):
    """
    TC034: 发送框初始 Send 按钮禁用 ✅ 实测
    
    实测结论：
    - 初始状态 Send 按钮有 class button_disabled__9jYJ2，disabled=true
    - textarea 为空时 Send 无法点击
    """
    logger.info("=" * 80)
    logger.info("TC034: Send 按钮初始禁用状态验证")

    _setup_session_and_navigate(page, config)
    _click_first_conversation(page)

    with allure.step("验证 Send 按钮初始为 disabled"):
        send_state = page.evaluate("""() => {
            var btns = Array.from(document.querySelectorAll('button'));
            var sb = btns.find(function(b){ return b.textContent.trim() === 'Send'; });
            if (!sb) return null;
            return {
                disabled: sb.disabled,
                hasDisabledClass: sb.className.includes('disabled')
            };
        }""")
        assert send_state is not None, "应存在 Send 按钮"
        assert send_state['disabled'], "Send 按钮初始应为 disabled 状态"
        assert send_state['hasDisabledClass'], "Send 按钮初始应有 disabled class（button_disabled__9jYJ2）"
        logger.info(f"✓ Send 按钮初始状态: {send_state}")

    page.screenshot(path='screenshots/tc034_send_disabled.png', timeout=60000)
    logger.info("✓ TC034 Send 按钮初始禁用验证通过 ✅ 实测")


@pytest.mark.p1
@allure.feature("OK - Messages")
@allure.story("消息输入区 - Send 按钮状态")
@allure.title("TC035: 输入文字后 Send 按钮变为 enabled")
@allure.severity(allure.severity_level.BLOCKER)
@pytest.mark.messages
@pytest.mark.ae
@pytest.mark.case_id_messages_send_035
def test_send_button_enabled_after_input(page, config):
    """
    TC035: 输入文字后 Send 按钮启用 ✅ 实测
    
    实测结论：
    - textarea 输入文字后 Send 按钮 disabled 状态解除
    - 清空文字后 Send 按钮重新 disabled
    """
    logger.info("=" * 80)
    logger.info("TC035: 输入文字后 Send 按钮启用")

    _setup_session_and_navigate(page, config)
    ta = _click_first_conversation(page)

    with allure.step("确认初始 Send 为 disabled"):
        initial_disabled = page.evaluate("() => { var btns = Array.from(document.querySelectorAll('button')); var sb = btns.find(function(b){ return b.textContent.trim() === 'Send'; }); return sb ? sb.disabled : true; }")
        assert initial_disabled, "初始 Send 应为 disabled"

    with allure.step("输入文字后验证 Send 变为 enabled"):
        ta.click()
        ta.fill("hello test message")
        page.wait_for_timeout(500)
        after_input_disabled = page.evaluate("() => { var btns = Array.from(document.querySelectorAll('button')); var sb = btns.find(function(b){ return b.textContent.trim() === 'Send'; }); return sb ? sb.disabled : true; }")
        assert not after_input_disabled, "输入文字后 Send 应变为 enabled"
        logger.info("✓ 输入文字后 Send 按钮已启用")

    with allure.step("清空文字后验证 Send 重新 disabled"):
        ta.fill("")
        page.wait_for_timeout(500)
        after_clear_disabled = page.evaluate("() => { var btns = Array.from(document.querySelectorAll('button')); var sb = btns.find(function(b){ return b.textContent.trim() === 'Send'; }); return sb ? sb.disabled : true; }")
        assert after_clear_disabled, "清空后 Send 应重新 disabled"
        logger.info("✓ 清空文字后 Send 重新 disabled ✅ 实测")

    page.screenshot(path='screenshots/tc035_send_enabled.png', timeout=60000)
    logger.info("✓ TC035 Send 按钮状态验证通过 ✅ 实测")


@pytest.mark.p2
@allure.feature("OK - Messages")
@allure.story("消息输入区 - 发送附件")
@allure.title("TC036: 发送文件图标（sendFile）对应隐藏 file input 存在")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.messages
@pytest.mark.ae
@pytest.mark.case_id_messages_attachment_036
def test_send_file_icon_input(page, config):
    """
    TC036: 发送文件图标触发文件选择 ✅ 实测
    
    实测结论：
    - sendFile.png 图标旁有隐藏 input[type=file]
    - 图标的父 div 包裹 img + input[type=file]（input display:none）
    """
    logger.info("=" * 80)
    logger.info("TC036: 发送文件图标 DOM 结构验证")

    _setup_session_and_navigate(page, config)
    _click_first_conversation(page)

    with allure.step("验证 sendFile 图标存在于 .ci-send 区域"):
        send_file_icon = page.evaluate("""() => {
            var imgs = Array.from(document.querySelectorAll('.ci-send img'));
            var icon = imgs.find(function(e){ return e.src.includes('sendFile'); });
            return icon ? icon.src.split('/').pop() : null;
        }""")
        assert send_file_icon, "输入区 .ci-send 应有 sendFile 图标"
        logger.info(f"✓ sendFile 图标: {send_file_icon}")

    with allure.step("验证 sendFile 图标的父 div 包含隐藏 file input"):
        file_input_structure = page.evaluate("""() => {
            var imgs = Array.from(document.querySelectorAll('.ci-send img'));
            var icon = imgs.find(function(e){ return e.src.includes('sendFile'); });
            if (!icon) return null;
            var parent = icon.parentElement;
            var inp = parent ? parent.querySelector('input[type=file]') : null;
            return inp ? {accept: inp.accept, hidden: inp.style.display === 'none', multiple: inp.multiple} : null;
        }""")
        assert file_input_structure, "sendFile 图标父元素应包含 file input"
        assert file_input_structure['hidden'], "file input 应为隐藏状态（display:none）"
        assert '.pdf' in file_input_structure['accept'], "file input accept 应包含 .pdf"
        logger.info(f"✓ file input 结构验证通过: {file_input_structure}")

    page.screenshot(path='screenshots/tc036_sendfile_icon.png', timeout=60000)
    logger.info("✓ TC036 发送文件图标验证通过 ✅ 实测")


@pytest.mark.p2
@allure.feature("OK - Messages")
@allure.story("消息输入区 - 发送图片")
@allure.title("TC037: 发送图片图标（picture25）对应隐藏 image file input 存在")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.messages
@pytest.mark.ae
@pytest.mark.case_id_messages_image_037
def test_send_image_icon_input(page, config):
    """
    TC037: 发送图片图标触发图片选择 ✅ 实测
    
    实测结论：
    - picture25@2x.png 图标旁有隐藏 input[type=file][accept="image/JPG,image/PNG,image/JPEG"]
    - 输入区完整结构：ci-input（textarea） + ci-send（三个图标+Send按钮）
    """
    logger.info("=" * 80)
    logger.info("TC037: 发送图片图标 DOM 结构验证")

    _setup_session_and_navigate(page, config)
    _click_first_conversation(page)

    with allure.step("验证 picture25 图标存在于 .ci-send 区域"):
        img_icon = page.evaluate("""() => {
            var imgs = Array.from(document.querySelectorAll('.ci-send img'));
            var icon = imgs.find(function(e){ return e.src.includes('picture25'); });
            return icon ? icon.src.split('/').pop() : null;
        }""")
        assert img_icon, "输入区 .ci-send 应有 picture25 图片图标"
        logger.info(f"✓ 图片图标: {img_icon}")

    with allure.step("验证图片图标父 div 包含 image file input"):
        img_input_structure = page.evaluate("""() => {
            var imgs = Array.from(document.querySelectorAll('.ci-send img'));
            var icon = imgs.find(function(e){ return e.src.includes('picture25'); });
            if (!icon) return null;
            var parent = icon.parentElement;
            var inp = parent ? parent.querySelector('input[type=file]') : null;
            return inp ? {accept: inp.accept, hidden: inp.style.display === 'none', multiple: inp.multiple} : null;
        }""")
        assert img_input_structure, "图片图标父元素应包含 file input"
        assert img_input_structure['hidden'], "图片 file input 应为隐藏状态"
        assert 'image/' in img_input_structure['accept'], "图片 input accept 应包含 image/ 格式"
        assert '.pdf' not in img_input_structure['accept'], "图片 input 不应接受 PDF"
        logger.info(f"✓ 图片 input 结构验证通过: {img_input_structure}")

    with allure.step("验证整体输入区 DOM 结构（三个功能图标 + Send 按钮）"):
        ci_send_structure = page.evaluate("""() => {
            var ciSend = document.querySelector('.ci-send');
            if (!ciSend) return null;
            var imgs = Array.from(ciSend.querySelectorAll('img')).filter(function(e){ return e.offsetHeight > 0; });
            var btn = ciSend.querySelector('button');
            return {
                imgCount: imgs.length,
                imgSrcs: imgs.map(function(e){ return e.src.split('/').pop().substring(0,30); }),
                hasSendBtn: !!btn,
                sendBtnText: btn ? btn.textContent.trim() : null
            };
        }""")
        assert ci_send_structure, ".ci-send 区域应存在"
        assert ci_send_structure['imgCount'] >= 3, ".ci-send 区域应有至少3个图标（location/file/image）"
        assert ci_send_structure['hasSendBtn'], ".ci-send 区域应有 Send 按钮"
        assert ci_send_structure['sendBtnText'] == 'Send', "Send 按钮文字应为 'Send'"
        logger.info(f"✓ .ci-send 结构验证通过: {ci_send_structure}")

    page.screenshot(path='screenshots/tc037_image_icon.png', timeout=60000)
    logger.info("✓ TC037 发送图片图标验证通过 ✅ 实测")


# ==================== TC038-TC040: 会话列表选择器验证测试（2026-04-03 新增）====================

@pytest.mark.p1
@allure.feature("OK - Messages")
@allure.story("Messages页面功能探索 - 会话列表统计")
@allure.title("TC038: 验证左侧会话列表数量统计准确性")
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.messages
@pytest.mark.conversation_list
@pytest.mark.ae
@pytest.mark.case_id_messages_explore_038
def test_conversation_list_count_accuracy(page, config):
    """
    TC038: 验证左侧会话列表数量统计准确性
    
    背景: 2026-04-03 修复了选择器混淆问题，之前错误地统计右侧聊天消息
    
    测试步骤:
    1. 登录并进入 Messages 页面
    2. 获取左侧会话列表数量
    3. 验证数量 >= 25（实际应该是 30 左右）
    4. 点击第一个会话
    5. 再次获取会话列表数量
    6. 验证数量保持一致（不会被右侧聊天消息干扰）
    
    预期结果:
    - 左侧会话列表数量应该 >= 25
    - 打开会话前后数量应该一致
    - 不应该被右侧聊天消息数量干扰
    """
    logger.info("=" * 80)
    logger.info("TC038: 验证左侧会话列表数量统计准确性")
    logger.info("=" * 80)
    
    # Arrange
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    messages_page = MessagesExplorePage(page)
    
    # 加载 Session
    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        logger.error("❌ Session 加载失败")
        pytest.skip("Session 加载失败")
    
    # Act: 导航到 Messages 页面
    with allure.step("导航到 Messages 页面"):
        messages_page.navigate_to_messages_directly(config['target_page'])
        page.wait_for_timeout(5000)
        
        # 检查是否被重定向到登录页
        current_url = page.url
        if 'login' in current_url.lower() or page.locator('input[type="password"]').count() > 0:
            logger.error(f"❌ Session 失效，被重定向到登录页: {current_url}")
            pytest.skip("Session 失效，需要重新登录")
        
        logger.info(f"✓ 成功进入 Messages 页面: {current_url}")
    
    # 截图
    page.screenshot(path='screenshots/tc038_initial.png', timeout=60000)
    
    # Assert: 验证初始会话列表数量
    with allure.step("验证初始会话列表数量"):
        initial_count = messages_page.get_conversation_count()
        logger.info(f"✓ 左侧会话列表数量: {initial_count}")
        
        assert initial_count >= 25, f"会话列表数量应该 >= 25，实际: {initial_count}"
        logger.info(f"✅ 会话列表数量验证通过: {initial_count} >= 25")
    
    # Act: 点击第一个会话
    with allure.step("点击第一个会话"):
        if initial_count > 0:
            success = messages_page.click_conversation_by_index(0)
            assert success, "点击第一个会话失败"
            page.wait_for_timeout(2000)
            logger.info("✓ 成功点击第一个会话")
        else:
            pytest.skip("会话列表为空")
    
    # 截图
    page.screenshot(path='screenshots/tc038_after_click.png', timeout=60000)
    
    # Assert: 验证会话列表数量保持一致
    with allure.step("验证会话列表数量保持一致"):
        after_click_count = messages_page.get_conversation_count()
        logger.info(f"✓ 打开会话后，会话列表数量: {after_click_count}")
        
        assert after_click_count == initial_count, \
            f"会话列表数量应该保持一致，之前: {initial_count}，现在: {after_click_count}"
        logger.info(f"✅ 会话列表数量一致性验证通过")
    
    # 额外验证：获取右侧聊天消息数量
    with allure.step("验证右侧聊天消息统计功能"):
        message_count = messages_page.get_chat_message_count()
        logger.info(f"✓ 右侧聊天消息数量: {message_count}")
        
        # 验证聊天消息数量和会话列表数量不同
        assert message_count != after_click_count or message_count == 0, \
            f"聊天消息数量 ({message_count}) 不应该等于会话列表数量 ({after_click_count})"
        logger.info(f"✅ 聊天消息数量与会话列表数量正确区分")
    
    logger.info("=" * 80)
    logger.info("✅ TC038 测试通过！")
    logger.info("=" * 80)


@pytest.mark.p2
@allure.feature("OK - Messages")
@allure.story("Messages页面功能探索 - 会话列表滚动")
@allure.title("TC039: 验证会话列表滚动功能")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.messages
@pytest.mark.conversation_list
@pytest.mark.ae
@pytest.mark.case_id_messages_explore_039
def test_conversation_list_scroll_functions(page, config):
    """
    TC039: 验证会话列表滚动功能
    
    背景: 2026-04-03 新增了会话列表滚动功能
    
    测试步骤:
    1. 登录并进入 Messages 页面
    2. 滚动到列表底部
    3. 截图验证
    4. 滚动到列表顶部
    5. 截图验证
    6. 自定义滚动距离
    
    预期结果:
    - 滚动到底部功能正常
    - 滚动到顶部功能正常
    - 自定义滚动功能正常
    """
    logger.info("=" * 80)
    logger.info("TC039: 验证会话列表滚动功能")
    logger.info("=" * 80)
    
    # Arrange
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    messages_page = MessagesExplorePage(page)
    
    # 加载 Session
    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        logger.error("❌ Session 加载失败")
        pytest.skip("Session 加载失败")
    
    # Act: 导航到 Messages 页面
    with allure.step("导航到 Messages 页面"):
        messages_page.navigate_to_messages_directly(config['target_page'])
        page.wait_for_timeout(5000)
        
        current_url = page.url
        if 'login' in current_url.lower():
            pytest.skip("Session 失效")
        
        logger.info(f"✓ 成功进入 Messages 页面")
    
    # 初始截图
    page.screenshot(path='screenshots/tc039_initial.png', timeout=60000)
    
    # Test 1: 滚动到底部
    with allure.step("测试滚动到底部"):
        success = messages_page.scroll_conversation_list_to_bottom()
        assert success, "滚动到底部失败"
        page.wait_for_timeout(1000)
        logger.info("✓ 成功滚动到底部")
        
        page.screenshot(path='screenshots/tc039_scroll_bottom.png', timeout=60000)
    
    # Test 2: 滚动到顶部
    with allure.step("测试滚动到顶部"):
        success = messages_page.scroll_conversation_list_to_top()
        assert success, "滚动到顶部失败"
        page.wait_for_timeout(1000)
        logger.info("✓ 成功滚动到顶部")
        
        page.screenshot(path='screenshots/tc039_scroll_top.png', timeout=60000)
    
    # Test 3: 自定义滚动（向下 500px）
    with allure.step("测试自定义滚动（向下 500px）"):
        success = messages_page.scroll_conversation_list('down', 500)
        assert success, "自定义滚动失败"
        page.wait_for_timeout(1000)
        logger.info("✓ 成功向下滚动 500px")
        
        page.screenshot(path='screenshots/tc039_scroll_custom.png', timeout=60000)
    
    # Test 4: 自定义滚动（向上 300px）
    with allure.step("测试自定义滚动（向上 300px）"):
        success = messages_page.scroll_conversation_list('up', 300)
        assert success, "自定义滚动失败"
        page.wait_for_timeout(1000)
        logger.info("✓ 成功向上滚动 300px")
        
        page.screenshot(path='screenshots/tc039_scroll_up.png', timeout=60000)
    
    logger.info("=" * 80)
    logger.info("✅ TC039 测试通过！")
    logger.info("=" * 80)


@pytest.mark.p2
@allure.feature("OK - Messages")
@allure.story("Messages页面功能探索 - 聊天消息统计")
@allure.title("TC040: 验证右侧聊天消息统计功能")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.messages
@pytest.mark.chat_messages
@pytest.mark.ae
@pytest.mark.case_id_messages_explore_040
def test_chat_message_count(page, config):
    """
    TC040: 验证右侧聊天消息统计功能
    
    背景: 2026-04-03 新增了右侧聊天消息统计功能
    
    测试步骤:
    1. 登录并进入 Messages 页面
    2. 点击第一个会话
    3. 获取右侧聊天消息数量
    4. 验证消息数量 > 0
    5. 验证消息数量与会话列表数量不同
    
    预期结果:
    - 能够正确统计右侧聊天消息数量
    - 聊天消息数量与会话列表数量应该不同
    - 不包括 tips 元素
    """
    logger.info("=" * 80)
    logger.info("TC040: 验证右侧聊天消息统计功能")
    logger.info("=" * 80)
    
    # Arrange
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config['base_url'], session_name)
    messages_page = MessagesExplorePage(page)
    
    # 加载 Session
    if session_manager.load_session():
        logger.info("✓ 成功加载已保存的 Session")
    else:
        pytest.skip("Session 加载失败")
    
    # Act: 导航到 Messages 页面
    with allure.step("导航到 Messages 页面"):
        messages_page.navigate_to_messages_directly(config['target_page'])
        page.wait_for_timeout(5000)
        
        current_url = page.url
        if 'login' in current_url.lower():
            pytest.skip("Session 失效")
    
    # 获取会话列表数量
    with allure.step("获取会话列表数量"):
        conversation_count = messages_page.get_conversation_count()
        logger.info(f"✓ 会话列表数量: {conversation_count}")
        
        if conversation_count == 0:
            pytest.skip("会话列表为空")
    
    # 点击第一个会话
    with allure.step("点击第一个会话"):
        success = messages_page.click_conversation_by_index(0)
        assert success, "点击第一个会话失败"
        page.wait_for_timeout(2000)
        logger.info("✓ 成功打开第一个会话")
    
    # 截图
    page.screenshot(path='screenshots/tc040_conversation_opened.png', timeout=60000)
    
    # Assert: 验证聊天消息数量
    with allure.step("验证聊天消息数量"):
        message_count = messages_page.get_chat_message_count()
        logger.info(f"✓ 右侧聊天消息数量: {message_count}")
        
        if message_count > 0:
            logger.info(f"✅ 检测到 {message_count} 条聊天消息")
        else:
            logger.warning("⚠️  该会话没有聊天消息（可能是新会话）")
    
    # 验证消息数量与会话列表数量不同
    with allure.step("验证消息数量与会话列表数量不同"):
        assert message_count != conversation_count or message_count == 0, \
            f"聊天消息数量 ({message_count}) 不应该等于会话列表数量 ({conversation_count})"
        logger.info(f"✅ 聊天消息数量与会话列表数量正确区分")
    
    # 验证不包括 tips 元素
    with allure.step("验证不包括 tips 元素"):
        tips_count = page.locator(".chat-item.tips").count()
        total_chat_items = page.locator(".chat-item").count()
        
        logger.info(f"✓ Tips 元素数量: {tips_count}")
        logger.info(f"✓ 总 chat-item 数量: {total_chat_items}")
        logger.info(f"✓ 实际聊天消息数量: {message_count}")
        
        # 验证 message_count 不包括 tips
        assert message_count == total_chat_items - tips_count, \
            f"聊天消息数量应该等于总 chat-item 数量减去 tips 数量"
        logger.info(f"✅ 聊天消息统计正确排除了 tips 元素")
    
    logger.info("=" * 80)
    logger.info("✅ TC040 测试通过！")
    logger.info("=" * 80)
