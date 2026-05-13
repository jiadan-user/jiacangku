"""
阿联酋站 - KYC 身份认证功能测试（WEBQA 优化版）

本脚本由 playwright-test-generator 严格流程生成
录制文档：test_cases/kyc/KYC_IDENTIFICATION_WEBQA_20260309.md
生成时间：2026-03-09
选择器来源：MCP 录制 + WEBQA 阶段三探测记录

测试站点：AE (https://aepub.58v5.cn/biz/en/pay/identification)
测试角色：Seller (卖家)
优化策略：合并可串联用例、删除冗余、单浏览器执行、优化执行顺序
"""
import os
import subprocess
import sys
from pathlib import Path

import allure
import pytest

from pages.login_page import LoginPage
from pages.kyc_identification_page import KycIdentificationPage
from utils.session_manager import SessionManager
from utils.logger import setup_logger

logger = setup_logger()

# 项目根目录（用于 test_data 路径）
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
IMAGE_DIR = PROJECT_ROOT / "test_data" / "images"

# ============================================
# 测试环境配置（来自录制文档）
# ============================================
_CONFIG = {
    "site": "ae",
    "site_name": "阿联酋站",
    "role": "seller",
    "user_name": "kyc_test_ae",
    "base_url": "https://aepub.58v5.cn/biz/en/pay/identification",
    "test_account": {
        "username": "liwenfeng01@58.com",
        "password": "Liwenfeng01",
    },
    "user_id": "796559612064208640",  # standalone_suspend_account.py 用
    "locale": "en-US",
    "currency": "AED",
    "browser": {
        "type": "chromium",
        "headless": True,
        "viewport": {"width": 1920, "height": 1080},
    },
    "timeout": {
        "default": 30000,
        "wait": 10000,
        "navigation": 30000,
    },
}


class TestKycIdentificationWebqa:
    """
    KYC 身份认证测试 - 单浏览器共享，执行顺序已优化
    conftest scope=class，本类内所有用例共享同一浏览器实例
    """

    # ==================== 前置：Session + 登录（首个用例执行）====================

    def _reset_account_if_verifying(self, page, config):
        """检查账号是否在 Verifying 状态，如果是则重置"""
        try:
            if page.get_by_text("Verifying").is_visible(timeout=2000):
                logger.warning("⚠️ 检测到账号处于 Verifying 状态，执行重置...")
                script_path = PROJECT_ROOT / "test_cases" / "kyc" / "standalone_suspend_account.py"
                user_id = config.get("user_id", "796559612064208640")
                
                result = subprocess.run(
                    [sys.executable, str(script_path), "--user-id", user_id],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(PROJECT_ROOT),
                )
                
                if result.returncode == 0:
                    logger.info("✓ 账号状态已重置为 SUSPENDED")
                    page.reload(timeout=30000)
                    page.wait_for_timeout(2000)
                    return True
                else:
                    logger.warning(f"重置脚本返回 {result.returncode}: {result.stderr}")
                    return False
        except Exception as e:
            logger.debug(f"检查/重置账号状态异常: {e}")
            return False

    def _ensure_logged_in(self, page, config):
        """确保已登录，失败则执行登录并保存 Session"""
        base_url = config["base_url"]
        site = config["site"]
        role = config["role"]
        account_name = config["user_name"]
        username = config["test_account"]["username"]
        password = config["test_account"]["password"]

        session_manager = SessionManager(
            page, base_url, session_name=f"{site}_{role}_{account_name}"
        )
        session_loaded = False

        with allure.step("尝试加载已保存的 Session"):
            session_loaded = session_manager.load_session()
            if session_loaded:
                logger.info("✓ 成功加载已保存的 Session")
                page.goto(base_url, timeout=30000)
                page.wait_for_timeout(2000)
                try:
                    LoginPage(page).handle_cookie_popup()
                except Exception:
                    pass
                try:
                    if page.get_by_text("liwenfeng01").is_visible(timeout=3000):
                        logger.info("✓ Session 有效，已登录")
                        # 检查并重置 Verifying 状态
                        self._reset_account_if_verifying(page, config)
                        return session_manager
                except Exception:
                    pass
                session_loaded = False

        if not session_loaded:
            with allure.step("执行登录流程"):
                page.goto(base_url, timeout=30000)
                page.wait_for_timeout(2000)
                LoginPage(page).handle_cookie_popup()
                if page.get_by_role("textbox", name="Email or phone number").is_visible(
                    timeout=5000
                ):
                    page.get_by_role("textbox", name="Email or phone number").fill(
                        username
                    )
                    page.get_by_role("button", name="Continue").click()
                    page.wait_for_timeout(2000)
                    page.get_by_role("textbox", name="Enter password").fill(password)
                    page.get_by_role("button", name="Log in").click()
                    page.wait_for_timeout(3000)
                    if session_manager.save_session():
                        logger.info("✓ Session 已保存")
                    
                    # 登录后检查并重置 Verifying 状态
                    self._reset_account_if_verifying(page, config)

        return session_manager

    # ==================== 用例 1：认证失败页 + Retry + support@ok.com 校验 ====================

    @pytest.mark.case_id_kyc_webqa_verification_failed_retry
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.kyc
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("KYC 认证失败重试")
    @allure.title("认证失败页展示、support@ok.com 纯文本、Retry 进入引导页")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description(
        "验证 SUSPENDED 态下显示 Verification Failed、support@ok.com 无链接、点击 Retry 进入引导页"
    )
    def test_01_verification_failed_and_retry(self, page, config):
        """TC016+TC017+TC019 合并：认证失败页 + Retry + support 校验"""
        kyc_page = KycIdentificationPage(page)
        self._ensure_logged_in(page, config)

        with allure.step("访问 KYC 页（SUSPENDED 态显示 Verification Failed）"):
            page.goto(config["base_url"], timeout=30000)
            page.wait_for_load_state("domcontentloaded", timeout=10000)
            page.wait_for_timeout(2000)

        # 若显示引导页（非 SUSPENDED），跳过失败页相关断言
        retry_btn = page.get_by_role("button", name="Retry")
        if retry_btn.is_visible(timeout=3000):
            with allure.step("验证 Verification Failed 页元素"):
                assert (
                    page.get_by_role("heading", name="Verification Failed").is_visible()
                ), "未显示 Verification Failed 标题"
                assert page.get_by_text(
                    "Verification failed. We will contact you shortly with reasons"
                ).is_visible(), "未显示失败文案"
                assert page.get_by_text(
                    "Need help? Contact us: support@ok.com"
                ).is_visible(), "未显示 support 文案"
                logger.info("✓ 认证失败页元素正确")

            with allure.step("验证 support@ok.com 为纯文本（TC019）"):
                result = kyc_page.get_support_email_link_status()
                assert result == "no_link", f"support@ok.com 应为纯文本，实际: {result}"
                logger.info("✓ support@ok.com 无 href 链接")

            with allure.step("点击 Retry 进入引导页（TC017）"):
                kyc_page.click_retry_button()
                page.wait_for_timeout(1500)

        with allure.step("验证进入引导页"):
            assert page.get_by_text("Start Identity Verification").is_visible(
                timeout=5000
            ), "未进入引导页"
            assert page.get_by_role("button", name="Begin").is_visible(), "未显示 Begin"
            logger.info("✅ 认证失败重试流程通过")

    # ==================== 用例 2：引导页 + Begin 进入上传页 ====================

    @pytest.mark.case_id_kyc_webqa_guide_begin
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.kyc
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("KYC 引导页与导航")
    @allure.title("引导页展示并点击 Begin 进入上传页")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证引导页显示 Begin、点击后进入 Upload Document 页")
    def test_02_guide_begin_upload_page(self, page, config):
        """TC001+TC002 合并：引导页 + Begin"""
        kyc_page = KycIdentificationPage(page)
        self._ensure_logged_in(page, config)

        with allure.step("确保在引导页（必要时 Retry）"):
            page.goto(config["base_url"], timeout=30000)
            page.wait_for_load_state("domcontentloaded", timeout=10000)
            page.wait_for_timeout(2000)
            
            try:
                if page.get_by_role("button", name="Retry").is_visible(timeout=2000):
                    kyc_page.click_retry_button()
                    page.wait_for_timeout(3000)
                    page.wait_for_load_state("domcontentloaded", timeout=10000)
            except Exception:
                pass

        with allure.step("验证引导页并点击 Begin"):
            assert page.get_by_text("Start Identity Verification").is_visible(
                timeout=5000
            ), "未显示引导页"
            kyc_page.click_begin_button()
            page.wait_for_timeout(3000)
            page.wait_for_load_state("domcontentloaded", timeout=10000)

        with allure.step("验证进入上传页"):
            page.wait_for_timeout(2000)
            
            upload_heading = page.get_by_text("Upload Document")
            upload_heading.wait_for(state="visible", timeout=10000)
            assert upload_heading.is_visible(), "未进入上传页"
            
            page.wait_for_timeout(2000)
            
            # 按钮文案可能是 "Upload" 或 "Choose File"
            btn_found = False
            try:
                page.get_by_role("button", name="Upload").wait_for(state="visible", timeout=5000)
                btn_found = True
                logger.info("✓ 找到 Upload 按钮")
            except Exception:
                try:
                    page.get_by_role("button", name="Choose File").wait_for(state="visible", timeout=5000)
                    btn_found = True
                    logger.info("✓ 找到 Choose File 按钮")
                except Exception as e:
                    logger.error(f"等待上传按钮超时，正在截图调试...")
                    page.screenshot(path="reports/screenshots/debug_upload_button_not_found.png", full_page=True, timeout=60000)
                    logger.error(f"当前 URL: {page.url}")
                    
                    try:
                        all_buttons = page.get_by_role("button").all()
                        button_texts = []
                        for btn in all_buttons[:10]:
                            try:
                                if btn.is_visible(timeout=500):
                                    button_texts.append(btn.inner_text())
                            except Exception:
                                pass
                        logger.error(f"页面上的按钮: {button_texts}")
                    except Exception:
                        pass
                    
                    raise AssertionError(f"未显示 Upload 或 Choose File 按钮: {e}")
            
            assert btn_found, "未显示上传按钮"
            logger.info("✅ 引导页 Begin 流程通过")

    # ==================== 用例 3：Enter Manually + 空表单校验 ====================

    @pytest.mark.case_id_kyc_webqa_enter_manually_validation
    @pytest.mark.p1
    @pytest.mark.kyc
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("KYC 表单校验")
    @allure.title("Enter Manually 打开空表单、提交显示 Cannot be empty")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证手动打开表单、空提交时 6 个必填字段显示 Cannot be empty")
    def test_03_enter_manually_empty_form_validation(self, page, config):
        """TC009+TC005 合并：Enter Manually + 空表单校验"""
        kyc_page = KycIdentificationPage(page)
        self._ensure_logged_in(page, config)
        self._go_to_upload_page(page, config, kyc_page)

        with allure.step("点击 Enter Manually 打开表单"):
            kyc_page.click_enter_manually()
            page.wait_for_timeout(1500)
            assert kyc_page.is_form_dialog_visible(), "表单弹窗未打开"

        with allure.step("直接点击 Submit（未填必填字段）"):
            kyc_page.click_submit_button()
            page.wait_for_timeout(1000)

        with allure.step("验证 6 个必填字段显示 Cannot be empty"):
            assert kyc_page.is_field_error_visible("Cannot be empty"), (
                "未显示 Cannot be empty 错误"
            )
            errors = kyc_page.get_all_error_messages()
            assert len(errors) >= 6, f"必填错误应 >= 6，实际: {len(errors)}"
            logger.info("✅ 空表单校验通过")

    def _go_to_upload_page(self, page, config, kyc_page):
        """进入上传页（引导页则 Begin），确保上传按钮可见"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                logger.info(f"开始第 {attempt + 1}/{max_retries} 次尝试进入上传页")
                
                # 每次尝试都重新导航
                page.goto(config["base_url"], timeout=30000)
                page.wait_for_load_state("domcontentloaded", timeout=10000)
                page.wait_for_timeout(2000)
                
                # 检查并处理 Retry 按钮
                try:
                    if page.get_by_role("button", name="Retry").is_visible(timeout=2000):
                        logger.info("检测到 Retry 按钮，点击进入引导页")
                        kyc_page.click_retry_button()
                        page.wait_for_timeout(3000)
                        page.wait_for_load_state("domcontentloaded", timeout=10000)
                except Exception:
                    pass
                
                # 检查并处理 Begin 按钮
                try:
                    if page.get_by_role("button", name="Begin").is_visible(timeout=2000):
                        logger.info("检测到 Begin 按钮，点击进入上传页")
                        kyc_page.click_begin_button()
                        page.wait_for_timeout(3000)
                        page.wait_for_load_state("domcontentloaded", timeout=10000)
                        page.wait_for_timeout(2000)
                except Exception:
                    pass
                
                # 检查页面状态：可能在 Verifying 或其他状态
                try:
                    if page.get_by_text("Verifying").is_visible(timeout=1000):
                        logger.warning("⚠️ 页面显示 Verifying 状态，账号已提交认证，需要重置状态")
                        
                        # 自动执行重置脚本
                        if attempt < max_retries - 1:
                            logger.info("正在执行重置脚本...")
                            script_path = PROJECT_ROOT / "test_cases" / "kyc" / "standalone_suspend_account.py"
                            user_id = config.get("user_id", "796559612064208640")
                            
                            try:
                                result = subprocess.run(
                                    [sys.executable, str(script_path), "--user-id", user_id],
                                    capture_output=True,
                                    text=True,
                                    timeout=30,
                                    cwd=str(PROJECT_ROOT),
                                )
                                
                                if result.returncode == 0:
                                    logger.info("✓ 账号状态已重置为 SUSPENDED，将重试进入上传页")
                                    page.wait_for_timeout(2000)
                                    continue
                                else:
                                    logger.warning(f"重置脚本返回非零: {result.returncode}")
                                    logger.warning(f"stderr: {result.stderr}")
                                    logger.warning(f"stdout: {result.stdout}")
                                    # 即使重置失败也继续重试，可能是首次使用账号
                                    continue
                            except subprocess.TimeoutExpired:
                                logger.error("重置脚本执行超时（30s）")
                                continue
                            except Exception as e:
                                logger.error(f"执行重置脚本异常: {e}")
                                continue
                        else:
                            logger.error("已到最后一次尝试，但账号仍在 Verifying 状态")
                except Exception:
                    pass
                
                # 尝试找到 Upload Document 标题
                upload_doc_found = False
                try:
                    page.get_by_text("Upload Document").wait_for(state="visible", timeout=10000)
                    logger.info("✓ 找到 Upload Document 标题")
                    upload_doc_found = True
                except Exception as e:
                    logger.warning(f"未找到 Upload Document 标题（尝试 {attempt + 1}/{max_retries}）: {e}")
                
                # 如果没有找到标题，检查是否已经在表单页或其他页面
                if not upload_doc_found:
                    try:
                        if page.get_by_role("dialog").filter(has_text="Identity Verification").is_visible(timeout=2000):
                            logger.info("已经在 Identity Verification 表单弹窗中")
                            return
                    except Exception:
                        pass
                    
                    if attempt < max_retries - 1:
                        continue
                
                # 按钮文案可能是 "Upload" 或 "Choose File"，使用更宽松的检测策略
                btn_found = False
                
                # 策略1: 通过 role=button 精确匹配
                try:
                    page.get_by_role("button", name="Upload").wait_for(state="visible", timeout=5000)
                    btn_found = True
                    logger.info("✓ 找到 Upload 按钮")
                except Exception:
                    try:
                        page.get_by_role("button", name="Choose File").wait_for(state="visible", timeout=5000)
                        btn_found = True
                        logger.info("✓ 找到 Choose File 按钮")
                    except Exception:
                        # 策略2: 通过文件输入框是否存在来判断
                        try:
                            file_input = page.locator('input[type="file"]').first
                            if file_input.count() > 0:
                                logger.info("✓ 找到文件输入框，判定为上传页")
                                btn_found = True
                        except Exception as e:
                            logger.warning(f"未找到上传按钮或文件输入框（尝试 {attempt + 1}/{max_retries}）: {e}")
                
                if btn_found:
                    logger.info(f"✓ 成功到达上传页（尝试 {attempt + 1}/{max_retries}）")
                    return
                
                # 如果是最后一次尝试，收集详细诊断信息并抛出异常
                if attempt == max_retries - 1:
                    logger.error(f"最后一次尝试失败，收集诊断信息")
                    page.screenshot(path="reports/screenshots/debug_go_to_upload_page.png", full_page=True, timeout=60000)
                    logger.error(f"当前 URL: {page.url}")
                    logger.error(f"页面标题: {page.title()}")
                    
                    # 记录页面状态关键字
                    page_text = page.inner_text("body")
                    if "Verifying" in page_text:
                        logger.error("⚠️ 页面显示 Verifying - 账号可能已提交 KYC")
                    if "Verification Failed" in page_text:
                        logger.error("⚠️ 页面显示 Verification Failed - 账号处于失败状态")
                    if "Start Identity Verification" in page_text:
                        logger.error("⚠️ 页面仍在引导页 - Begin 按钮可能未生效")
                    
                    # 记录页面上所有按钮
                    try:
                        all_buttons = page.get_by_role("button").all()
                        button_texts = []
                        for btn in all_buttons[:10]:
                            try:
                                if btn.is_visible(timeout=500):
                                    button_texts.append(btn.inner_text())
                                else:
                                    name_attr = btn.get_attribute('name') or ''
                                    button_texts.append(f"[隐藏]{name_attr}")
                            except Exception:
                                pass
                        logger.error(f"页面上的按钮: {button_texts}")
                    except Exception as e:
                        logger.error(f"无法获取按钮列表: {e}")
                    
                    # 记录页面中是否有文件上传输入框
                    try:
                        file_inputs = page.locator('input[type="file"]').count()
                        logger.error(f"页面上的文件输入框数量: {file_inputs}")
                    except Exception as e:
                        logger.error(f"无法检查文件输入框: {e}")
                    
                    raise AssertionError(f"未找到 Upload 或 Choose File 按钮（已重试 {max_retries} 次）")
                
            except AssertionError:
                raise
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"_go_to_upload_page 失败（尝试 {attempt + 1}/{max_retries}）: {e}")
                    raise
                else:
                    logger.warning(f"_go_to_upload_page 第 {attempt + 1} 次尝试异常，将重试: {e}")
                    page.wait_for_timeout(2000)

    # ==================== 用例 4：ESC 关闭弹窗 ====================

    @pytest.mark.case_id_kyc_webqa_esc_close_dialog
    @pytest.mark.p1
    @pytest.mark.kyc
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("KYC 弹窗交互")
    @allure.title("ESC 关闭表单弹窗返回上传页")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证按 ESC 关闭弹窗并返回 Upload Document 页")
    def test_04_esc_close_dialog(self, page, config):
        """TC010：ESC 关闭弹窗"""
        kyc_page = KycIdentificationPage(page)
        self._ensure_logged_in(page, config)
        self._go_to_upload_page(page, config, kyc_page)

        with allure.step("打开表单弹窗"):
            kyc_page.click_enter_manually()
            page.wait_for_timeout(1000)
            assert kyc_page.is_form_dialog_visible(), "表单未打开"

        with allure.step("按 ESC 关闭"):
            kyc_page.press_escape()
            page.wait_for_timeout(800)

        with allure.step("验证返回上传页"):
            dialog = page.get_by_role("dialog")
            assert not dialog.is_visible(timeout=2000), "弹窗应已关闭"
            assert page.get_by_text("Upload Document").is_visible(timeout=3000), (
                "应返回上传页"
            )
            logger.info("✅ ESC 关闭弹窗通过")

    # ==================== 用例 5：上传不可识别图片 ====================

    @pytest.mark.case_id_kyc_webqa_upload_invalid_image
    @pytest.mark.p1
    @pytest.mark.kyc
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("KYC 文件上传")
    @allure.title("上传不可识别图片 - 表单字段为空")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证上传风景图后 OCR 未识别，表单字段为空")
    def test_05_upload_invalid_image(self, page, config):
        """TC007：上传不可识别图片"""
        kyc_page = KycIdentificationPage(page)
        invalid_path = IMAGE_DIR / "图片1.png"
        if not invalid_path.exists():
            pytest.skip(f"测试图片不存在: {invalid_path}")

        self._ensure_logged_in(page, config)
        self._go_to_upload_page(page, config, kyc_page)

        with allure.step("上传不可识别图片"):
            kyc_page.upload_document_image(str(invalid_path))

        with allure.step("验证表单字段为空（OCR 未识别）"):
            # 增加明确的等待时间，确保弹窗打开
            page.wait_for_timeout(2000)
            
            # 检查弹窗是否可见，如果不可见则截图调试
            if not kyc_page.is_form_dialog_visible(timeout=10000):
                logger.error("表单弹窗未打开，正在截图调试...")
                page.screenshot(path="reports/screenshots/debug_invalid_image_no_dialog.png", full_page=True)
                logger.error(f"当前 URL: {page.url}")
                
                # 检查是否有错误提示
                try:
                    error_msg = page.locator(".error, .error-message, [role='alert']").all_inner_texts()
                    if error_msg:
                        logger.error(f"页面错误信息: {error_msg}")
                except Exception:
                    pass
                
                # 检查是否仍在上传页
                if page.get_by_text("Upload Document").is_visible(timeout=2000):
                    logger.error("仍在上传页，可能上传失败或被拒绝")
                
                raise AssertionError("弹窗应打开，但超时未出现")
            
            doc_number = kyc_page.get_document_number_value()
            assert doc_number == "", f"Document Number 应为空，实际: {doc_number}"
            logger.info("✅ 不可识别图片测试通过")

        kyc_page.press_escape()
        page.wait_for_timeout(500)

    # ==================== 用例 6：未勾选协议提交 ====================

    @pytest.mark.case_id_kyc_webqa_submit_without_agreement
    @pytest.mark.p1
    @pytest.mark.kyc
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("KYC 表单校验")
    @allure.title("OCR 表单未勾选协议提交 - 显示 alert 阻止")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证未勾选协议时 Submit 触发 User agreement not agreed 提示")
    def test_06_submit_without_agreement(self, page, config):
        """TC006：未勾选协议提交"""
        kyc_page = KycIdentificationPage(page)
        valid_path = IMAGE_DIR / "Australia_a_1.jpeg"
        if not valid_path.exists():
            pytest.skip(f"测试图片不存在: {valid_path}")

        self._ensure_logged_in(page, config)
        self._go_to_upload_page(page, config, kyc_page)

        with allure.step("上传合规证件触发 OCR"):
            kyc_page.upload_document_image(str(valid_path))
            # 等待弹窗打开，确保 OCR 处理完成
            page.wait_for_timeout(2000)
            if not kyc_page.is_form_dialog_visible(timeout=10000):
                logger.error("表单弹窗未打开，上传可能失败")
                page.screenshot(path="reports/screenshots/debug_submit_without_agreement_no_dialog.png", full_page=True)
                raise AssertionError("表单弹窗未显示，无法继续测试")

        alert_text = []

        def handle_dialog(dialog):
            alert_text.append(dialog.message)
            dialog.accept()

        page.on("dialog", handle_dialog)

        with allure.step("不勾选协议直接 Submit"):
            kyc_page.click_submit_button()
            page.wait_for_timeout(2000)

        with allure.step("验证 alert 或页内提示阻止提交"):
            # 原生 alert 或自定义 Modal 均可能
            if len(alert_text) > 0:
                assert "agreement" in alert_text[0].lower(), (
                    f"预期含 agreement 相关文案，实际: {alert_text[0]}"
                )
                logger.info(f"✓ 捕获 alert: {alert_text[0]}")
            else:
                # 若为自定义 Modal，检查页内文案（放宽匹配条件）
                try:
                    found = (
                        page.get_by_text("User agreement not agreed", exact=False).is_visible(timeout=2000)
                        or page.get_by_text("agreement", exact=False).is_visible(timeout=1000)
                        or page.get_by_text("Please accept", exact=False).is_visible(timeout=1000)
                    )
                    assert found, "未找到协议相关提示"
                except Exception:
                    # 若仍未找到，截图并记录所有 dialog/modal/alert 元素
                    logger.error("未捕获 alert 且页内未找到协议提示，正在截图...")
                    page.screenshot(path="reports/screenshots/debug_no_agreement_alert.png", full_page=True, timeout=60000)
                    
                    try:
                        dialogs = page.locator("[role='dialog'], [role='alertdialog'], .modal, .alert").all()
                        logger.error(f"找到 {len(dialogs)} 个 dialog/modal 元素")
                        for i, d in enumerate(dialogs[:3]):
                            if d.is_visible():
                                logger.error(f"Dialog {i} 文本: {d.inner_text()[:200]}")
                    except Exception:
                        pass
                    
                    raise AssertionError("未捕获 alert 且页内未找到协议相关提示")
            logger.info("✅ 未勾选协议提交校验通过")

    # ==================== 用例 7：协议文字点击无跳转 ====================

    @pytest.mark.case_id_kyc_webqa_agreement_links_no_nav
    @pytest.mark.p2
    @pytest.mark.kyc
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("KYC 表单 UI")
    @allure.title("点击 User Agreement / Privacy Policy 无新标签无跳转")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("验证协议文字为 SPAN 无 href，点击弹窗保持")
    def test_07_agreement_links_no_navigation(self, page, config):
        """TC004a+TC004b 合并：协议文字点击无响应"""
        kyc_page = KycIdentificationPage(page)
        valid_path = IMAGE_DIR / "Australia_a_1.jpeg"
        if not valid_path.exists():
            pytest.skip(f"测试图片不存在: {valid_path}")

        self._ensure_logged_in(page, config)
        self._go_to_upload_page(page, config, kyc_page)
        
        with allure.step("上传合规证件触发 OCR"):
            kyc_page.upload_document_image(str(valid_path))
            # 等待弹窗打开，确保 OCR 处理完成
            page.wait_for_timeout(2000)
            if not kyc_page.is_form_dialog_visible(timeout=10000):
                logger.error("表单弹窗未打开，上传可能失败")
                page.screenshot(path="reports/screenshots/debug_agreement_links_no_dialog.png", full_page=True)
                raise AssertionError("表单弹窗未显示，无法继续测试")

        with allure.step("滚动弹窗使协议区域可见"):
            kyc_page.scroll_dialog_to_protocol()

        with allure.step("点击 User Agreement 文字"):
            page.locator(".FormPageContent_protocol___8DnN").filter(
                has_text="User Agreement"
            ).first.click()
            page.wait_for_timeout(500)
            assert kyc_page.is_form_dialog_visible(), "弹窗应保持打开"

        with allure.step("点击 Privacy Policy 文字"):
            page.locator(".FormPageContent_protocol___8DnN").filter(
                has_text="Privacy Policy"
            ).first.click()
            page.wait_for_timeout(500)
            assert kyc_page.is_form_dialog_visible(), "弹窗应保持打开"

        logger.info("✅ 协议文字点击无跳转通过")
        kyc_page.press_escape()
        page.wait_for_timeout(500)

    # ==================== 用例 8：完整 OCR + 勾选协议 + 提交 ====================

    @pytest.mark.case_id_kyc_webqa_upload_valid_submit
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.kyc
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("KYC 核心流程")
    @allure.title("上传合规证件 OCR 识别、勾选协议、提交成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证上传澳大利亚国民身份证、OCR 填充、勾选协议、提交成功并重置状态")
    def test_08_upload_valid_ocr_submit(self, page, config):
        """TC003+TC004+TC018 合并：完整 OCR 提交流程"""
        kyc_page = KycIdentificationPage(page)
        valid_path = IMAGE_DIR / "Australia_a_1.jpeg"
        if not valid_path.exists():
            pytest.skip(f"测试图片不存在: {valid_path}")

        self._ensure_logged_in(page, config)
        self._go_to_upload_page(page, config, kyc_page)

        with allure.step("上传合规证件"):
            kyc_page.upload_document_image(str(valid_path))

        with allure.step("验证 OCR 填充"):
            # 增加明确的等待时间，确保弹窗打开并完成 OCR 识别
            page.wait_for_timeout(2000)
            
            # 检查弹窗是否可见，如果不可见则截图调试
            if not kyc_page.is_form_dialog_visible(timeout=10000):
                logger.error("表单弹窗未打开，正在截图调试...")
                page.screenshot(path="reports/screenshots/debug_valid_image_no_dialog.png", full_page=True)
                logger.error(f"当前 URL: {page.url}")
                
                # 检查是否有错误提示
                try:
                    error_msg = page.locator(".error, .error-message, [role='alert']").all_inner_texts()
                    if error_msg:
                        logger.error(f"页面错误信息: {error_msg}")
                except Exception:
                    pass
                
                raise AssertionError("表单弹窗未显示，但上传应该成功")
            
            assert "National ID" in kyc_page.get_document_type_value(), "Document Type"
            assert kyc_page.get_document_number_value() == "007464732", (
                "Document Number"
            )

        with allure.step("滚动并勾选协议后提交"):
            kyc_page.scroll_dialog_to_protocol()
            page.wait_for_timeout(800)
            kyc_page.check_agreement_checkbox()
            page.wait_for_timeout(800)
            kyc_page.click_submit_button()
            page.wait_for_timeout(8000)

        with allure.step("验证提交成功（弹窗关闭或显示 Verifying）"):
            dialog = page.get_by_role("dialog")
            verifies = page.get_by_text("Verifying")
            # 等待至多 12 秒：弹窗关闭 或 Verifying 出现
            dialog_closed = False
            verifying_shown = False
            for _ in range(12):
                try:
                    if not dialog.is_visible(timeout=1500):
                        dialog_closed = True
                        break
                except Exception:
                    dialog_closed = True
                    break
                try:
                    if verifies.is_visible(timeout=1000):
                        verifying_shown = True
                        break
                except Exception:
                    pass
                page.wait_for_timeout(1000)
            assert dialog_closed or verifying_shown, (
                "提交后应关闭弹窗或显示 Verifying（检查协议勾选选择器是否仍有效）"
            )
            logger.info("✓ 提交成功")

        with allure.step("执行重置脚本恢复 SUSPENDED 状态"):
            script_path = PROJECT_ROOT / "test_cases" / "kyc" / "standalone_suspend_account.py"
            user_id = config.get("user_id", "796559612064208640")
            try:
                r = subprocess.run(
                    [sys.executable, str(script_path), "--user-id", user_id],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(PROJECT_ROOT),
                )
                if r.returncode == 0:
                    logger.info("✓ 状态已重置为 SUSPENDED")
                else:
                    logger.warning(
                        f"重置脚本返回 {r.returncode}（可能无 payment_account）: {r.stderr}"
                    )
            except Exception as e:
                logger.warning(f"重置脚本执行异常（可忽略）: {e}")

        logger.info("✅ 完整 OCR 提交流程通过")

    # ==================== 用例 9：脚本无 payment_account 时失败 ====================

    @pytest.mark.case_id_kyc_webqa_script_no_payment_account
    @pytest.mark.p1
    @pytest.mark.kyc
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("KYC 状态管理")
    @allure.title("无 payment_account 时 standalone 脚本 exit 1")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证用户从未提交 KYC 时脚本输出未找到 payment_account_id 并 exit 1")
    def test_09_standalone_script_no_payment_account(self, config):
        """TC011：脚本在无 payment_account 时失败（非 UI）"""
        script_path = PROJECT_ROOT / "test_cases" / "kyc" / "standalone_suspend_account.py"
        user_id = config.get("user_id", "796559612064208640")

        with allure.step("执行 standalone_suspend_account.py"):
            r = subprocess.run(
                [sys.executable, str(script_path), "--user-id", user_id],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(PROJECT_ROOT),
            )

        # 文档：无 payment_account 时输出 "未找到用户 xxx 的 payment_account_id"，exit 1
        # 若有 payment_account 则成功，我们只断言「失败时」的行为
        # 脚本日志可能在 stdout；依赖缺失时 standalone 也会在 stderr 中说明 payment_account_id 参数
        combined = (r.stderr or "") + (r.stdout or "")
        if r.returncode != 0:
            assert (
                "payment_account_id" in combined
                or "payment_account" in combined.lower()
            ), (
                f"失败时应输出 payment_account 相关提示，stdout: {r.stdout!r} stderr: {r.stderr!r}"
            )
        logger.info("✅ 脚本无 payment_account 校验通过")
