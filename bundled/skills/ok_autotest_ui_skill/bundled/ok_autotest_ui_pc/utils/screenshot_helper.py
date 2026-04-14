"""
截图辅助工具
解决 Playwright 截图时字体加载超时的问题
"""
from playwright.sync_api import Page
from typing import Optional
import time


def safe_screenshot(
    page: Page,
    path: str,
    timeout: int = 60000,
    full_page: bool = False,
    retry_count: int = 2
) -> bool:
    """
    安全截图，处理字体加载超时问题
    
    Args:
        page: Playwright Page 对象
        path: 截图保存路径
        timeout: 超时时间（毫秒），默认 60 秒
        full_page: 是否截取整个页面，默认 False
        retry_count: 重试次数，默认 2 次
        
    Returns:
        bool: 截图是否成功
    """
    for attempt in range(retry_count):
        try:
            # 等待页面稳定
            page.wait_for_load_state('networkidle', timeout=10000)
            
            # 尝试截图
            page.screenshot(
                path=path,
                timeout=timeout,
                full_page=full_page,
                animations='disabled'  # 禁用动画，加快截图
            )
            return True
            
        except Exception as e:
            if attempt < retry_count - 1:
                print(f"截图失败（尝试 {attempt + 1}/{retry_count}），重试中... 错误: {str(e)}")
                time.sleep(1)
                continue
            else:
                print(f"截图失败，已达到最大重试次数。错误: {str(e)}")
                # 最后一次尝试：使用更宽松的参数
                try:
                    page.screenshot(
                        path=path,
                        timeout=120000,  # 2 分钟
                        full_page=full_page
                    )
                    return True
                except Exception as final_error:
                    print(f"最终截图失败: {str(final_error)}")
                    return False


def screenshot_with_scroll(
    page: Page,
    path: str,
    scroll_delay: int = 500,
    timeout: int = 60000
) -> bool:
    """
    滚动页面后截图，确保所有内容加载完成
    
    Args:
        page: Playwright Page 对象
        path: 截图保存路径
        scroll_delay: 滚动后等待时间（毫秒）
        timeout: 超时时间（毫秒）
        
    Returns:
        bool: 截图是否成功
    """
    try:
        # 滚动到页面底部，触发懒加载
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(scroll_delay)
        
        # 滚动回顶部
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(scroll_delay)
        
        # 截图
        return safe_screenshot(page, path, timeout=timeout)
        
    except Exception as e:
        print(f"滚动截图失败: {str(e)}")
        return False


def screenshot_element(
    page: Page,
    selector: str,
    path: str,
    timeout: int = 30000
) -> bool:
    """
    截取特定元素
    
    Args:
        page: Playwright Page 对象
        selector: 元素选择器
        path: 截图保存路径
        timeout: 超时时间（毫秒）
        
    Returns:
        bool: 截图是否成功
    """
    try:
        element = page.locator(selector).first
        element.wait_for(state='visible', timeout=timeout)
        element.screenshot(path=path, timeout=timeout)
        return True
        
    except Exception as e:
        print(f"元素截图失败: {str(e)}")
        return False
