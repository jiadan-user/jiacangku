# 无需登录场景代码示例

> 当 `config['test_account']` 为 None 时的代码生成模板

---

## 脚本顶部 `_CONFIG`

```python
"""
美国站 - 公开页面测试

本脚本由 playwright-test-generator 生成
录制文档：docs/public_page_test.md
生成时间：2026-02-28
"""
import pytest
import allure
from pages.home_page import HomePage
from utils.logger import setup_logger

logger = setup_logger()

# ============================================
# 测试环境配置（无需登录）
# ============================================
_CONFIG = {
    "site": "us",
    "site_name": "美国站",
    "role": "visitor",           # 访客
    "user_name": "guest",        # 游客
    "base_url": "https://us.58v5.cn",
    "test_account": None,        # 无需登录
    "locale": "en-US",
    "currency": "USD",
    "browser": {
        "type": "chromium",
        "headless": False,
        "viewport": {"width": 1920, "height": 1080}
    },
    "timeout": {
        "default": 30000,
        "wait": 10000,
        "navigation": 30000
    }
}
```

---

## 测试用例代码

```python
@pytest.mark.case_id_public_page_01
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("OK")
@allure.story("公开页面访问")
@allure.title("访问首页并验证核心元素显示")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证未登录用户访问首页时，核心元素正常显示")
def test_visit_homepage_should_display_core_elements(page, config):
    """访问首页并验证核心元素显示"""
    
    # ==================== Arrange ====================
    logger.info("=" * 50)
    logger.info(f"开始测试：访问首页并验证核心元素")
    logger.info(f"站点: {config['site_name']}")
    logger.info(f"URL: {config['base_url']}")
    
    # 无需登录，直接导航到首页
    with allure.step("访问首页"):
        page.goto(config['base_url'])
        logger.info(f"✓ 已访问首页: {config['base_url']}")
    
    # ==================== Act ====================
    home_page = HomePage(page)
    
    with allure.step("等待页面加载完成"):
        home_page.wait_for_page_load()
        logger.info("✓ 页面加载完成")
    
    # ==================== Assert ====================
    with allure.step("验证核心元素显示"):
        # 验证 Logo 显示
        assert home_page.is_logo_visible(), "Logo 未显示"
        logger.info("✓ Logo 显示正常")
        
        # 验证导航栏显示
        assert home_page.is_navbar_visible(), "导航栏未显示"
        logger.info("✓ 导航栏显示正常")
        
        # 验证登录按钮显示
        assert home_page.is_login_button_visible(), "登录按钮未显示"
        logger.info("✓ 登录按钮显示正常")
    
    logger.info("=" * 50)
```

---

## 关键点

1. **`_CONFIG` 中 `test_account` 为 None**
2. **跳过登录和 SessionManager**
3. **直接使用 `page.goto(config['base_url'])`**
4. **日志中不输出账号信息**
5. **验证点聚焦于公开可见的元素**

---

## 与需要登录场景的对比

| 维度 | 需要登录 | 无需登录 |
|------|----------|----------|
| `test_account` | `{"username": "...", "password": "..."}` | `None` |
| `role` | `seller` / `buyer` | `visitor` / `guest` |
| `user_name` | `dc_seller_us` | `guest` |
| 登录逻辑 | 使用 SessionManager | 跳过 |
| 页面访问 | 登录后导航 | 直接 `page.goto()` |
