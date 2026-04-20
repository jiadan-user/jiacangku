# test_cases/体验/详情页/推荐模块/conftest.py
"""推荐模块测试 conftest"""

import pytest
from utils.browser_manager import BrowserManager
from utils.logger import setup_logger

logger = setup_logger()


@pytest.fixture(scope="function")
def page():
    """
    Function-scoped page fixture for recommendation tests
    
    每个推荐模块测试使用独立的浏览器会话
    """
    manager = None
    page_instance = None
    
    try:
        manager = BrowserManager()
        page_instance = manager.start_browser(
            browser_type='chromium',
            headless=False,
            viewport={"width": 1920, "height": 1080}
        )
        
        manager.mark_in_use()
        
        yield page_instance
        
    except Exception as e:
        logger.error(f"浏览器启动失败: {e}")
        raise
        
    finally:
        if manager:
            manager.mark_released()
            
        if page_instance:
            try:
                page_instance.close()
            except Exception as e:
                logger.warning(f"关闭 Page 失败: {e}")
                
        if manager and manager.context:
            try:
                manager.context.close()
            except Exception as e:
                logger.warning(f"关闭 Context 失败: {e}")
                
        if manager and manager.browser:
            try:
                manager.browser.close()
            except Exception as e:
                logger.warning(f"关闭 Browser 失败: {e}")
