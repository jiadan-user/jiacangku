# pages/marketplace_post_page.py
import re

from pages.base_page import BasePage
from utils.logger import setup_logger


class MarketplacePostPage(BasePage):
    """Marketplace 发布页面对象（基于MCP录制生成）"""
    
    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()
    
    # ========== 页面元素选择器（基于MCP录制）==========
    
    # === 图片上传相关 ===
    FILE_INPUT = 'input[type="file"]'  # 文件输入框（MCP录制验证）
    IMAGE_COUNTER = ':text-matches("\\d+/9")'  # 图片计数器（MCP录制验证）
    MAIN_BUTTON = "button:has-text('Main')"  # 已上传图片的Main按钮（MCP录制验证）
    DELETE_IMAGE_ICON = "img[alt='delete']"  # 删除图标（MCP录制验证）
    
    # === 表单字段（MCP观察到的ID）===
    TITLE_INPUT = "#title"  # Title输入框
    DESCRIPTION_INPUT = "#content"  # Description输入框
    PRICE_INPUT = "#amount"  # Price输入框
    LOCATION_INPUT = "input[placeholder='Set the location for your post.']"  # Location输入框
    
    # === 分类选择（MCP录制验证）===
    MORE_CATEGORIES_BUTTON = "text='More Categories'"  # More Categories按钮
    BROWSE_CATEGORY_BUTTON = "text='Or browse to find a category'"  # Or browse按钮
    
    # === Delivery Options（MCP录制验证）===
    SELLER_PAYS_OPTION = "paragraph:has-text('Seller pays for postage')"  # Seller pays选项
    BUYER_PAYS_OPTION = "paragraph:has-text('Buyer pays for postage')"  # Buyer pays选项
    ARRANGE_PICKUP_OPTION = "text='Arrange pickup with the buyer'"  # Arrange pickup选项
    
    # === 提交按钮 ===
    POST_BUTTON = "button:has-text('Post')"  # Post按钮（MCP录制验证）
    
    # === 错误提示（MCP观察验证）===
    PICTURE_ERROR_MESSAGE = "text='Please upload a photo before submitting.'"  # 图片必填错误
    
    # ========== 页面操作方法（静默执行）==========
    
    def navigate_to_publish_page(self):
        """
        导航到Marketplace发布页面
        使用直接URL导航（基于MCP录制成功的方式）
        """
        try:
            # 导航到发布页面
            self.page.goto("https://aepub.58v5.cn/biz/en/publish/classified", 
                          wait_until="domcontentloaded", timeout=90000)
            
            # 【关键修复】不要等待 load 事件（可能因慢资源超时）
            # 改为等待关键元素出现，确保页面核心功能已加载
            self.page.wait_for_selector(
                'input[type="file"]',  # 文件上传框（页面核心功能）
                state="visible", 
                timeout=30000
            )
            
            # 额外等待，确保页面完全渲染（包括分类区域）
            # 从截图看，分类区域可能需要更长时间才能渲染出来
            self.page.wait_for_timeout(5000)
            
            # 滚动到页面底部再回到顶部，触发所有区域的渲染
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self.page.wait_for_timeout(1000)
            self.page.evaluate("window.scrollTo(0, 0)")
            self.page.wait_for_timeout(1000)
            
        except Exception as e:
            self.logger.error(f"导航到发布页面失败: {e}")
            raise
    
    def upload_single_image(self, image_path):
        """
        上传单张图片（基于MCP录制的代码）
        
        Args:
            image_path: 图片文件的绝对路径
        
        MCP录制的代码：
        const fileInput = page.locator('input[type="file"]');
        await fileInput.setInputFiles('path/to/image.png');
        """
        try:
            self.page.locator(self.FILE_INPUT).set_input_files(image_path)
            self.page.wait_for_timeout(3000)
        except Exception as e:
            self.logger.error(f"上传图片失败: {e}")
            raise
    
    def upload_multiple_images(self, image_paths):
        """
        上传多张图片（基于MCP录制的代码）
        
        Args:
            image_paths: 图片文件路径列表
        
        MCP录制的代码：
        await fileInput.setInputFiles(['path1.png', 'path2.png', 'path3.png']);
        """
        try:
            self.page.locator(self.FILE_INPUT).set_input_files(image_paths)
            self.page.wait_for_timeout(4000)
        except Exception as e:
            self.logger.error(f"上传多张图片失败: {e}")
            raise
    
    def delete_first_image(self):
        """
        删除第一张已上传的图片（基于MCP录制的代码）
        
        MCP录制的流程：
        1. 点击Main按钮打开图片对话框
        2. 点击删除图标
        
        MCP录制的代码：
        await page.getByRole('button', { name: 'Main' }).first().click();
        await page.getByRole('img', { name: 'delete' }).click();
        """
        try:
            # 点击Main按钮打开图片预览对话框
            self.page.get_by_role("button", name="Main").first.click()
            self.page.wait_for_timeout(1000)
            
            # 点击删除图标
            self.page.get_by_role("img", name="delete").click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"删除图片失败: {e}")
            raise
    
    def fill_title(self, title):
        """
        填写标题
        
        Args:
            title: 标题文本
        """
        try:
            self.page.locator(self.TITLE_INPUT).fill(title)
        except Exception as e:
            self.logger.error(f"填写标题失败: {e}")
            raise
    
    def fill_description(self, description):
        """
        填写描述
        
        Args:
            description: 描述文本
        """
        try:
            self.page.locator(self.DESCRIPTION_INPUT).fill(description)
        except Exception as e:
            self.logger.error(f"填写描述失败: {e}")
            raise
    
    def fill_price(self, price):
        """
        填写价格
        
        Args:
            price: 价格（字符串或数字）
        """
        try:
            self.page.locator(self.PRICE_INPUT).fill(str(price))
        except Exception as e:
            self.logger.error(f"填写价格失败: {e}")
            raise
    
    def click_post_button(self):
        """
        点击Post按钮
        """
        try:
            # 滚动到页面底部确保按钮可见
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self.page.wait_for_timeout(1000)
            
            self.page.get_by_role("button", name="Post").click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击Post按钮失败: {e}")
            raise
    
    def is_picture_error_visible(self, timeout=5000):
        """
        判断图片必填错误提示是否显示（基于MCP观察）
        
        Args:
            timeout: 超时时间（毫秒）
        
        Returns:
            bool: 是否显示错误
        """
        try:
            error_msg = self.page.get_by_text("Please upload a photo before submitting.")
            return error_msg.is_visible(timeout=timeout)
        except Exception:
            return False
    
    def wait_for_image_counter(self, count_text, timeout=5000):
        """
        等待图片计数器显示指定文本（基于MCP录制的验证代码）
        
        Args:
            count_text: 期望的计数器文本，如 "1/9", "3/9"
            timeout: 超时时间（毫秒）
        
        MCP录制的代码：
        await page.getByText("1/9").first().waitFor({ state: 'visible' });
        """
        try:
            self.page.get_by_text(count_text).first.wait_for(state="visible", timeout=timeout)
        except Exception as e:
            self.logger.error(f"等待计数器显示 '{count_text}' 失败: {e}")
            raise

    def _prepare_category_section_after_upload(self):
        """
        上传后分类区异步渲染，等待分类区域加载并滚动到可见位置。
        
        【关键修复】移除 networkidle（在 SPA 中经常超时）
        改为等待分类输入框或 More Categories 按钮出现
        """
        # 先等待图片上传完成的标志（图片计数器或 Main 按钮）
        try:
            self.page.locator('button:has-text("Main")').first.wait_for(
                state="visible", timeout=10000
            )
            self.logger.info("✓ 图片上传完成（检测到 Main 按钮）")
        except Exception:
            self.logger.warning("未检测到 Main 按钮，继续执行")
        
        # 【关键修复】使用 Playwright 显式等待，直到分类区域真正出现
        # 沙箱网络慢，AI 推荐分类需要时间，最多等待 90 秒
        self.logger.info("等待分类区域加载（AI 推荐分类需要时间）...")
        
        category_found = False
        
        # 方案1: 等待 More Categories 按钮（优先，因为这是用户要点击的）
        try:
            more_cat = self.page.get_by_text(re.compile(r"More\s+Categories", re.I)).first
            more_cat.wait_for(state="visible", timeout=90000)  # 显式等待最多 90 秒
            more_cat.scroll_into_view_if_needed(timeout=5000)
            category_found = True
            self.logger.info("✓ More Categories 按钮已出现")
        except Exception as e1:
            self.logger.warning(f"未找到 More Categories 按钮: {e1}")
            
            # 方案2: 等待分类输入框（备选）
            try:
                cat = self.page.locator("#categoryId").first
                cat.wait_for(state="visible", timeout=30000)
                cat.scroll_into_view_if_needed(timeout=5000)
                category_found = True
                self.logger.info("✓ 找到分类输入框 #categoryId")
            except Exception as e2:
                self.logger.warning(f"未找到 #categoryId: {e2}")
        
        # 如果都没找到，保存调试信息
        if not category_found:
            self.logger.error("⚠️ 分类区域未找到，保存调试信息")
            try:
                self.page.screenshot(path="debug_category_not_found.png", full_page=True)
                page_html = self.page.content()
                with open("debug_category_not_found.html", "w", encoding="utf-8") as f:
                    f.write(page_html)
                self.logger.info("✓ 已保存调试文件: debug_category_not_found.png/html")
            except Exception:
                pass
        
        # 额外等待确保页面稳定
        self.page.wait_for_timeout(500)

    def _try_click_category_id_input(self):
        """部分站点需先点分类输入框 #categoryId，More Categories / Or browse 才会挂载到 DOM。"""
        try:
            el = self.page.locator("#categoryId")
            if el.count() == 0:
                return
            el.first.wait_for(state="visible", timeout=20000)
            el.first.scroll_into_view_if_needed(timeout=10000)
            el.first.click(timeout=12000)
            self.page.wait_for_timeout(1200)
            self.logger.info("✓ 已点击 #categoryId 展开分类区")
        except Exception as e:
            self.logger.debug(f"点击 #categoryId 跳过: {e}")

    def _click_more_categories_strategies(self, timeout_ms: int = 90000):
        """依次尝试多种定位方式点击「More Categories」（文案拆节点、非 button 等）。"""
        more_pat = re.compile(r"More\s+Categories", re.I)
        n = 5
        per = max(12000, timeout_ms // n)
        last_err = None
        strategies = [
            ("text=/regex/", lambda: self.page.locator(r"text=/More\s+Categories/i").first),
            ("get_by_text", lambda: self.page.get_by_text(more_pat).first),
            ("role=button", lambda: self.page.get_by_role("button", name=more_pat).first),
            (
                "filter(button,a,span,div)",
                lambda: self.page.locator("button, a, span, div").filter(has_text=more_pat).first,
            ),
            (
                "xpath",
                lambda: self.page.locator(
                    "xpath=(//button|//a|//span|//div)"
                    "[contains(translate(normalize-space(.), "
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), "
                    "'more categories')]"
                ).first,
            ),
        ]
        for name, factory in strategies:
            try:
                loc = factory()
                loc.wait_for(state="visible", timeout=per)
                loc.scroll_into_view_if_needed(timeout=10000)
                self.page.wait_for_timeout(300)
                try:
                    loc.click(timeout=20000)
                except Exception as e:
                    self.logger.warning(f"More Categories ({name}) 常规点击失败: {e}")
                    loc.click(force=True, timeout=20000)
                self.logger.info(f"✓ More Categories 点击成功 ({name})")
                return
            except Exception as e:
                last_err = e
                self.logger.debug(f"More Categories 策略 {name} 未命中: {e}")
        raise last_err if last_err else TimeoutError("More Categories 全部策略失败")

    def _wait_and_click_text(self, pattern: str, label: str, timeout: int = 60000):
        """
        等待文案出现并点击（pattern 为正则）。超时默认 60s，避免分类区加载慢导致 30s 失败。
        点击失败时尝试 force（顶栏/底栏遮挡时）。
        """
        rx = re.compile(pattern, re.I)
        loc = (
            self.page.get_by_text(rx).first
            .or_(self.page.get_by_role("button", name=rx).first)
            .or_(self.page.locator("a, button").filter(has_text=rx).first)
        )
        loc.wait_for(state="visible", timeout=timeout)
        loc.scroll_into_view_if_needed(timeout=15000)
        self.page.wait_for_timeout(400)
        try:
            loc.click(timeout=20000)
        except Exception as e:
            self.logger.warning(f"{label} 常规点击失败，尝试 force 点击: {e}")
            loc.click(force=True, timeout=20000)

    def _try_click_or_browse_only(self, or_browse_pat, timeout_ms: int) -> bool:
        """若「Or browse…」已可见则点击并返回 True。"""
        try:
            ob = self.page.get_by_text(or_browse_pat).first
            ob.wait_for(state="visible", timeout=timeout_ms)
            ob.scroll_into_view_if_needed()
            try:
                ob.click(timeout=15000)
            except Exception as e:
                self.logger.warning(f"Or browse 常规点击失败: {e}")
                ob.click(force=True, timeout=15000)
            self.page.wait_for_timeout(800)
            self.logger.info("✓ 已点击 Or browse（跳过 More Categories）")
            return True
        except Exception:
            return False

    def _open_category_browse_dialog(self, timeout: int = 90000):
        """
        打开「浏览分类」：兼容多种布局。
        - 若已直接展示「Or browse…」则只点它；
        - 否则先点 #categoryId，再尝试 Or browse，再依次尝试「More Categories」多种定位；
        - 最后再点「Or browse」（若上一步未点过）。
        """
        self._prepare_category_section_after_upload()
        self.page.wait_for_timeout(2500)

        or_browse_pat = re.compile(r"Or\s+browse\s+to\s+find\s+a\s+category", re.I)

        # 1) 页面上已有 Or browse
        if self._try_click_or_browse_only(or_browse_pat, timeout_ms=15000):
            return

        # 2) 点分类输入框后再看 Or browse / More Categories
        self._try_click_category_id_input()
        if self._try_click_or_browse_only(or_browse_pat, timeout_ms=12000):
            return

        # 3) More Categories（多策略）
        self.logger.info("步骤: 查找并点击 More Categories")
        self._click_more_categories_strategies(timeout_ms=timeout)
        self.page.wait_for_timeout(1000)

        # 4) 再点 Or browse
        self._wait_and_click_text(
            r"Or\s+browse\s+to\s+find\s+a\s+category",
            "Or browse to find a category",
            timeout=min(45000, timeout),
        )
    
    def select_category_cell_phones_apple(self):
        """
        选择分类：Electronics → Cell Phones → Apple
        
        严格按照MCP录制的代码执行：
        1. 点击 "More Categories"
        2. 点击 "Or browse to find a category"
        3. 依次选择 Electronics → Cell Phones → Apple
        """
        try:
            self._prepare_category_section_after_upload()
            # 步骤1: 点击 "More Categories"
            self.logger.info("步骤1: 点击 'More Categories'")
            self._wait_and_click_text(r"More\s+Categories", "More Categories")
            self.page.wait_for_timeout(1000)

            # 步骤2: 点击 "Or browse to find a category"
            self.logger.info("步骤2: 点击 'Or browse to find a category'")
            self._wait_and_click_text(
                r"Or\s+browse\s+to\s+find\s+a\s+category",
                "Or browse to find a category",
            )
            self.page.wait_for_timeout(1000)
            
            # 步骤3: 选择 Electronics（使用div + regex精确匹配）
            self.logger.info("步骤3: 选择 Electronics")
            self.page.locator("div").filter(has_text=re.compile("^Electronics$")).click()
            self.page.wait_for_timeout(800)
            
            # 步骤4: 选择 Cell Phones（使用div + regex精确匹配）
            self.logger.info("步骤4: 选择 Cell Phones")
            self.page.locator("div").filter(has_text=re.compile("^Cell Phones$")).click()
            self.page.wait_for_timeout(800)
            
            # 步骤5: 选择 Apple（使用span，因为这是最后一级）
            self.logger.info("步骤5: 选择 Apple")
            self.page.locator("span").filter(has_text="Apple").click()
            self.page.wait_for_timeout(800)
            
            self.logger.info("✓ 已选择分类: Electronics → Cell Phones → Apple")
        except Exception as e:
            self.logger.error(f"选择分类失败: {e}")
            self.page.screenshot(path="debug_category_selection_failed.png")
            raise
    
    def select_category_free_stuff(self):
        """
        选择分类：Marketplace → Free Stuff
        
        用于TC017测试不同分类的影响
        """
        try:
            # 点击分类输入框
            category_input = self.page.locator("#categoryId")
            category_input.scroll_into_view_if_needed()
            self.page.wait_for_timeout(500)
            category_input.click(timeout=10000)
            self.page.wait_for_timeout(1000)
            
            # 选择 Marketplace
            self.page.get_by_text("Marketplace", exact=True).click()
            self.page.wait_for_timeout(500)
            
            # 选择 Free Stuff
            self.page.get_by_text("Free Stuff", exact=True).click()
            self.page.wait_for_timeout(1000)
            
            self.logger.info("✓ 已选择分类: Marketplace → Free Stuff")
        except Exception as e:
            self.logger.error(f"选择分类失败: {e}")
            raise
    
    def select_category_via_browse(self, category_path):
        """
        通过浏览方式选择分类（基于MCP录制）
        
        Args:
            category_path: 分类路径列表，如 ["Electronics", "Cell Phones", "Apple"]
        
        MCP录制的完整流程：
        1. 点击 "More Categories"
        2. 点击 "Or browse to find a category"
        3. 依次点击分类路径中的每个分类
        
        MCP录制的示例代码：
        await page.locator('div').filter({ hasText: /^Electronics$/ }).click();
        await page.locator('div').filter({ hasText: /^Cell Phones$/ }).click();
        await page.locator('span').filter({ hasText: 'Apple' }).click();
        """
        try:
            self._prepare_category_section_after_upload()
            self._wait_and_click_text(r"More\s+Categories", "More Categories")
            self.page.wait_for_timeout(1000)

            self._wait_and_click_text(
                r"Or\s+browse\s+to\s+find\s+a\s+category",
                "Or browse to find a category",
            )
            self.page.wait_for_timeout(1000)
            
            # 依次点击分类路径（除了最后一个）
            for i, category in enumerate(category_path):
                if i < len(category_path) - 1:
                    # 中间层级使用div定位器
                    self.page.locator("div").filter(has_text=re.compile(f"^{category}$")).click()
                else:
                    # 最后一层使用span定位器（品牌层级）
                    self.page.locator("span").filter(has_text=category).click()
                self.page.wait_for_timeout(800)
            
            self.logger.info(f"✓ 已选择分类: {' → '.join(category_path)}")
        except Exception as e:
            self.logger.error(f"选择分类失败: {e}")
            raise

    def _click_delivery_option_paragraph(self, text: str):
        """
        点击配送说明段落。发布页底部固定 Post 按钮、顶栏会拦截视口边缘的点击，
        故先滚到视口中部并微上移，再必要时 force 点击。
        """
        loc = self.page.get_by_role("paragraph").filter(has_text=text).first
        loc.wait_for(state="visible", timeout=15000)
        loc.evaluate(
            "el => el.scrollIntoView({ block: 'center', inline: 'nearest' })"
        )
        self.page.wait_for_timeout(400)
        # 固定底栏仍可能盖住目标，再上移一点
        self.page.evaluate("window.scrollBy(0, -100)")
        self.page.wait_for_timeout(300)
        try:
            loc.click(timeout=8000)
        except Exception as e:
            self.logger.warning(f"配送选项常规点击失败，改用 force 点击: {e}")
            loc.click(force=True, timeout=15000)
        self.page.wait_for_timeout(800)
    
    def select_seller_pays_postage(self):
        """
        选择 Delivery Option: "Seller pays for postage"（基于MCP录制 - TC011）
        
        MCP录制的代码：
        await page.getByRole('paragraph').filter({ hasText: 'Seller pays for postage' }).click();
        """
        try:
            self._click_delivery_option_paragraph("Seller pays for postage")
            self.logger.info("✓ 已选择配送选项: Seller pays for postage")
        except Exception as e:
            self.logger.error(f"选择 'Seller pays for postage' 失败: {e}")
            raise
    
    def select_buyer_pays_postage(self):
        """
        选择 Delivery Option: "Buyer pays for postage"（基于MCP录制 - TC012）
        
        MCP录制的代码：
        await page.getByRole('paragraph').filter({ hasText: 'Buyer pays for postage' }).click();
        """
        try:
            self._click_delivery_option_paragraph("Buyer pays for postage")
            self.logger.info("✓ 已选择配送选项: Buyer pays for postage")
        except Exception as e:
            self.logger.error(f"选择 'Buyer pays for postage' 失败: {e}")
            raise
    
    def select_arrange_pickup(self):
        """
        选择 Delivery Option: "Arrange pickup with the buyer"（基于MCP录制 - TC013）
        
        最终方案：
        - Toggle 开关是一个独立的可点击元素，位于文本右侧
        - 必须点击 toggle 本身（不是文本），才能激活它
        - Toggle 从灰色（OFF）变为绿色（ON）表示已激活
        """
        try:
            self.logger.info("尝试激活 'Arrange pickup' toggle开关...")
            
            # 关键：滚动到 "Arrange pickup" 文本，确保其在视口内
            arrange_text = self.page.get_by_text("Arrange pickup with the buyer", exact=True).first
            arrange_text.scroll_into_view_if_needed()
            self.page.wait_for_timeout(1000)
            
            self.logger.info("✓ 已滚动到 'Arrange pickup' 区域")
            
            # 方法：找到包含 "Arrange pickup" 文本的行，然后在这一行中找到toggle（通常是按钮或switch元素）
            # Toggle 通常在文本的右侧，可能是一个 button, [role="switch"], 或特定class的div
            
            # 尝试1: 使用包含特定class的元素（如 switch, toggle等）
            try:
                # 定位包含文本的容器
                container = arrange_text.locator('xpath=ancestor::*[contains(@class, "item") or contains(@class, "row") or position()=1][1]')
                # 在容器中查找toggle（通常有switch/toggle相关class或role）
                toggle = container.locator('[role="switch"], button, [class*="switch"], [class*="toggle"]').last
                toggle.click(force=True)
                self.logger.info("✓ 方法1: 点击 toggle 元素成功")
            except:
                # 尝试2: 点击文本右侧的位置（toggle通常在右侧）
                # 获取文本元素的边界框，然后点击其右侧
                bbox = arrange_text.bounding_box()
                if bbox:
                    # 点击文本右侧约100像素的位置（toggle的大概位置）
                    self.page.mouse.click(bbox['x'] + bbox['width'] + 100, bbox['y'] + bbox['height'] / 2)
                    self.logger.info("✓ 方法2: 点击文本右侧位置成功")
                else:
                    raise Exception("无法获取元素边界框")
            
            self.page.wait_for_timeout(1000)
            
            # 截图确认toggle状态
            self.page.screenshot(path="debug_arrange_pickup_final.png")
            
            self.logger.info("✓ 已选择配送选项: Arrange pickup with the buyer")
        except Exception as e:
            self.logger.error(f"选择 'Arrange pickup with the buyer' 失败: {e}")
            self.page.screenshot(path="debug_arrange_pickup_failed.png")
            raise
    
    def verify_success_page(self, timeout=10000):
        """
        验证提交成功页面（基于MCP录制）

        MCP录制观察到的成功页面特征：
        - URL: https://aepub.58v5.cn/biz/en/publish/success?id=xxxxx
        - Title: "Submitted successfully" (可能有变化)
        - Heading: "Post Submitted!"

        Returns:
            bool: 是否成功跳转到成功页面
        """
        try:
            # 等待URL变化到成功页面
            self.page.wait_for_url("**/publish/success?id=*", timeout=timeout)
            
            # 获取当前页面信息用于日志
            current_url = self.page.url
            page_title = self.page.title()
            
            self.logger.info(f"✓ 页面已跳转到: {current_url}")
            self.logger.info(f"✓ 页面标题: {page_title}")

            # 验证成功提示文本（这是最可靠的标志）
            try:
                success_heading = self.page.get_by_role("heading", name="Post Submitted!")
                success_heading.wait_for(state="visible", timeout=5000)
                self.logger.info("✓ 找到成功提示: 'Post Submitted!'")
            except:
                # 如果找不到 heading，但 URL 已经是 success 页面，也认为成功
                if "/publish/success" in current_url:
                    self.logger.info("✓ URL 确认为成功页面（未找到 heading，但 URL 正确）")
                else:
                    raise

            self.logger.info("✓ 提交成功，页面跳转到成功页")
            return True
        except Exception as e:
            self.logger.error(f"验证成功页面失败: {e}")
            current_url = self.page.url
            self.logger.error(f"当前失败 URL: {current_url}")
            return False

