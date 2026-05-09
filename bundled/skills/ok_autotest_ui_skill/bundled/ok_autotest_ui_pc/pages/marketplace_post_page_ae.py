"""
Marketplace Post Page Object

AE站二手商品发布页面对象
支持图片上传、AI生成描述、动态类别选择、位置选择等功能
"""
import re
from pathlib import Path

_UPLOAD_INPUT_SELECTORS = (
    "input[type=file].upload-input",
    "input.upload-input",
    "form input[type=file]",
    "input[type=file]",
)
from pages.base_page import BasePage
from utils.logger import setup_logger


class MarketplacePostPage(BasePage):
    """Marketplace发布页面对象"""
    
    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()
    
    # ========== 图片上传区域 ==========
    CHOOSE_FILE_BUTTON = "button:has-text('Choose File')"  # 隐藏的按钮
    UPLOAD_AREA = "div:has-text('Upload')"  # 可点击的上传框
    IMAGE_COUNTER = "text=/\\d+\\/9/"
    IMAGE_THUMBNAIL_MAIN = "button:has-text('Main')"
    IMAGE_DELETE_ICON = "img[alt='delete']"
    IMAGE_CLOSE_ICON = "img[alt='close-icon']"
    SET_AS_MAIN_BUTTON = "button:has-text('Set as Main')"
    
    # ========== 基础表单字段 ==========
    TITLE_INPUT = "#title"
    TITLE_COUNTER = "text=/\\d+\\/200/"
    DESCRIPTION_INPUT = "#content"
    PRICE_INPUT = "#amount"
    
    # ========== AI功能按钮 ==========
    WRITE_WITH_AI_BUTTON = "button:has-text('Write with AI')"
    AI_WORKING_BUTTON = "button:has-text('AI is working on it')"
    UNDO_BUTTON = "button:has-text('Undo')"
    SHUFFLE_BUTTON = "button:has-text('Shuffle')"
    POLISH_WITH_AI_BUTTON = "button:has-text('Polish with AI')"
    
    # ========== 类别选择 ==========
    MORE_CATEGORIES_LINK = "text=More Categories"
    CATEGORY_SEARCH_INPUT = "input[placeholder*='category']"
    BROWSE_CATEGORY_LINK = "text=Or browse to find a category"
    CATEGORY_DISPLAY = "text=/Marketplace.*/"
    
    # ========== 详情字段（Details - 动态显示） ==========
    CONDITION_EXCELLENT = "text=Excellent"
    CONDITION_NEW = "text=New"
    STORAGE_128GB = "text=128 GB"
    ORIGINALITY_ORIGINAL = "text=100% Original"
    BATTERY_90_PLUS = "text=Battery 90%+"
    
    # ========== 交付选项 ==========
    DELIVERY_SELLER_PAYS = "paragraph:has-text('Seller pays for postage')"
    DELIVERY_BUYER_PAYS = "paragraph:has-text('Buyer pays for postage')"
    DELIVERY_NO_DELIVERY = "paragraph:has-text('No delivery required')"
    DELIVERY_ARRANGE_PICKUP = "text=Arrange pickup with the buyer"
    
    # ========== 位置字段 ==========
    LOCATION_INPUT = "input[placeholder*='location']"
    LOCATE_ME_BUTTON = "text=Locate me"
    ZOOM_IN_BUTTON = "button[aria-label='Zoom in']"
    ZOOM_OUT_BUTTON = "button[aria-label='Zoom out']"
    
    # ========== 操作按钮 ==========
    SAVE_DRAFT_BUTTON = "text=Save the draft"
    POST_BUTTON = "button:has-text('Post')"
    
    # ========== 验证错误提示 ==========
    TITLE_ERROR = "text=Please enter a title before submitting."
    DESCRIPTION_ERROR = "text=Please enter the description before submitting, description must be at least 12 characters."
    CATEGORY_ERROR = "text=Please fill out this field."
    PRICE_ERROR = "text=Please fill out this field."
    DRAFT_SAVED_ALERT = "text=Draft saved"
    
    # ========== 页面导航方法 ==========
    
    def navigate_to_marketplace_post_page(self):
        """
        导航到Marketplace发布页面
        路径：首页 → 点击'···' → 点击'Post' → 点击'Marketplace'
        """
        try:
            self.goto("/en/city-abu-dhabi/", timeout=30000)
            self.wait_for_page_load()
            
            self.page.locator("text=···").click()
            self.page.wait_for_timeout(1000)
            
            self.page.get_by_text("Post", exact=True).click()
            self.page.wait_for_timeout(1000)
            
            self.page.get_by_text("Marketplace", exact=True).click()
            self.page.wait_for_load_state("domcontentloaded", timeout=10000)
        except Exception as e:
            self.logger.error(f"导航到Marketplace发布页面失败: {e}")
            raise
    
    def navigate_directly_to_publish_page(self):
        """直接导航到发布页面URL"""
        try:
            self.goto("https://aepub.58v5.cn/biz/en/publish/classified", timeout=30000)
            self.wait_for_page_load()
        except Exception as e:
            self.logger.error(f"直接导航到发布页面失败: {e}")
            raise
    
    # ========== 图片上传方法 ==========
    
    
    def upload_single_image(self, image_path):
        """
        上传单张图片（推荐方式：使用expect_file_chooser）
        
        从proof文档学到：使用file chooser方式更稳定
        从调试发现：页面没有可见的"Choose File"按钮，而是有隐藏的file input
        
        Args:
            image_path: 图片文件路径
        """
        try:
            path_resolved = Path(image_path).expanduser().resolve()
            if not path_resolved.is_file():
                raise FileNotFoundError(f"测试图片不存在或不可读: {path_resolved}")
            path_str = str(path_resolved)

            self.dismiss_blocking_overlays()
            self.page.evaluate("""
            () => {
                const inp = document.querySelector('input.upload-input')
                    || document.querySelector('input[type=file]');
                if (inp) inp.scrollIntoView({ block: 'center', inline: 'nearest' });
            }
            """)
            self.page.wait_for_timeout(200)

            for sel in _UPLOAD_INPUT_SELECTORS:
                loc = self.page.locator(sel).first
                try:
                    if loc.count() == 0:
                        continue
                    loc.wait_for(state="attached", timeout=20000)
                    loc.set_input_files(path_str, timeout=90000)
                    self.page.wait_for_timeout(2000)
                    self.logger.info(f"✓ 已上传图片: {path_str}")
                    return
                except Exception as e:
                    self.logger.debug(f"upload 选择器 {sel} 失败: {e}")
                    continue

            # 方法2: 隐藏 input 未挂载时，点按钮或脚本触发 file chooser
            self.dismiss_blocking_overlays()
            with self.page.expect_file_chooser(timeout=45000) as fc_info:
                upload_btn = self.page.get_by_role("button", name="Choose File").or_(
                    self.page.get_by_role("button").filter(has_text="Upload")
                ).or_(
                    self.page.locator("button:has-text('Choose')")
                )
                try:
                    upload_btn.first.click(timeout=12000, force=True)
                except Exception:
                    triggered = self.page.evaluate("""
                    () => {
                        const inp = document.querySelector('input[type=file]');
                        if (inp) { inp.click(); return true; }
                        return false;
                    }
                    """)
                    if not triggered:
                        # evaluate 在部分 headless/遮罩 场景会挂起，优先再试直接点第一个 file input
                        fin = self.page.locator("input[type=file]").first
                        if fin.count() > 0:
                            fin.evaluate("el => el.click()")
                        else:
                            upload_btn.first.click(timeout=20000, force=True)

            file_chooser = fc_info.value
            file_chooser.set_files(path_str)
            self.page.wait_for_timeout(2000)
            self.logger.info(f"✓ 已上传图片: {path_str}")
        except Exception as e:
            self.logger.error(f"图片上传失败: {e}")
            raise
    
    def upload_images(self, image_paths):
        """
        上传多张图片（逐张上传）
        
        注意：playwright-cli的upload命令每次只能上传1张
        
        Args:
            image_paths: 图片路径列表或单个路径
        """
        # 确保传入的是列表
        if isinstance(image_paths, (str, Path)):
            image_paths = [str(image_paths)]
        else:
            image_paths = [str(p) for p in image_paths]

        # 逐张上传
        for i, img_path in enumerate(image_paths, 1):
            self.upload_single_image(img_path)
            self.logger.info(f"✓ 已上传 {i}/{len(image_paths)} 张图片")
    
    
    
    def get_image_counter_text(self):
        """获取图片计数器文本（如：'2/9'）"""
        try:
            counter = self.page.locator("text=/\\d+\\/9/").first.inner_text()
            return counter
        except Exception as e:
            # 计数器可能在9张图片时消失（从proof_tc007学到）
            self.logger.warning(f"获取图片计数器失败（可能已隐藏）: {e}")
            return None
    
    def get_image_count(self):
        """
        获取已上传图片数量
        
        从proof文档学到：通过.item元素计数
        """
        try:
            count = self.page.locator(".item").count()
            return count
        except Exception as e:
            self.logger.error(f"获取图片数量失败: {e}")
            return 0
    
    def get_main_badge_count(self):
        """获取Main标记数量（应该始终为1）"""
        try:
            count = self.page.locator("text=Main").count()
            return count
        except Exception as e:
            self.logger.error(f"获取Main标记数量失败: {e}")
            return 0
    
    def is_upload_button_visible(self):
        """
        判断"Choose File"上传按钮是否可见
        
        从proof_tc008学到：上传9张后按钮从DOM移除
        """
        try:
            btn_count = self.page.get_by_role("button", name="Choose File").count()
            return btn_count > 0
        except Exception as e:
            self.logger.error(f"检查上传按钮可见性失败: {e}")
            return False
    
    def click_image_thumbnail(self, index=1):
        """
        点击第N张图片缩略图（打开预览Modal）
        
        从proof_tc009学到：需要使用dispatchEvent绕过bg-container拦截
        
        Args:
            index: 0-based索引，0=第1张、1=第2张...
        """
        try:
            # 使用JS dispatchEvent绕过UI拦截
            self.page.evaluate(f"""
                () => {{
                    const images = document.querySelectorAll('.show-img');
                    if (images.length > {index}) {{
                        images[{index}].dispatchEvent(new MouseEvent('click', {{ 
                            bubbles: true, 
                            cancelable: true 
                        }}));
                    }}
                }}
            """)
            self.page.wait_for_timeout(1000)
            self.logger.info(f"✓ 已打开第{index+1}张图片预览Modal")
        except Exception as e:
            self.logger.error(f"点击第{index+1}张图片缩略图失败: {e}")
            raise
    
    def click_delete_in_modal(self):
        """在图片预览Modal中点击删除按钮"""
        try:
            self.page.locator("img[alt='delete']").click()
            self.page.wait_for_timeout(1000)
            self.logger.info("✓ 已点击删除按钮")
        except Exception as e:
            self.logger.error(f"点击删除按钮失败: {e}")
            raise
    
    def confirm_delete_dialog(self):
        """
        确认删除对话框
        
        从proof_tc010学到：有时对话框不出现，需要try-except
        """
        try:
            # 等待确认对话框（可能不出现）
            self.page.wait_for_selector("text=Are you sure", timeout=2000)
            self.page.get_by_role("button", name="OK").click()
            self.page.wait_for_timeout(1000)
            self.logger.info("✓ 已确认删除对话框")
        except Exception as e:
            # 对话框未出现，直接跳过
            self.logger.warning(f"删除确认对话框未出现或已自动关闭: {e}")
            self.page.wait_for_timeout(1000)
    
    def delete_image_by_index(self, index=0):
        """
        删除第N张图片（完整3步流程）
        
        从proof_tc009学到：删除需要3步：
        1. 点击缩略图打开Modal
        2. 点击delete图标
        3. 确认对话框（可能不出现）
        
        Args:
            index: 0-based索引，0=第1张、1=第2张...
        """
        try:
            # Step 1: 打开预览Modal
            self.click_image_thumbnail(index)
            
            # Step 2: 点击删除图标
            self.click_delete_in_modal()
            
            # Step 3: 确认删除（可能不出现确认框）
            self.confirm_delete_dialog()
            
            # 验证Modal已关闭
            self.page.wait_for_timeout(1000)
            assert self.page.locator("[role=dialog]").count() == 0, "Modal should be closed after delete"
            
            self.logger.info(f"✓ 已删除第{index+1}张图片")
        except Exception as e:
            self.logger.error(f"删除第{index+1}张图片失败: {e}")
            raise
    
    def click_set_as_main_in_modal(self, button_index=0):
        """
        在图片预览Modal中点击Set as Main按钮
        
        从proof_tc011学到：
        - Modal内有多个"Set as Main"按钮（每张图片1个）
        - 需要点击当前查看图片对应的按钮
        - 点击后按钮会变为disabled
        - ⚠️ Bug: Main标记可能未同步到外部缩略图列表
        
        Args:
            button_index: 按钮索引（0=第1个按钮，1=第2个...）
        """
        try:
            all_btns = self.page.get_by_role("button", name="Set as Main").all()
            if len(all_btns) > button_index:
                all_btns[button_index].click()
                self.page.wait_for_timeout(1000)
                self.logger.info(f"✓ 已点击第{button_index+1}个Set as Main按钮")
            else:
                raise ValueError(f"Set as Main按钮数量不足（需要>{button_index}，实际{len(all_btns)}）")
        except Exception as e:
            self.logger.error(f"点击Set as Main按钮失败: {e}")
            raise
    
    def close_image_modal(self):
        """关闭图片预览Modal"""
        try:
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(500)
            self.logger.info("✓ 已关闭图片预览Modal")
        except Exception as e:
            self.logger.error(f"关闭图片Modal失败: {e}")
            raise
    
    def click_modal_next_button(self):
        """在图片预览Modal中点击Next按钮"""
        try:
            self.page.get_by_role("button", name="next").click()
            self.page.wait_for_timeout(500)
            self.logger.info("✓ 已点击Next按钮")
        except Exception as e:
            self.logger.error(f"点击Next按钮失败: {e}")
            raise
    
    def click_modal_prev_button(self):
        """在图片预览Modal中点击Prev按钮"""
        try:
            self.page.get_by_role("button", name="prev").click()
            self.page.wait_for_timeout(500)
            self.logger.info("✓ 已点击Prev按钮")
        except Exception as e:
            self.logger.error(f"点击Prev按钮失败: {e}")
            raise
    
    def click_modal_bottom_thumbnail(self, index=-1):
        """
        在图片预览Modal中点击底部缩略图
        
        从proof_tc012学到：底部缩略图是最后N个img元素
        
        Args:
            index: -1表示最后一张，-2表示倒数第2张...
        """
        try:
            dialog = self.page.locator("[role=dialog]")
            all_imgs = dialog.locator("img[alt*='图片']").all()
            # 底部缩略图是后半部分
            all_imgs[index].click()
            self.page.wait_for_timeout(500)
            self.logger.info(f"✓ 已点击底部缩略图（index={index}）")
        except Exception as e:
            self.logger.error(f"点击底部缩略图失败: {e}")
            raise
    
    def get_modal_counter_text(self):
        """
        获取Modal内部计数器文本（如："3/5"）
        
        注意：页面可能有多个计数器（外部"X/9"和Modal内"X/Y"）
        """
        try:
            all_counters = self.page.locator("text=/[0-9]+\\/[0-9]+/").all_text_contents()
            # 返回所有计数器（调用方自行过滤）
            return all_counters
        except Exception as e:
            self.logger.error(f"获取Modal计数器失败: {e}")
            return []
    
    # ========== 基础表单字段方法 ==========
    
    def input_title(self, title):
        """输入标题"""
        try:
            self.page.locator(self.TITLE_INPUT).fill(title)
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"输入标题失败: {e}")
            raise
    
    def get_title_value(self):
        """获取标题内容"""
        try:
            return self.page.locator(self.TITLE_INPUT).input_value()
        except Exception as e:
            self.logger.error(f"获取标题内容失败: {e}")
            return ""
    
    def get_title_counter_text(self):
        """获取标题字符计数器文本（如：'42/200'）"""
        try:
            counter = self.page.locator("text=/\\d+\\/200/").inner_text()
            return counter
        except Exception as e:
            self.logger.error(f"获取标题计数器失败: {e}")
            return None
    
    def input_description(self, description):
        """输入描述"""
        try:
            self.page.locator(self.DESCRIPTION_INPUT).fill(description)
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"输入描述失败: {e}")
            raise
    
    def get_description_value(self):
        """获取描述内容"""
        try:
            return self.page.locator(self.DESCRIPTION_INPUT).input_value()
        except Exception as e:
            self.logger.error(f"获取描述内容失败: {e}")
            return ""
    
    def input_price(self, price):
        """输入价格"""
        try:
            self.page.locator(self.PRICE_INPUT).fill(str(price))
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"输入价格失败: {e}")
            raise
    
    def get_price_value(self):
        """获取价格内容"""
        try:
            return self.page.locator(self.PRICE_INPUT).input_value()
        except Exception as e:
            self.logger.error(f"获取价格内容失败: {e}")
            return ""
    
    # ========== AI功能方法 ==========
    
    def click_write_with_ai(self):
        """点击描述区 AI 按钮（多文案：Write/Generate/Describe with AI；多策略：role、filter、JS）。"""
        try:
            self.page.wait_for_timeout(800)
            for cre in (
                re.compile(r"Write\s*with\s*AI", re.I),
                re.compile(r"Generate\s+with\s+AI", re.I),
                re.compile(r"Describe\s+with\s+AI", re.I),
                re.compile(r"Create\s+with\s+AI", re.I),
            ):
                loc = self.page.get_by_role("button", name=cre)
                if loc.count() > 0:
                    loc.first.click(force=True)
                    self.page.wait_for_timeout(1000)
                    self.logger.info("✓ 已点击描述区 AI（role/button）")
                    return
        except Exception as e:
            self.logger.warning(f"role 定位 AI 描述按钮失败: {e}")
        try:
            for cre in (
                re.compile(r"Write\s*with\s*AI", re.I),
                re.compile(r"Generate\s+with\s+AI", re.I),
                re.compile(r"Describe\s+with\s+AI", re.I),
            ):
                alt = self.page.locator("button").filter(has_text=cre)
                if alt.count() > 0:
                    alt.first.click(force=True)
                    self.page.wait_for_timeout(1000)
                    self.logger.info("✓ 已点击描述区 AI（button filter）")
                    return
        except Exception as e:
            self.logger.warning(f"button filter 失败: {e}")
        _js_ai_btn_re = (
            r"(write|generate|create|describe|polish)\s+with\s+ai|"
            r"ai\s*[-\u2013]\s*(write|description|generate)|"
            r"\bAI\s+description\b"
        )
        ok = self.page.evaluate(
            """(pattern) => {
            const re = new RegExp(pattern, 'i');
            const nodes = Array.from(document.querySelectorAll('button, [role="button"], a, span'));
            for (const el of nodes) {
                if (!el.offsetParent) continue;
                const t = (el.innerText || el.textContent || '').replace(/\\s+/g, ' ').trim();
                if (re.test(t)) {
                    const clickTarget = el.closest('button') || el;
                    clickTarget.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                    return true;
                }
            }
            return false;
        }""",
            _js_ai_btn_re,
        )
        if not ok:
            self.logger.error("未找到描述区 AI 按钮（Write/Generate/Describe with AI 等）")
            raise Exception("未找到 Write with AI 按钮")
        self.page.wait_for_timeout(1000)
        self.logger.info("✓ 已点击描述区 AI（JS）")
    
    def wait_for_ai_generation_complete(self, timeout=30000):
        """等待AI生成完成（AI is working on it文本消失）"""
        try:
            self.page.get_by_text("AI is working on it").first.wait_for(state='hidden', timeout=timeout)
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"等待AI生成完成超时: {e}")
            raise
    
    def click_undo_button(self):
        """点击Undo按钮"""
        try:
            self.page.get_by_role('button', name='Undo').click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击Undo按钮失败: {e}")
            raise
    
    def click_shuffle_button(self):
        """点击Shuffle按钮（重新生成）"""
        try:
            self.page.get_by_role('button', name='Shuffle').click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击Shuffle按钮失败: {e}")
            raise
    
    # ========== 类别选择方法 ==========
    
    def click_category_field(self):
        """点击Category字段，当AI推荐区域尚未显示时使用
        
        新UI（2026-04）：
        - 填写Title后AI通常自动展开Suggested Categories，无需手动点击
        - 仅当Suggested Categories未自动出现时（如某些特殊状态）才需要调用此方法
        """
        try:
            # 先检查Suggested Categories是否已经显示
            suggested = self.page.locator("text=Suggested Categories")
            if suggested.is_visible():
                self.logger.info("✓ Suggested Categories已自动展开，无需点击Category字段")
                return

            # 尝试点击Category字段（空白状态下的 "Select Category >" 区域）
            cat_field = self.page.locator(".category.float-label-child")
            if cat_field.count() > 0 and cat_field.is_visible():
                cat_field.click()
                self.page.wait_for_timeout(1500)
                self.logger.info("✓ 已点击Category字段，等待推荐区域展开")
                return

            # 最终fallback：等待AI推荐自然出现（最多10秒）
            self.logger.info("⏳ 等待Suggested Categories自动出现...")
            for i in range(10):
                self.page.wait_for_timeout(1000)
                if suggested.is_visible():
                    self.logger.info(f"  ✓ 第{i+1}秒 Suggested Categories已出现")
                    return
            self.logger.warning("⚠️ Suggested Categories未在10秒内出现")
        except Exception as e:
            self.logger.error(f"点击Category字段失败: {e}")
            raise

    def ensure_recommend_category_ui_ready(self, fallback_title: str = "Product for category test"):
        """确保推荐区/More Categories 可点：无标题时补填并等待 AI。"""
        try:
            has_panel = self.page.evaluate("""
            () => {
                return document.querySelectorAll('[class*="recommend-category_moreCategory"]').length > 0
                    || document.querySelectorAll('[class*="recommendCategoryItem"]').length > 0;
            }
            """)
            if has_panel:
                return
            title_val = ""
            try:
                title_val = (self.page.locator("#title").input_value() or "").strip()
            except Exception:
                pass
            if not title_val:
                self.input_title(fallback_title)
            self.logger.info("⏳ 等待 AI 推荐区加载...")
            for i in range(60):
                self.page.wait_for_timeout(1000)
                if self.page.evaluate("""
                () => document.querySelectorAll(
                    '[class*="recommend-category_moreCategory"], [class*="moreCategory"]'
                ).length > 0
                """):
                    self.logger.info(f"  ✓ 第{i+1}秒 More Categories 已出现")
                    return
            self.logger.warning("⚠️ 推荐区可能仍未在60秒内加载，继续尝试点击 More Categories")
        except Exception as e:
            self.logger.warning(f"ensure_recommend_category_ui_ready: {e}")

    def dismiss_blocking_overlays(self):
        """关闭可能遮挡主表单的登录弹窗、全屏遮罩等（独立 geolocation 等场景易出现）。"""
        for _ in range(3):
            try:
                self.page.keyboard.press("Escape")
                self.page.wait_for_timeout(180)
            except Exception:
                pass
        try:
            self.page.evaluate("""
            () => {
                const lower = (s) => (s || '').toLowerCase();
                const tryClose = (root) => {
                    if (!root) return false;
                    const seq = [
                        'button[aria-label="Close"]', '.btn-close', '[data-bs-dismiss="modal"]',
                        '[data-bs-dismiss]', 'button.close'
                    ];
                    for (const sel of seq) {
                        const x = root.querySelector(sel);
                        if (x && x.offsetParent !== null) { x.click(); return true; }
                    }
                    for (const b of root.querySelectorAll('button, [role="button"]')) {
                        const t = lower(b.textContent || '');
                        if (t === '×' || t === 'close' || (b.getAttribute('aria-label') || '').toLowerCase() === 'close')
                            { b.click(); return true; }
                    }
                    return false;
                };
                const isCategoryFlowDialog = (el) => {
                    if (!el) return false;
                    const cls = typeof el.className === 'string'
                        ? el.className
                        : String((el.className && el.className.baseVal) || el.className || '');
                    if (cls.includes('category-search') || cls.includes('category-select')) return true;
                    if (el.querySelector && el.querySelector('.category-search-dialog, .category-select-modal')) return true;
                    const t = lower(el.innerText || '').slice(0, 600);
                    return t.includes('search for category') || t.includes('or browse to find a category');
                };
                const looksLikeLogin = (el) => {
                    if (isCategoryFlowDialog(el)) return false;
                    const cls = typeof el.className === 'string'
                        ? el.className
                        : String((el.className && el.className.baseVal) || el.className || '');
                    const id = (el.id || '').toLowerCase();
                    if (cls.includes('loginModal') || cls.includes('LoginModal') || id.includes('login')) return true;
                    const t = lower(el.innerText || '').slice(0, 800);
                    return t.includes('log in') || t.includes('sign in') || t.includes('continue with');
                };
                let killed = false;
                document.querySelectorAll('[role="dialog"], .modal.show, [class*="loginModal"], [class*="LoginModal"]')
                    .forEach((m) => {
                        if (isCategoryFlowDialog(m)) return;
                        if (getComputedStyle(m).visibility === 'hidden' && m.offsetParent === null) return;
                        if (!looksLikeLogin(m)) return;
                        if (tryClose(m)) killed = true;
                    });
                // 仍挡在中间的登录容器：直接隐藏（最后手段，避免 Playwright 点击被拦截）
                document.querySelectorAll('[class*="loginModal"], [class*="LoginModal"], [class*="LoginPC"]')
                    .forEach((m) => {
                        if (isCategoryFlowDialog(m)) return;
                        if (!m.offsetParent) return;
                        if (!looksLikeLogin(m)) return;
                        m.style.setProperty('display', 'none', 'important');
                        m.setAttribute('aria-hidden', 'true');
                        killed = true;
                    });
                if (killed) {
                    document.querySelectorAll('.modal-backdrop').forEach((b) => b.remove());
                    document.body.classList.remove('modal-open');
                    document.body.style.overflow = '';
                    document.body.style.paddingRight = '';
                }
            }
            """)
            self.page.wait_for_timeout(280)
        except Exception:
            pass
        try:
            self.page.evaluate("""
            () => {
                const nodes = document.querySelectorAll('[role="dialog"]');
                for (const m of nodes) {
                    if (m.querySelector('.category-search-dialog, .category-select-modal')) continue;
                    const cls = (m.className && m.className.toString) ? m.className.toString() : '';
                    if (cls.includes('category-search') || cls.includes('category-select')) continue;
                    if (!m.offsetParent) continue;
                    const t = (m.innerText || '').toLowerCase();
                    if (t.includes('log in') || t.includes('sign in') || t.includes('continue with')) {
                        const x = m.querySelector('button[aria-label="Close"], .btn-close, [data-bs-dismiss]');
                        if (x) { x.click(); return; }
                    }
                }
            }
            """)
            self.page.wait_for_timeout(300)
        except Exception:
            pass

    def _wait_category_modal_any(self, timeout_ms: int = 10000) -> bool:
        """Search Modal 或已含列表的 Browse Modal 任一出现即视为类别流程已打开。"""
        try:
            self.page.wait_for_function(
                """
                () => {
                    if (document.querySelector('.category-search-dialog')) return true;
                    const m = document.querySelector('.category-select-modal');
                    return !!(m && m.querySelectorAll('.list-item').length > 0);
                }
                """,
                timeout=timeout_ms,
            )
            return True
        except Exception:
            return False

    def _try_open_category_search_modal_fallback(self) -> bool:
        """More Categories 未出现时：主表单 Or browse / Category 行 / 文案入口。"""
        try:
            opened = self.page.evaluate("""
            () => {
              const hit = (t) => /or browse to find a category/i.test(
                  (t || '').replace(/\\s+/g, ' ').trim()
              );
              for (const el of document.querySelectorAll('a, button, span, div, p')) {
                if (el.closest('[role="dialog"]') || !el.offsetParent) continue;
                const tx = (el.textContent || '').trim();
                if (hit(tx) && tx.length < 140) {
                  el.scrollIntoView({ block: 'center' });
                  el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                  return true;
                }
              }
              return false;
            }
            """)
            if opened and self._wait_category_modal_any(12000):
                self.logger.info("✓ 已通过主表单 Or browse 打开类别弹层")
                return True
        except Exception:
            pass
        try:
            for _ in range(2):
                self.page.locator(".category.float-label-child").first.click(timeout=10000, force=True)
                self.page.wait_for_timeout(2200)
                if self._wait_category_modal_any(8000):
                    self.logger.info("✓ 已通过 Category 行点击打开类别弹层")
                    return True
        except Exception:
            pass
        try:
            self.page.get_by_text(re.compile(r"Select\s+Category", re.I)).first.click(
                timeout=8000, force=True
            )
            self.page.wait_for_timeout(2000)
            if self._wait_category_modal_any(8000):
                self.logger.info("✓ 已通过 Select Category 文案打开类别弹层")
                return True
        except Exception:
            pass
        return False

    def click_more_categories(self):
        """点击More Categories链接（打开 Search For Category 对话框）
        
        新UI（2026-04）流程：
        - 填写Title后AI自动展开Suggested Categories（含 More Categories 链接）
        - 本方法点击 More Categories → 弹出 Search For Category Modal
        - 再调用 click_browse_to_find_category() 打开 Browse Modal（.category-select-modal）
        
        注意：More Categories 节点常在 DOM 中但 Playwright is_visible 为 false（动画/CSS），
        因此用 DOM 计数 + JS 点击，不用 is_visible。
        """
        try:
            self.dismiss_blocking_overlays()
            self.page.evaluate("""
            () => {
                const pick = document.querySelector('[class*="recommend-category"]')
                    || document.querySelector('.category.float-label-child')
                    || document.querySelector('.form-item');
                if (pick) pick.scrollIntoView({ block: 'center', inline: 'nearest' });
            }
            """)
            self.page.wait_for_timeout(400)
            try:
                self.page.evaluate("window.scrollTo(0, 0)")
                self.page.wait_for_timeout(200)
            except Exception:
                pass
            self.ensure_category_modals_dismissed()

            cat_field = self.page.locator(".category.float-label-child")
            if cat_field.count() > 0 and cat_field.is_visible():
                self.logger.info("⏳ Category字段未展开，先点击展开...")
                self.dismiss_blocking_overlays()
                try:
                    cat_field.click(timeout=8000, force=True)
                except Exception:
                    self.page.evaluate("""
                    () => {
                        const c = document.querySelector('.category.float-label-child');
                        if (c) c.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                    }
                    """)
                self.page.wait_for_timeout(1500)

            self.ensure_recommend_category_ui_ready()

            # 已选过类别时推荐区常收起：先点 Category 区域重新展开，再点 More Categories
            try:
                reopen = self.page.evaluate("""
                () => {
                    const cat = document.querySelector('.category.float-label-child');
                    if (cat && cat.offsetParent !== null) {
                        cat.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                        return true;
                    }
                    const items = document.querySelectorAll('[class*="suggestedCategory"], [class*="recommend-category"]');
                    for (const el of items) {
                        if (el.offsetParent !== null && (el.textContent.includes('Marketplace') || el.textContent.includes('›'))) {
                            el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                            return true;
                        }
                    }
                    return false;
                }
                """)
                if reopen:
                    self.page.wait_for_timeout(1500)
            except Exception:
                pass

            # Playwright 层兜底：与旧版 test_post_marketplace 一致，部分构建 class 为 *moreCategory*
            try:
                alt = self.page.locator('[class*="moreCategory"]').first
                if alt.count() > 0:
                    alt.scroll_into_view_if_needed(timeout=10000)
                    alt.click(timeout=25000, force=True)
                    if self._wait_category_modal_any(18000):
                        self.page.wait_for_timeout(400)
                        self.logger.info("✓ 已点击 More Categories（[class*=\"moreCategory\"]）")
                        return
            except Exception:
                pass
            try:
                cid = self.page.locator("#categoryId")
                if cid.count() > 0:
                    cid.scroll_into_view_if_needed(timeout=8000)
                    cid.click(timeout=10000, force=True)
                    self.page.wait_for_timeout(1500)
                    if self._wait_category_modal_any(8000):
                        self.logger.info("✓ 已通过 #categoryId 打开类别弹层")
                        return
            except Exception:
                pass

            max_wait = 120
            for i in range(max_wait):
                clicked = self.page.evaluate("""
                () => {
                    const clickEl = (el) => {
                        if (!el || el.closest('[role="dialog"]')) return false;
                        el.scrollIntoView({ block: 'center', inline: 'nearest' });
                        el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                        return true;
                    };
                    const selectors = [
                        '[class*="recommend-category_moreCategory"]',
                        '[class*="moreCategory"]',
                        '[class*="more_category"]',
                    ];
                    for (const sel of selectors) {
                        for (const el of document.querySelectorAll(sel)) {
                            if (clickEl(el)) return true;
                        }
                    }
                    const byText = Array.from(document.querySelectorAll('a, button, span, div, p')).find(el => {
                        if (!el || el.closest('[role="dialog"]') || !el.offsetParent) return false;
                        const t = (el.textContent || '').replace(/\\s+/g, ' ').trim();
                        return /^More Categories$/i.test(t) && t.length < 40;
                    });
                    if (byText && clickEl(byText)) return true;
                    return false;
                }
                """)
                if clicked:
                    if self._wait_category_modal_any(15000):
                        self.page.wait_for_timeout(500)
                        self.logger.info("✓ 已点击More Categories，类别弹层已弹出")
                        return
                    self.logger.warning("点击后未立即出现类别弹层，重试等待...")
                self.page.wait_for_timeout(1000)
                if i % 4 == 0:
                    self.dismiss_blocking_overlays()
                    self.logger.info(f"  第{i+1}秒等待 More Categories 可点击...")

            # 已选类别后推荐区常无 More Categories：点类别面包屑/字段再试
            self.logger.warning("常规方式未找到 More Categories，尝试点击已选类别区域展开...")
            if self._try_click_category_breadcrumb_to_expand():
                self.page.wait_for_timeout(2000)
                for j in range(40):
                    clicked = self.page.evaluate("""
                    () => {
                        const clickEl = (el) => {
                            if (!el || el.closest('[role="dialog"]')) return false;
                            el.scrollIntoView({ block: 'center', inline: 'nearest' });
                            el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                            return true;
                        };
                        for (const sel of ['[class*="recommend-category_moreCategory"]', '[class*="moreCategory"]']) {
                            for (const el of document.querySelectorAll(sel)) {
                                if (clickEl(el)) return true;
                            }
                        }
                        const byText = Array.from(document.querySelectorAll('a, button, span, div, p')).find(el => {
                            if (!el || el.closest('[role="dialog"]') || !el.offsetParent) return false;
                            const t = (el.textContent || '').replace(/\\s+/g, ' ').trim();
                            return /^More Categories$/i.test(t) && t.length < 40;
                        });
                        return byText ? clickEl(byText) : false;
                    }
                    """)
                    if clicked:
                        if self._wait_category_modal_any(12000):
                            self.page.wait_for_timeout(400)
                            self.logger.info("✓ 已点击More Categories（面包屑展开后），类别弹层已弹出")
                            return
                    self.page.wait_for_timeout(800)

            if self._try_open_category_search_modal_fallback():
                return

            raise Exception("未在120秒内找到或可点击 More Categories")

        except Exception as e:
            self.logger.error(f"点击More Categories失败: {e}")
            raise

    def open_category_browse_for_edit(self):
        """已选过类别后再次换类：优先点击表单内类别路径打开 Browse；失败则 More Categories → Or browse。"""
        self.dismiss_blocking_overlays()
        self.page.evaluate("""
        () => {
            const pick = document.querySelector('[class*="recommend-category"]')
                || document.querySelector('.category.float-label-child')
                || document.querySelector('.form-item .category');
            if (pick) pick.scrollIntoView({ block: 'center', inline: 'nearest' });
        }
        """)
        self.page.wait_for_timeout(500)
        self.ensure_category_modals_dismissed()
        opened = self.page.evaluate("""
        () => {
            const items = document.querySelectorAll('.form-item');
            for (const item of items) {
                const block = item.innerText || '';
                if (!/Category/i.test(block)) continue;
                const nodes = item.querySelectorAll('div, span, button');
                for (const n of nodes) {
                    if (!n.offsetParent || n.closest('[role="dialog"]')) continue;
                    const t = (n.textContent || '').replace(/\\s+/g, ' ').trim();
                    if (t.includes('Marketplace') && t.length > 10 && t.length < 220) {
                        n.scrollIntoView({ block: 'center', inline: 'nearest' });
                        n.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                        return true;
                    }
                }
            }
            return false;
        }
        """)
        self.page.wait_for_timeout(2800)
        has_list = self.page.evaluate("""
        () => {
            const m = document.querySelector('.category-select-modal');
            return !!(m && m.querySelectorAll('.list-item').length > 0);
        }
        """)
        if has_list:
            self.logger.info("✓ 已通过表单内类别路径打开 Browse Modal")
            return
        try:
            self.click_category_field_to_edit()
            self.page.wait_for_timeout(2500)
            has_list = self.page.evaluate("""
            () => {
                const m = document.querySelector('.category-select-modal');
                return !!(m && m.querySelectorAll('.list-item').length > 0);
            }
            """)
            if has_list:
                self.logger.info("✓ 已点击 Category 编辑区后 Browse Modal 打开")
                return
            has_search = self.page.evaluate(
                "() => !!document.querySelector('.category-search-dialog')"
            )
            if has_search:
                self.logger.info("✓ Category 点击后已打开 Search Modal，转入 Or browse")
                self.click_browse_to_find_category()
                return
        except Exception:
            pass
        self.logger.info("⏳ 未直接打开 Browse，回退 More Categories 流程")
        self.click_more_categories()
        self.click_browse_to_find_category()

    def _try_click_category_breadcrumb_to_expand(self) -> bool:
        """点击主页面上已选类别的展示区域，尝试重新展开推荐/More Categories。"""
        try:
            return bool(self.page.evaluate("""
            () => {
                const inMain = (el) => el && el.offsetParent !== null && !el.closest('[role="dialog"]');
                const tryClick = (el) => {
                    if (!el || !inMain(el)) return false;
                    el.scrollIntoView({ block: 'center', inline: 'nearest' });
                    el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                    return true;
                };
                const cat = document.querySelector('.category.float-label-child');
                if (tryClick(cat)) return true;
                const items = document.querySelectorAll(
                    '[class*="suggestedCategoryContainer"] [class*="pathName"], ' +
                    '[class*="recommend-category_pathName"], ' +
                    '[class*="category"] [class*="bread"], .form-item .category *'
                );
                for (const el of items) {
                    const tx = (el.textContent || '').trim();
                    if (tx && tx.includes('Marketplace') && tx.length < 400) {
                        if (tryClick(el)) return true;
                    }
                }
                const divs = document.querySelectorAll('div');
                for (const el of divs) {
                    if (!inMain(el)) continue;
                    const tx = el.textContent || '';
                    if (tx.includes('›') && tx.includes('Marketplace') && tx.length < 220) {
                        if (tryClick(el)) return true;
                    }
                }
                return false;
            }
            """))
        except Exception:
            return False
    
    def click_browse_to_find_category(self):
        """点击Or browse to find a category，打开 Browse（category-select-modal）
        
        新UI（2026-04）：
        - 此链接在 Search For Category Modal（.category-search-dialog）内
        - 点击后关闭 Search Modal，打开 Browse Modal（.category-select-modal）
        - Browse Modal 的 visible 属性可能为 False（CSS动画），改用内容存在判断
        """
        try:
            has_browse = self.page.evaluate("""
            () => {
                const m = document.querySelector('.category-select-modal');
                return !!(m && m.querySelectorAll('.list-item').length > 0);
            }
            """)
            if has_browse:
                self.logger.info("✓ Browse Modal 已就绪，跳过 Search Modal 内 Or browse")
                return

            # 勿在打开 Browse 前调用强 dismiss：曾误关含「Continue」文案的 Search Modal
            # 确保 Search Modal 已在 DOM（动画期可能不可见，故用 attached）
            self.page.wait_for_selector(".category-search-dialog", state="attached", timeout=15000)
            self.page.wait_for_timeout(500)

            # 弹窗容器常拦截 Playwright 命中测试：只点真实 <a>/<button>，避免点到含子节点全文的大 div 导致无效点击
            browse_js = """
            () => {
                const modal = document.querySelector('.category-search-dialog');
                if (!modal) return false;
                const hit = (t) => /or browse to find/i.test((t || '').replace(/\\s+/g, ' ').trim());
                for (const a of modal.querySelectorAll('a')) {
                    if (!a.offsetParent) continue;
                    if (hit(a.textContent)) { a.click(); return true; }
                }
                for (const el of modal.querySelectorAll('button, [role="button"]')) {
                    const t = (el.textContent || '').replace(/\\s+/g, ' ').trim();
                    if (!el.offsetParent || t.length > 160) continue;
                    if (hit(t)) { el.click(); return true; }
                }
                return false;
            }
            """
            opened = False
            for attempt in range(3):
                clicked = self.page.evaluate(browse_js)
                if not clicked:
                    browse_link = self.page.get_by_text("Or browse to find a category")
                    try:
                        browse_link.click(timeout=8000, force=True)
                    except Exception:
                        browse_link.evaluate("el => el.click()")
                self.page.wait_for_timeout(1000)
                try:
                    self._wait_for_category_select_modal(timeout=12000)
                    opened = True
                    break
                except Exception:
                    self.logger.warning(
                        f"Browse Modal 未就绪（第{attempt + 1}/3 次），将重试点击 Or browse..."
                    )
                    self.page.wait_for_timeout(600)
            if not opened:
                raise Exception("多次点击 Or browse 后仍未打开 category-select-modal（无 .list-item）")

            self.page.wait_for_timeout(300)
            self.logger.info("✓ 已点击browse按钮，Browse Modal已打开")
        except Exception as e:
            self.logger.error(f"点击browse to find category失败: {e}")
            raise
    
    def click_category_field_to_edit(self):
        """点击已选择的Category字段区域来重新打开Modal（用于切换类别）"""
        try:
            self.page.wait_for_timeout(1000)
            
            # 策略1: 找到Edit图标或按钮
            edit_icon = self.page.locator("[class*='category'] svg, [class*='category'] [class*='edit']").first
            if edit_icon.count() > 0 and edit_icon.is_visible():
                edit_icon.click()
                self.page.wait_for_timeout(2000)
                self.logger.info("✓ 已点击Edit图标")
                return
            
            # 策略2: 点击表单内 Category 行已选路径（兼容多种 DOM 结构）
            js_code = """
            () => {
                const items = document.querySelectorAll('.form-item, [class*="form-item"]');
                for (const fi of items) {
                    const block = fi.innerText || '';
                    if (!/category/i.test(block)) continue;
                    const pathEl = fi.querySelector(
                        '[class*="path"], [class*="bread"], [class*="category"] [class*="text"], ' +
                        '[class*="suggestedCategory"]'
                    );
                    if (pathEl && pathEl.offsetParent && !pathEl.closest('[role="dialog"]')) {
                        pathEl.scrollIntoView({ block: 'center' });
                        pathEl.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                        return true;
                    }
                }
                const nodes = Array.from(document.querySelectorAll('div, span'));
                for (const el of nodes) {
                    if (!el.offsetParent || el.closest('[role="dialog"]')) continue;
                    const text = (el.textContent || '').replace(/\\s+/g, ' ').trim();
                    if (text.length < 20 || text.length > 380) continue;
                    if (!text.includes('Apple') && !text.includes('Cell Phones')) continue;
                    if (!text.includes('Electronics') && !text.includes('Marketplace')) continue;
                    el.scrollIntoView({ block: 'center' });
                    el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                    return true;
                }
                return false;
            }
            """
            result = self.page.evaluate(js_code)
            if result:
                self.page.wait_for_timeout(2000)
                self.logger.info("✓ 已点击Category显示区域")
                return
            
            raise Exception("无法找到Category编辑入口")
        except Exception as e:
            self.logger.error(f"点击Category字段失败: {e}")
            raise
    
    def select_category_electronics(self):
        """选择Electronics类别
        
        新UI（2026-04）：在 .category-select-modal（Browse Modal）中使用 .list-item 定位类别
        """
        try:
            self._wait_for_category_select_modal(timeout=8000)
            self.page.wait_for_timeout(200)

            js_code = """
            () => {
                const modal = document.querySelector('.category-select-modal');
                if (!modal) return false;
                const items = Array.from(modal.querySelectorAll('.list-item'));
                const target = items.find(el => el.textContent.trim() === 'Electronics');
                if (target) { target.click(); return true; }
                return false;
            }
            """
            result = self.page.evaluate(js_code)
            if not result:
                raise Exception("未找到Electronics类别元素（Browse Modal .list-item）")

            self.page.wait_for_timeout(300)  # 缩短等待，避免子列表被重置
            self.logger.info("✓ 已选择Electronics类别")
        except Exception as e:
            self.logger.error(f"选择Electronics类别失败: {e}")
            raise
    
    def select_category_cell_phones(self):
        """选择Cell Phones类别
        
        新UI（2026-04）：在 Browse Modal 中使用 .list-item 定位类别
        注意：点击后子列表只会显示约700ms，需立即选择Apple等子类别
        """
        try:
            self.page.wait_for_timeout(200)

            js_code = """
            () => {
                const modal = document.querySelector('.category-select-modal');
                if (!modal) return false;
                const items = Array.from(modal.querySelectorAll('.list-item'));
                const target = items.find(el => el.textContent.trim() === 'Cell Phones');
                if (target) { target.click(); return true; }
                return false;
            }
            """
            result = self.page.evaluate(js_code)
            if not result:
                raise Exception("未找到Cell Phones类别元素（Browse Modal .list-item）")

            self.page.wait_for_timeout(300)  # 缩短等待，子列表在700ms后会重置
            self.logger.info("✓ 已选择Cell Phones类别")
        except Exception as e:
            self.logger.error(f"选择Cell Phones类别失败: {e}")
            raise

    def select_category_electronics_cell_phones_apple(self):
        """Browse Modal 已打开时，短间隔三连选 Electronics → Cell Phones → Apple（避免子列表约700ms被重置）。
        
        增强版：如果首次选择失败（未找到 Cell Phones），自动关闭重开 Modal 重试一次。
        """
        for retry_count in range(2):  # 最多尝试2次
            try:
                self._select_electronics_cellphones_apple_once()
                return  # 成功则直接返回
            except Exception as e:
                error_msg = str(e)
                if "未找到 Cell Phones" in error_msg and retry_count == 0:
                    self.logger.warning(
                        f"⚠️ 首次类目选择失败（{error_msg}），关闭Modal重新打开后重试..."
                    )
                    try:
                        # 关闭所有可能的Modal
                        self.ensure_category_modals_dismissed()
                        self.page.wait_for_timeout(800)
                        # 重新打开类目选择流程
                        self.click_more_categories()
                        self.page.wait_for_timeout(500)
                        self.click_browse_to_find_category()
                        self.page.wait_for_timeout(500)
                    except Exception as reopen_err:
                        self.logger.error(f"重新打开Browse Modal失败: {reopen_err}")
                        raise e  # 抛出原始错误
                    # 继续循环进行第二次尝试
                else:
                    # 非Cell Phones错误，或已是第二次尝试，直接抛出
                    raise

    def _select_electronics_cellphones_apple_once(self):
        """执行一次完整的 Electronics → Cell Phones → Apple 选择（内部方法）。"""
        try:
            self._wait_for_category_select_modal(timeout=15000)
            self.page.wait_for_timeout(400)

            def _click_name(name: str) -> bool:
                return self.page.evaluate(
                    """
                    (name) => {
                        const modal = document.querySelector('.category-select-modal');
                        if (!modal) return false;
                        const norm = (s) => (s || '').replace(/\\s+/g, ' ').trim();
                        const items = Array.from(
                            modal.querySelectorAll('.list-item, [class*="list-item"], li[role="option"], [class*="ListItem"]')
                        );
                        const nlow = (name || '').toLowerCase();
                        let target = items.find((el) => norm(el.textContent) === name);
                        if (!target) {
                            target = items.find((el) => {
                                const t = norm(el.textContent);
                                if (!t) return false;
                                const tl = t.toLowerCase();
                                if (tl === nlow) return true;
                                if (t.length < 80) {
                                    if (t.includes(name) || tl.includes(nlow)) return true;
                                }
                                return false;
                            });
                        }
                        if (target) {
                            target.scrollIntoView({ block: 'center' });
                            target.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                            return true;
                        }
                        return false;
                    }
                    """,
                    name,
                )

            def _pick_apple() -> bool:
                try:
                    self.page.wait_for_function(
                        """
                        () => {
                            const modal = document.querySelector('.category-select-modal');
                            if (!modal) return false;
                            return Array.from(modal.querySelectorAll('.list-item')).some(
                                el => el.textContent.trim() === 'Apple'
                            );
                        }
                        """,
                        timeout=5000,
                    )
                except Exception:
                    pass
                self.page.wait_for_timeout(100)
                for _ in range(28):
                    if _click_name("Apple"):
                        return True
                    self.page.wait_for_timeout(70)
                return False

            # 顶级常为站点大类（Jobs/Property/Marketplace/…），需先进入 Marketplace 再选 Electronics
            root_labels = self.page.evaluate("""
            () => {
                const m = document.querySelector('.category-select-modal');
                if (!m) return [];
                return Array.from(
                    m.querySelectorAll('.list-item, [class*="list-item"], li[role="option"]')
                ).map(el => (el.textContent || '').replace(/\\s+/g, ' ').trim()).filter(Boolean);
            }
            """)
            if root_labels and "Marketplace" in root_labels and "Electronics" not in root_labels:
                if _click_name("Marketplace"):
                    self.page.wait_for_timeout(500)
                else:
                    self.logger.warning("⚠️ 检测到顶级 Marketplace 入口但点击失败，继续尝试 Electronics")

            elec_ok = False
            for _attempt in range(40):
                if _click_name("Electronics"):
                    elec_ok = True
                    break
                self.page.wait_for_timeout(450)
            if not elec_ok:
                avail = self.page.evaluate("""
                () => {
                    const m = document.querySelector('.category-select-modal');
                    if (!m) return [];
                    return Array.from(m.querySelectorAll('.list-item, [class*="list-item"], li')).map(
                        el => (el.textContent || '').replace(/\\s+/g, ' ').trim()
                    ).filter(Boolean).slice(0, 40);
                }
                """)
                raise Exception(f"未找到 Electronics，当前列表项: {avail}")
            # Electronics 后子列可能尚未渲染，先等 Cell Phones 行出现再点（无头长跑更稳）
            self.page.wait_for_timeout(400)
            try:
                self.page.wait_for_function(
                    """
                    () => {
                        const m = document.querySelector('.category-select-modal');
                        if (!m) return false;
                        return Array.from(
                            m.querySelectorAll('.list-item, [class*="list-item"], li[role="option"], [class*="ListItem"]')
                        ).some((el) => /cell\\s*phones/i.test((el.textContent || '').trim()));
                    }
                    """,
                    timeout=30000,
                )
            except Exception:
                self.logger.warning("Electronics 后 30s 内未稳定出现 Cell Phones 行，仍尝试点击")

            cell_phones_clicked = False
            if _click_name("Cell Phones"):
                cell_phones_clicked = True
            else:
                try:
                    self.page.wait_for_function(
                        """
                        () => {
                            const m = document.querySelector('.category-select-modal');
                            if (!m) return false;
                            return Array.from(
                                m.querySelectorAll('.list-item, [class*="list-item"], li[role="option"], [class*="ListItem"]')
                            ).some((el) => /cell\\s*phones/i.test((el.textContent || '').trim()));
                        }
                        """,
                        timeout=30000,
                    )
                except Exception:
                    pass
                for _r in range(55):
                    if _click_name("Cell Phones"):
                        cell_phones_clicked = True
                        break
                    self.page.wait_for_timeout(350)
                if not cell_phones_clicked:
                    raise Exception("未找到 Cell Phones")
            # Cell Phones 点击后等待子列（常为 Apple）刷新，避免立即点 Apple 命中旧列表
            self._wait_cell_phones_sublist_stable(timeout_ms=28000)
            self.page.wait_for_timeout(220)
            if not _pick_apple():
                # 列表偶发回到顶级：再点一次 Cell Phones 路径后重试 Apple
                self.logger.warning("⚠️ Apple 首次未点到，重试 Electronics → Cell Phones → Apple")
                if _click_name("Electronics"):
                    self.page.wait_for_timeout(200)
                if _click_name("Cell Phones"):
                    self._wait_cell_phones_sublist_stable(timeout_ms=22000)
                    self.page.wait_for_timeout(180)
                if not _pick_apple():
                    avail = self.page.evaluate("""
                    () => {
                        const m = document.querySelector('.category-select-modal');
                        if (!m) return [];
                        return Array.from(m.querySelectorAll('.list-item')).map(el => el.textContent.trim()).slice(0, 22);
                    }
                    """)
                    raise Exception(f"未找到 Apple，当前列表: {avail}")
            self.wait_for_category_modal_closed()
            self.page.wait_for_timeout(800)
            self.logger.info("✓ 已选择 Electronics > Cell Phones > Apple")
        except Exception as e:
            self.logger.error(f"三连选手机类别失败: {e}")
            raise

    def _wait_for_category_select_modal(self, timeout=8000):
        """等待 category-select-modal 出现并可用（兼容 CSS opacity/transform 动画）"""
        start = self.page.evaluate("() => Date.now()")
        deadline = timeout
        for _ in range(deadline // 500):
            result = self.page.evaluate("""
            () => {
                const modal = document.querySelector('.category-select-modal');
                if (!modal) return false;
                const items = modal.querySelectorAll('.list-item');
                return items.length > 0;
            }
            """)
            if result:
                self.page.wait_for_timeout(200)
                return
            self.page.wait_for_timeout(500)
        raise Exception("category-select-modal 未在规定时间内加载 .list-item")

    def _select_category_item_by_name(self, name, is_final=False):
        """通用类别选择器：在 .category-select-modal 中通过名称点击 .list-item
        
        Args:
            name: 类别名称（精确匹配）
            is_final: 是否为最终叶子节点（True 则等待两个 Modal 都关闭）
        """
        try:
            # 等待 Browse Modal 内容加载（用自定义等待替代 wait_for_selector visible）
            self._wait_for_category_select_modal(timeout=8000)
            self.page.wait_for_timeout(300)

            js_code = f"""
            () => {{
                const modal = document.querySelector('.category-select-modal');
                if (!modal) return false;
                const items = Array.from(modal.querySelectorAll('.list-item'));
                const target = items.find(el => el.textContent.trim() === '{name}');
                if (target) {{ target.click(); return true; }}
                return false;
            }}
            """
            result = self.page.evaluate(js_code)
            if not result:
                # 获取可用项目列表用于调试
                available = self.page.evaluate("""
                () => {
                    const modal = document.querySelector('.category-select-modal');
                    if (!modal) return [];
                    return Array.from(modal.querySelectorAll('.list-item')).map(el => el.textContent.trim());
                }
                """)
                raise Exception(f"未找到 '{name}'，可用项: {available}")

            if is_final:
                # 最终叶子节点：等待两个 Modal 都关闭
                self.wait_for_category_modal_closed()
                self.page.wait_for_timeout(1000)
            else:
                # 中间节点：等待子列表刷新（缩短到300ms，避免页面自动重置回顶级）
                self.page.wait_for_timeout(300)

            self.logger.info(f"✓ 已选择类别: {name}")
        except Exception as e:
            self.logger.error(f"选择类别 '{name}' 失败: {e}")
            raise

    def select_category_apple(self):
        """选择Apple品牌（最终叶子节点，选后Modal关闭）"""
        self._select_category_item_by_name("Apple", is_final=True)

    def ensure_category_modals_dismissed(self):
        """关闭可能残留的类别 Search/Browse Modal（避免拦截后续点击）。"""
        try:
            for _ in range(4):
                still = self.page.evaluate("""
                () => {
                    const browse = document.querySelector('.category-select-modal');
                    const search = document.querySelector('.category-search-dialog');
                    const vis = (el) => {
                        if (!el) return false;
                        return el.classList.contains('show') || el.getAttribute('aria-hidden') === 'false';
                    };
                    return vis(browse) || vis(search);
                }
                """)
                if not still:
                    break
                self.page.keyboard.press("Escape")
                self.page.wait_for_timeout(450)
        except Exception:
            pass

    def wait_for_category_modal_closed(self):
        """等待 Category Browse Modal 真正关闭（list-item 消失 + show 类移除）。"""
        try:
            modal = self.page.locator(".category-select-modal")
            try:
                modal.wait_for(state="hidden", timeout=8000)
            except Exception:
                self.ensure_category_modals_dismissed()
            self.ensure_category_modals_dismissed()
            self.logger.info("✓ Category Modal已关闭")
        except Exception as e:
            self.logger.warning(f"等待Modal关闭时出现异常: {e}")

    def select_category_computers(self):
        """选择Computers类别（中间节点，300ms后选子类）"""
        self._select_category_item_by_name("Computers")

    def select_category_laptops(self):
        """选择Laptops类别"""
        self._select_category_item_by_name("Laptops", is_final=True)

    def select_category_baby_kids_items(self):
        """选择Baby Kids Items类别"""
        self._select_category_item_by_name("Baby Kids Items")

    def select_category_baby_toys(self):
        """选择Baby Toys类别（最终叶子节点）"""
        try:
            self.page.wait_for_timeout(1000)
            js_code = """
            () => {
                const elements = Array.from(document.querySelectorAll('div[role="dialog"] *'));
                const target = elements.find(el => el.textContent.trim() === 'Baby Toys' && el.offsetParent !== null);
                if (target) {
                    target.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
                    return true;
                }
                return false;
            }
            """
            result = self.page.evaluate(js_code)
            if not result:
                raise Exception("未找到Baby Toys类别元素")
            
            self.wait_for_category_modal_closed()
            self.page.wait_for_timeout(1000)
            self.logger.info("✓ 已选择Baby Toys类别")
        except Exception as e:
            self.logger.error(f"选择Baby Toys类别失败: {e}")
            raise

    def select_category_others(self):
        """选择Others子类别（最终叶子节点）"""
        self._select_category_item_by_name("Others", is_final=True)

    def select_category_books_movies_and_music(self):
        """选择Books · Movies And Music顶级类别（使用模糊匹配兼容不同·符号编码）"""
        try:
            self.page.wait_for_selector("div[role='dialog'].category-select-modal", timeout=5000)
            self.page.wait_for_timeout(300)
            result = self.page.evaluate("""
            () => {
                const modal = document.querySelector('.category-select-modal[role="dialog"]')
                    || Array.from(document.querySelectorAll('[role="dialog"]')).find(d => d.querySelector('.list-item'));
                if (!modal) return false;
                const items = Array.from(modal.querySelectorAll('.list-item'));
                // 模糊匹配：包含Books且包含Music
                const target = items.find(el => {
                    const t = el.textContent.trim();
                    return t.includes('Books') && t.includes('Music');
                });
                if (target) { target.click(); return true; }
                return false;
            }
            """)
            if not result:
                # fallback: 精确匹配
                self._select_category_item_by_name("Books · Movies And Music")
            else:
                self.page.wait_for_timeout(280)
                self.logger.info("✓ 已选择Books · Movies And Music类别")
        except Exception as e:
            self.logger.error(f"选择Books · Movies And Music失败: {e}")
            raise

    def select_category_books(self):
        """选择Books子类别（最终叶子节点）"""
        self._select_category_item_by_name("Books", is_final=True)

    def _ensure_browse_shows_root_categories(self):
        """换类时 Browse 可能仍停留在 Electronics 子树，尝试返回直至出现顶级「Books · Movies And Music」。"""
        for _ in range(10):
            has_target = self.page.evaluate("""
            () => {
                const m = document.querySelector('.category-select-modal');
                if (!m) return false;
                return Array.from(m.querySelectorAll('.list-item')).some(el => {
                    const t = el.textContent.trim();
                    return t.includes('Books') && t.includes('Music');
                });
            }
            """)
            if has_target:
                return
            went = self.page.evaluate("""
            () => {
                const modal = document.querySelector('.category-select-modal');
                if (!modal) return false;
                const nodes = Array.from(modal.querySelectorAll('button, a, [role="button"], svg, span'));
                for (const el of nodes) {
                    const t = (el.textContent || '').trim();
                    const aria = (el.getAttribute('aria-label') || '').toLowerCase();
                    if (/^back$/i.test(t) || aria.includes('back') || aria.includes('previous')) {
                        (el.closest('button') || el).click();
                        return true;
                    }
                }
                const iconBack = modal.querySelector('[class*="back"], [class*="Back"], [class*="arrow-left"]');
                if (iconBack && iconBack.offsetParent) {
                    iconBack.click();
                    return true;
                }
                return false;
            }
            """)
            if not went:
                break
            self.page.wait_for_timeout(400)

    def switch_from_phone_to_books_category(self):
        """已选手机类后切换到 Books：优先用 Search 关键词，避免 Browse 仍停留在 Electronics 子树。"""
        self.dismiss_blocking_overlays()
        self.ensure_category_modals_dismissed()
        try:
            self.click_category_field_to_edit()
        except Exception:
            self.logger.warning("点击 Category 编辑区未成功，尝试表单内路径点击")
            self.page.evaluate("""
            () => {
                const items = document.querySelectorAll('.form-item, [class*="form-item"]');
                for (const fi of items) {
                    if (!/category/i.test(fi.innerText || '')) continue;
                    const pathEl = fi.querySelector('[class*="path"], [class*="bread"], [class*="category"]');
                    if (pathEl && pathEl.offsetParent) {
                        pathEl.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                        return true;
                    }
                }
                return false;
            }
            """)
        self.page.wait_for_timeout(2200)
        if not self.page.evaluate("() => !!document.querySelector('.category-search-dialog')"):
            raise Exception("未打开 Category 搜索弹窗，无法切换到 Books")
        self.page.wait_for_timeout(400)
        # 必须限定在 Search Modal 内，避免匹配到页面其他 Search 输入框
        dlg = self.page.locator(".category-search-dialog")
        inp = dlg.locator("input[type='text'], input:not([type='hidden'])").first
        try:
            inp.click(timeout=8000, force=True)
        except Exception:
            self.page.evaluate("""
            () => {
                const d = document.querySelector('.category-search-dialog');
                if (!d) return;
                const el = d.querySelector('input[type="text"], input:not([type="hidden"])');
                if (el) el.focus();
            }
            """)
        inp.fill("")
        try:
            inp.press_sequentially("Books", delay=45)
        except Exception:
            inp.fill("Books")
        try:
            inp.evaluate("""
            el => {
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
            """)
        except Exception:
            pass
        self.page.wait_for_timeout(6000)
        picked = False
        try:
            self.page.locator(".category-search-dialog .list-item").first.click(timeout=6000, force=True)
            picked = True
        except Exception:
            pass
        if not picked:
            picked = self.page.evaluate("""
            () => {
                const dlg = document.querySelector('.category-search-dialog');
                if (!dlg) return false;
                const rows = dlg.querySelectorAll(
                    '.list-item, [class*="list-item"], [class*="ListItem"], li[role="option"], li, button'
                );
                for (const el of rows) {
                    const t = (el.textContent || '').replace(/\\s+/g, ' ').trim();
                    if (t.length < 4 || t.length > 240) continue;
                    if (/book/i.test(t) && (/music|movie|›|·/i.test(t))) {
                        el.click();
                        return true;
                    }
                }
                const cand = Array.from(dlg.querySelectorAll('div, span, a'));
                for (const el of cand) {
                    const t = (el.textContent || '').replace(/\\s+/g, ' ').trim();
                    if (t.length < 8 || t.length > 240) continue;
                    if (/books/i.test(t) && (/music|movies/i.test(t))) {
                        el.click();
                        return true;
                    }
                }
                return false;
            }
            """)
        if not picked:
            raise Exception("搜索框未匹配到 Books · Movies And Music 结果")
        self.page.wait_for_timeout(2200)
        if self.page.evaluate(
            "() => !!document.querySelector('.category-select-modal .list-item')"
        ):
            self._wait_for_category_select_modal(timeout=8000)
            self.page.wait_for_timeout(200)
            leaf_ok = False
            for _ in range(24):
                if self.page.evaluate("""
                () => {
                    const modal = document.querySelector('.category-select-modal');
                    if (!modal) return false;
                    const items = Array.from(modal.querySelectorAll('.list-item'));
                    const hit = items.find(el => {
                        const t = el.textContent.trim();
                        return t === 'Books' || (/^Books\\b/.test(t) && t.length < 36);
                    });
                    if (hit) { hit.click(); return true; }
                    return false;
                }
                """):
                    leaf_ok = True
                    break
                self.page.wait_for_timeout(90)
            if not leaf_ok:
                raise Exception("Browse 中未点到 Books 叶子")
            self.wait_for_category_modal_closed()
            self.page.wait_for_timeout(600)
        self.logger.info("✓ 已切换到 Books 类（搜索路径）")

    def select_books_under_books_movies_and_music(self):
        """Browse Modal：Books · Movies And Music → Books 叶子（短间隔，避免子列表被重置）。"""
        try:
            self._wait_for_category_select_modal(timeout=8000)
            self.page.wait_for_timeout(150)
            self._ensure_browse_shows_root_categories()
            self.page.wait_for_timeout(200)
            r1 = self.page.evaluate("""
            () => {
                const modal = document.querySelector('.category-select-modal');
                if (!modal) return false;
                const items = Array.from(modal.querySelectorAll('.list-item'));
                const t = items.find(el => {
                    const x = el.textContent.trim();
                    return x.includes('Books') && x.includes('Music');
                });
                if (t) { t.click(); return true; }
                return false;
            }
            """)
            if not r1:
                raise Exception("未找到 Books · Movies And Music 行")
            self.page.wait_for_timeout(200)
            try:
                self.page.wait_for_function(
                    """
                    () => {
                        const modal = document.querySelector('.category-select-modal');
                        if (!modal) return false;
                        return Array.from(modal.querySelectorAll('.list-item')).some(
                            el => el.textContent.trim() === 'Books'
                        );
                    }
                    """,
                    timeout=5000,
                )
            except Exception:
                pass
            self.page.wait_for_timeout(120)

            def _click_books_leaf() -> bool:
                return self.page.evaluate("""
                () => {
                    const modal = document.querySelector('.category-select-modal');
                    if (!modal) return false;
                    const items = Array.from(modal.querySelectorAll('.list-item'));
                    const exact = items.find(el => el.textContent.trim() === 'Books');
                    if (exact) { exact.click(); return true; }
                    const loose = items.find(el => {
                        const t = el.textContent.trim();
                        return t === 'Books' || (/^Books\\b/i.test(t) && t.length < 40);
                    });
                    if (loose) { loose.click(); return true; }
                    return false;
                }
                """)

            r2 = False
            for _ in range(22):
                if _click_books_leaf():
                    r2 = True
                    break
                self.page.wait_for_timeout(80)
            if not r2:
                avail = self.page.evaluate("""
                () => {
                    const m = document.querySelector('.category-select-modal');
                    if (!m) return [];
                    return Array.from(m.querySelectorAll('.list-item')).map(el => el.textContent.trim());
                }
                """)
                raise Exception(f"未找到 Books 叶子，可用项: {avail}")
            self.wait_for_category_modal_closed()
            self.page.wait_for_timeout(600)
            self.logger.info("✓ 已选择 Books · Movies And Music > Books")
        except Exception as e:
            self.logger.error(f"选择 Books 类路径失败: {e}")
            raise

    def select_baby_kids_items_then_baby_toys(self):
        """Browse Modal：Baby Kids Items → Baby Toys（短间隔）。"""
        try:
            self._wait_for_category_select_modal(timeout=8000)
            self.page.wait_for_timeout(150)
            if not self.page.evaluate("""
            () => {
                const modal = document.querySelector('.category-select-modal');
                if (!modal) return false;
                const items = Array.from(modal.querySelectorAll('.list-item'));
                const t = items.find(el => el.textContent.trim() === 'Baby Kids Items');
                if (t) { t.click(); return true; }
                return false;
            }
            """):
                raise Exception("未找到 Baby Kids Items")
            self.page.wait_for_timeout(220)
            if not self.page.evaluate("""
            () => {
                const modal = document.querySelector('.category-select-modal');
                if (!modal) return false;
                const items = Array.from(modal.querySelectorAll('.list-item'));
                const t = items.find(el => el.textContent.trim() === 'Baby Toys');
                if (t) { t.click(); return true; }
                return false;
            }
            """):
                raise Exception("未找到 Baby Toys")
            self.wait_for_category_modal_closed()
            self.page.wait_for_timeout(600)
            self.logger.info("✓ 已选择 Baby Kids Items > Baby Toys")
        except Exception as e:
            self.logger.error(f"选择 Baby Toys 路径失败: {e}")
            raise
    
    def select_first_suggested_category(self):
        """点击第一个AI推荐类别（使用真实 CSS class 定位）"""
        try:
            # 等待推荐类别容器出现（用 DOM 存在代替 visible）
            for _ in range(15):
                cnt = self.page.evaluate("""
                () => document.querySelectorAll(
                    '.recommend-category_recommendCategoryItem__lWYRw, [class*="recommendCategoryItem"]'
                ).length
                """)
                if cnt > 0:
                    break
                self.page.wait_for_timeout(1000)
            
            # 点击第一个推荐类别（兼容 CSS module 哈希变化）
            result = self.page.evaluate("""
            () => {
                let items = document.querySelectorAll('.recommend-category_recommendCategoryItem__lWYRw');
                if (items.length === 0) {
                    items = document.querySelectorAll('[class*="recommendCategoryItem"]');
                }
                if (items.length === 0) return false;
                items[0].click();
                return items[0].textContent.trim().slice(0, 60);
            }
            """)
            if not result:
                raise Exception("未找到推荐类别项 [class*=\"recommendCategoryItem\"]")
            
            self.page.wait_for_timeout(1500)
            self.logger.info(f"✓ 已选择第一个AI推荐类别: {result}")
        except Exception as e:
            self.logger.error(f"点击第一个推荐类别失败: {e}")
            raise
    
    def select_suggested_category_by_text(self, category_text: str):
        """点击指定的AI推荐类别（通过文本匹配）
        
        Args:
            category_text: 类别路径文本，如 "Books" 或 "Apple"
        """
        try:
            # AI推荐类别显示为完整路径，如 "MarketplaceBooks · Movies And MusicBooks"
            # 使用部分文本匹配，查找包含目标类别名的推荐项
            suggested = self.page.locator(f"text=/{category_text}/").first
            suggested.click()
            self.page.wait_for_timeout(1500)
            self.logger.info(f"✓ 已点击AI推荐类别: {category_text}")
        except Exception as e:
            self.logger.error(f"点击推荐类别'{category_text}'失败: {e}")
            raise
    
    def get_category_display_text(self):
        """获取已选择的类别显示文本（完整路径，例如 'MarketplaceElectronicsCell Phones\nApple'）"""
        try:
            # 使用Category label的父容器获取完整类别路径
            # 这会包含面包屑导航的完整文本
            category_container = self.page.locator("label:has-text('Category')").locator("..")
            category_text = category_container.inner_text()
            # 移除"Category *"标签文本，只保留面包屑
            category_path = category_text.replace("Category *", "").strip()
            return category_path
        except Exception as e:
            self.logger.error(f"获取类别显示文本失败: {e}")
            return ""
    
    # ========== Details字段方法（动态显示） ==========
    
    def select_condition_excellent(self):
        """选择 Condition：优先 Excellent；线上文案可能为 Like New / Good 等，故在 Condition 区域内点第一个匹配项。"""
        try:
            self.dismiss_blocking_overlays()
            self.page.evaluate(
                "() => window.scrollTo(0, Math.max(0, document.body.scrollHeight * 0.25))"
            )
            self.page.wait_for_timeout(500)
            clicked = self.page.evaluate("""
            () => {
                const inDialog = (el) => el && el.closest('[role="dialog"]');
                const blocks = Array.from(document.querySelectorAll(
                    '.form-item, [class*="form-item"], section, .float-label-child, [class*="detail"], [class*="Detail"]'
                ));
                const block = blocks.find(
                    (b) => !inDialog(b) && /condition|state|成色/i.test(b.innerText || '')
                );
                if (!block) return false;
                block.scrollIntoView({ block: 'center' });
                const candidates = Array.from(
                    block.querySelectorAll(
                        'button, [role="radio"], label, [role="button"], span, div, p, li, a'
                    )
                );
                const norm = (s) => (s || '').replace(/\\s+/g, ' ').trim();
                const score = (t) => {
                    if (!t || t.length < 2 || t.length > 48) return 0;
                    if (/^excellent$/i.test(t)) return 100;
                    if (/like\\s*new|like-new/i.test(t)) return 80;
                    if (/^new$/i.test(t) || /^brand\\s*new$/i.test(t)) return 70;
                    if (/good|fair|used|refurb/i.test(t)) return 50;
                    return 0;
                };
                let best = null;
                let bestScore = 0;
                for (const o of candidates) {
                    if (!o.offsetParent) continue;
                    const t = norm(o.textContent);
                    const sc = score(t);
                    if (sc > bestScore) {
                        bestScore = sc;
                        best = o;
                    }
                }
                if (best && bestScore > 0) {
                    best.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                    return true;
                }
                return false;
            }
            """)
            if not clicked:
                for pat in (
                    r"^Excellent$",
                    r"Like New",
                    r"^Good$",
                    r"^New$",
                    r"Excellent",
                ):
                    try:
                        self.page.get_by_text(re.compile(pat, re.I)).first.click(
                            timeout=12000, force=True
                        )
                        break
                    except Exception:
                        continue
                else:
                    raise TimeoutError("未找到 Condition 选项（Excellent / Like New / Good 等）")
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择Excellent条件失败: {e}")
            raise
    
    def _select_storage_native_select_fallback(self) -> bool:
        """部分构建用原生 <select> 展示容量；选第一个含 GB/TB 的非首项 option。"""
        try:
            selects = self.page.locator("main select")
            n = selects.count()
            for i in range(min(n, 15)):
                sel = selects.nth(i)
                opts = sel.locator("option")
                oc = opts.count()
                if oc < 2:
                    continue
                texts = []
                for j in range(oc):
                    try:
                        texts.append((opts.nth(j).inner_text() or "").strip())
                    except Exception:
                        texts.append("")
                if not any(re.search(r"gb|tb", t, re.I) for t in texts):
                    continue
                for j in range(1, oc):
                    t = texts[j] if j < len(texts) else ""
                    if not t or re.match(r"^choose|^select|^please", t, re.I):
                        continue
                    try:
                        sel.select_option(index=j)
                        self.page.wait_for_timeout(450)
                        self.logger.info("✓ 已通过原生 select 选择容量: %s", t[:40])
                        return True
                    except Exception:
                        continue
        except Exception as e:
            self.logger.warning("native select 容量兜底失败: %s", e)
        return False

    def select_storage_128gb(self):
        """选择 Storage：优先 128 GB；文案可能是 128GB / 128 G / 或列表中首项含 128。"""
        try:
            self.dismiss_blocking_overlays()
            self.page.evaluate(
                "() => window.scrollTo(0, Math.max(0, document.body.scrollHeight * 0.4))"
            )
            self.page.wait_for_timeout(400)
            clicked = self.page.evaluate("""
            () => {
                const blocks = Array.from(document.querySelectorAll(
                    '.form-item, [class*="form-item"], section, .float-label-child, [class*="detail"]'
                ));
                const block = blocks.find(
                    (b) => /storage|capacity|memory|rom|存储/i.test(b.innerText || '')
                );
                if (!block) return false;
                block.scrollIntoView({ block: 'center' });
                const opts = Array.from(
                    block.querySelectorAll('button, [role="radio"], label, span, div, p, li, a')
                );
                const norm = (s) => (s || '').replace(/\\s+/g, ' ').trim();
                let hit = opts.find((o) => {
                    if (!o.offsetParent) return false;
                    const t = norm(o.textContent);
                    return /128/.test(t) && (/gb|g\\b|go/i.test(t) || t.length < 12);
                });
                if (!hit) {
                    hit = opts.find((o) => {
                        if (!o.offsetParent) return false;
                        return /^128/.test(norm(o.textContent));
                    });
                }
                if (hit) {
                    hit.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                    return true;
                }
                const anyCap = opts.find((o) => {
                    if (!o.offsetParent) return false;
                    const t = norm(o.textContent);
                    return /^\\d+\\s*(GB|TB|gb|tb|Go)/i.test(t) || /^\\d+\\s*G\\b/i.test(t);
                });
                if (anyCap) {
                    anyCap.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                    return true;
                }
                return false;
            }
            """)
            if not clicked:
                for pat in (
                    r"128\s*GB",
                    r"128GB",
                    r"128\s*G\b",
                    r"\b128\b",
                ):
                    try:
                        self.page.get_by_text(re.compile(pat, re.I)).first.click(
                            timeout=8000, force=True
                        )
                        break
                    except Exception:
                        continue
                else:
                    try:
                        self.page.locator("main").get_by_text(
                            re.compile(r"\d+\s*(GB|TB)", re.I)
                        ).first.click(timeout=8000, force=True)
                    except Exception:
                        if self._select_storage_native_select_fallback():
                            pass
                        else:
                            raise TimeoutError(
                                "未找到 Storage 容量选项（芯片/文本/native select）"
                            )
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择128 GB存储失败: {e}")
            raise
    
    def select_storage_1tb(self):
        """选择Storage: 1 TB"""
        try:
            self.page.get_by_text('1 TB', exact=True).click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择1 TB存储失败: {e}")
            raise
    
    def select_originality_original(self):
        """选择Originality: 100% Original"""
        try:
            self.page.get_by_text('100% Original').click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择100% Original失败: {e}")
            raise
    
    def select_battery_health_90(self):
        """选择Battery health: Battery 90%+"""
        try:
            self.page.get_by_text('Battery 90%+').click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择Battery 90%+失败: {e}")
            raise

    def _wait_cell_phones_sublist_stable(self, timeout_ms: int = 28000) -> None:
        """Cell Phones 选中后，等待子类列表就绪（如 Apple），降低无头长跑下误点旧列表概率。"""
        try:
            self.page.wait_for_function(
                """
                () => {
                    const m = document.querySelector('.category-select-modal');
                    if (!m) return false;
                    const texts = Array.from(
                        m.querySelectorAll('.list-item, [class*="list-item"], li[role="option"], [class*="ListItem"]')
                    ).map((el) => (el.textContent || '').replace(/\\s+/g, ' ').trim()).filter(Boolean);
                    if (!texts.length) return false;
                    if (texts.some((t) => /^Apple$/i.test(t) || /iPhone|iPad|MacBook/i.test(t))) return true;
                    if (texts.some((t) => /Samsung|Google Pixel|Huawei|OnePlus|Xiaomi|OPPO|vivo|realme/i.test(t))) {
                        return true;
                    }
                    return false;
                }
                """,
                timeout=timeout_ms,
            )
        except Exception as e:
            self.logger.warning(
                f"Cell Phones 子列表稳定等待未在 {timeout_ms}ms 内满足，仍继续选 Apple: {e}"
            )
        self.page.wait_for_timeout(300)

    # ========== 交付选项方法 ==========
    # 与 `marketplace_post_page.py` 中 MCP 录制路径一致：
    # getByRole('paragraph').filter({ hasText: '...' }) + 滚到底部 + scrollIntoView + scrollBy(-100) 避开固定 Post 底栏
    # 线上文案可能从 postage 改为 shipping 等，故同一选项使用多候选串 + radio/label 兜底。

    def _wait_delivery_section_visible(self, timeout_ms: int = 28000) -> None:
        """类目等表单就绪后，显式等待 Delivery / Shipping 区块出现在主线（与 TC063 检测一致）。"""
        try:
            self.page.wait_for_function(
                """
                () => {
                    const body = document.body && document.body.innerText
                        ? document.body.innerText.replace(/\\s+/g, ' ')
                        : '';
                    if (/Delivery\\s*Options/i.test(body)) return true;
                    if (/Seller pays for postage|Buyer pays for postage|No delivery required|No shipping required/i.test(body)) {
                        return true;
                    }
                    const main = document.querySelector('main');
                    if (!main || !main.innerText) return false;
                    const t = main.innerText.replace(/\\s+/g, ' ');
                    return (
                        /Delivery|Shipping options|Postage/i.test(t)
                        && /pays for postage|pays for shipping|delivery required|shipping required/i.test(t)
                    );
                }
                """,
                timeout=timeout_ms,
            )
            self.logger.info("✓ Delivery 区域已就绪（可见性等待通过）")
        except Exception as e:
            self.logger.warning(
                f"Delivery 区域可见性等待未在 {timeout_ms}ms 内满足，仍尝试点击配送项: {e}"
            )
        self.page.wait_for_timeout(350)

    def _scroll_to_delivery_block(self) -> None:
        """将 Delivery / Shipping 区域滚入视口，便于选项已渲染。"""
        self.dismiss_blocking_overlays()
        for name in ("Delivery", "Delivery options", "Shipping", "Postage"):
            try:
                h = self.page.get_by_role("heading", name=re.compile(rf"^{re.escape(name)}", re.I))
                if h.count() > 0:
                    h.first.scroll_into_view_if_needed(timeout=5000)
                    self.page.wait_for_timeout(350)
                    return
            except Exception:
                continue
        try:
            self.page.locator("main").get_by_text(re.compile(r"delivery|shipping|postage", re.I)).first.scroll_into_view_if_needed(
                timeout=5000
            )
            self.page.wait_for_timeout(350)
        except Exception:
            pass

    def _click_delivery_option_paragraph(self, candidate_texts: list[str]):
        """按候选文案依次尝试点击配送选项（paragraph/div/label/radio）。"""
        self._wait_delivery_section_visible()
        last_err: Exception | None = None
        for text in candidate_texts:
            try:
                self._scroll_to_delivery_block()
                self.dismiss_blocking_overlays()
                self.page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)")
                self.page.wait_for_timeout(600)

                pat = re.compile(r"\s+".join(re.escape(w) for w in text.split()), re.I)

                loc = None
                for factory in (
                    lambda: self.page.get_by_role("radio", name=pat).first,
                    lambda: self.page.locator("label").filter(has_text=pat).first,
                    lambda: self.page.get_by_text(pat).first,
                    lambda: self.page.get_by_role("paragraph").filter(has_text=text).first,
                    lambda: self.page.locator("main").locator("div,span,p,label").filter(has_text=pat).first,
                ):
                    try:
                        cand = factory()
                        cand.wait_for(state="attached", timeout=25000)
                        loc = cand
                        break
                    except Exception:
                        continue
                if loc is None:
                    raise TimeoutError(f"未找到配送选项文案: {text}")

                loc.evaluate("el => el.scrollIntoView({ block: 'center', inline: 'nearest' })")
                self.page.wait_for_timeout(400)
                self.page.evaluate("window.scrollBy(0, -100)")
                self.page.wait_for_timeout(300)
                try:
                    loc.click(timeout=20000)
                except Exception as e:
                    self.logger.warning(f"配送选项常规点击失败，改用 force: {e}")
                    loc.click(force=True, timeout=28000)
                self.page.wait_for_timeout(800)
                self.logger.info(f"✓ 已点击配送选项（匹配: {text!r}）")
                return
            except Exception as e:
                last_err = e
                self.logger.warning(f"配送候选 {text!r} 未命中，尝试下一文案: {e}")
        assert last_err is not None
        raise last_err

    def select_delivery_seller_pays(self):
        """选择Seller pays for postage"""
        try:
            self._click_delivery_option_paragraph(
                [
                    "Seller pays for postage",
                    "Seller pays for shipping",
                    "Seller pays shipping",
                ]
            )
            self.logger.info("✓ 已选择 Seller pays（postage/shipping）")
        except Exception as e:
            self.logger.error(f"选择Seller pays失败: {e}")
            raise
    
    def select_delivery_buyer_pays(self):
        """选择Buyer pays for postage"""
        try:
            self._click_delivery_option_paragraph(
                [
                    "Buyer pays for postage",
                    "Buyer pays for shipping",
                    "Buyer pays shipping",
                    "Buyer covers postage",
                    "Paid by buyer",
                ]
            )
            self.logger.info("✓ 已选择 Buyer pays（postage/shipping）")
        except Exception as e:
            self.logger.error(f"选择Buyer pays失败: {e}")
            raise
    
    def select_delivery_no_delivery(self):
        """选择No delivery required"""
        try:
            self._click_delivery_option_paragraph(
                [
                    "No delivery required",
                    "No shipping required",
                    "No delivery",
                ]
            )
            self.logger.info("✓ 已选择 No delivery / no shipping")
        except Exception as e:
            self.logger.error(f"选择No delivery失败: {e}")
            raise
    
    def select_arrange_pickup(self):
        """开启Arrange pickup with the buyer toggle"""
        try:
            self.page.locator("text=/Arrange pickup with the buyer/").click()
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"选择Arrange pickup失败: {e}")
            raise
    
    # ========== 位置方法 ==========
    
    def input_location(self, location):
        """输入位置（搜索）"""
        try:
            self.page.get_by_role('textbox', name='Set the location for your').fill(location)
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"输入位置失败: {e}")
            raise
    
    def get_location_value(self):
        """获取位置输入框内容"""
        try:
            return self.page.get_by_role('textbox', name='Set the location for your').input_value()
        except Exception as e:
            self.logger.error(f"获取位置内容失败: {e}")
            return ""
    
    def search_location(self, location_name: str):
        """搜索位置并选择第一个结果
        
        新UI（2026-04）：搜索结果使用 .res-list-group-item，需用 JS click 绕过 pointer interception
        
        Args:
            location_name: 位置名称，如 "Abu Dhabi Mall"
        """
        try:
            loc_input = self.page.locator("#location")
            loc_input.scroll_into_view_if_needed()
            loc_input.click()
            loc_input.fill(location_name)
            # 等待搜索结果出现
            self.page.wait_for_selector(".res-list-group-item", timeout=8000)
            self.page.wait_for_timeout(500)

            # 使用 JS 点击第一个搜索结果（绕过 pointer interception）
            result = self.page.evaluate("""
            () => {
                const item = document.querySelector('.res-list-group-item');
                if (item && item.offsetParent !== null) {
                    item.click();
                    return true;
                }
                return false;
            }
            """)
            if not result:
                raise Exception(f"未找到Location搜索结果: {location_name}")

            self.page.wait_for_timeout(1000)
            self.logger.info(f"✓ 已选择位置: {location_name}")
        except Exception as e:
            self.logger.error(f"搜索并选择位置 '{location_name}' 失败: {e}")
            raise

    def click_locate_me(self):
        """点击 Locate me（避免匹配到整块地图容器 div；先尝试关掉登录弹窗）。"""
        try:
            self.dismiss_blocking_overlays()
            self.page.locator("#location").scroll_into_view_if_needed()
            self.page.wait_for_timeout(400)
            clicked = self.page.evaluate("""
            () => {
                const nodes = document.querySelectorAll('button, a, [role="button"]');
                for (const el of nodes) {
                    if (!el.offsetParent || el.closest('[role="dialog"]')) continue;
                    const t = (el.textContent || '').replace(/\\s+/g, ' ').trim();
                    if (!/^Locate me$/i.test(t)) continue;
                    el.scrollIntoView({ block: 'center', inline: 'nearest' });
                    el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
                    return true;
                }
                return false;
            }
            """)
            if not clicked:
                tgt = self.page.get_by_text(re.compile(r"^Locate me$", re.I)).first
                tgt.click(timeout=20000, force=True)
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击Locate me失败: {e}")
            raise
    
    # ========== 操作按钮方法 ==========
    
    def wait_for_condition_detail_visible(self, timeout=20000):
        """等待手机类目 Details 区出现 Condition 标签（类目切换后异步渲染）。"""
        loc = self.page.get_by_text(re.compile(r"^\s*Condition\s*$", re.I))
        loc.first.wait_for(state="visible", timeout=timeout)

    def click_save_draft(self):
        """点击Save the draft按钮（与 Post 一致：去遮罩 + 强制/JS 点击）"""
        try:
            self.dismiss_blocking_overlays()
            draft = self.page.get_by_text("Save the draft").first
            draft.scroll_into_view_if_needed()
            self.page.wait_for_timeout(500)
            try:
                draft.click(timeout=8000, force=True)
            except Exception as e1:
                self.logger.warning(f"Save draft 正常点击失败: {e1}，尝试 evaluate")
                try:
                    draft.evaluate("el => el.click()")
                except Exception:
                    self.page.evaluate("""
                    () => {
                        const lower = (s) => (s || '').toLowerCase();
                        for (const el of document.querySelectorAll('button, a, [role="button"]')) {
                            const t = lower((el.textContent || '').trim());
                            if (t.includes('save') && t.includes('draft')) {
                                el.click();
                                return true;
                            }
                        }
                        return false;
                    }
                    """)
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击Save draft按钮失败: {e}")
            raise
    
    def click_post_button(self):
        """点击Post按钮（优化版：处理拦截问题）"""
        try:
            post_button = self.page.get_by_role('button', name='Post')
            
            # 1. 滚动到按钮位置
            post_button.scroll_into_view_if_needed()
            self.page.wait_for_timeout(1000)
            
            # 2. 等待按钮可点击
            post_button.wait_for(state="visible", timeout=5000)
            
            # 3. 尝试正常点击
            try:
                post_button.click(timeout=5000)
                self.page.wait_for_timeout(2000)
                self.logger.info("✓ 已点击Post按钮（正常点击）")
                return
            except Exception as e1:
                self.logger.warning(f"正常点击失败: {e1}，尝试evaluate点击")
            
            # 4. 使用evaluate强制点击（绕过拦截）
            post_button.evaluate("el => el.click()")
            self.page.wait_for_timeout(2000)
            self.logger.info("✓ 已点击Post按钮（evaluate点击）")
            
        except Exception as e:
            self.logger.error(f"点击Post按钮失败: {e}")
            raise
    
    # ========== 验证方法 ==========
    
    def is_title_error_visible(self, timeout=3000):
        """判断Title错误提示是否显示"""
        try:
            return self.page.get_by_text('Please enter a title before submitting.').is_visible(timeout=timeout)
        except Exception:
            return False
    
    def is_description_error_visible(self, timeout=3000):
        """判断Description错误提示是否显示"""
        try:
            return self.page.get_by_text('Please enter the description before submitting').first.is_visible(timeout=timeout)
        except Exception:
            return False
    
    def is_category_error_visible(self, timeout=3000):
        """判断Category错误提示是否显示"""
        try:
            errors = self.page.get_by_text('Please fill out this field.')
            return errors.count() > 0
        except Exception:
            return False
    
    def is_price_error_visible(self, timeout=3000):
        """判断Price错误提示是否显示"""
        try:
            return self.is_visible(self.PRICE_ERROR, timeout=timeout)
        except Exception:
            return False
    
    def is_draft_saved_alert_visible(self, timeout=5000):
        """判断Draft saved Toast提示是否显示
        
        保存成功后会显示Toast：
        - "Draft Saved Successfully"
        - "Saved to Account - My Post - Drafts"
        - Toast约2-3秒后自动消失
        
        同时按钮文本会变为"Draft saved"
        """
        try:
            toast = self.page.get_by_text('Draft Saved Successfully')
            if toast.count() > 0 and toast.first.is_visible(timeout=min(3000, timeout)):
                return True
        except Exception:
            pass
        try:
            saved = self.page.get_by_text(re.compile(r'Saved to Account', re.I))
            if saved.count() > 0 and saved.first.is_visible(timeout=min(timeout, 3000)):
                return True
        except Exception:
            pass
        try:
            button = self.page.get_by_role('button', name='Draft saved')
            if button.count() > 0 and button.is_visible(timeout=min(3000, timeout)):
                return True
        except Exception:
            pass
        try:
            d = self.page.get_by_text(re.compile(r"draft\s*saved|saved\s*success|saved to", re.I))
            if d.count() > 0 and d.first.is_visible(timeout=min(4000, timeout)):
                return True
        except Exception:
            pass
        return False
    
    def is_undo_button_visible(self, timeout=3000):
        """判断Undo按钮是否显示（AI生成后）"""
        try:
            return self.page.get_by_role('button', name='Undo').is_visible(timeout=timeout)
        except Exception:
            return False
    
    def is_shuffle_button_visible(self, timeout=3000):
        """判断Shuffle按钮是否显示（AI生成后）"""
        try:
            return self.page.get_by_role('button', name='Shuffle').is_visible(timeout=timeout)
        except Exception:
            return False
