"""
Debug script to inspect ES Jobs page filter area elements
"""
import pytest
from pages.jobs_list_page_es import JobsListPageES
from test_cases.zhaopin.es_login_helper import ensure_es_logged_in
from utils.logger import setup_logger

logger = setup_logger()

_CONFIG = {
    "site": "es",
    "site_name": "西班牙站",
    "role": "jobseeker",
    "user_name": "wang_es",
    "base_url": "https://es.58v5.cn",
    "test_account": {
        "username": "wangyongli@58.com",
        "password": "Qwer1234"
    },
    "browser": {
        "type": "chromium",
        "headless": False,
        "viewport": {"width": 1920, "height": 1080}
    }
}


def test_debug_filter_elements(page, config):
    """Debug: 检查筛选器区域的实际元素"""
    ensure_es_logged_in(page, config)
    logger.info("✓ 已登录ES站")
    
    jobs_list_page = JobsListPageES(page)
    jobs_list_page.navigate_to_jobs_list()
    logger.info("✓ 已导航到Jobs列表页")
    
    # 等待额外时间确保页面加载
    page.wait_for_timeout(2000)
    
    # 检查各种选择器
    logger.info(f"当前URL: {page.url}")
    
    # 尝试查找#listPageFilterArea
    filter_area = page.locator("#listPageFilterArea")
    logger.info(f"#listPageFilterArea count: {filter_area.count()}")
    logger.info(f"#listPageFilterArea visible: {filter_area.first.is_visible() if filter_area.count() > 0 else False}")
    
    # 尝试直接查找Madrid文本
    madrid_text = page.get_by_text("Madrid")
    logger.info(f"Madrid text count: {madrid_text.count()}")
    if madrid_text.count() > 0:
        logger.info(f"Madrid text visible: {madrid_text.first.is_visible()}")
    
    # 尝试直接查找Job Type文本
    job_type = page.get_by_text("Job Type")
    logger.info(f"Job Type text count: {job_type.count()}")
    if job_type.count() > 0:
        logger.info(f"Job Type text visible: {job_type.first.is_visible()}")
    
    # 获取页面HTML结构
    filter_area_html = page.evaluate("""
        () => {
            const el = document.querySelector('#listPageFilterArea');
            return el ? el.outerHTML.substring(0, 500) : 'NOT FOUND';
        }
    """)
    logger.info(f"#listPageFilterArea HTML: {filter_area_html}")
    
    # 暂停让我们可以手动检查
    page.pause()
