# pages/vidflow_group_task_page.py
"""
Vidflow 消息管理 - 群发任务列表页
选择器基于用例文档推断，建议 MCP 录制后替换为实测选择器。
"""
from pages.base_page import BasePage
from utils.logger import setup_logger


class VidflowGroupTaskPage(BasePage):
    """群发任务列表页 Page Object（静默执行）"""

    def __init__(self, page):
        super().__init__(page)
        self.logger = setup_logger()

    def navigate_to_group_task_list(self, base_url):
        """打开群发任务列表直链"""
        try:
            url = f"{base_url.rstrip('/')}/#/groupTaskManagement/groupTaskList"
            self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception as e:
            self.logger.error(f"打开群发任务列表失败: {e}")
            raise

    def is_on_group_task_list_page(self, timeout=10000):
        """当前是否在群发任务列表页（URL 含 groupTaskManagement/groupTaskList）"""
        try:
            self.page.wait_for_url("**/groupTaskManagement/groupTaskList**", timeout=timeout)
            return True
        except Exception:
            return "groupTaskList" in self.page.url

    def click_message_management_tab(self):
        """点击「消息管理」tab/菜单"""
        try:
            self.page.get_by_text("消息管理").first.click()
            self.page.wait_for_timeout(1500)
        except Exception as e:
            self.logger.error(f"点击消息管理失败: {e}")
            raise

    def click_group_task_entry(self):
        """在消息管理下点击「群发任务」入口（侧栏子项易被父级遮挡，优先点包含文字的菜单项或 force）"""
        try:
            # 优先点击包含「群发任务」的 sidebar 菜单项（可点击的父级），避免被 sidebar-menu 遮挡
            menu_item = self.page.locator(".sidebar-menu-item").filter(has_text="群发任务").first
            if menu_item.is_visible(timeout=3000):
                menu_item.click(timeout=10000)
            else:
                self.page.get_by_text("群发任务").first.click(force=True, timeout=10000)
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击群发任务入口失败: {e}")
            raise

    def is_list_or_empty_visible(self, timeout=8000):
        """列表或空状态是否展示（表格/空状态区域）"""
        try:
            # 有数据：表格或列表容器；无数据：空状态
            self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
            return True
        except Exception:
            return False

    def get_list_row_count(self):
        """获取当前页列表行数（表格 tbody tr 或等效，选择器需实测）"""
        try:
            rows = self.page.locator("table tbody tr").all()
            return len(rows)
        except Exception:
            try:
                rows = self.page.locator("[class*='table'] tbody tr").all()
                return len(rows)
            except Exception:
                return 0

    def is_empty_state_visible(self, timeout=3000):
        """是否展示空状态文案/插图"""
        try:
            for text in ("暂无", "无数据", "没有", "empty", "无结果"):
                if self.page.get_by_text(text).first.is_visible(timeout=1000):
                    return True
            return False
        except Exception:
            return False

    def click_page_2_or_next(self):
        """分页：点击第 2 页或「下一页」"""
        try:
            next_btn = self.page.get_by_role("button", name="下一页").first
            if next_btn.is_visible(timeout=3000):
                next_btn.click()
                self.page.wait_for_timeout(2000)
                return
            self.page.get_by_text("2").first.click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"分页切换失败: {e}")
            raise

    def set_page_size(self, size):
        """每页条数切换（如 20、50）；页面上是「10 条/页」一行字可点，点开后再选目标条数"""
        try:
            # 点击「X 条/页」可点文字展开下拉（Ant Design 为 ant-select-content-value 等，避免点内部 input 被遮挡）
            trigger = (
                self.page.locator(".ant-pagination .ant-select-content-value").first
                .or_(self.page.get_by_title("10 条/页").first)
                .or_(self.page.locator(".ant-pagination").get_by_text("条/页").first)
            )
            trigger.click(timeout=8000)
            self.page.wait_for_timeout(500)
            self.page.get_by_text(str(size), exact=True).first.click(timeout=5000)
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"设置每页条数失败: {e}")
            raise

    def set_page_size_to_second_option(self):
        """每页条数：展开下拉后选择第二项（索引 1）"""
        try:
            trigger = (
                self.page.locator(".ant-pagination .ant-select-content-value").first
                .or_(self.page.get_by_title("10 条/页").first)
                .or_(self.page.locator(".ant-pagination").get_by_text("条/页").first)
            )
            trigger.click(timeout=8000)
            self.page.wait_for_timeout(500)
            # Ant Design 下拉选项通常在 .ant-select-item 或 .ant-select-item-option
            options = self.page.locator(".ant-select-item, .ant-select-item-option")
            options.nth(1).click(timeout=5000)
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"选择每页条数第二项失败: {e}")
            raise

    def fill_search_keyword(self, keyword):
        """搜索框输入关键词"""
        try:
            search = self.page.get_by_placeholder("搜索").or_(self.page.get_by_placeholder("请输入")).first
            search.fill(keyword)
            self.page.wait_for_timeout(500)
        except Exception:
            try:
                self.page.locator("input[type=\"search\"]").first.fill(keyword)
            except Exception as e:
                self.logger.error(f"输入搜索关键词失败: {e}")
                raise

    def trigger_search(self):
        """触发搜索（回车或点击搜索按钮）"""
        try:
            search_btn = self.page.get_by_role("button", name="搜索").first
            if search_btn.is_visible(timeout=2000):
                search_btn.click()
            else:
                self.page.keyboard.press("Enter")
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"触发搜索失败: {e}")
            raise

    def wait_for_filter_applied(self, timeout=6000):
        """筛选按钮点击后等待列表/接口更新生效（等待 dom 稳定 + 预留接口与表格重绘时间）"""
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=min(timeout, 4000))
            self.page.wait_for_timeout(2000)
        except Exception:
            self.page.wait_for_timeout(2000)

    def click_reset_filters(self):
        """点击重置按钮，清空已有筛选（搜索关键词、状态、时间等）"""
        try:
            reset_btn = self.page.get_by_role("button", name="重置").or_(
                self.page.get_by_text("重置").first
            ).first
            reset_btn.click(timeout=10000)
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击重置失败: {e}")
            raise

    def is_reset_button_visible(self, timeout=3000):
        """重置按钮是否可见（有筛选条件时通常展示）"""
        try:
            return (
                self.page.get_by_role("button", name="重置").first.is_visible(timeout=timeout)
                or self.page.get_by_text("重置").first.is_visible(timeout=timeout)
            )
        except Exception:
            return False

    def open_status_filter_dropdown(self):
        """点击状态筛选下拉框（展示为「全部状态」的触发器）打开下拉"""
        try:
            # 优先用表单内带「全部状态」的 ant-select；若无则用任意包含该文案的 ant-select
            trigger = (
                self.page.locator(".ant-form-item-control-input-content .ant-select").filter(
                    has=self.page.get_by_text("全部状态")
                )
                .or_(self.page.locator(".ant-select").filter(has_text="全部状态"))
                .first
            )
            trigger.click(timeout=10000)
            self.page.wait_for_timeout(600)
        except Exception as e:
            self.logger.error(f"打开状态筛选下拉失败: {e}")
            raise

    def select_status_option_in_dropdown(self, status_text):
        """在下拉框中点击指定状态选项（如：已暂停、已完成）"""
        try:
            # 选项可能在 .ant-select-item 或下拉层内，优先精确匹配文案
            opt = self.page.locator(".ant-select-item, .ant-select-item-option").filter(
                has_text=status_text
            ).first
            if opt.is_visible(timeout=3000):
                opt.click(timeout=10000)
            else:
                self.page.get_by_text(status_text, exact=True).first.click(timeout=10000)
            self.page.wait_for_timeout(800)
        except Exception as e:
            self.logger.error(f"选择状态选项「{status_text}」失败: {e}")
            raise

    def wait_for_status_dropdown_closed(self, timeout=3000):
        """等待状态筛选下拉关闭，避免遮罩挡住筛选按钮导致点击无效"""
        try:
            dropdown = self.page.locator(".ant-select-dropdown").first
            dropdown.wait_for(state="hidden", timeout=timeout)
        except Exception:
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(400)
        self.page.wait_for_timeout(300)

    def click_filter_button(self):
        """点击筛选按钮，触发筛选。优先点击 <span>筛 选</span>（中间有空格）确保生效"""
        try:
            # 页面上为 <span>筛 选</span>，文案中间有空格，必须点该 span 才生效
            filter_span = self.page.locator("span").filter(has_text="筛 选").first
            if filter_span.is_visible(timeout=3000):
                filter_span.click(timeout=10000, force=True)
                self.wait_for_filter_applied()
                return
            filter_btn = self.page.get_by_role("button", name="筛选").first
            if filter_btn.is_visible(timeout=2000):
                filter_btn.click(timeout=10000, force=True)
                self.wait_for_filter_applied()
                return
            self.page.get_by_text("筛选").first.click(timeout=10000, force=True)
            self.wait_for_filter_applied()
        except Exception as e:
            self.logger.error(f"点击筛选按钮失败: {e}")
            raise

    def click_filter_button_in_form(self):
        """在筛选表单区域内点击「筛选」或「查询」按钮（状态/日期共用区域，确保点对）"""
        try:
            # 筛选区域：包含 .ant-select（状态）或 .ant-picker-range（日期）的 form 或同一行
            form_area = self.page.locator(".ant-form").filter(
                has=self.page.locator(".ant-select, .ant-picker-range")
            ).first
            if form_area.is_visible(timeout=2000):
                for name in ("筛选", "查询", "搜索"):
                    btn = form_area.get_by_role("button", name=name).first
                    if btn.is_visible(timeout=1500):
                        btn.click(timeout=8000)
                        self.wait_for_filter_applied()
                        return
            self.click_filter_button()
            self.wait_for_filter_applied()
        except Exception:
            self.click_filter_button()
            self.wait_for_filter_applied()

    def select_status_filter(self, status_text):
        """按任务状态筛选：打开下拉 → 选状态 → 点击筛选（如：已暂停）"""
        try:
            self.open_status_filter_dropdown()
            self.select_status_option_in_dropdown(status_text)
            self.click_filter_button()
        except Exception as e:
            self.logger.error(f"选择状态筛选失败: {e}")
            raise

    def select_status_filter_legacy(self, status_text):
        """按任务状态筛选（旧：直接点文案，无下拉与筛选按钮）"""
        try:
            self.page.get_by_text(status_text).first.click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"选择状态筛选失败: {e}")
            raise

    def fill_start_date(self, start_date):
        """点击开始时间输入框并输入日期（如 2026-02-01）"""
        try:
            start_input = self.page.locator(".ant-picker-range .ant-picker-input").first.locator("input")
            start_input.click(timeout=8000)
            self.page.wait_for_timeout(300)
            start_input.fill(start_date)
            self.page.wait_for_timeout(300)
            start_input.press("Tab")
            self.page.wait_for_timeout(400)
        except Exception as e:
            self.logger.error(f"填写开始时间失败: {e}")
            raise

    def fill_end_date(self, end_date):
        """点击结束时间输入框并输入日期（如 2026-02-28）"""
        try:
            end_input = self.page.locator(".ant-picker-range .ant-picker-input").nth(1).locator("input")
            end_input.click(timeout=8000)
            self.page.wait_for_timeout(300)
            end_input.fill(end_date)
            self.page.wait_for_timeout(300)
            # 失焦以提交日期（Ant Design 需 blur 后表单才更新）
            end_input.press("Tab")
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"填写结束时间失败: {e}")
            raise

    def wait_for_date_picker_closed(self, timeout=3000):
        """等待日期选择器面板关闭，避免遮罩挡住筛选按钮导致点击无效"""
        try:
            dropdown = self.page.locator(".ant-picker-dropdown").first
            dropdown.wait_for(state="hidden", timeout=timeout)
        except Exception:
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(400)
        self.page.wait_for_timeout(300)

    def select_date_range(self, start_date, end_date):
        """选择开始/结束日期并点击筛选：填日期→等待面板关闭→点击 <span>筛 选</span>（与 TC009 一致）"""
        try:
            if start_date:
                self.fill_start_date(start_date)
            if end_date:
                self.fill_end_date(end_date)
            self.page.wait_for_timeout(500)
            self.wait_for_date_picker_closed()
            self.click_filter_button()
        except Exception as e:
            self.logger.error(f"选择时间范围失败: {e}")
            raise

    def click_new_task(self):
        """点击新建/创建任务"""
        try:
            for text in ("新建", "创建任务", "新建任务"):
                btn = self.page.get_by_role("button", name=text).first
                if btn.is_visible(timeout=3000):
                    btn.click()
                    self.page.wait_for_timeout(2000)
                    return
            self.page.get_by_text("新建").first.click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击新建任务失败: {e}")
            raise

    def is_modal_visible(self, timeout=3000):
        """新建/编辑弹窗是否打开"""
        try:
            return self.page.locator("[class*='modal'], [class*='dialog']").first.is_visible(timeout=timeout)
        except Exception:
            return False

    def click_next_step_in_modal(self):
        """新建任务弹窗内点击「下一步」按钮"""
        try:
            next_btn = self.page.get_by_role("button", name="下一步").first
            if next_btn.is_visible(timeout=5000):
                next_btn.click()
                self.page.wait_for_timeout(1000)
                return
            self.page.get_by_text("下一步").first.click()
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击下一步失败: {e}")
            raise

    def fill_required_task_name(self, name):
        """填写任务名称（必填项之一，选择器需实测）"""
        try:
            self.page.get_by_placeholder("任务名称").or_(self.page.get_by_label("任务名称")).first.fill(name)
            self.page.wait_for_timeout(300)
        except Exception:
            try:
                self.page.locator("input[name*='name'], input[placeholder*='名称']").first.fill(name)
            except Exception as e:
                self.logger.error(f"填写任务名称失败: {e}")
                raise

    def submit_modal(self):
        """弹窗内点击提交/确定"""
        try:
            for name in ("确定", "提交", "保存", "Submit"):
                btn = self.page.get_by_role("button", name=name).first
                if btn.is_visible(timeout=2000):
                    btn.click()
                    self.page.wait_for_timeout(2000)
                    return
        except Exception as e:
            self.logger.error(f"提交弹窗失败: {e}")
            raise

    def cancel_or_close_modal(self):
        """点击取消或关闭弹窗。优先点击文案「取 消」的 span（中间可能有空格）确保生效。"""
        try:
            # 与筛选按钮类似，页面上可能为 <span>取 消</span>，优先点该 span
            cancel_span = self.page.locator("span").filter(has_text="取 消").first
            if cancel_span.is_visible(timeout=2000):
                cancel_span.click(timeout=8000, force=True)
                self.page.wait_for_timeout(1000)
                return
            cancel_btn = self.page.get_by_role("button", name="取消").first
            if cancel_btn.is_visible(timeout=2000):
                cancel_btn.click(timeout=8000, force=True)
                self.page.wait_for_timeout(1000)
                return
            self.page.get_by_text("取消").first.click(timeout=8000, force=True)
            self.page.wait_for_timeout(1000)
        except Exception:
            try:
                self.page.locator("[class*='close'], [aria-label='Close']").first.click(timeout=5000)
                self.page.wait_for_timeout(1000)
            except Exception as e:
                self.logger.error(f"关闭弹窗失败: {e}")
                raise

    def click_edit_on_first_task(self):
        """点击第一条任务的「编辑」入口"""
        try:
            self.page.get_by_text("编辑").first.click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击编辑失败: {e}")
            raise

    def click_first_row_three_dots_icon(self):
        """点击 data-icon=\"more\" 元素展开操作菜单（优先第一行最后一列内，否则整页第一个）"""
        try:
            # 优先：第一行最后一列内的 data-icon="more"
            first_row = self.page.locator("table tbody tr").first
            last_cell = first_row.locator("td").last
            more_in_cell = last_cell.locator('[data-icon="more"]').first
            if more_in_cell.is_visible(timeout=2000):
                more_in_cell.click(timeout=10000)
            else:
                # 兜底：整页第一个 data-icon="more"（列表首行操作图标）
                self.page.locator('[data-icon="more"]').first.click(timeout=10000)
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击 data-icon=more 失败: {e}")
            raise

    def click_detail_in_dropdown(self):
        """在展开的下拉/菜单中点击「详情」按钮"""
        try:
            self.page.get_by_text("详情", exact=True).first.click(timeout=8000)
            self.page.wait_for_timeout(500)
        except Exception as e:
            self.logger.error(f"点击菜单中的详情失败: {e}")
            raise

    def close_detail_modal_with_x(self):
        """点击详情页弹窗右上角的 X 按钮关闭弹窗"""
        try:
            close_btn = self.page.locator(".ant-modal-close").first
            if not close_btn.is_visible(timeout=2000):
                close_btn = self.page.locator("[aria-label='Close']").first
            close_btn.click(timeout=8000)
            self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"点击弹窗关闭按钮失败: {e}")
            raise

    def click_view_detail_on_first_task(self):
        """点击第一条任务的「查看」/任务名称/详情入口（旧方式，保留兼容）"""
        try:
            for text in ("查看", "详情"):
                loc = self.page.get_by_text(text).first
                if loc.is_visible(timeout=3000):
                    loc.click()
                    self.page.wait_for_timeout(2000)
                    return
            self.page.locator("table tbody tr").first.locator("a").first.click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击查看详情失败: {e}")
            raise

    def click_delete_or_cancel_task(self):
        """点击某条任务的删除/取消按钮"""
        try:
            for text in ("删除", "取消"):
                btn = self.page.get_by_text(text).first
                if btn.is_visible(timeout=3000):
                    btn.click()
                    self.page.wait_for_timeout(1500)
                    return
        except Exception as e:
            self.logger.error(f"点击删除/取消失败: {e}")
            raise

    def confirm_delete_modal(self, confirm=True):
        """二次确认弹窗：确定或取消"""
        try:
            if confirm:
                for name in ("确定", "删除", "取消任务", "Confirm"):
                    btn = self.page.get_by_role("button", name=name).first
                    if btn.is_visible(timeout=2000):
                        btn.click()
                        self.page.wait_for_timeout(2000)
                        return
            else:
                self.page.get_by_role("button", name="取消").first.click()
                self.page.wait_for_timeout(1000)
        except Exception as e:
            self.logger.error(f"确认弹窗操作失败: {e}")
            raise

    def click_export_button(self):
        """点击导出按钮"""
        try:
            self.page.get_by_role("button", name="导出").first.click()
            self.page.wait_for_timeout(2000)
        except Exception as e:
            self.logger.error(f"点击导出失败: {e}")
            raise

    def get_submit_button(self):
        """获取提交按钮 locator（用于重复点击等）"""
        return self.page.get_by_role("button", name="确定").or_(self.page.get_by_role("button", name="提交")).first
