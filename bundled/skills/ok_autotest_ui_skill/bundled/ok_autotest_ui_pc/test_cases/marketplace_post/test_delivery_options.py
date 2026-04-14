"""
OK Marketplace - Delivery Options 测试（基于MCP录制生成）

测试范围：配送选项选择、完整提交流程
测试站点：AE (https://aepub.58v5.cn)
测试目标：验证 Marketplace 发布页面的 Delivery Options 功能
基于：2026-03-02 MCP Playwright录制 - TC011和TC012

浏览器：本模块内覆盖父级 `page` fixture（scope=module），保证 TC011/TC012/TC013
        共用同一浏览器实例，模块结束后关闭。
"""
import os
import re
import pytest
import allure
from datetime import datetime
from pathlib import Path
from pages.login_page import LoginPage
from pages.marketplace_post_page import MarketplacePostPage
from utils.logger import setup_logger

logger = setup_logger()


@pytest.fixture(scope="module")
def page(config):
    """
    本文件专用：模块级浏览器，与 test_cases/conftest 行为一致，
    显式覆盖父级 fixture，避免上游改为 function scope 时本模块多开窗口。
    """
    from utils.browser_manager import BrowserManager

    browser_manager = BrowserManager()
    pg = browser_manager.start_browser(
        browser_type=config["browser"]["type"],
        headless=config["browser"]["headless"],
        base_url=config["base_url"],
        viewport=config["browser"]["viewport"],
    )
    browser_manager.mark_in_use()

    if os.environ.get("DEBUG_PAUSE", "").lower() in ("1", "true", "yes"):
        try:
            pg.pause()
        except Exception:
            pass

    yield pg

    browser_manager.mark_released()
    if os.environ.get("KEEP_BROWSER_OPEN", "").lower() not in ("1", "true", "yes"):
        browser_manager.close_browser(pg)


def ensure_ae_logged_in(page, config, failure_screenshot="debug_login_failed.png"):
    """
    导航到 AE 首页并确保已登录；若模块内上一用例已登录则跳过账号流程。
    """
    login_page = LoginPage(page)
    logger.info("确保登录态: 打开首页并检查 session")
    login_page.navigate_to_home_page(base_url=config["base_url"])
    page.wait_for_timeout(2000)
    login_page.handle_cookie_popup()
    page.wait_for_timeout(500)
    if login_page.is_login_button_text_changed(timeout=8000):
        logger.info(f"✓ 已登录，跳过登录: {config['test_account']['username']}")
        return
    try:
        login_page.login(
            email=config["test_account"]["username"],
            password=config["test_account"]["password"],
        )
        logger.info(f"✓ 登录成功: {config['test_account']['username']}")
    except Exception as e:
        logger.error(f"❌ 登录失败: {e}")
        try:
            page.screenshot(path=failure_screenshot, timeout=60000)
        except Exception:
            pass
        raise


def wait_for_delivery_options_section(page, timeout=15000):
    """
    等待配送选项区域渲染。页面未必展示英文标题「Delivery Options」，
    改为等待任一典型选项段落（与页面对象选择器一致）。
    """
    logger.info("等待配送选项区域加载...")
    marker = page.get_by_role("paragraph").filter(
        has_text=re.compile(
            r"Seller pays for postage|Buyer pays for postage|Arrange pickup with the buyer",
            re.I,
        )
    ).first
    marker.wait_for(state="visible", timeout=timeout)
    logger.info("✓ 配送选项区域已显示（按选项文案检测）")


# ========== 测试环境配置 ==========
_CONFIG = {
    "site": "ae",
    "site_name": "AE站",
    "role": "seller",
    "user_name": "test_seller_ae",
    "base_url": "https://ae.58v5.cn/en/city-abu-dhabi/",
    "test_account": {
        "username": "wangyongli@58.com",
        "password": "Qwer1234"
    },
    "target_page": "https://aepub.58v5.cn/biz/en/publish/classified",
    "browser": {
        "type": "chromium",
        "headless": False,
        "viewport": {"width": 1920, "height": 1080}
    }
}

# 测试图片目录
IMAGE_DIR = Path("test_data/images")

# 发帖 Title 末尾 aitest 标识（便于列表/后台识别自动化数据）
POST_TITLE_AITEST_SUFFIX = " aitest"


@pytest.mark.case_id_delivery_tc011
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.marketplace
@pytest.mark.ae
@allure.feature("OK")
@allure.story("Delivery Options")
@allure.title("TC011: 选择 'Seller pays for postage' 完整提交应该成功")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
验证选择 "Seller pays for postage" 配送选项后能够成功提交帖子

前置条件：
- 已登录
- 所有必填字段已填写（Pictures、Title、Description、Category、Price、Location）

执行步骤：
1. 在 Delivery Options 区域，点击 "Seller pays for postage" 选项
2. 观察该选项是否被选中（高亮或勾选标记）
3. 点击 "Post" 按钮
4. 观察提交结果

预期结果：
- "Seller pays for postage" 被选中
- 提交成功，页面跳转到成功页（https://aepub.58v5.cn/biz/en/publish/success?id=xxxxx）
- 显示 "Post Submitted!" 成功提示
""")
def test_tc011_seller_pays_postage(page, config):
    """TC011: 选择 'Seller pays for postage' 完整提交"""
    
    # ========== Arrange：准备测试数据和对象 ==========
    post_page = MarketplacePostPage(page)
    
    logger.info("="*80)
    logger.info("TC011: 选择 'Seller pays for postage' 完整提交")
    logger.info("="*80)
    
    # 查找测试图片
    test_images = list(IMAGE_DIR.glob("*.png"))
    if not test_images:
        pytest.skip("测试图片目录中没有图片文件")
    
    test_image = str(test_images[0].absolute())
    logger.info(f"测试图片: {test_image}")
    
    # 测试数据（添加时间戳和Delivery Options类型标识）
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_data = {
        "title": f"iPhone 14 Pro Max - Seller Pays Postage - {timestamp}{POST_TITLE_AITEST_SUFFIX}",
        "description": "Brand new iPhone 14 Pro Max with 256GB storage. Test delivery option: Seller pays for postage.",
        "price": "3500"
    }
    
    # ========== Act：执行测试步骤 ==========
    
    # 步骤0: 登录（模块内复用浏览器与 session，已登录则跳过）
    logger.info("步骤0: 登录")
    ensure_ae_logged_in(page, config, failure_screenshot="debug_login_failed.png")
    
    # 步骤1: 导航到发布页面
    logger.info("步骤1: 导航到发布页面")
    post_page.navigate_to_publish_page()
    
    # 步骤2: 上传图片
    logger.info(f"步骤2: 上传图片 - {test_image}")
    post_page.upload_single_image(test_image)
    
    # 等待图片上传完成（关键：等待足够时间让图片完全上传并显示建议分类）
    logger.info("等待图片上传完成并显示分类建议...")
    page.wait_for_timeout(3000)
    
    # 验证图片计数器
    try:
        post_page.wait_for_image_counter("1/9", timeout=5000)
        logger.info("✓ 图片上传成功，计数器显示 1/9")
    except Exception as e:
        logger.warning(f"图片计数器验证失败: {e}")
    
    # 步骤3: 选择Category - Cell Phones → Apple
    logger.info("步骤3: 选择分类 - Cell Phones → Apple")
    
    # 先保存页面HTML以便调试
    page_html = page.content()
    with open("debug_page_after_upload.html", "w", encoding="utf-8") as f:
        f.write(page_html)
    logger.info("✓ 已保存页面HTML: debug_page_after_upload.html")
    
    # 保存截图
    page.screenshot(path="debug_before_category_selection.png", full_page=True, timeout=60000)
    logger.info("✓ 已保存完整截图: debug_before_category_selection.png")
    
    post_page.select_category_cell_phones_apple()
    wait_for_delivery_options_section(page)
    page.wait_for_timeout(500)
    
    # 步骤4: 填写必填字段
    logger.info("步骤4: 填写Title、Description、Price")
    post_page.fill_title(test_data["title"])
    page.wait_for_timeout(500)
    post_page.fill_description(test_data["description"])
    page.wait_for_timeout(500)
    post_page.fill_price(test_data["price"])
    page.wait_for_timeout(500)
    
    # 步骤5: 选择 Delivery Option - Seller pays for postage（TC011核心步骤）
    logger.info("步骤5: 选择 Delivery Option - Seller pays for postage")
    post_page.select_seller_pays_postage()
    
    # 步骤6: 点击Post按钮提交
    logger.info("步骤6: 点击Post按钮提交")
    post_page.click_post_button()
    
    # ========== Assert：验证结果 ==========
    logger.info("验证: 检查是否成功跳转到成功页")
    assert post_page.verify_success_page(), "提交失败，未跳转到成功页面"
    
    logger.info("✅ TC011测试通过: 'Seller pays for postage' 选项提交成功")


@pytest.mark.case_id_delivery_tc012
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.marketplace
@pytest.mark.ae
@allure.feature("OK")
@allure.story("Delivery Options")
@allure.title("TC012: 选择 'Buyer pays for postage' 完整提交应该成功")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
验证选择 "Buyer pays for postage" 配送选项后能够成功提交帖子

前置条件：
- 已登录
- 所有必填字段已填写（Pictures、Title、Description、Category、Price、Location）

执行步骤：
1. 在 Delivery Options 区域，点击 "Buyer pays for postage" 选项
2. 观察该选项是否被选中
3. 点击 "Post" 按钮
4. 观察提交结果

预期结果：
- "Buyer pays for postage" 被选中
- 提交成功，页面跳转到成功页
- 显示 "Post Submitted!" 成功提示
""")
def test_tc012_buyer_pays_postage(page, config):
    """TC012: 选择 'Buyer pays for postage' 完整提交"""
    
    # ========== Arrange：准备测试数据和对象 ==========
    post_page = MarketplacePostPage(page)
    
    logger.info("="*80)
    logger.info("TC012: 选择 'Buyer pays for postage' 完整提交")
    logger.info("="*80)
    
    # 查找测试图片
    test_images = list(IMAGE_DIR.glob("*.png"))
    if not test_images:
        pytest.skip("测试图片目录中没有图片文件")
    
    test_image = str(test_images[0].absolute())
    logger.info(f"测试图片: {test_image}")
    
    # 测试数据（添加时间戳和Delivery Options类型标识）
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_data = {
        "title": f"iPhone 14 Pro Max - Buyer Pays Postage - {timestamp}{POST_TITLE_AITEST_SUFFIX}",
        "description": "Brand new iPhone 14 Pro Max with 256GB storage. Test delivery option: Buyer pays for postage.",
        "price": "3500"
    }
    
    # ========== Act：执行测试步骤 ==========
    
    # 步骤1: 登录（模块内复用浏览器与 session，已登录则跳过）
    logger.info("步骤1: 登录")
    ensure_ae_logged_in(page, config, failure_screenshot="debug_tc012_login_failed.png")
    
    # 步骤2: 导航到发布页面
    logger.info("步骤2: 导航到发布页面")
    post_page.navigate_to_publish_page()
    
    # 步骤3: 上传图片
    logger.info(f"步骤3: 上传图片 - {test_image}")
    post_page.upload_single_image(test_image)
    page.wait_for_timeout(4000)
    logger.info("✓ 图片上传完成")
    
    # 步骤4: 选择Category - Cell Phones → Apple
    logger.info("步骤4: 选择分类 - Cell Phones → Apple")
    post_page.select_category_cell_phones_apple()
    wait_for_delivery_options_section(page)
    page.wait_for_timeout(500)
    
    # 步骤5: 填写必填字段
    logger.info("步骤5: 填写Title、Description、Price")
    post_page.fill_title(test_data["title"])
    post_page.fill_description(test_data["description"])
    post_page.fill_price(test_data["price"])
    
    # 步骤6: 选择 Delivery Option - Buyer pays for postage（TC012核心步骤）
    logger.info("步骤6: 选择 Delivery Option - Buyer pays for postage")
    post_page.select_buyer_pays_postage()
    
    # 步骤7: 点击Post按钮提交
    logger.info("步骤7: 点击Post按钮提交")
    post_page.click_post_button()
    
    # ========== Assert：验证结果 ==========
    logger.info("验证: 检查是否成功跳转到成功页")
    assert post_page.verify_success_page(), "提交失败，未跳转到成功页面"
    
    logger.info("✅ TC012测试通过: 'Buyer pays for postage' 选项提交成功")


###############################################################################
# TC013: 选择 "Arrange pickup with the buyer" 完整提交
###############################################################################

@pytest.mark.case_id_delivery_tc013
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.marketplace
@pytest.mark.ae
@allure.feature("OK")
@allure.story("Delivery Options")
@allure.title("TC013: 选择 'Arrange pickup with the buyer' 完整提交")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
验证选择 "Arrange pickup with the buyer" 配送选项后能够成功提交帖子

MCP录制发现：
- "Arrange pickup with the buyer" 是一个 toggle switch（开关），不是 radio button
- 需要点击包含此文本的整个行区域来激活 toggle
- 激活后 toggle 会从灰色（OFF）变为绿色（ON）

前置条件：
- 需要登录
- 所有必填字段已填写（Pictures、Title、Description、Category、Price、Location）

执行步骤：
1. 登录系统
2. 导航到发布页面
3. 上传图片
4. 选择分类 Marketplace → Electronics → Cell Phones → Apple
5. 填写Title、Description、Price
6. 在 Delivery Options 区域，点击 "Arrange pickup with the buyer" toggle开关
7. 点击 "Post" 按钮

预期结果：
- "Arrange pickup with the buyer" toggle被激活
- 提交成功，页面跳转到成功页
- 显示 "Post Submitted!" 成功提示
""")
def test_tc013_arrange_pickup(page, config):
    """
    TC013: 选择 'Arrange pickup with the buyer' 完整提交
    """
    logger.info("=" * 80)
    logger.info("开始执行 TC013: 选择 'Arrange pickup with the buyer' 完整提交")
    logger.info("=" * 80)
    
    post_page = MarketplacePostPage(page)
    
    # ========== 步骤0: 登录（模块内复用浏览器与 session，已登录则跳过）==========
    logger.info("步骤0: 登录")
    ensure_ae_logged_in(page, config, failure_screenshot="debug_tc013_login_failed.png")
    
    # ========== 步骤1: 导航到发布页面 ==========
    logger.info("步骤1: 导航到发布页面")
    post_page.navigate_to_publish_page()
    page.wait_for_timeout(2000)
    logger.info("✓ 已导航到发布页面")
    
    # ========== 步骤2: 上传图片 ==========
    logger.info("步骤2: 上传图片")
    image_path = os.path.join(os.path.dirname(__file__), "../../test_data/images/apple_phone.png")
    post_page.upload_single_image(image_path)
    page.wait_for_timeout(2000)
    logger.info("✓ 图片上传成功")
    
    # ========== 步骤3: 选择分类 - Cell Phones → Apple ==========
    logger.info("步骤3: 选择分类 - Cell Phones → Apple")
    post_page.select_category_cell_phones_apple()
    wait_for_delivery_options_section(page)
    page.wait_for_timeout(500)
    logger.info("✓ 分类选择成功")
    
    # ========== 步骤4: 填写表单 ==========
    logger.info("步骤4: 填写表单")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    post_page.fill_title(
        f"iPhone 14 Pro Max - Arrange Pickup - {timestamp}{POST_TITLE_AITEST_SUFFIX}"
    )
    post_page.fill_description("Brand new iPhone 14 Pro Max with 256GB storage. Test delivery option: Arrange pickup with the buyer.")
    post_page.fill_price("3500")
    page.wait_for_timeout(1000)
    logger.info("✓ 表单填写完成")
    
    # ========== 步骤5: 选择 Delivery Options - Arrange pickup ==========
    logger.info("步骤5: 选择 Delivery Options - Arrange pickup with the buyer")
    post_page.select_arrange_pickup()
    page.wait_for_timeout(1000)
    logger.info("✓ Delivery Options 选择完成")
    
    # ========== 步骤6: 提交 ==========
    logger.info("步骤6: 点击Post按钮提交")
    
    # 提交前截图
    page.screenshot(path="debug_tc013_before_submit.png", timeout=60000)
    logger.info("✓ 已保存提交前截图")
    
    post_page.click_post_button()
    
    # 等待一下，看看有没有错误提示
    page.wait_for_timeout(3000)
    
    # 如果提交失败，截图当前页面状态
    current_url = page.url
    if "success" not in current_url:
        page.screenshot(path="debug_tc013_submit_failed.png", full_page=True, timeout=60000)
        page_html = page.content()
        with open("debug_tc013_submit_failed.html", "w", encoding="utf-8") as f:
            f.write(page_html)
        logger.warning(f"⚠️ 提交后仍停留在: {current_url}")
        logger.info("✓ 已保存失败截图和HTML")
    
    # ========== Assert：验证结果 ==========
    logger.info("验证: 检查是否成功跳转到成功页")
    assert post_page.verify_success_page(), "提交失败，未跳转到成功页面"
    
    logger.info("✅ TC013测试通过: 'Arrange pickup with the buyer' 选项提交成功")
