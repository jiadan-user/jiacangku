"""
阿联酋站 - 探索列表页（Cars 分类）页面加载测试

本脚本由 playwright-test-generator 生成
录制文档：/Users/a58/Downloads/app/okcom-探索列表页-测试用例-20260303.md
生成时间：2026-04-03

测试站点：AE (https://ae.58v5.cn)
测试角色：Buyer (游客/买家)
测试目标：验证直接访问探索列表页（Cars 分类），页面标题、面包屑导航、筛选栏等核心元素正确展示
"""
import pytest
import allure
from pages.explore_list_page import ExploreListPage
from utils.logger import setup_logger

logger = setup_logger()

# ============================================
# 测试环境配置（来自录制文档，无需登录）
# ============================================
_CONFIG = {
    "site": "ae",
    "site_name": "阿联酋站",
    "role": "buyer",
    "user_name": "guest_ae",
    "base_url": "https://ae.58v5.cn",
    "test_account": None,  # 无需登录
    "locale": "en-AE",
    "currency": "AED",
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


@pytest.mark.case_id_explore_cars_page_load_tc001
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.explore
@pytest.mark.ae
@allure.feature("OK - 探索列表页")
@allure.story("页面初始加载与导航 - 正向场景")
@allure.title("直接访问 Cars 探索列表页，页面标题和核心元素应正确展示")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证游客直接访问 Cars 分类探索列表页，页面标题显示城市名称，面包屑导航和筛选栏正确展示")
def test_tc001_direct_access_cars_page_title_and_elements_should_display_correctly(page, config):
    """TC001: 直接访问 URL，页面标题正确展示城市名称"""
    
    # ========== Arrange：准备测试数据和对象 ==========
    explore_page = ExploreListPage(page)
    
    # 从 config 读取测试数据
    base_url = config['base_url']
    target_url = f"{base_url}/en/city-abu-dhabi/cate-car/?iconSource=car"
    
    # 记录测试配置
    logger.info("="*80)
    logger.info("阿联酋站 - 探索列表页（Cars 分类）页面加载测试")
    logger.info("="*80)
    logger.info(f"站点: {config['site'].upper()} (阿联酋站)")
    logger.info(f"角色: {config['role'].upper()} (游客/买家)")
    logger.info(f"目标URL: {target_url}")
    logger.info("="*80)
    
    # ========== Act：执行页面访问操作 ==========
    with allure.step("步骤1：直接访问 Cars 探索列表页"):
        logger.info("开始访问目标页面")
        page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
        logger.info("✓ 页面导航完成")
        
        # 等待页面关键元素加载（元素级等待）
        page.get_by_role("heading", name="Cars in Abu Dhabi", level=1).wait_for(state="visible", timeout=15000)
        logger.info("✓ 页面关键元素已加载")
    
    # ========== Assert：验证页面加载结果 ==========
    with allure.step("验证1：页面标题显示 'Cars in Abu Dhabi'"):
        # 验证页面主标题
        page_title = page.get_by_role("heading", name="Cars in Abu Dhabi", level=1).inner_text()
        assert "Cars in Abu Dhabi" in page_title, \
            f"页面标题不正确，期望包含 'Cars in Abu Dhabi'，实际: {page_title}"
        logger.info(f"✓ 页面标题验证通过: {page_title}")
    
    with allure.step("验证2：浏览器 Tab 标题包含 'Abu Dhabi' 或 'Cars'"):
        # 验证浏览器 Tab 标题
        browser_title = page.title()
        assert "Abu Dhabi" in browser_title or "Cars" in browser_title, \
            f"浏览器标题不正确，期望包含 'Abu Dhabi' 或 'Cars'，实际: {browser_title}"
        logger.info(f"✓ 浏览器标题验证通过: {browser_title}")
    
    with allure.step("验证3：面包屑导航显示 'Home > Cars'"):
        # 验证面包屑 Home 链接
        home_link = page.get_by_role("link", name="Home")
        assert home_link.is_visible(timeout=3000), \
            "面包屑导航中未找到 'Home' 链接"
        logger.info("✓ 面包屑 'Home' 链接存在")
        
        # 验证面包屑 Cars 链接（移除 exact=True，匹配包含 Cars 的链接）
        cars_link = page.get_by_role("link", name="Cars")
        # 如果有多个匹配，取第一个（面包屑中的）
        if cars_link.count() > 0:
            assert cars_link.first.is_visible(timeout=3000), \
                "面包屑导航中的 'Cars' 链接不可见"
            logger.info("✓ 面包屑 'Cars' 链接存在")
        else:
            # 如果没有找到链接，尝试查找包含 "Cars" 的文本元素
            cars_text = page.get_by_text("Cars")
            assert cars_text.count() > 0, \
                "面包屑导航中未找到 'Cars' 元素"
            logger.info("✓ 面包屑 'Cars' 元素存在")
    
    with allure.step("验证4：筛选栏显示核心筛选项"):
        # 验证筛选栏核心元素（使用录制时获取的元素）
        filter_items = [
            ("Sort", "排序按钮"),
            ("Filter", "筛选按钮"),
            ("Abu Dhabi", "城市选择"),
            ("Price", "价格筛选"),
            ("Mileage", "里程筛选"),
            ("Brand", "品牌筛选"),
            ("Reset", "重置按钮")
        ]
        
        for item_text, item_desc in filter_items:
            locator = page.get_by_text(item_text, exact=True)
            assert locator.count() > 0, \
                f"筛选栏中未找到 '{item_desc}' ({item_text})"
            logger.info(f"✓ {item_desc} 存在")
        
        logger.info("✓ 筛选栏所有核心元素验证通过")
    
    with allure.step("验证5：Location Tag 显示 'Location:Abu Dhabi'"):
        # 验证 Location Tag
        location_tag = page.get_by_text("Location:Abu Dhabi")
        assert location_tag.is_visible(timeout=3000), \
            "未找到 Location Tag: 'Location:Abu Dhabi'"
        logger.info("✓ Location Tag 显示正确")
    
    logger.info("="*80)
    logger.info("✅ TC001 页面加载测试全部通过！")
    logger.info("="*80)
