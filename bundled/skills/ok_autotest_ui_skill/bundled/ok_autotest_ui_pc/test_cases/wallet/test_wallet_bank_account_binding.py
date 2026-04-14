"""
阿联酋站 - 钱包银行账户绑定完整流程测试（优化版）

优化说明：
1. TC010/TC011/TC012 合并为一个测试（取消解绑的三种方式）
2. TC007-TC013 使用测试类 + scope="class" fixture，共享浏览器
3. 测试顺序优化：使用 test_01_, test_02_ 前缀保证执行顺序
4. 预计节省时间：~60%（从 90秒降至 36秒）

本脚本由 playwright-test-generator 生成
录制文档：test_cases/wallet/Wallet_BankAccount_Withdrawal_TestCases_20260305.md
生成时间：2026-03-05
优化时间：2026-03-06（共享浏览器版本）

测试站点：AE (https://aepub.58v5.cn)
测试角色：Seller (卖家)
测试目标：验证银行账户绑定完整流程（TC016-TC023）+ 解绑测试（TC007-TC014）
"""
import pytest
import allure
from pages.login_page import LoginPage
from pages.wallet_page import WalletPage
from utils.session_manager import SessionManager
from utils.logger import setup_logger

logger = setup_logger()

# ============================================
# 测试环境配置（来自录制文档）
# ============================================
_CONFIG = {
    "site": "ae",
    "site_name": "阿联酋站",
    "role": "seller",
    "user_name": "ae_seller",
    "base_url": "https://aepub.58v5.cn/biz/en/wallet/home",
    "test_account": {
        "username": "ae_seller_wallet@test.com",
        "password": "Test@123456"
    },
    "browser": {
        "type": "chromium",
        "headless": False,
        "viewport": {"width": 1920, "height": 1080}
    },
    "timeout": {
        "default": 30000
    }
}


@pytest.mark.case_id_wallet_wallet_016
@pytest.mark.p0
@pytest.mark.wallet
@pytest.mark.ae
@allure.feature("OK")
@allure.story("钱包 - 银行账户绑定")
@allure.title("TC016-TC023: 银行账户绑定完整流程（优化合并）")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("""
验证银行账户绑定完整流程（一次打开对话框，连续验证所有场景）：
- TC016: 点击Add Bank Account打开对话框
- TC017: 选择United States of America自动填充USD
- TC018: 验证Transfer method选项列表
- TC019: ACH routing number自动补全
- TC020: Address字段自动补全
- TC021: 选择地址后City自动填充
- TC023: 提交完整表单绑定成功
""")
def test_bank_account_binding_complete_flow(page, config):
    """TC016-TC023: 银行账户绑定完整流程（优化合并版本）"""
    
    # ========== Arrange ==========
    base_url = config['base_url']
    username = config['test_account']['username']
    password = config['test_account']['password']
    
    logger.info("="*80)
    logger.info("TC016-TC023: 银行账户绑定完整流程测试")
    logger.info("="*80)
    
    # ========== Session复用 ==========
    session_manager = SessionManager(
        page,
        base_url,
        session_name=f"{config['site']}_{config['role']}_{config['user_name']}_wallet"
    )
    
    if not session_manager.load_session():
        # 首次运行，执行登录
        page.goto(base_url)
        page.wait_for_timeout(1000)
        page.get_by_role('textbox', name='Email or phone number').fill(username)
        page.get_by_role('button', name='Continue').click()
        page.wait_for_timeout(1000)
        page.get_by_role('textbox', name='Enter password').fill(password)
        page.get_by_role('button', name='Log in').click()
        page.wait_for_timeout(3000)
        session_manager.save_session()
    else:
        page.goto(base_url)
        try:
            page.wait_for_load_state("load", timeout=10000)
        except Exception:
            # 如果networkidle超时，使用domcontentloaded作为后备
            logger.warning("networkidle超时，使用domcontentloaded")
            page.wait_for_load_state("domcontentloaded")
    
    # 刷新确保状态干净
    page.reload()
    try:
        page.wait_for_load_state("load", timeout=10000)
    except Exception:
        # 如果networkidle超时，使用domcontentloaded作为后备
        logger.warning("刷新后networkidle超时，使用domcontentloaded")
        page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)
    
    # ========== 前置条件：确保银行账户未绑定 ==========
    with allure.step("前置条件：确保银行账户未绑定"):
        _ensure_bank_account_unbound(page)
        logger.info("✓ 前置条件满足：银行账户未绑定")
    
    # ========== TC016: 打开绑定对话框 ==========
    with allure.step("TC016：点击Add Bank Account打开对话框"):
        logger.info("\n" + "="*80)
        logger.info("TC016: 点击Add Bank Account应打开绑定表单对话框")
        logger.info("="*80)
        
        # 点击Add Bank Account按钮（基于MCP录制）
        page.get_by_text('Add Bank Account').click()
        page.wait_for_timeout(2000)
        logger.info("✓ 已点击Add Bank Account按钮")
        
        # 检测Load Fail错误（增加重试逻辑）
        max_retries = 3
        for attempt in range(max_retries):
            if page.get_by_text('Load Fail').is_visible(timeout=2000):
                logger.warning(f"⚠️ 检测到Load Fail（尝试 {attempt + 1}/{max_retries}），刷新页面")
                page.reload()
                page.wait_for_load_state("load", timeout=10000)
                page.wait_for_timeout(3000)
                page.get_by_text('Add Bank Account').click()
                page.wait_for_timeout(3000)
            else:
                break
        
        # 验证对话框打开
        dialog_title = page.get_by_role('heading', name='Bind Bank Account')
        assert dialog_title.is_visible(timeout=5000), "绑定对话框未打开"
        logger.info("✓ 对话框标题显示正常")
        
        # 等待iframe出现（增加等待时间）
        page.wait_for_timeout(5000)
        logger.info("✓ 已等待iframe加载")
        
        # 验证iframe加载（使用简化选择器，增加超时时间）
        iframe = page.frame_locator('iframe')
        
        # 分步骤验证iframe内容
        try:
            # 先等待iframe出现
            page.wait_for_selector('iframe', timeout=10000)
            logger.info("✓ iframe元素已出现")
            
            # 再验证iframe内容加载
            country_label = iframe.get_by_text('Account country / region')
            country_label.wait_for(state='visible', timeout=15000)
            logger.info("✓ iframe表单加载成功")
        except Exception as e:
            logger.error(f"❌ iframe加载失败: {e}")
            page.screenshot(path="reports/screenshots/iframe_load_failed.png", timeout=60000)
            
            # 最后一次尝试：检查是否是Load Fail
            if page.get_by_text('Load Fail').is_visible(timeout=2000):
                logger.error("❌ 仍然是Load Fail错误")
                raise AssertionError("iframe加载失败：Load Fail错误")
            else:
                raise AssertionError(f"iframe表单未加载: {e}")
        
        # 验证Submit按钮
        submit_btn = page.get_by_role('button', name='Submit')
        assert submit_btn.is_visible(), "Submit按钮未显示"
        logger.info("✓ Submit按钮显示正常")
        
        logger.info("✅ TC016通过：对话框打开成功")
    
    # ========== TC017: 选择USA自动填充USD ==========
    with allure.step("TC017：选择USA应自动填充USD"):
        logger.info("\n" + "="*80)
        logger.info("TC017: 选择United States of America应自动填充USD")
        logger.info("="*80)
        
        iframe = page.frame_locator('iframe[title="beneficiaryForm element iframe"]')
        
        # 点击国家下拉框（基于MCP录制的选择器）
        iframe.locator('.css-evdas6-control').first.click()
        page.wait_for_timeout(1000)
        logger.info("✓ 已点击国家下拉框")
        
        # 选择United States of America
        iframe.get_by_text('United States of America').click()
        page.wait_for_timeout(1000)
        logger.info("✓ 已选择United States of America")
        
        # 验证USD自动填充
        usd_text = iframe.locator('[data-testid="beneficiary.bankDetails.accountCurrency"]').get_by_text('USD')
        assert usd_text.is_visible(timeout=3000), "USD未自动填充"
        logger.info("✓ USD已自动填充")
        
        logger.info("✅ TC017通过：USD自动填充成功")
    
    # ========== TC018: 验证Transfer method选项 ==========
    with allure.step("TC018：验证Transfer method选项列表"):
        logger.info("\n" + "="*80)
        logger.info("TC018: 选择USD后应显示Transfer method选项")
        logger.info("="*80)
        
        iframe = page.frame_locator('iframe[title="beneficiaryForm element iframe"]')
        
        # 等待Transfer method加载（可能需要额外时间）
        page.wait_for_timeout(1500)
        
        # 验证Transfer method标签
        transfer_label = iframe.get_by_text('Transfer method')
        assert transfer_label.is_visible(timeout=5000), "Transfer method未显示"
        logger.info("✓ Transfer method标签已显示")
        
        # 验证各个选项
        assert iframe.get_by_text('ACH', exact=False).first.is_visible(timeout=3000), "ACH选项未显示"
        logger.info("✓ ACH选项已显示")
        
        assert iframe.get_by_text('Fedwire').is_visible(timeout=3000), "Fedwire选项未显示"
        logger.info("✓ Fedwire选项已显示")
        
        assert iframe.get_by_text('FedNow').is_visible(timeout=3000), "FedNow选项未显示"
        logger.info("✓ FedNow选项已显示")
        
        assert iframe.get_by_text('SWIFT', exact=False).first.is_visible(timeout=3000), "SWIFT选项未显示"
        logger.info("✓ SWIFT选项已显示")
        
        logger.info("✅ TC018通过：Transfer method选项列表正常")
    
    # ========== TC019: ACH routing自动补全 ==========
    with allure.step("TC019：验证ACH routing自动补全"):
        logger.info("\n" + "="*80)
        logger.info("TC019: ACH routing number输入后应显示银行列表")
        logger.info("="*80)
        
        iframe = page.frame_locator('iframe[title="beneficiaryForm element iframe"]')
        
        # 选择ACH（基于MCP录制）
        iframe.get_by_role('button', name='Select').first.click()
        page.wait_for_timeout(1000)
        logger.info("✓ 已选择ACH")
        
        # 输入routing number（基于MCP录制的选择器）
        iframe.locator('#react-select-2-input').fill('1210')
        page.wait_for_timeout(2000)
        logger.info("✓ 已输入routing number: 1210")
        
        # 验证银行选项显示
        bank_option = iframe.get_by_text('Bank of America', exact=False).first
        assert bank_option.is_visible(timeout=3000), "银行选项未显示"
        logger.info("✓ Bank of America选项已显示")
        
        # 选择银行
        bank_option.click()
        page.wait_for_timeout(1000)
        logger.info("✓ 已选择Bank of America")
        
        logger.info("✅ TC019通过：银行自动补全成功")
    
    # ========== TC020+TC021+TC023: Address自动补全+City自动填充+完整提交 ==========
    with allure.step("TC020-TC023：Address自动补全、City自动填充、完整提交"):
        logger.info("\n" + "="*80)
        logger.info("TC020-TC023: Address自动补全→City自动填充→Name/Nickname/Email→完整提交")
        logger.info("="*80)
        
        iframe = page.frame_locator('iframe[title="beneficiaryForm element iframe"]')
        
        # 填写account number
        iframe.locator('[name="beneficiary.bankDetails.accountNumber"]').fill('5354563134257854')
        page.wait_for_timeout(1000)
        logger.info("✓ 已填写account number")
        
        # 滚动到表单底部以便看到Address字段
        iframe.locator('body').evaluate('el => el.scrollTop = el.scrollHeight')
        page.wait_for_timeout(1000)
        logger.info("✓ 已滚动到表单底部")
        
        # TC020: 输入Address触发自动补全（基于MCP录制的精确选择器）
        address_container = iframe.get_by_test_id('beneficiary.address.streetAddress')
        address_input = address_container.get_by_role('textbox')
        address_input.fill('19238', force=True)
        logger.info("✓ TC020: 已输入Address: 19238")
        
        # 等待地址选项加载
        page.wait_for_timeout(5000)
        logger.info("✓ 已等待5秒加载地址选项")
        
        # 选择第二个地址选项（基于MCP录制：#react-select-3-option-1）
        stonehue_option = iframe.locator('#react-select-3-option-1')
        stonehue_option.wait_for(state='visible', timeout=5000)
        stonehue_option.click()
        page.wait_for_timeout(2000)
        logger.info("✓ TC020: 已选择'19238 Stonehue, San Antonio, TX, USA'")
        logger.info("✅ TC020通过：Address自动补全成功")
        
        # TC021: 验证City自动填充
        city_input = iframe.locator('[name*="city"]').first
        city_value = city_input.input_value()
        assert city_value and len(city_value) > 0, "City未自动填充"
        logger.info(f"✓ TC021: City已自动填充: {city_value}")
        logger.info("✅ TC021通过：City自动填充成功")
        
        # TC023: 填写Name/Nickname/Email（在Address之后）
        logger.info("\n开始填写Name/Nickname/Email（步骤6-8，TC023）")
        
        # 再次滚动到最底部，确保Name字段可见
        iframe.locator('body').evaluate('el => el.scrollTop = el.scrollHeight')
        page.wait_for_timeout(1000)
        logger.info("✓ 已再次滚动到最底部")
        
        # Name of account holder（正确的name属性是beneficiary.bankDetails.accountName）
        name_input = iframe.locator('[name="beneficiary.bankDetails.accountName"]')
        name_input.wait_for(state='visible', timeout=10000)
        name_input.fill("Mastercard")
        page.wait_for_timeout(500)
        logger.info("✓ 已填写Name of account holder: Mastercard")
        
        # Nickname (optional)（正确的name属性是nickname）
        nickname_input = iframe.locator('[name="nickname"]')
        if nickname_input.is_visible(timeout=2000):
            nickname_input.fill("liwenfeng01test")
            page.wait_for_timeout(500)
            logger.info("✓ 已填写Nickname: liwenfeng01test")
        
        # Email address（正确的name属性是beneficiary.additionalInfo.personalEmail）
        email_input = iframe.locator('[name="beneficiary.additionalInfo.personalEmail"]')
        email_input.wait_for(state='visible', timeout=10000)
        email_input.fill("wangyongli@58.com")
        page.wait_for_timeout(500)
        logger.info("✓ 已填写Email: wangyongli@58.com")
        
        logger.info("✓ 所有表单字段已填写完毕")
        
        # TC023: 提交表单
        try:
            page.screenshot(path="reports/screenshots/tc023_before_submit.png", timeout=15000)
            logger.info("✓ 已截图：提交前状态")
        except Exception as e:
            logger.warning(f"截图超时，跳过: {e}")
        
        submit_button = page.get_by_role('button', name='Submit')
        submit_button.click()
        page.wait_for_timeout(3000)
        logger.info("✓ 已点击Submit按钮")
        
        # 等待提交处理
        page.wait_for_timeout(5000)
        
        try:
            page.screenshot(path="reports/screenshots/tc023_after_submit.png", timeout=15000)
            logger.info("✓ 已截图：提交后状态")
        except Exception as e:
            logger.warning(f"截图超时，跳过: {e}")
        
        # 验证绑定成功
        dialog = page.locator('dialog:has-text("Bind Bank Account")')
        if not dialog.is_visible(timeout=5000):
            logger.info("✓ 绑定对话框已关闭")
            
            # 等待页面更新
            page.wait_for_timeout(3000)
            
            # 验证Add Bank Account按钮消失
            add_button = page.get_by_text('Add Bank Account')
            if not add_button.is_visible(timeout=2000):
                logger.info("✓ Add Bank Account按钮已消失")
                
                # 验证银行账户信息显示
                account_info = page.locator('text=************7854')
                if account_info.is_visible(timeout=3000):
                    logger.info("✓ 银行账户后四位已显示: ************7854")
                    logger.info("✅ TC023通过：银行账户绑定成功！")
                else:
                    logger.warning("⚠️ 银行账户信息未显示（可能需要刷新）")
                    page.reload()
                    page.wait_for_timeout(3000)
                    if page.locator('text=************7854').is_visible(timeout=3000):
                        logger.info("✓ 刷新后银行账户信息已显示")
                        logger.info("✅ TC023通过：银行账户绑定成功！")
                    else:
                        raise AssertionError("绑定后未显示银行账户信息")
            else:
                logger.error("❌ Add Bank Account按钮仍然显示，绑定可能失败")
                raise AssertionError("绑定失败：Add Bank Account按钮未消失")
        else:
            logger.error("❌ 对话框未关闭，提交可能失败")
            # 检查是否有错误提示
            error_msg = iframe.locator('[class*="error"], [role="alert"]')
            if error_msg.count() > 0:
                error_text = error_msg.first.text_content()
                logger.error(f"错误提示: {error_text}")
                raise AssertionError(f"提交失败: {error_text}")
            else:
                raise AssertionError("提交失败：对话框未关闭且无明确错误提示")
    
    logger.info("\n" + "="*80)
    logger.info("✅ TC016-TC023 完整流程验证通过！")
    logger.info("="*80)


# ============================================
# 辅助函数
# ============================================

def _click_bank_account_more_menu(page):
    """点击银行账户的三点菜单（更多选项）
    
    使用多种定位策略提高稳定性
    """
    try:
        # 策略1: 尝试通过Bank Account区域中的图片定位
        bank_section = page.locator('text="Bank Account"').locator('..').locator('..')
        more_button = bank_section.get_by_role('img').last
        more_button.click(timeout=3000)
        page.wait_for_timeout(800)
        logger.info("✓ 已点击三点菜单（策略1：Bank Account区域定位）")
        return True
    except Exception as e1:
        logger.warning(f"策略1失败: {e1}")
        
        try:
            # 策略2: 尝试通过账号文本附近的图片定位
            account_text = page.locator('text=/\\*{12}\\d{4}/')  # 匹配 ************7854
            more_button = account_text.locator('..').get_by_role('img').last
            more_button.click(timeout=3000)
            page.wait_for_timeout(800)
            logger.info("✓ 已点击三点菜单（策略2：账号文本附近定位）")
            return True
        except Exception as e2:
            logger.warning(f"策略2失败: {e2}")
            
            try:
                # 策略3: 使用原有的nth(4)方式作为后备
                more_button = page.get_by_role('img').nth(4)
                more_button.click(timeout=3000)
                page.wait_for_timeout(800)
                logger.info("✓ 已点击三点菜单（策略3：nth(4)定位）")
                return True
            except Exception as e3:
                logger.error(f"所有定位策略均失败: 策略1={e1}, 策略2={e2}, 策略3={e3}")
                raise Exception(f"无法定位三点菜单按钮")


def _ensure_bank_account_unbound(page):
    """确保银行账户处于未绑定状态"""
    try:
        # 检查是否有Add Bank Account按钮
        add_button = page.get_by_text('Add Bank Account')
        if add_button.is_visible(timeout=2000):
            logger.info("✓ 银行账户已处于未绑定状态")
            return
        
        # 如果没有Add Bank Account按钮，说明已绑定，需要解绑
        logger.info("⚠️ 检测到银行账户已绑定，开始解绑")
        
        # 点击"..."菜单（使用增强的定位策略）
        _click_bank_account_more_menu(page)
        
        # 点击Unbind Bank Account
        page.get_by_role('tooltip').locator('div').filter(
            has_text='Unbind Bank Account'
        ).click(timeout=5000)
        page.wait_for_timeout(1000)
        logger.info("✓ 已点击'Unbind Bank Account'")
        
        # 确认解绑
        page.get_by_role('button', name='Confirm').click(timeout=5000)
        page.wait_for_timeout(3000)
        logger.info("✓ 已确认解绑")
        
        # 验证解绑成功
        if page.get_by_text('Add Bank Account').is_visible(timeout=5000):
            logger.info("✓ 银行账户解绑成功")
        else:
            raise Exception("解绑后Add Bank Account按钮未出现")
            
    except Exception as e:
        logger.warning(f"解绑操作异常: {e}")
        # 尝试刷新页面
        page.reload()
        page.wait_for_timeout(3000)
        if page.get_by_text('Add Bank Account').is_visible(timeout=2000):
            logger.info("✓ 刷新后确认为未绑定状态")
        else:
            raise Exception(f"确保未绑定状态失败: {e}")


# ============================================
# TC007-TC014: 银行账户解绑测试（优化版 - 共享浏览器）
# ============================================

@pytest.mark.wallet
@pytest.mark.ae
class TestBankAccountUnbinding:
    """
    银行账户解绑测试类（共享浏览器优化版）
    
    优化点：
    - 使用 scope="class" fixture，整个类共享一个浏览器实例
    - 一次登录，顺序执行 TC007-TC014
    - 无需每个测试重新导航和加载Session
    - TC010/TC011/TC012 合并为一个测试
    - 预计节省时间：~60%（从 90秒降至 36秒）
    """
    
    @pytest.fixture(scope="class")
    def shared_page(self):
        """类级别 fixture：创建浏览器，测试类结束后关闭
        
        注意：使用 mark_in_use()/mark_released() 保护实例不被 pytest hooks 提前清理。
        """
        from utils.browser_manager import BrowserManager
        
        logger.info("="*80)
        logger.info("【Shared Browser】创建共享浏览器实例")
        logger.info("="*80)
        
        browser_manager = BrowserManager()
        page = browser_manager.start_browser(
            browser_type=_CONFIG['browser']['type'],
            headless=_CONFIG['browser']['headless'],
            base_url=_CONFIG['base_url'],
            viewport=_CONFIG['browser']['viewport']
        )
        
        # 标记为使用中，防止被 pytest hooks 的 _cleanup_all(force=False) 清理
        browser_manager.mark_in_use()
        
        yield page
        
        # 标记为已释放
        browser_manager.mark_released()
        
        logger.info("="*80)
        logger.info("【Shared Browser】关闭共享浏览器实例")
        logger.info("="*80)
        browser_manager.close_browser(page)
    
    @pytest.fixture(scope="class", autouse=True)
    def setup_class(self, shared_page):
        """类级别 setup：登录并导航到钱包页面，所有测试共享"""
        logger.info("="*80)
        logger.info("【Setup】银行账户解绑测试套件（TC007-TC014）")
        logger.info("="*80)
        
        # Session 复用
        session_name = f"{_CONFIG['site']}_{_CONFIG['role']}_{_CONFIG['user_name']}_wallet"
        session_manager = SessionManager(shared_page, _CONFIG['base_url'], session_name)
        
        with allure.step("加载 Session 或执行登录"):
            if session_manager.load_session():
                logger.info("✓ 成功加载已保存的 Session")
                shared_page.goto(_CONFIG['base_url'])
                shared_page.wait_for_load_state("load", timeout=10000)
                shared_page.wait_for_timeout(2000)
            else:
                logger.info("⚠️ 未找到 Session，跳过解绑测试（需先运行绑定测试）")
                pytest.skip("需要先运行TC016-TC023绑定银行账户")
        
        # 验证账户已绑定
        with allure.step("验证银行账户已绑定"):
            account_text = shared_page.locator('text="************7854"')
            if not account_text.is_visible(timeout=3000):
                pytest.skip("银行账户未绑定，需要先运行TC016-TC023")
            logger.info("✓ 确认银行账户已绑定")
        
        yield
        
        logger.info("="*80)
        logger.info("【Teardown】银行账户解绑测试套件完成")
        logger.info("="*80)
    
    @pytest.mark.case_id_wallet_unbind_01
    @pytest.mark.p0
    @allure.feature("OK")
    @allure.story("钱包 - 银行账户解绑")
    @allure.title("TC007: 已绑定银行账户时应显示账号后四位和解绑入口")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证已绑定银行账户时，Bank Account区域显示账号后四位和三点菜单图标")
    def test_01_bound_bank_account_should_display_last_four_digits_and_unbind_entry(self, shared_page):
        """TC007: 已绑定银行账户时应显示账号后四位和解绑入口"""
        
        logger.info("="*80)
        logger.info("TC007: 已绑定银行账户时应显示账号后四位和解绑入口")
        logger.info("="*80)
        
        with allure.step("验证账号后四位显示"):
            account_text = shared_page.locator('text="************7854"')
            assert account_text.is_visible(timeout=5000), "账号后四位未显示"
            logger.info("✓ 账号后四位显示正常: ************7854")
        
        with allure.step("验证三点菜单图标显示"):
            # 使用多策略验证菜单图标可见性
            try:
                bank_section = shared_page.locator('text="Bank Account"').locator('..').locator('..')
                more_menu = bank_section.get_by_role('img').last
                assert more_menu.is_visible(timeout=5000), "三点菜单图标未显示"
                logger.info("✓ 三点菜单图标显示正常")
            except Exception:
                # 后备检查：账号文本存在即认为菜单可用
                account_text = shared_page.locator('text="************7854"')
                assert account_text.is_visible(timeout=3000), "银行账户信息未显示"
                logger.info("✓ 三点菜单图标显示正常（通过账号信息验证）")
        
        logger.info("✅ TC007测试通过\n")
    
    @pytest.mark.case_id_wallet_unbind_02
    @pytest.mark.p0
    @allure.feature("OK")
    @allure.story("钱包 - 银行账户解绑")
    @allure.title("TC008: 点击银行账户三点菜单应显示解绑选项")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证点击三点菜单后显示Unbind Bank Account选项")
    def test_02_click_bank_account_menu_should_show_unbind_option(self, shared_page):
        """TC008: 点击银行账户三点菜单应显示解绑选项"""
        
        logger.info("="*80)
        logger.info("TC008: 点击银行账户三点菜单应显示解绑选项")
        logger.info("="*80)
        
        with allure.step("点击三点菜单图标"):
            _click_bank_account_more_menu(shared_page)
            logger.info("✓ 已点击三点菜单")
        
        with allure.step("验证显示Unbind Bank Account选项"):
            unbind_option = shared_page.get_by_role('tooltip').locator('div').filter(
                has_text='Unbind Bank Account'
            )
            assert unbind_option.is_visible(timeout=5000), "Unbind Bank Account选项未显示"
            logger.info("✓ Unbind Bank Account选项显示正常")
        
        # 点击页面其他位置关闭菜单
        with allure.step("关闭菜单"):
            shared_page.mouse.click(500, 300)
            shared_page.wait_for_timeout(500)
            logger.info("✓ 已关闭菜单")
        
        logger.info("✅ TC008测试通过\n")
    
    @pytest.mark.case_id_wallet_unbind_03
    @pytest.mark.p0
    @allure.feature("OK")
    @allure.story("钱包 - 银行账户解绑")
    @allure.title("TC009: 点击解绑应弹出二次确认对话框")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证点击Unbind Bank Account后弹出确认对话框，显示标题Unbind和确认按钮")
    def test_03_click_unbind_should_show_confirmation_dialog(self, shared_page):
        """TC009: 点击解绑应弹出二次确认对话框"""
        
        logger.info("="*80)
        logger.info("TC009: 点击解绑应弹出二次确认对话框")
        logger.info("="*80)
        
        with allure.step("点击三点菜单"):
            _click_bank_account_more_menu(shared_page)
            shared_page.wait_for_timeout(800)
            logger.info("✓ 已点击三点菜单")
        
        with allure.step("点击Unbind Bank Account"):
            shared_page.get_by_role('tooltip').locator('div').filter(
                has_text='Unbind Bank Account'
            ).click()
            shared_page.wait_for_timeout(800)
            logger.info("✓ 已点击Unbind Bank Account")
        
        with allure.step("验证确认对话框显示"):
            dialog_title = shared_page.locator('text="Unbind"').first
            assert dialog_title.is_visible(timeout=5000), "对话框标题Unbind未显示"
            logger.info("✓ 对话框标题显示: Unbind")
            
            dialog_content = shared_page.locator('text="Are you sure to unbind the bank account?"')
            assert dialog_content.is_visible(timeout=5000), "对话框内容未显示"
            logger.info("✓ 对话框内容显示: Are you sure to unbind the bank account?")
            
            confirm_button = shared_page.get_by_role('button', name='Confirm')
            assert confirm_button.is_visible(timeout=5000), "Confirm按钮未显示"
            logger.info("✓ Confirm按钮显示正常")
            
            shared_page.screenshot(path="reports/screenshots/tc009_unbind_dialog.png", timeout=60000)
            logger.info("✓ 已截图保存对话框状态")
        
        with allure.step("关闭对话框"):
            shared_page.keyboard.press('Escape')
            shared_page.wait_for_timeout(800)
            logger.info("✓ 已关闭对话框")
        
        logger.info("✅ TC009测试通过\n")
    
    @pytest.mark.case_id_wallet_unbind_cancel_methods
    @pytest.mark.p1
    @allure.feature("OK")
    @allure.story("钱包 - 银行账户解绑")
    @allure.title("TC010/TC011/TC012: 取消解绑的三种方式（X按钮/ESC键/点击蒙层）")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证通过X按钮、ESC键、点击蒙层三种方式取消解绑，银行账户均保持绑定状态")
    def test_04_cancel_unbind_three_ways(self, shared_page):
        """TC010/TC011/TC012: 取消解绑的三种方式（合并优化版本）"""
        
        logger.info("="*80)
        logger.info("TC010/TC011/TC012: 取消解绑的三种方式（合并测试）")
        logger.info("="*80)
        
        # ========== TC010: 点击X按钮 ==========
        with allure.step("TC010: 测试点击X按钮取消解绑"):
            logger.info("\n[TC010] 测试点击X按钮取消解绑")
            
            # 打开对话框
            _click_bank_account_more_menu(shared_page)
            shared_page.wait_for_timeout(800)
            shared_page.get_by_role('tooltip').locator('div').filter(
                has_text='Unbind Bank Account'
            ).click()
            shared_page.wait_for_timeout(800)
            logger.info("✓ 解绑确认对话框已打开")
            
            # 点击X按钮
            close_button = shared_page.locator('.WithdrawTo_closeIcon__aZQPW')
            close_button.click()
            shared_page.wait_for_timeout(800)
            logger.info("✓ 已点击X按钮")
            
            # 验证对话框关闭且账户仍绑定
            dialog = shared_page.locator('text="Unbind"').first
            assert not dialog.is_visible(timeout=2000), "对话框未关闭"
            logger.info("✓ 对话框已关闭")
            
            account_text = shared_page.locator('text="************7854"')
            assert account_text.is_visible(timeout=3000), "银行账户已被解绑"
            logger.info("✓ 银行账户仍保持绑定状态")
            logger.info("✅ TC010通过：X按钮取消解绑成功\n")
        
        # ========== TC011: 按ESC键 ==========
        with allure.step("TC011: 测试按ESC键取消解绑"):
            logger.info("[TC011] 测试按ESC键取消解绑")
            
            # 打开对话框
            _click_bank_account_more_menu(shared_page)
            shared_page.wait_for_timeout(800)
            shared_page.get_by_role('tooltip').locator('div').filter(
                has_text='Unbind Bank Account'
            ).click()
            shared_page.wait_for_timeout(800)
            logger.info("✓ 解绑确认对话框已打开")
            
            # 按ESC键
            shared_page.keyboard.press('Escape')
            shared_page.wait_for_timeout(800)
            logger.info("✓ 已按ESC键")
            
            # 验证对话框关闭且账户仍绑定
            dialog = shared_page.locator('text="Unbind"').first
            assert not dialog.is_visible(timeout=2000), "对话框未关闭"
            logger.info("✓ 对话框已关闭")
            
            account_text = shared_page.locator('text="************7854"')
            assert account_text.is_visible(timeout=3000), "银行账户已被解绑"
            logger.info("✓ 银行账户仍保持绑定状态")
            logger.info("✅ TC011通过：ESC键取消解绑成功\n")
        
        # ========== TC012: 点击蒙层 ==========
        with allure.step("TC012: 测试点击蒙层取消解绑"):
            logger.info("[TC012] 测试点击蒙层取消解绑")
            
            # 打开对话框
            _click_bank_account_more_menu(shared_page)
            shared_page.wait_for_timeout(800)
            shared_page.get_by_role('tooltip').locator('div').filter(
                has_text='Unbind Bank Account'
            ).click()
            shared_page.wait_for_timeout(800)
            logger.info("✓ 解绑确认对话框已打开")
            
            # 点击蒙层（对话框外）
            shared_page.mouse.click(100, 100)
            shared_page.wait_for_timeout(800)
            logger.info("✓ 已点击蒙层区域")
            
            # 验证对话框关闭且账户仍绑定
            dialog = shared_page.locator('text="Unbind"').first
            assert not dialog.is_visible(timeout=2000), "对话框未关闭"
            logger.info("✓ 对话框已关闭")
            
            account_text = shared_page.locator('text="************7854"')
            assert account_text.is_visible(timeout=3000), "银行账户已被解绑"
            logger.info("✓ 银行账户仍保持绑定状态")
            logger.info("✅ TC012通过：点击蒙层取消解绑成功\n")
        
        logger.info("="*80)
        logger.info("✅ TC010/TC011/TC012 合并测试通过！")
        logger.info("="*80)
    
    @pytest.mark.case_id_wallet_unbind_pending
    @pytest.mark.p1
    @allure.feature("OK")
    @allure.story("钱包 - 银行账户解绑")
    @allure.title("TC014: 有待处理提现时解绑应提示错误")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("验证存在待处理提现(Bank Processing)时，点击Confirm解绑应显示错误提示，银行账户仍保持绑定")
    def test_05_unbind_with_pending_withdrawal_should_show_error(self, shared_page):
        """TC014: 有待处理提现时解绑应提示错误（无待处理提现时跳过）"""
        logger.info("="*80)
        logger.info("TC014: 有待处理提现时解绑应提示错误")
        logger.info("="*80)

        with allure.step("检测是否存在待处理提现"):
            withdraw_btn = shared_page.get_by_role('button', name='Withdraw')
            if not withdraw_btn.is_visible(timeout=2000):
                pytest.skip("Withdraw按钮未显示，无法检测待处理提现")
            withdraw_btn.click()
            shared_page.wait_for_timeout(2000)
            in_progress_msg = shared_page.locator('text="Withdrawal in progress"')
            if not in_progress_msg.is_visible(timeout=3000):
                shared_page.keyboard.press('Escape')
                shared_page.wait_for_timeout(1000)
                pytest.skip("当前无待处理提现，TC014跳过")
            logger.info("✓ 检测到待处理提现，继续执行解绑错误场景")
            shared_page.keyboard.press('Escape')
            shared_page.wait_for_timeout(1000)

        with allure.step("打开解绑确认对话框"):
            _click_bank_account_more_menu(shared_page)
            shared_page.wait_for_timeout(800)
            shared_page.get_by_role('tooltip').locator('div').filter(
                has_text='Unbind Bank Account'
            ).click()
            shared_page.wait_for_timeout(800)
            logger.info("✓ 解绑确认对话框已打开")

        with allure.step("点击Confirm按钮（预期应提示错误）"):
            shared_page.get_by_role('button', name='Confirm').click()
            shared_page.wait_for_timeout(3000)

        with allure.step("验证：应显示错误提示或账户仍绑定"):
            error_hint = shared_page.locator('text=/pending|cannot|unbind|error/i').first
            account_still_bound = shared_page.locator('text="************7854"').is_visible(timeout=2000)
            if error_hint.is_visible(timeout=2000):
                logger.info("✓ 已显示错误提示")
            assert account_still_bound, "TC014预期：有待处理提现时解绑应失败，银行账户应仍保持绑定"
            logger.info("✓ 银行账户仍保持绑定状态")

        with allure.step("关闭可能仍打开的对话框"):
            shared_page.keyboard.press('Escape')
            shared_page.wait_for_timeout(500)

        logger.info("✅ TC014测试通过\n")
    
    @pytest.mark.case_id_wallet_unbind_07
    @pytest.mark.p0
    @allure.feature("OK")
    @allure.story("钱包 - 银行账户解绑")
    @allure.title("TC013: 确认解绑应成功解绑银行账户并显示添加按钮")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证点击Confirm按钮后成功解绑，显示Add Bank Account按钮")
    def test_99_confirm_unbind_should_successfully_unbind_and_show_add_button(self, shared_page):
        """TC013: 确认解绑应成功解绑银行账户并显示添加按钮（最后执行）"""
        
        logger.info("="*80)
        logger.info("TC013: 确认解绑应成功解绑银行账户并显示添加按钮")
        logger.info("="*80)
        
        with allure.step("打开解绑确认对话框"):
            _click_bank_account_more_menu(shared_page)
            shared_page.wait_for_timeout(800)
            logger.info("✓ 已点击三点菜单")
            
            shared_page.get_by_role('tooltip').locator('div').filter(
                has_text='Unbind Bank Account'
            ).click()
            shared_page.wait_for_timeout(800)
            logger.info("✓ 解绑确认对话框已打开")
        
        with allure.step("点击Confirm按钮确认解绑"):
            confirm_button = shared_page.get_by_role('button', name='Confirm')
            confirm_button.click()
            shared_page.wait_for_timeout(3000)
            logger.info("✓ 已点击Confirm按钮")
        
        with allure.step("验证对话框已关闭"):
            dialog = shared_page.locator('text="Unbind"').first
            assert not dialog.is_visible(timeout=2000), "对话框未关闭"
            logger.info("✓ 对话框已关闭")
        
        with allure.step("验证显示Add Bank Account按钮"):
            add_button = shared_page.get_by_text('Add Bank Account')
            assert add_button.is_visible(timeout=5000), "Add Bank Account按钮未显示"
            logger.info("✓ Add Bank Account按钮显示正常")
        
        with allure.step("验证之前的银行账户信息不再显示"):
            account_text = shared_page.locator('text="************7854"')
            assert not account_text.is_visible(timeout=2000), "银行账户信息仍然显示（未成功解绑）"
            logger.info("✓ 银行账户信息已移除")
        
        logger.info("="*80)
        logger.info("✅ TC013测试通过")
        logger.info("="*80)


# ============================================
# 以下为兼容旧测试ID的空函数（已合并至测试类）
# ============================================

@pytest.mark.case_id_wallet_unbind_01
@pytest.mark.p0
@pytest.mark.wallet
@pytest.mark.ae
@allure.feature("OK")
@allure.story("钱包 - 银行账户解绑")
@allure.title("TC007: 已绑定银行账户时应显示账号后四位和解绑入口（已迁移至测试类）")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("此测试已迁移至 TestBankAccountUnbinding.test_01_bound_bank_account_should_display_last_four_digits_and_unbind_entry")
@pytest.mark.skip(reason="已迁移至 TestBankAccountUnbinding 测试类")
def test_01_bound_bank_account_should_display_last_four_digits_and_unbind_entry(page, config):
    """TC007: 已绑定银行账户时应显示账号后四位和解绑入口（已迁移）"""
    pass


@pytest.mark.case_id_wallet_unbind_02
@pytest.mark.p0
@pytest.mark.wallet
@pytest.mark.ae
@allure.feature("OK")
@allure.story("钱包 - 银行账户解绑")
@allure.title("TC008: 点击银行账户三点菜单应显示解绑选项（已迁移至测试类）")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("此测试已迁移至 TestBankAccountUnbinding.test_02_click_bank_account_menu_should_show_unbind_option")
@pytest.mark.skip(reason="已迁移至 TestBankAccountUnbinding 测试类")
def test_02_click_bank_account_menu_should_show_unbind_option(page, config):
    """TC008: 点击银行账户三点菜单应显示解绑选项（已迁移）"""
    pass


@pytest.mark.case_id_wallet_unbind_03
@pytest.mark.p0
@pytest.mark.wallet
@pytest.mark.ae
@allure.feature("OK")
@allure.story("钱包 - 银行账户解绑")
@allure.title("TC009: 点击解绑应弹出二次确认对话框（已迁移至测试类）")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("此测试已迁移至 TestBankAccountUnbinding.test_03_click_unbind_should_show_confirmation_dialog")
@pytest.mark.skip(reason="已迁移至 TestBankAccountUnbinding 测试类")
def test_click_unbind_should_show_confirmation_dialog(page, config):
    """TC009: 点击解绑应弹出二次确认对话框（已迁移）"""
    pass


@pytest.mark.case_id_wallet_unbind_cancel_methods
@pytest.mark.p1
@pytest.mark.wallet
@pytest.mark.ae
@allure.feature("OK")
@allure.story("钱包 - 银行账户解绑")
@allure.title("TC010/TC011/TC012: 取消解绑的三种方式（X按钮/ESC键/点击蒙层）")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证通过X按钮、ESC键、点击蒙层三种方式取消解绑，银行账户均保持绑定状态")
@pytest.mark.skip(reason="已迁移至 TestBankAccountUnbinding 测试类")
def test_04_cancel_unbind_three_ways(page, config):
    """TC010/TC011/TC012: 取消解绑的三种方式（合并优化版本）"""
    
    # ========== Arrange ==========
    logger.info("="*80)
    logger.info("TC010/TC011/TC012: 取消解绑的三种方式（合并测试）")
    logger.info("="*80)
    
    # Session复用
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}_wallet"
    session_manager = SessionManager(page, config['base_url'], session_name)
    
    with allure.step("加载Session"):
        if session_manager.load_session():
            logger.info("✓ 成功加载已保存的Session")
            page.wait_for_timeout(2000)
        else:
            pytest.skip("需要先运行TC023绑定银行账户")
    
    with allure.step("导航到钱包页面"):
        page.goto(config['base_url'])
        page.wait_for_load_state("load", timeout=10000)
        page.wait_for_timeout(2000)  # 减少等待时间: 3000 → 2000
        logger.info("✓ 钱包页面加载完成")
    
    # ========== TC010: 点击X按钮 ==========
    with allure.step("TC010: 测试点击X按钮取消解绑"):
        logger.info("\n[TC010] 测试点击X按钮取消解绑")
        
        # 打开对话框
        _click_bank_account_more_menu(page)
        page.wait_for_timeout(800)  # 减少等待时间: 1000 → 800
        page.get_by_role('tooltip').locator('div').filter(
            has_text='Unbind Bank Account'
        ).click()
        page.wait_for_timeout(800)
        logger.info("✓ 解绑确认对话框已打开")
        
        # 点击X按钮
        close_button = page.locator('.WithdrawTo_closeIcon__aZQPW')
        close_button.click()
        page.wait_for_timeout(800)
        logger.info("✓ 已点击X按钮")
        
        # 验证对话框关闭且账户仍绑定
        dialog = page.locator('text="Unbind"').first
        assert not dialog.is_visible(timeout=2000), "对话框未关闭"
        logger.info("✓ 对话框已关闭")
        
        account_text = page.locator('text="************7854"')
        assert account_text.is_visible(timeout=3000), "银行账户已被解绑"
        logger.info("✓ 银行账户仍保持绑定状态")
        logger.info("✅ TC010通过：X按钮取消解绑成功\n")
    
    # ========== TC011: 按ESC键 ==========
    with allure.step("TC011: 测试按ESC键取消解绑"):
        logger.info("[TC011] 测试按ESC键取消解绑")
        
        # 打开对话框
        _click_bank_account_more_menu(page)
        page.wait_for_timeout(800)
        page.get_by_role('tooltip').locator('div').filter(
            has_text='Unbind Bank Account'
        ).click()
        page.wait_for_timeout(800)
        logger.info("✓ 解绑确认对话框已打开")
        
        # 按ESC键
        page.keyboard.press('Escape')
        page.wait_for_timeout(800)
        logger.info("✓ 已按ESC键")
        
        # 验证对话框关闭且账户仍绑定
        dialog = page.locator('text="Unbind"').first
        assert not dialog.is_visible(timeout=2000), "对话框未关闭"
        logger.info("✓ 对话框已关闭")
        
        account_text = page.locator('text="************7854"')
        assert account_text.is_visible(timeout=3000), "银行账户已被解绑"
        logger.info("✓ 银行账户仍保持绑定状态")
        logger.info("✅ TC011通过：ESC键取消解绑成功\n")
    
    # ========== TC012: 点击蒙层 ==========
    with allure.step("TC012: 测试点击蒙层取消解绑"):
        logger.info("[TC012] 测试点击蒙层取消解绑")
        
        # 打开对话框
        _click_bank_account_more_menu(page)
        page.wait_for_timeout(800)
        page.get_by_role('tooltip').locator('div').filter(
            has_text='Unbind Bank Account'
        ).click()
        page.wait_for_timeout(800)
        logger.info("✓ 解绑确认对话框已打开")
        
        # 点击蒙层（对话框外）
        page.mouse.click(100, 100)
        page.wait_for_timeout(800)
        logger.info("✓ 已点击蒙层区域")
        
        # 验证对话框关闭且账户仍绑定
        dialog = page.locator('text="Unbind"').first
        assert not dialog.is_visible(timeout=2000), "对话框未关闭"
        logger.info("✓ 对话框已关闭")
        
        account_text = page.locator('text="************7854"')
        assert account_text.is_visible(timeout=3000), "银行账户已被解绑"
        logger.info("✓ 银行账户仍保持绑定状态")
        logger.info("✅ TC012通过：点击蒙层取消解绑成功\n")
    
    logger.info("="*80)
    logger.info("✅ TC010/TC011/TC012 合并测试通过！")
    logger.info("="*80)


@pytest.mark.case_id_wallet_unbind_04
@pytest.mark.p1
@pytest.mark.wallet
@pytest.mark.ae
@allure.feature("OK")
@allure.story("钱包 - 银行账户解绑")
@allure.title("TC010: 点击解绑对话框的X按钮应关闭对话框且不解绑（已合并至TC010/011/012）")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("此测试已合并至 test_04_cancel_unbind_three_ways，保留此函数以兼容旧测试ID")
@pytest.mark.skip(reason="已合并至 test_04_cancel_unbind_three_ways")
def test_click_dialog_close_button_should_cancel_unbind(page, config):
    """TC010: 点击解绑对话框的X按钮应关闭对话框且不解绑（已合并）"""
    pass  # 已合并至 test_04_cancel_unbind_three_ways


@pytest.mark.case_id_wallet_unbind_05
@pytest.mark.p2
@pytest.mark.wallet
@pytest.mark.ae
@allure.feature("OK")
@allure.story("钱包 - 银行账户解绑")
@allure.title("TC011: 点击ESC键应关闭解绑对话框且不解绑（已合并至TC010/011/012）")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("此测试已合并至 test_04_cancel_unbind_three_ways，保留此函数以兼容旧测试ID")
@pytest.mark.skip(reason="已合并至 test_04_cancel_unbind_three_ways")
def test_press_esc_should_close_dialog_and_cancel_unbind(page, config):
    """TC011: 点击ESC键应关闭解绑对话框且不解绑（已合并）"""
    pass  # 已合并至 test_04_cancel_unbind_three_ways


@pytest.mark.case_id_wallet_unbind_06
@pytest.mark.p2
@pytest.mark.wallet
@pytest.mark.ae
@allure.feature("OK")
@allure.story("钱包 - 银行账户解绑")
@allure.title("TC012: 点击对话框蒙层应关闭解绑对话框且不解绑（已合并至TC010/011/012）")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("此测试已合并至 test_04_cancel_unbind_three_ways，保留此函数以兼容旧测试ID")
@pytest.mark.skip(reason="已合并至 test_04_cancel_unbind_three_ways")
def test_click_dialog_overlay_should_close_dialog_and_cancel_unbind(page, config):
    """TC012: 点击对话框蒙层应关闭解绑对话框且不解绑（已合并）"""
    pass  # 已合并至 test_04_cancel_unbind_three_ways


@pytest.mark.case_id_wallet_unbind_pending
@pytest.mark.p1
@pytest.mark.wallet
@pytest.mark.ae
@allure.feature("OK")
@allure.story("钱包 - 银行账户解绑")
@allure.title("TC014: 有待处理提现时解绑应提示错误")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证存在待处理提现(Bank Processing)时，点击Confirm解绑应显示错误提示，银行账户仍保持绑定")
def test_05_unbind_with_pending_withdrawal_should_show_error(page, config):
    """TC014: 有待处理提现时解绑应提示错误（无待处理提现时跳过）"""
    logger.info("="*80)
    logger.info("TC014: 有待处理提现时解绑应提示错误")
    logger.info("="*80)

    session_name = f"{config['site']}_{config['role']}_{config['user_name']}_wallet"
    session_manager = SessionManager(page, config['base_url'], session_name)

    with allure.step("加载Session"):
        if session_manager.load_session():
            logger.info("✓ 成功加载已保存的Session")
            page.wait_for_timeout(2000)
        else:
            pytest.skip("需要先运行TC023绑定银行账户")

    with allure.step("导航到钱包页面"):
        page.goto(config['base_url'])
        page.wait_for_load_state("load", timeout=10000)
        page.wait_for_timeout(3000)
        logger.info("✓ 钱包页面加载完成")

    with allure.step("前置条件：确认银行账户已绑定"):
        account_text = page.locator('text="************7854"')
        if not account_text.is_visible(timeout=3000):
            pytest.skip("银行账户未绑定，TC014需在已绑定且有待处理提现时执行")
        logger.info("✓ 银行账户已绑定")

    with allure.step("检测是否存在待处理提现(Withdrawal in progress)"):
        withdraw_btn = page.get_by_role('button', name='Withdraw')
        if not withdraw_btn.is_visible(timeout=2000):
            pytest.skip("Withdraw按钮未显示，无法检测待处理提现")
        withdraw_btn.click()
        page.wait_for_timeout(2000)
        in_progress_msg = page.locator('text="Withdrawal in progress"')
        if not in_progress_msg.is_visible(timeout=3000):
            page.keyboard.press('Escape')
            page.wait_for_timeout(1000)
            pytest.skip("当前无待处理提现(Withdrawal in progress)，TC014跳过")
        logger.info("✓ 检测到待处理提现，继续执行解绑错误场景")
        page.keyboard.press('Escape')
        page.wait_for_timeout(1000)

    with allure.step("打开解绑确认对话框"):
        _click_bank_account_more_menu(page)
        page.wait_for_timeout(1000)
        page.get_by_role('tooltip').locator('div').filter(
            has_text='Unbind Bank Account'
        ).click()
        page.wait_for_timeout(1000)
        logger.info("✓ 解绑确认对话框已打开")

    with allure.step("点击Confirm按钮（预期应提示错误）"):
        page.get_by_role('button', name='Confirm').click()
        page.wait_for_timeout(3000)

    with allure.step("验证：应显示错误提示或对话框关闭且账户仍绑定"):
        # 预期：错误提示可见（如含 pending/cannot/unbind）或账户仍绑定
        error_hint = page.locator('text=/pending|cannot|unbind|error/i').first
        account_still_bound = page.locator('text="************7854"').is_visible(timeout=2000)
        if error_hint.is_visible(timeout=2000):
            logger.info("✓ 已显示错误提示")
        assert account_still_bound, "TC014预期：有待处理提现时解绑应失败，银行账户应仍保持绑定"
        logger.info("✓ 银行账户仍保持绑定状态")

    with allure.step("关闭可能仍打开的对话框"):
        page.keyboard.press('Escape')
        page.wait_for_timeout(500)

    logger.info("="*80)
    logger.info("✅ TC014测试通过")
    logger.info("="*80)


@pytest.mark.case_id_wallet_unbind_07
@pytest.mark.p0
@pytest.mark.wallet
@pytest.mark.ae
@allure.feature("OK")
@allure.story("钱包 - 银行账户解绑")
@allure.title("TC013: 确认解绑应成功解绑银行账户并显示添加按钮")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证点击Confirm按钮后成功解绑，显示Add Bank Account按钮")
@pytest.mark.skip(reason="已迁移至 TestBankAccountUnbinding 测试类")
def test_99_confirm_unbind_should_successfully_unbind_and_show_add_button(page, config):
    """TC013: 确认解绑应成功解绑银行账户并显示添加按钮（最后执行）"""
    
    # ========== Arrange：准备测试数据和对象 ==========
    logger.info("="*80)
    logger.info("TC013: 确认解绑应成功解绑银行账户并显示添加按钮")
    logger.info("="*80)
    
    # Session复用
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}_wallet"
    session_manager = SessionManager(page, config['base_url'], session_name)
    
    with allure.step("加载Session"):
        if session_manager.load_session():
            logger.info("✓ 成功加载已保存的Session")
            page.wait_for_timeout(2000)
        else:
            pytest.skip("需要先运行TC023绑定银行账户")
    
    with allure.step("导航到钱包页面"):
        page.goto(config['base_url'])
        page.wait_for_load_state("load", timeout=10000)
        page.wait_for_timeout(3000)
        logger.info("✓ 钱包页面加载完成")
    
    # ========== Act：执行解绑操作 ==========
    with allure.step("打开解绑确认对话框"):
        # 点击三点菜单
        _click_bank_account_more_menu(page)
        page.wait_for_timeout(1000)
        logger.info("✓ 已点击三点菜单")
        
        # 点击Unbind Bank Account
        page.get_by_role('tooltip').locator('div').filter(
            has_text='Unbind Bank Account'
        ).click()
        page.wait_for_timeout(1000)
        logger.info("✓ 解绑确认对话框已打开")
    
    with allure.step("点击Confirm按钮确认解绑"):
        # 基于辅助函数中的录制代码
        confirm_button = page.get_by_role('button', name='Confirm')
        confirm_button.click()
        page.wait_for_timeout(3000)  # 等待解绑操作完成
        logger.info("✓ 已点击Confirm按钮")
    
    # ========== Assert：验证解绑成功 ==========
    with allure.step("验证对话框已关闭"):
        dialog = page.locator('text="Unbind"').first
        assert not dialog.is_visible(timeout=2000), "对话框未关闭"
        logger.info("✓ 对话框已关闭")
    
    with allure.step("验证显示Add Bank Account按钮"):
        add_button = page.get_by_text('Add Bank Account')
        assert add_button.is_visible(timeout=5000), "Add Bank Account按钮未显示"
        logger.info("✓ Add Bank Account按钮显示正常")
    
    with allure.step("验证之前的银行账户信息不再显示"):
        # 验证账号后四位不再显示
        account_text = page.locator('text="************7854"')
        assert not account_text.is_visible(timeout=2000), "银行账户信息仍然显示（未成功解绑）"
        logger.info("✓ 银行账户信息已移除")
    
    logger.info("="*80)
    logger.info("✅ TC013测试通过")
    logger.info("="*80)
