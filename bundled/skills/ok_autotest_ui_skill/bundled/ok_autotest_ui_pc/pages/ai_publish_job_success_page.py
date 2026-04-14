# pages/ai_publish_job_success_page.py
from pages.base_page import BasePage
from utils.logger import setup_logger


# ON状态开关图片文件名（src中包含此字符串）
SWITCH_ON_IMG = "icon_switch_checked"
# OFF状态开关图片文件名（src中包含此字符串）
SWITCH_OFF_IMG = "icon_switch.b4dbfa4c"


class AiPublishJobSuccessPage(BasePage):
    """Job发布成功页 - EasyChat AI开关页面对象（静默执行）"""

    # ---------- 选择器常量 ----------
    _HEADING = "h1"
    _CARD = ".chat-ai-switch"
    _CARD_TITLE = ".ChatAiSwitch_title__fNjbo"
    _CARD_DESC = ".ChatAiSwitch_description__cNDzd"
    _SWITCH_ICON = ".ChatAiSwitch_switchIcon__rIxD3"

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    # ========== 等待与导航 ==========

    def wait_for_success_page(self, timeout: int = 15000):
        """等待发布成功页加载完成（h1 可见）"""
        try:
            self.page.locator(self._HEADING).wait_for(state="visible", timeout=timeout)
        except Exception as e:
            self.logger.error(f"等待成功页失败: {e}")
            raise

    def navigate_to_success_page(self, base_url: str, job_id: str):
        """直接导航到指定 Job 成功页"""
        url = f"{base_url}/biz/en/publish/success?id={job_id}"
        try:
            self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            self.wait_for_success_page()
        except Exception as e:
            self.logger.error(f"导航到成功页失败: {e}")
            raise

    # ========== 页面内容校验 ==========

    def get_heading_text(self) -> str:
        """获取页面 h1 标题文字"""
        return self.page.locator(self._HEADING).inner_text()

    def is_success_page(self) -> bool:
        """判断是否处于发布成功页（URL 包含 /publish/success）"""
        return "/publish/success" in self.page.url

    def is_card_visible(self) -> bool:
        """判断 EasyChat 卡片是否可见"""
        return self.is_visible(self._CARD)

    def get_card_title_text(self) -> str:
        """获取 EasyChat 卡片标题文字"""
        return self.page.locator(self._CARD_TITLE).inner_text()

    def get_card_description_text(self) -> str:
        """获取 EasyChat 卡片描述文字"""
        return self.page.locator(self._CARD_DESC).inner_text()

    # ========== 开关操作 ==========

    def click_switch(self):
        """点击 EasyChat 开关（切换 ON/OFF）"""
        try:
            self.page.locator(self._SWITCH_ICON).click()
            self.page.wait_for_timeout(800)
        except Exception as e:
            self.logger.error(f"点击开关失败: {e}")
            raise

    def get_switch_src(self) -> str:
        """获取开关图标的 src 属性"""
        return self.page.locator(self._SWITCH_ICON).get_attribute("src") or ""

    def is_switch_on(self) -> bool:
        """判断开关是否处于 ON（蓝色/勾选）状态"""
        src = self.get_switch_src()
        return SWITCH_ON_IMG in src

    def is_switch_off(self) -> bool:
        """判断开关是否处于 OFF（灰色）状态"""
        src = self.get_switch_src()
        return SWITCH_OFF_IMG in src and SWITCH_ON_IMG not in src

    def wait_for_switch_on(self, timeout: int = 5000):
        """等待开关变为 ON 状态"""
        self.page.wait_for_function(
            f"() => document.querySelector('{self._SWITCH_ICON}')?.src?.includes('{SWITCH_ON_IMG}')",
            timeout=timeout,
        )

    def wait_for_switch_off(self, timeout: int = 5000):
        """等待开关变为 OFF 状态"""
        self.page.wait_for_function(
            f"() => {{ const s = document.querySelector('{self._SWITCH_ICON}')?.src || ''; "
            f"return s.includes('{SWITCH_OFF_IMG}') && !s.includes('{SWITCH_ON_IMG}'); }}",
            timeout=timeout,
        )

    # ========== 刷新 ==========

    def refresh_page(self):
        """刷新页面并等待 EasyChat 卡片重新出现"""
        try:
            self.page.reload(wait_until="domcontentloaded")
            self.page.wait_for_timeout(2000)
            self.page.locator(self._CARD).wait_for(state="visible", timeout=10000)
        except Exception as e:
            self.logger.error(f"刷新页面失败: {e}")
            raise

    # ========== Job 发布辅助（TC001 用）==========

    def fill_job_basics_and_continue(
        self,
        title: str = "Software Architect",
        salary_min: str = "5000",
        salary_max: str = "10000",
    ):
        """
        填写 Job Basics 页面必填项并点击 Continue。
        - Job Title：输入关键词后点击联想第一项
        - Job Function：点击 Recommendations 第一条推荐项
        - Salary：选 Min/Max（传入纯数字字符串，如 "5000"）
        """
        try:
            # Job Title
            self.page.locator("#title").click()
            keyword = title.split()[0]
            self.page.locator("#title").fill(keyword)
            self.page.wait_for_timeout(1000)
            self.page.get_by_text(title, exact=True).first.click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"填写 Job Title 失败: {e}")
            raise

        try:
            # Job Function - 打开下拉 → 点 "Engineering" 一级 → 点右侧第一个子项
            self.page.locator("div").filter(has_text="Select Job Functions").nth(4).click()
            self.page.wait_for_timeout(1000)
            # 在 form 内精确点击 "Engineering" 一级分类（避免匹配到其他文本）
            self.page.locator("form").get_by_text("Engineering", exact=True).click()
            self.page.wait_for_timeout(800)
            # 点击右侧第一个二级子项 "Aerospace Engineering"
            self.page.get_by_text("Aerospace Engineering").first.click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择 Job Function 失败: {e}")
            raise

        try:
            # Salary Min - 通过 pc-select-text 定位（更稳定）
            salary_selectors = self.page.locator(".pc-select-text")
            # 第0个是 Pay Type，第1个是 Min，第2个是 Max
            salary_selectors.nth(1).click()
            self.page.wait_for_timeout(500)
            self.page.get_by_text(salary_min, exact=True).first.click()
            self.page.wait_for_timeout(300)

            # Salary Max
            salary_selectors.nth(2).click()
            self.page.wait_for_timeout(500)
            self.page.get_by_text(salary_max, exact=True).first.click()
            self.page.wait_for_timeout(300)

            # Continue
            self.page.get_by_role("button", name="Continue").click()
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"填写 Salary/Continue 失败: {e}")
            raise

    def fill_job_description_and_continue(self, description: str):
        """填写 Job Description 并点击 Continue"""
        try:
            # 等待 Job Description 文本框可见，确认已进入 Job Details 步骤
            self.page.locator("#content").wait_for(state="visible", timeout=20000)
            self.page.locator("#content").fill(description)
            self.page.wait_for_timeout(500)
            self.page.get_by_role("button", name="Continue").click()
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"填写 Job Description 失败: {e}")
            raise

    def click_post_button(self):
        """点击 Post 发布按钮，并等待跳转到发布成功页"""
        try:
            self.page.get_by_role("button", name="Post").click()
            self.page.wait_for_url("**/publish/success**", timeout=30000)
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            self.page.wait_for_timeout(2000)
            self.page.locator(self._CARD).wait_for(state="visible", timeout=10000)
        except Exception as e:
            self.logger.error(f"点击 Post 按钮失败: {e}")
            raise
