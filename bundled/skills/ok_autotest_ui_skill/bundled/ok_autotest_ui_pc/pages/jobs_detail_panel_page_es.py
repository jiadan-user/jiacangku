"""
ES站 Jobs列表页 详情面板 Page Object
专门用于ES站（西班牙站）招聘列表页右侧详情面板的内容展示与操作功能测试

页面URL: https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs
包含功能:
  - 点击列表卡片加载详情面板
  - 详情面板信息验证（标题/薪资/公司/职位标签/Description）
  - 本人帖操作：Withdraw / Edit（包括Withdraw确认弹窗）
  - 非本人帖操作：Contact（已登录跳转聊天页；未登录弹出登录引导弹窗）
  - 通用操作：Favourites / New tab / Share
  - 操作后 toast 验证
  - 操作跳转 URL 验证
  - 未登录场景：clearCookies 模拟，验证按钮权限隔离

录制依据: MCP Playwright 浏览器录制（2026-03-20 全量重录）
"""

import re

from pages.base_page import BasePage
from utils.logger import setup_logger


class JobsDetailPanelPageES(BasePage):
    """
    ES站职位列表页 - 详情面板操作 Page Object
    URL: https://es.58v5.cn/en/city-madrid2/cate-jobs/?iconSource=jobs
    """

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    # ==================== 导航 ====================

    def navigate_to_jobs_list(self, base_url: str):
        """导航到ES站招聘列表页"""
        try:
            target_url = f"{base_url}/en/city-madrid2/cate-jobs/?iconSource=jobs"
            self.page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
            try:
                self.page.wait_for_load_state("networkidle", timeout=8000)
            except Exception:
                pass
        except Exception as e:
            self.logger.error(f"导航到ES站招聘列表页失败: {e}")
            raise

    def navigate_to_jobs_list_without_login(self, base_url: str):
        """清除Cookie后导航到ES站招聘列表页（模拟未登录状态）"""
        try:
            self.page.context.clear_cookies()
            target_url = f"{base_url}/en/city-madrid2/cate-jobs/?iconSource=jobs"
            self.page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
            try:
                self.page.wait_for_load_state("networkidle", timeout=8000)
            except Exception:
                pass
            # 处理 Cookie 同意弹窗
            self._handle_cookie_consent_if_present()
        except Exception as e:
            self.logger.error(f"未登录状态导航失败: {e}")
            raise

    def _handle_cookie_consent_if_present(self):
        """处理页面 Cookie 同意弹窗（如果存在）"""
        try:
            only_essential = self.page.get_by_role("button", name="Only essential")
            if only_essential.is_visible(timeout=4000):
                only_essential.click()
                self.page.wait_for_timeout(1000)
                return
        except Exception:
            pass
        try:
            accept_all = self.page.get_by_role("button", name="Accept all")
            if accept_all.is_visible(timeout=2000):
                accept_all.click()
                self.page.wait_for_timeout(1000)
        except Exception:
            pass

    # ==================== 卡片点击 ====================

    def click_card_by_info_id(self, info_id: str):
        """
        通过帖子 InfoID 点击左侧列表卡片（href 中含 infoId，不受标题文案变更影响）

        Args:
            info_id: 帖子 InfoID（如非本人帖 6504835552588510）
        """
        try:
            scoped = self.page.locator(
                f'[class*="list-components-item-job-card"] a[href*="{info_id}"]'
            )
            if scoped.count() == 0:
                scoped = self.page.locator(f'a[href*="{info_id}"]')
            link = scoped.first
            link.wait_for(state="visible", timeout=20000)
            link.scroll_into_view_if_needed()
            link.click(timeout=30000)
            self.page.wait_for_timeout(1500)
        except Exception as e:
            self.logger.error(f"通过 infoId={info_id} 点击列表卡片失败: {e}")
            raise

    def click_first_non_own_job_card(self, own_post_info_id: str) -> str:
        """
        点击左侧列表中第一条「非本人」职位卡片。

        固定 infoId 的帖子可能已下架或不在当前城市列表，因此用「排除本人帖 id」方式选取，
        避免强依赖历史种子数据仍挂在列表上。

        Args:
            own_post_info_id: 本人帖 InfoID，含该 id 的卡片会跳过

        Returns:
            从卡片 DOM 解析到的帖子 InfoID（若无法解析则为空字符串，可再调用 get_detail_info_id_from_new_tab_href）
        """
        try:
            self.page.wait_for_selector(
                '[class*="list-components-item-job-card"]',
                timeout=20000,
            )
            cards = self.page.locator('[class*="list-components-item-job-card"]')
            n = cards.count()
            if n == 0:
                raise RuntimeError("列表页未找到职位卡片")

            for i in range(min(n, 50)):
                card = cards.nth(i)
                try:
                    html = card.evaluate("el => el.outerHTML || ''")
                except Exception:
                    continue
                if own_post_info_id in html:
                    continue
                m = re.search(r"-(\d{12,})(?:[\"'/]|$)", html or "")
                info_id = m.group(1) if m else ""
                if not info_id:
                    try:
                        href = card.locator("a[href]").first.get_attribute("href") or ""
                        info_id = self._extract_info_id_from_href(href)
                    except Exception:
                        pass
                card.scroll_into_view_if_needed()
                card.click(timeout=20000)
                self.page.wait_for_timeout(1500)
                return info_id

            raise RuntimeError(
                f"未找到非本人职位卡片（列表 {n} 条均含本人帖 id {own_post_info_id}）"
            )
        except Exception as e:
            self.logger.error(f"点击非本人职位卡片失败: {e}")
            raise

    def _extract_info_id_from_href(self, href: str) -> str:
        if not href:
            return ""
        for pattern in (r"-(\d{12,})(?:/|$)", r"infoId=(\d+)", r"/(\d{12,})/"):
            m = re.search(pattern, href, re.I)
            if m:
                return m.group(1)
        return ""

    def get_detail_info_id_from_new_tab_href(self) -> str:
        """从详情区链接解析当前帖子 InfoID（用于接口比对）。优先 New tab，其次详情卡片内帖子链接。"""
        try:
            href = self.get_new_tab_href() or ""
            if not href:
                href = (
                    self.page.get_by_role("link", name="New tab").first.get_attribute("href")
                    or ""
                )
            pid = self._extract_info_id_from_href(href)
            if pid:
                return pid
            # New tab 可能为 javascript: 或空，改为扫描详情卡片内 a[href]
            try:
                links = self.page.locator('[class*="detailsCard"] a[href]').all()
                for link in links[:20]:
                    try:
                        h = link.get_attribute("href") or ""
                        pid = self._extract_info_id_from_href(h)
                        if pid:
                            return pid
                    except Exception:
                        continue
            except Exception:
                pass
            # 最后从详情卡片 HTML 中提取典型 slug-id 形态
            try:
                html = self.page.locator('[class*="detailsCard"]').first.evaluate(
                    "el => el ? el.innerHTML : ''"
                )
                m = re.search(r"-(\d{12,})(?:[\"'/]|$)", html or "")
                if m:
                    return m.group(1)
            except Exception:
                pass
            # 属性 / 全文扫描（New tab 无 href、列表卡片无标准链接时）
            try:
                dom_id = self.page.evaluate("""
                    () => {
                      const roots = document.querySelectorAll(
                        '[class*="detailsCard"], [class*="JobDetail"], [class*="detail"]'
                      );
                      for (const root of roots) {
                        for (const a of root.attributes || []) {
                          const m = (a.value || '').match(/(\\d{13,16})/);
                          if (m) return m[1];
                        }
                        const html = root.innerHTML || '';
                        const m2 = html.match(/-(\\d{13,16})(?:["'/\\\\?]|$)/);
                        if (m2) return m2[1];
                      }
                      return '';
                    }
                """)
                if dom_id:
                    return str(dom_id)
            except Exception:
                pass
        except Exception as e:
            self.logger.error(f"解析详情区 infoId 失败: {e}")
        return ""

    def resolve_info_id_for_current_detail_panel(self, own_post_info_id: str) -> str:
        """
        根据当前详情面板标题，在详情区 DOM 中出现的候选数字 id 中通过 imcinfo 反查匹配的帖子 InfoID。
        用于列表/详情 DOM 中不含标准链接时的兜底（TC014 等）。仅扫描详情卡片，避免整页噪声 id。
        """
        panel_title = (self.get_detail_panel_title() or "").strip()
        if not panel_title:
            return ""
        try:
            detail_html = ""
            try:
                detail_html = self.page.locator('[class*="detailsCard"]').first.evaluate(
                    "el => el ? el.innerHTML : ''"
                ) or ""
            except Exception:
                detail_html = ""
            candidates = set(re.findall(r"\d{13,16}", detail_html))
            # 详情区偶无不暴露数字 id，回退整页候选（imcinfo 探测使用 quiet=True）
            if len(candidates) < 2:
                candidates |= set(re.findall(r"\d{13,16}", self.page.content() or ""))
            exact, partial = [], []
            for cid in candidates:
                if cid == own_post_info_id:
                    continue
                data = self.fetch_post_info_from_api(cid, quiet=True)
                api_t = str(data.get("Title", "")).strip()
                if not api_t:
                    continue
                if api_t == panel_title:
                    exact.append(cid)
                elif api_t in panel_title or panel_title in api_t:
                    partial.append((len(api_t), cid))
            if exact:
                return exact[0]
            if partial:
                partial.sort(reverse=True)
                return partial[0][1]
        except Exception as e:
            self.logger.error(f"resolve_info_id_for_current_detail_panel: {e}")
        return ""

    def click_card_by_text(self, title_text: str):
        """
        通过帖子标题文本点击对应卡片

        Args:
            title_text: 帖子标题关键词（如 "software engineer"）
        """
        try:
            # 找到所有匹配文本的元素，选择列表卡片区域内的那个（非详情面板）
            matches = self.page.get_by_text(title_text).all()
            clicked = False
            for el in matches:
                try:
                    # 跳过详情面板中的元素（类名含 detailsCard）
                    class_name = el.evaluate("el => el.className || ''")
                    if 'detailsCard' in class_name or 'DetailsCard' in class_name:
                        continue
                    el.scroll_into_view_if_needed()
                    el.click()
                    clicked = True
                    break
                except Exception:
                    continue
            if not clicked:
                self.page.get_by_text(title_text).first.click()
            self.page.wait_for_timeout(1500)
        except Exception as e:
            self.logger.error(f"点击标题为'{title_text}'的卡片失败: {e}")
            raise

    # ==================== 详情面板 - 文本信息读取 ====================

    def get_detail_panel_title(self) -> str:
        """获取详情面板帖子标题文本"""
        try:
            title_el = self.page.locator("[class*='detailsCardTitle']").first
            return title_el.text_content(timeout=5000) or ""
        except Exception:
            try:
                title_el = self.page.locator(".jobDetail-title, .detail-container h1").first
                return title_el.text_content(timeout=3000) or ""
            except Exception as e:
                self.logger.error(f"获取详情面板标题失败: {e}")
                return ""

    def get_detail_salary_text(self) -> str:
        """获取详情面板薪资文本（如 '€ 5,000/year'）"""
        try:
            salary_el = self.page.locator("[class*='detailsCardPrice']").first
            return salary_el.text_content(timeout=5000) or ""
        except Exception as e:
            self.logger.error(f"获取详情面板薪资失败: {e}")
            return ""

    def get_detail_company_text(self) -> str:
        """获取详情面板公司名文本（标题下方区域）"""
        try:
            company_el = self.page.locator("[class*='detailsCardCompany']").first
            return company_el.text_content(timeout=5000) or ""
        except Exception as e:
            self.logger.error(f"获取详情面板公司名失败: {e}")
            return ""

    def get_job_tags_count(self) -> int:
        """获取详情面板职位标签数量"""
        try:
            tags = self.page.locator("[class*='detailsCardEmploymentItem'], [class*='employmentItem']").all()
            return len(tags)
        except Exception:
            return 0

    def get_description_content_text(self) -> str:
        """获取 Description 段落内容文本"""
        try:
            desc_el = self.page.locator("[class*='descriptionWrapper'] p, [class*='DescriptionContent'] p").first
            return (desc_el.text_content(timeout=5000) or "").strip()
        except Exception as e:
            self.logger.error(f"获取Description内容失败: {e}")
            return ""

    # ==================== 详情面板 - 可见性判断 ====================

    def is_detail_panel_visible(self) -> bool:
        """检查右侧详情面板是否可见（通过 Description 标题判断）"""
        try:
            desc_el = self.page.locator("[class*='descriptionTitle']").first
            if desc_el.is_visible(timeout=5000):
                return True
            return self.page.get_by_text("Description").first.is_visible(timeout=3000)
        except Exception:
            return False

    def is_detail_description_visible(self) -> bool:
        """检查详情面板 Description 区域标题和内容段落是否均可见"""
        try:
            desc_title = self.page.locator("[class*='descriptionTitle']").first
            if not desc_title.is_visible(timeout=5000):
                return False
            desc_para = self.page.locator("[class*='descriptionWrapper'] p, [class*='DescriptionContent'] p").first
            return desc_para.is_visible(timeout=3000)
        except Exception:
            return False

    def is_logged_in_state(self) -> bool:
        """判断当前页面是否处于已登录状态（右上角是否有 Log in / Register）"""
        try:
            login_btn = self.page.get_by_text("Log in / Register").first
            return not login_btn.is_visible(timeout=3000)
        except Exception:
            return True

    def is_logged_out_state(self) -> bool:
        """判断当前是否处于未登录状态（右上角显示 Log in / Register）"""
        try:
            login_btn = self.page.get_by_text("Log in / Register").first
            return login_btn.is_visible(timeout=5000)
        except Exception:
            return False

    # ==================== 操作按钮 - 可见性判断 ====================

    def is_withdraw_button_visible(self) -> bool:
        """检查 Withdraw 按钮是否可见（仅本人帖已登录时显示）"""
        try:
            btn = self.page.get_by_role("button", name="Withdraw")
            return btn.is_visible(timeout=3000)
        except Exception:
            return False

    def is_edit_button_visible(self) -> bool:
        """检查 Edit 按钮是否可见（仅本人帖已登录时显示）"""
        try:
            btn = self.page.get_by_role("button", name="Edit")
            return btn.is_visible(timeout=3000)
        except Exception:
            return False

    def is_contact_button_visible(self) -> bool:
        """检查 Contact 按钮是否可见（非本人帖或未登录时显示）"""
        try:
            btn = self.page.get_by_role("button", name="Contact")
            return btn.is_visible(timeout=3000)
        except Exception:
            return False

    def is_favourites_button_visible(self) -> bool:
        """检查 Favourites 按钮是否可见（通用）"""
        try:
            btn = self.page.get_by_text("Favourites").first
            return btn.is_visible(timeout=3000)
        except Exception:
            return False

    def is_new_tab_link_visible(self) -> bool:
        """检查 New tab 链接是否可见（通用）"""
        try:
            link = self.page.get_by_role("link", name="New tab").first
            return link.is_visible(timeout=3000)
        except Exception:
            return False

    def is_share_button_visible(self) -> bool:
        """检查 Share 按钮是否可见（通用）"""
        try:
            btn = self.page.get_by_text("Share").first
            return btn.is_visible(timeout=3000)
        except Exception:
            return False

    # ==================== 操作按钮 - 执行操作 ====================

    def click_edit_button(self):
        """点击 Edit 按钮（本人帖），跳转到编辑页"""
        try:
            self.page.get_by_role("button", name="Edit").click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击Edit按钮失败: {e}")
            raise

    def click_withdraw_button(self):
        """点击 Withdraw 按钮（本人帖），弹出确认对话框"""
        try:
            self.page.get_by_role("button", name="Withdraw").click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击Withdraw按钮失败: {e}")
            raise

    def click_contact_button(self):
        """点击 Contact 按钮（非本人帖），已登录时跳转聊天页，未登录时弹出登录引导弹窗"""
        try:
            self.page.get_by_role("button", name="Contact").click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击Contact按钮失败: {e}")
            raise

    def click_favourites_button(self):
        """点击 Favourites 按钮，触发收藏/取消收藏"""
        try:
            # 优先使用 detailsCardBtnItem 类选择器（精确匹配 Favourites 按钮）
            fav_btn = self.page.locator("[class*='detailsCardBtnItem']:has-text('Favourites')").first
            fav_btn.click(timeout=10000)
        except Exception:
            try:
                self.page.get_by_text("Favourites").first.click()
            except Exception as e:
                self.logger.error(f"点击Favourites按钮失败: {e}")
                raise

    def click_share_button(self):
        """点击 Share 按钮，触发复制链接"""
        try:
            self.page.get_by_text("Share").first.click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击Share按钮失败: {e}")
            raise

    def click_new_tab_link(self):
        """点击 New tab 链接，在新标签页打开帖子详情页"""
        try:
            self.page.get_by_role("link", name="New tab").first.click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击New tab链接失败: {e}")
            raise

    # ==================== Withdraw 确认弹窗 ====================

    def is_withdraw_dialog_visible(self) -> bool:
        """检查 Withdraw 确认对话框是否出现（自定义弹层，标题 'Heads Up'）"""
        try:
            heading = self.page.get_by_text("Heads Up").first
            return heading.is_visible(timeout=5000)
        except Exception:
            return False

    def get_withdraw_dialog_body_text(self) -> str:
        """获取 Withdraw 对话框正文文本"""
        try:
            body = self.page.get_by_text("Do you want to withdraw the listing?")
            return (body.text_content(timeout=3000) or "").strip()
        except Exception:
            return ""

    def is_withdraw_dialog_has_cancel_button(self) -> bool:
        """检查 Withdraw 对话框是否包含 Cancel 按钮"""
        try:
            btn = self.page.get_by_role("button", name="Cancel")
            return btn.is_visible(timeout=3000)
        except Exception:
            return False

    def is_withdraw_dialog_has_ok_button(self) -> bool:
        """检查 Withdraw 对话框是否包含 OK 按钮"""
        try:
            btn = self.page.get_by_role("button", name="OK")
            return btn.is_visible(timeout=3000)
        except Exception:
            return False

    def click_withdraw_dialog_cancel(self):
        """点击 Withdraw 对话框中的 Cancel 按钮，关闭对话框"""
        try:
            self.page.get_by_role("button", name="Cancel").click()
            self.page.wait_for_timeout(800)
        except Exception as e:
            self.logger.error(f"点击Withdraw对话框Cancel按钮失败: {e}")
            raise

    def click_withdraw_dialog_close_icon(self):
        """点击 Withdraw 对话框右上角 × 关闭按钮"""
        try:
            close_btn = self.page.locator("img[alt='close']").first
            close_btn.click()
            self.page.wait_for_timeout(800)
        except Exception:
            try:
                close_btn = self.page.get_by_role("button", name="close").first
                close_btn.click()
                self.page.wait_for_timeout(800)
            except Exception as e:
                self.logger.error(f"点击Withdraw对话框×关闭按钮失败: {e}")
                raise

    # ==================== 未登录场景 - 登录引导弹窗 ====================

    def is_login_guide_dialog_visible(self) -> bool:
        """检查未登录点击Contact后弹出的登录引导弹窗是否可见（标题 'Welcome to OK.com'）"""
        try:
            heading = self.page.get_by_text("Welcome to OK.com")
            return heading.is_visible(timeout=5000)
        except Exception:
            return False

    def is_login_guide_dialog_has_email_input(self) -> bool:
        """检查登录引导弹窗是否包含 Email or phone number 输入框"""
        try:
            # 弹窗中输入框的 label 文本为 "Email or phone number"，placeholder 为 "placeholder"
            dialog = self.page.get_by_role("dialog")
            input_el = dialog.get_by_role("textbox").first
            return input_el.is_visible(timeout=3000)
        except Exception:
            try:
                input_el = self.page.get_by_text("Email or phone number").first
                return input_el.is_visible(timeout=3000)
            except Exception:
                return False

    def is_login_guide_continue_button_disabled(self) -> bool:
        """检查登录引导弹窗中 Continue 按钮初始状态是否为 disabled"""
        try:
            btn = self.page.get_by_role("button", name="Continue")
            return btn.is_disabled(timeout=3000)
        except Exception:
            return False

    def click_login_guide_dialog_close(self):
        """点击登录引导弹窗右上角 × 关闭按钮"""
        try:
            # 关闭按钮是 img 元素，class 含 'closeBtn'
            close_btn = self.page.locator("img[class*='closeBtn']").first
            close_btn.click()
            self.page.wait_for_timeout(800)
        except Exception:
            try:
                close_btn = self.page.locator("[aria-label='Close'], button.close, button[class*='close'], img[alt='close']").first
                close_btn.click()
                self.page.wait_for_timeout(800)
            except Exception as e:
                self.logger.error(f"点击登录引导弹窗×关闭按钮失败: {e}")
                raise

    # ==================== New tab - 新标签页 ====================

    def click_new_tab_and_get_new_page(self):
        """
        点击 New tab 链接，等待新标签页打开，返回新标签页 Page 对象

        Returns:
            新标签页 Page 对象（Playwright Page）
        """
        try:
            with self.page.context.expect_page() as new_page_info:
                self.page.get_by_role("link", name="New tab").first.click()
            new_page = new_page_info.value
            new_page.wait_for_load_state("domcontentloaded", timeout=15000)
            try:
                new_page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                pass
            return new_page
        except Exception as e:
            self.logger.error(f"点击New tab并等待新标签页失败: {e}")
            raise

    def get_new_tab_href(self) -> str:
        """获取 New tab 链接的 href 属性值（可能为空字符串，为动态赋值）"""
        try:
            href = self.page.get_by_role("link", name="New tab").first.get_attribute("href")
            return href or ""
        except Exception:
            return ""

    # ==================== Resume 入口 ====================

    def is_resume_entry_visible(self) -> bool:
        """检查详情面板侧边的 Resume 入口是否可见"""
        try:
            resume_el = self.page.get_by_text("Resume").first
            return resume_el.is_visible(timeout=5000)
        except Exception:
            return False

    def click_resume_entry(self):
        """点击 Resume 入口，跳转到简历填写页"""
        try:
            self.page.get_by_text("Resume").first.click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击Resume入口失败: {e}")
            raise

    # ==================== 接口查询：帖子信息（标题/描述） ====================

    def fetch_post_info_from_api(self, info_id: str, *, quiet: bool = False) -> dict:
        """
        通过接口查询帖子信息，返回包含 Title、Content 等字段的字典

        接口：GET https://easypost.58v5.cn/crawl/imcinfo/{infoId}
        主要字段：Title（帖子标题）、Content（帖子描述/正文）

        Args:
            info_id: 帖子 InfoID（如 "6522669642316510"）
            quiet: 为 True 时不记录 imcinfo 空响应错误（用于候选 id 探测）

        Returns:
            dict，接口返回的 JSON 对象；若请求失败则返回空 dict
        """
        try:
            url = f"https://easypost.58v5.cn/crawl/imcinfo/{info_id}"
            result = self.page.evaluate(f"""
                async () => {{
                    try {{
                        const resp = await fetch('{url}', {{
                            method: 'GET',
                            headers: {{ 'Content-Type': 'application/json' }}
                        }});
                        if (!resp.ok) return null;
                        return await resp.json();
                    }} catch (e) {{
                        return null;
                    }}
                }}
            """)
            if result is None:
                if not quiet:
                    self.logger.error(f"接口 imcinfo/{info_id} 返回 null 或请求失败")
                return {}
            return result
        except Exception as e:
            if not quiet:
                self.logger.error(f"fetch_post_info_from_api 失败 (infoId={info_id}): {e}")
            return {}

    def get_post_title_from_api(self, info_id: str) -> str:
        """
        从接口返回结果中提取帖子标题（Title 字段）

        Args:
            info_id: 帖子 InfoID

        Returns:
            标题字符串，若接口失败则返回空字符串
        """
        data = self.fetch_post_info_from_api(info_id)
        return str(data.get("Title", "")).strip()

    def get_post_content_from_api(self, info_id: str) -> str:
        """
        从接口返回结果中提取帖子描述（Content 字段）

        Args:
            info_id: 帖子 InfoID

        Returns:
            描述字符串，若接口失败则返回空字符串
        """
        data = self.fetch_post_info_from_api(info_id)
        return str(data.get("Content", "")).strip()

    # ==================== Toast / Alert 验证 ====================

    def get_toast_text(self) -> str:
        """获取 toast/alert 提示文本"""
        try:
            alert_el = self.page.get_by_role("alert").first
            text = alert_el.text_content(timeout=5000) or ""
            return text.strip()
        except Exception as e:
            self.logger.error(f"获取toast文本失败: {e}")
            return ""

    def wait_for_toast(self, expected_text: str, timeout_ms: int = 5000) -> bool:
        """等待含指定文案的 toast 出现（使用 wait_for_selector 立即捕获）"""
        # 优先使用 wait_for_selector（最快，直到 toast 出现才返回）
        try:
            self.page.wait_for_selector(
                f"[role='alert']:has-text('{expected_text}')",
                timeout=timeout_ms
            )
            return True
        except Exception:
            pass
        # 备用：Bootstrap toast 样式
        try:
            self.page.wait_for_selector(
                f".toast:has-text('{expected_text}')",
                timeout=2000
            )
            return True
        except Exception:
            pass
        # 最后检查当前 alert 文案（toast 可能已消失，只检查现存的）
        try:
            alert_els = self.page.get_by_role("alert").all()
            for alert_el in alert_els:
                try:
                    text = (alert_el.text_content(timeout=500) or "").lower()
                    if text and expected_text.lower() in text:
                        return True
                except Exception:
                    pass
        except Exception:
            pass
        return False

    def wait_for_toast_text(self, timeout_ms: int = 5000) -> str:
        """等待任意 toast 出现并返回其文本内容（用于判断 Added/Removed 状态）"""
        try:
            self.page.wait_for_selector("[role='alert']", timeout=timeout_ms)
            alert_els = self.page.get_by_role("alert").all()
            for el in alert_els:
                try:
                    text = (el.text_content(timeout=500) or "").strip()
                    if text:
                        return text
                except Exception:
                    pass
        except Exception:
            pass
        try:
            self.page.wait_for_selector(".toast", timeout=2000)
            els = self.page.locator(".toast").all()
            for el in els:
                try:
                    text = (el.text_content(timeout=500) or "").strip()
                    if text:
                        return text
                except Exception:
                    pass
        except Exception:
            pass
        return ""
