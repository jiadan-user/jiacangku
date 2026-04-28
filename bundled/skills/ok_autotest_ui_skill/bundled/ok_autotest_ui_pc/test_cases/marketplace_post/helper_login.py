"""
辅助脚本：自动登录并验证发布页（与 marketplace_login_helper 一致）

使用方法：
    pytest test_cases/marketplace_post/helper_login.py -v -s

账号：下方 _CONFIG['test_account'] 优先；仅当未配置时再使用环境变量
MARKETPLACE_TEST_PHONE / MARKETPLACE_TEST_PASSWORD（见 marketplace_login_helper）。
"""
import pytest

from utils.logger import setup_logger
from utils.marketplace_login_helper import login_and_navigate_to_post_page

logger = setup_logger()

# conftest 的 config fixture 依赖模块级 _CONFIG
_CONFIG = {
    "base_url": "https://aepub.58v5.cn",
    "test_account": {
        "phone": "15038372881",
        "password": "a123456",
    },
    "browser": {"type": "chromium", "headless": False, "viewport": {"width": 1920, "height": 1080}},
}


@pytest.mark.helper
def test_helper_login(page, config):
    """辅助脚本：自动登录并进入 classified 发布页"""
    
    logger.info("="*80)
    logger.info("辅助脚本：自动登录（login_and_navigate_to_post_page）")
    logger.info("="*80)

    acc = config.get("test_account") or {}
    base_url = config.get("base_url") or "https://aepub.58v5.cn"
    phone = acc.get("phone") or acc.get("username")
    password = acc.get("password")

    login_and_navigate_to_post_page(page, base_url, phone=phone, password=password)

    page.screenshot(path="debug_publish_page.png", timeout=60000)
    logger.info("✓ 已保存截图: debug_publish_page.png")
    
    # 保持浏览器打开一段时间，让用户可以手动验证
    logger.info("")
    logger.info("="*80)
    logger.info("✅ 登录流程完成！")
    logger.info("浏览器将保持打开30秒，请手动验证登录状态...")
    logger.info("Session已保存，后续测试将自动使用此登录状态")
    logger.info("="*80)
    
    # 非固定盲等：可手动关页签提前结束，或最长 30s
    try:
        page.wait_for_event("close", timeout=30000)
    except Exception:
        pass
    
    logger.info("✓ 辅助脚本执行完成")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
