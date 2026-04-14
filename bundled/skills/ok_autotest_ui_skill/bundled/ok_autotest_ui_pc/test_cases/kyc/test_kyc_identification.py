"""
阿联酋站 - KYC 身份认证功能测试

本脚本由 playwright-test-generator 生成
录制文档：docs/KYC_Identity_Verification_Test_Cases_20260303.md
生成时间：2026-03-03

测试站点：AE (https://aepub.58v5.cn)
测试角色：Seller (卖家)
测试目标：验证 KYC 身份认证功能，包括图片 OCR 识别和手动输入表单校验
"""
import pytest
import allure
from pages.login_page import LoginPage
from pages.kyc_identification_page import KycIdentificationPage
from utils.session_manager import SessionManager
from utils.logger import setup_logger

logger = setup_logger()

# ============================================
# 测试环境配置（来自录制文档，录制与运行使用同一账号）
# ============================================
_CONFIG = {
    "site": "ae",                    # 来自文档「站点」
    "site_name": "阿联酋站",          # 来自文档「站点名称」
    "role": "seller",                # 来自文档「角色」
    "user_name": "kyc_ae_seller",    # 来自文档「账号名称」，用于 session 命名
    "base_url": "https://aepub.58v5.cn/biz/en/pay/identification",  # 来自文档「基础URL」- KYC 页面完整地址
    "test_account": {
        "username": "liwenfeng01@58.com",  # 来自文档「测试账号」
        "password": "Liwenfeng01"          # 来自文档「测试密码」
    },
    "locale": "en-US",
    "currency": "AED",
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


@pytest.mark.case_id_kyc_upload_valid_id_01
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.kyc
@pytest.mark.ae
@allure.feature("OK")
@allure.story("KYC 身份认证 - 图片 OCR 识别")
@allure.title("上传有效证件图片 - OCR 成功识别（澳大利亚国民身份证）")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证上传澳大利亚国民身份证图片后，OCR 能够成功识别并自动填充表单字段")
def test_upload_valid_id_ocr_success(page, config):
    """上传有效证件图片 - OCR 成功识别测试"""
    
    # ========== Arrange：准备测试数据和对象 ==========
    login_page = LoginPage(page)
    kyc_page = KycIdentificationPage(page)
    
    # 从 config 读取测试数据
    site = config['site']
    role = config['role']
    account_name = config['user_name']
    base_url = config['base_url']
    username = config['test_account']['username']
    password = config['test_account']['password']
    
    # 测试图片路径
    test_image_path = r"D:\58code\58code\ok_autotest_ui_pc\test_data\images\Australia_a_1.jpeg"
    
    # 记录测试配置
    logger.info("="*80)
    logger.info("阿联酋站 - KYC 身份认证 - 上传有效证件图片测试")
    logger.info("="*80)
    logger.info(f"站点: {site.upper()} (阿联酋站)")
    logger.info(f"角色: {role.upper()} (卖家)")
    logger.info(f"账号: {account_name}")
    logger.info(f"邮箱: {username}")
    logger.info(f"测试图片: {test_image_path}")
    logger.info("="*80)
    
    # ========== Session 复用机制：尝试加载已有登录状态 ==========
    session_manager = SessionManager(page, base_url, session_name=f"{site}_{role}_{account_name}")
    session_loaded = False
    
    with allure.step("尝试加载已保存的 Session"):
        session_loaded = session_manager.load_session()
        if session_loaded:
            logger.info("✓ 成功加载已保存的 Session")
            # 必须先访问页面，Cookie 才会生效，才能验证登录状态
            page.goto(base_url, timeout=30000)
            page.wait_for_timeout(2000)
            try:
                login_page.handle_cookie_popup()
            except Exception:
                pass
            # 验证是否已登录（检查右上角是否显示用户名）
            try:
                is_logged_in = page.get_by_text("liwenfeng01").is_visible(timeout=3000)
                if is_logged_in:
                    logger.info("✓ Session 有效，已登录状态")
                    logger.info("✅ 跳过登录步骤，直接进入测试！")
                else:
                    logger.info("⚠️ Session 已过期，需要重新登录")
                    session_loaded = False
            except Exception:
                logger.info("⚠️ Session 验证失败，需要重新登录")
                session_loaded = False
        else:
            logger.info("⚠️ 未找到已保存的 Session，需要执行登录")
    
    # ========== Act 阶段1：执行登录操作（仅在 Session 无效时执行）==========
    if not session_loaded:
        with allure.step("步骤1：直接访问 KYC 认证页面（未登录会自动跳转登录）"):
            logger.info("开始登录流程")
            page.goto(base_url, timeout=30000)
            page.wait_for_timeout(2000)
            logger.info("✓ 访问 KYC 页面")
        
        # 检查是否需要登录（录制：弹窗自动出现，包含 Email or phone number 输入框）
        with allure.step("步骤2：检查登录状态"):
            try:
                if page.get_by_role("textbox", name="Email or phone number").is_visible(timeout=5000):
                    logger.info("检测到登录弹窗，开始登录流程")
                    
                    with allure.step("步骤3：处理Cookie弹窗"):
                        login_page.handle_cookie_popup()
                        logger.info("✓ 已处理Cookie弹窗（如果存在）")
                    
                    with allure.step(f"步骤4：在登录弹窗中输入邮箱 {username}"):
                        page.get_by_role("textbox", name="Email or phone number").fill(username)
                        page.get_by_role("button", name="Continue").click()
                        page.wait_for_timeout(2000)
                        logger.info("✓ 输入邮箱完成")
                    
                    with allure.step("步骤5：输入密码并点击Log in"):
                        page.get_by_role("textbox", name="Enter password").fill(password)
                        page.get_by_role("button", name="Log in").click()
                        page.wait_for_timeout(3000)
                        logger.info("✓ 输入密码完成")
                    
                    with allure.step("验证登录成功"):
                        page.wait_for_load_state("domcontentloaded", timeout=10000)
                        logger.info("✅ 登录成功！")
                    
                    with allure.step("保存 Session"):
                        if session_manager.save_session():
                            logger.info("✓ Session 已保存，下次测试将自动复用")
                    
                    # 登录后重新访问 KYC 页面
                    with allure.step("步骤6：重新访问 KYC 认证页面"):
                        page.goto(base_url, timeout=30000)
                        page.wait_for_timeout(2000)
                        logger.info("✓ 重新进入 KYC 认证引导页")
                else:
                    logger.info("✓ 已登录状态，无需登录")
            except Exception as e:
                logger.error(f"登录检查失败: {e}")
                # 继续执行，可能已经在 KYC 页面
                pass
    
    # ========== Act 阶段2：点击 Begin 按钮 ==========
    with allure.step("步骤7：点击 Begin 按钮"):
        # 检查是否在引导页（有 Begin 按钮）
        try:
            if page.get_by_role("button", name="Begin").is_visible(timeout=3000):
                kyc_page.click_begin_button()
                page.wait_for_timeout(1000)
                logger.info("✓ 点击 Begin 按钮，进入上传页面")
            else:
                logger.info("✓ 已经在上传页面，无需点击 Begin")
        except Exception:
            logger.info("✓ 已经在上传页面，无需点击 Begin")
    
    # ========== Act 阶段3：上传有效证件图片 ==========
    with allure.step(f"步骤8：上传澳大利亚国民身份证图片"):
        kyc_page.upload_document_image(test_image_path)
        logger.info(f"✓ 上传图片: {test_image_path}")
        logger.info("✓ 等待 OCR 识别完成...")
    
    # ========== Assert：验证 OCR 识别结果 ==========
    with allure.step("验证 OCR 识别成功并正确填充表单"):
        # 验证表单弹窗已显示
        assert kyc_page.is_form_dialog_visible(), "表单弹窗未显示"
        logger.info("✓ 表单弹窗已显示")
        
        # 验证图片缩略图已显示
        assert kyc_page.is_upload_thumbnail_visible(), "上传的图片缩略图未显示"
        logger.info("✓ 图片缩略图已显示")
        
        # 验证 Document Type
        doc_type = kyc_page.get_document_type_value()
        assert "National ID" in doc_type, f"Document Type 识别错误，期望包含 'National ID'，实际: {doc_type}"
        logger.info(f"✓ Document Type 识别正确: {doc_type}")
        
        # 验证 Document Number
        doc_number = kyc_page.get_document_number_value()
        assert doc_number == "007464732", f"Document Number 识别错误，期望 '007464732'，实际: {doc_number}"
        logger.info(f"✓ Document Number 识别正确: {doc_number}")
        
        # 验证 First Name
        first_name = kyc_page.get_first_name_value()
        assert first_name == "SALLY", f"First Name 识别错误，期望 'SALLY'，实际: {first_name}"
        logger.info(f"✓ First Name 识别正确: {first_name}")
        
        # 验证 Last Name
        last_name = kyc_page.get_last_name_value()
        assert last_name == "MALLETT", f"Last Name 识别错误，期望 'MALLETT'，实际: {last_name}"
        logger.info(f"✓ Last Name 识别正确: {last_name}")
    
    logger.info("="*80)
    logger.info("✅ TC001 - 上传有效证件图片 OCR 识别测试全部通过！")
    logger.info("="*80)


@pytest.mark.case_id_kyc_upload_invalid_image_02
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.kyc
@pytest.mark.ae
@allure.feature("OK")
@allure.story("KYC 身份认证 - 图片 OCR 识别")
@allure.title("上传无效图片 - OCR 识别失败（风景照片）")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证上传非证件图片（风景照片）后，OCR 识别失败，所有字段为空，用户可以手动填写")
def test_upload_invalid_image_ocr_fail(page, config):
    """上传无效图片 - OCR 识别失败测试"""
    
    # ========== Arrange：准备测试数据和对象 ==========
    login_page = LoginPage(page)
    kyc_page = KycIdentificationPage(page)
    
    # 从 config 读取测试数据
    site = config['site']
    role = config['role']
    account_name = config['user_name']
    username = config['test_account']['username']
    
    # 测试图片路径（风景照片）
    test_image_path = r"D:\58code\58code\ok_autotest_ui_pc\test_data\images\图片1.png"
    
    # 记录测试配置
    logger.info("="*80)
    logger.info("阿联酋站 - KYC 身份认证 - 上传无效图片测试")
    logger.info("="*80)
    logger.info(f"站点: {site.upper()} (阿联酋站)")
    logger.info(f"角色: {role.upper()} (卖家)")
    logger.info(f"账号: {account_name}")
    logger.info(f"邮箱: {username}")
    logger.info(f"测试图片: {test_image_path}")
    logger.info("="*80)
    
    # ========== Session 复用：直接使用已保存的登录状态 ==========
    base_url = config['base_url']
    session_manager = SessionManager(page, base_url, session_name=f"{site}_{role}_{account_name}")
    
    with allure.step("加载已保存的 Session"):
        session_loaded = session_manager.load_session()
        if session_loaded:
            logger.info("✓ 成功加载已保存的 Session")
            logger.info("✅ 跳过登录步骤！")
        else:
            logger.info("⚠️ Session 加载失败，请先运行 TC001 完成登录")
            pytest.skip("需要先运行 TC001 完成登录并保存 Session")
    
    # ========== Act 阶段1：访问 KYC 认证页面 ==========
    with allure.step("步骤1：访问 KYC 认证页面"):
        page.goto(base_url, timeout=30000)
        page.wait_for_timeout(2000)
        logger.info("✓ 访问 KYC 认证页面")
    
    with allure.step("步骤2：点击 Begin 按钮（如果在引导页）"):
        try:
            if page.get_by_role("button", name="Begin").is_visible(timeout=3000):
                kyc_page.click_begin_button()
                page.wait_for_timeout(1000)
                logger.info("✓ 点击 Begin 按钮，进入上传页面")
            else:
                logger.info("✓ 已经在上传页面")
        except Exception:
            logger.info("✓ 已经在上传页面")
    
    # ========== Act 阶段2：上传无效图片（风景照片）==========
    with allure.step(f"步骤3：上传风景照片"):
        kyc_page.upload_document_image(test_image_path)
        logger.info(f"✓ 上传图片: {test_image_path}")
        logger.info("✓ 等待 OCR 识别完成...")
    
    # ========== Assert：验证 OCR 识别失败 ==========
    with allure.step("验证 OCR 识别失败，所有字段为空"):
        # 验证表单弹窗已显示
        assert kyc_page.is_form_dialog_visible(), "表单弹窗未显示"
        logger.info("✓ 表单弹窗已显示")
        
        # 验证图片缩略图已显示
        assert kyc_page.is_upload_thumbnail_visible(), "上传的图片缩略图未显示"
        logger.info("✓ 图片缩略图已显示（风景照片）")
        
        # 验证 Document Type 为空（显示占位符）
        doc_type = kyc_page.get_document_type_value()
        assert doc_type == "Document Type", f"Document Type 应为空（占位符），实际: {doc_type}"
        logger.info(f"✓ Document Type 为空（占位符文字）: {doc_type}")
        
        # 验证 Document Number 为空
        doc_number = kyc_page.get_document_number_value()
        assert doc_number == "", f"Document Number 应为空，实际: {doc_number}"
        logger.info("✓ Document Number 为空")
        
        # 验证 First Name 为空
        first_name = kyc_page.get_first_name_value()
        assert first_name == "", f"First Name 应为空，实际: {first_name}"
        logger.info("✓ First Name 为空")
        
        # 验证 Last Name 为空
        last_name = kyc_page.get_last_name_value()
        assert last_name == "", f"Last Name 应为空，实际: {last_name}"
        logger.info("✓ Last Name 为空")
    
    logger.info("="*80)
    logger.info("✅ TC002 - 上传无效图片 OCR 识别失败测试全部通过！")
    logger.info("="*80)


@pytest.mark.case_id_kyc_submit_empty_form_04
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.kyc
@pytest.mark.ae
@allure.feature("OK")
@allure.story("KYC 身份认证 - 表单校验")
@allure.title("提交空表单 - 所有必填字段校验")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证不填写任何字段直接提交表单时，所有必填字段显示错误提示 'Cannot be empty'")
def test_submit_empty_form_validation(page, config):
    """提交空表单 - 所有必填字段校验测试"""
    
    # ========== Arrange：准备测试数据和对象 ==========
    login_page = LoginPage(page)
    kyc_page = KycIdentificationPage(page)
    
    # 从 config 读取测试数据
    site = config['site']
    role = config['role']
    account_name = config['user_name']
    username = config['test_account']['username']
    
    # 记录测试配置
    logger.info("="*80)
    logger.info("阿联酋站 - KYC 身份认证 - 提交空表单校验测试")
    logger.info("="*80)
    logger.info(f"站点: {site.upper()} (阿联酋站)")
    logger.info(f"角色: {role.upper()} (卖家)")
    logger.info(f"账号: {account_name}")
    logger.info(f"邮箱: {username}")
    logger.info("="*80)
    
    # ========== Session 复用：直接使用已保存的登录状态 ==========
    base_url = config['base_url']
    session_manager = SessionManager(page, base_url, session_name=f"{site}_{role}_{account_name}")
    
    with allure.step("加载已保存的 Session"):
        session_loaded = session_manager.load_session()
        if session_loaded:
            logger.info("✓ 成功加载已保存的 Session")
            logger.info("✅ 跳过登录步骤！")
        else:
            logger.info("⚠️ Session 加载失败，请先运行 TC001 完成登录")
            pytest.skip("需要先运行 TC001 完成登录并保存 Session")
    
    # ========== Act 阶段1：访问 KYC 认证页面 ==========
    with allure.step("步骤1：访问 KYC 认证页面"):
        page.goto(base_url, timeout=30000)
        page.wait_for_timeout(2000)
        logger.info("✓ 访问 KYC 认证页面")
    
    with allure.step("步骤2：点击 Begin 按钮（如果在引导页）"):
        try:
            if page.get_by_role("button", name="Begin").is_visible(timeout=3000):
                kyc_page.click_begin_button()
                page.wait_for_timeout(1000)
                logger.info("✓ 点击 Begin 按钮，进入上传页面")
            else:
                logger.info("✓ 已经在上传页面")
        except Exception:
            logger.info("✓ 已经在上传页面")
    
    # ========== Act 阶段2：点击 Enter Manually 打开手动输入表单 ==========
    with allure.step("步骤3：点击 Enter Manually 链接"):
        kyc_page.click_enter_manually()
        logger.info("✓ 点击 Enter Manually，打开手动输入表单")
    
    # ========== Act 阶段3：不填写任何字段，直接提交 ==========
    with allure.step("步骤4：不填写任何字段，直接点击 Submit 按钮"):
        kyc_page.click_submit_button()
        logger.info("✓ 点击 Submit 按钮（未填写任何字段）")
        page.wait_for_timeout(1000)
    
    # ========== Assert：验证所有必填字段显示错误提示 ==========
    with allure.step("验证所有必填字段显示错误提示 'Cannot be empty'"):
        # 验证表单弹窗仍然显示（提交被阻止）
        assert kyc_page.is_form_dialog_visible(), "表单弹窗应该仍然显示（提交被阻止）"
        logger.info("✓ 表单弹窗仍然显示，提交被阻止")
        
        # 验证是否显示错误提示
        assert kyc_page.is_field_error_visible("Cannot be empty"), "未显示必填字段错误提示"
        logger.info("✓ 显示必填字段错误提示")
        
        # 获取所有错误提示
        error_messages = kyc_page.get_all_error_messages()
        error_count = len(error_messages)
        
        # 验证至少有 6 个必填字段显示错误（Document Type, Document Number, Issuing Country, Date of Birth, First Name, Last Name）
        assert error_count >= 6, f"必填字段错误提示数量不足，期望 >= 6，实际: {error_count}"
        logger.info(f"✓ 必填字段错误提示数量: {error_count} 条")
        logger.info(f"✓ 错误提示文案: 'Cannot be empty'")
    
    logger.info("="*80)
    logger.info("✅ TC004 - 提交空表单校验测试全部通过！")
    logger.info("="*80)
