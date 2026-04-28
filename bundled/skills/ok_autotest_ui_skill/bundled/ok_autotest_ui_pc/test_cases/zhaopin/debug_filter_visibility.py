import sys
from test_cases.zhaopin.explicit_waits import dom_content_loaded_soft, network_idle_soft, sg_wait_jobs_list_url, sg_after_home_jobs_icon
env python3
"""
调试脚本：检查搜索后筛选器区域的可见性状态
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from playwright.sync_api import sync_playwright
from pages.jobs_list_page_es import JobsListPageES
from utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    base_url = "https://ok.jobs"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        
        jobs_list_page = JobsListPageES(page)
        
        # 1. 导航到Jobs列表页
        logger.info("1. 导航到Jobs列表页...")
        jobs_list_page.navigate_to_jobs_list()
        dom_content_loaded_soft(page, 20000)
        # 2. 输入搜索关键词
        logger.info('2. 输入搜索关键词 "manager"')
        jobs_list_page.input_search_keyword("manager")
        dom_content_loaded_soft(page, 20000)
        # 3. 点击搜索按钮
        logger.info("3. 点击Search按钮")
        jobs_list_page.click_search_button()
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass
        dom_content_loaded_soft(page, 20000)
        logger.info(f"当前URL: {page.url}")
        
        # 4. 检查元素
        logger.info("\n=== 检查筛选器元素 ===")
        
        madrid_elements = page.get_by_text("Madrid").all()
        logger.info(f"Madrid元素数量: {len(madrid_elements)}")
        for i, elem in enumerate(madrid_elements):
            is_vis = elem.is_visible()
            bounding_box = elem.bounding_box() if is_vis else None
            logger.info(f"  Madrid[{i}]: visible={is_vis}, box={bounding_box}")
        
        job_type_elements = page.get_by_text("Job Type").all()
        logger.info(f"\nJob Type元素数量: {len(job_type_elements)}")
        for i, elem in enumerate(job_type_elements):
            is_vis = elem.is_visible()
            bounding_box = elem.bounding_box() if is_vis else None
            logger.info(f"  Job Type[{i}]: visible={is_vis}, box={bounding_box}")
        
        salary_elements = page.get_by_text("Salary").all()
        logger.info(f"\nSalary元素数量: {len(salary_elements)}")
        for i, elem in enumerate(salary_elements):
            is_vis = elem.is_visible()
            bounding_box = elem.bounding_box() if is_vis else None
            logger.info(f"  Salary[{i}]: visible={is_vis}, box={bounding_box}")
        
        # 5. 尝试滚动到筛选器区域
        logger.info("\n=== 尝试滚动到筛选器 ===")
        try:
            # 尝试滚动到第一个Madrid元素
            if len(madrid_elements) > 0:
                madrid_elements[0].scroll_into_view_if_needed()
                dom_content_loaded_soft(page, 20000)
                logger.info(f"滚动后Madrid[0] visible: {madrid_elements[0].is_visible()}")
        except Exception as e:
            logger.error(f"滚动失败: {e}")
        
        # 6. 检查viewport和滚动位置
        viewport_size = page.viewport_size
        scroll_y = page.evaluate("window.scrollY")
        logger.info(f"\nViewport: {viewport_size}, ScrollY: {scroll_y}")
        
        # 7. 暂停以便手动检查
        logger.info("\n=== 暂停，请手动检查页面 ===")
        page.pause()
        
        browser.close()

if __name__ == "__main__":
    main()
