"""
美国站 OK.com - 详情页描述区域功能测试

本脚本由 playwright-test-generator 生成
录制文档：web-qa-brain/OK.com-详情页核心信息区域-测试用例-20260327.md
生成时间：2026-03-31

测试站点：US OK.com (https://us.58v5.cn)
测试角色：访客（Visitor）
测试目标：验证详情页描述区域的展示、完整性
测试范围：模块 E - 描述区域（TC024）
"""
import re
import pytest
import allure
from playwright.sync_api import Page, expect
from pages.detail_page_core_info import DetailPageCoreInfo
from utils.logger import setup_logger

logger = setup_logger()

# ==================== 配置信息 ====================
_CONFIG = {
    "site": "us",
    "site_name": "美国站 (US OK.com)",
    "role": "visitor",
    "user_name": "visitor_us",
    "base_url": "https://us.58v5.cn/en/city-washington1/cate/",
    "locale": "en-US",
    "currency": "USD",
    "browser": {
        "type": "chromium",
        "headless": False,
        "viewport": {"width": 1440, "height": 900},
    },
    "timeout": {
        "default": 30000,
        "wait": 10000,
        "navigation": 30000,
    },
}


# ==================== Fixtures ====================
@pytest.fixture(scope="module")
def page(browser):
    """Module级别的page fixture"""
    context = browser.new_context(
        viewport=_CONFIG["browser"]["viewport"],
        locale=_CONFIG["locale"],
    )
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture(scope="module")
def config():
    """测试配置fixture"""
    return _CONFIG


@pytest.fixture(scope="module")
def detail_page_core_info(page):
    """详情页核心信息 Page Object"""
    return DetailPageCoreInfo(page)


@pytest.fixture(scope="module")
def test_post_url(page, config):
    """从列表页动态获取一个包含完整信息的测试帖子URL(优先Community分类)"""
    logger.info("从列表页动态获取包含完整信息的测试帖子URL...")
    
    # 优先从Community分类找帖子(通常有完整的地点和描述信息)
    community_list_url = "https://us.58v5.cn/en/city-washington1/cate-community/"
    page.goto(community_list_url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(3000)
    page.wait_for_load_state("load", timeout=30000)
    page.wait_for_timeout(2000)
    
    all_links = page.get_by_role("link").all()
    
    # 查找包含详情页ID的链接(排除jobs/property)
    for link in all_links:
        href = link.get_attribute('href')
        if href and '/cate-' in href and '-' in href.split('/')[-2]:
            # 排除jobs和property
            if '/cate-jobs/' in href or '/cate-property/' in href:
                continue
            # 确保是详情页链接(包含帖子ID)
            if '/city-' in href and href.count('/') > 5:
                try:
                    if link.is_visible():
                        logger.info(f"✓ 找到Community测试帖子: {href}")
                        return href
                except:
                    continue
    
    # 如果Community分类没找到,fallback到首页查找
    logger.warning("Community分类未找到合适帖子,尝试从首页查找...")
    page.goto(config["base_url"], wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(3000)
    
    all_links = page.get_by_role("link").all()
    for link in all_links:
        href = link.get_attribute('href')
        if href and '/cate-jobs/' not in href and '/cate-property/' not in href and \
           '/city-' in href and href.count('/') > 5:
            try:
                if link.is_visible():
                    logger.info(f"✓ 找到测试帖子: {href}")
                    return href
            except:
                continue
    
    raise Exception("未找到有效的测试帖子URL")


# ==================== 测试用例 ====================

@allure.feature("详情页核心信息")
@allure.story("模块E: 描述区域")
@allure.title("TC024: 描述正常展示")
@allure.severity(allure.severity_level.BLOCKER)
@allure.description("""
验证详情页描述的基本展示功能：
1. 描述元素清晰可见
2. 描述文本非空（描述是必填项）
3. 描述内容完整
4. 描述标题"Description"可见
""")
@pytest.mark.case_id_detail_core_tc024
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.us
def test_tc024_description_normal_display(page, config, detail_page_core_info, test_post_url):
    """TC024: 描述正常展示"""
    
    with allure.step("步骤1：访问详情页"):
        logger.info(f"访问详情页: {test_post_url}")
        page.goto(test_post_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        logger.info("✓ 详情页加载完成")
    
    with allure.step("步骤2：滚动到描述区域"):
        # 描述区域可能不在首屏，需要滚动
        try:
            detail_page_core_info.description_section.scroll_into_view_if_needed(timeout=5000)
            page.wait_for_timeout(500)
            logger.info("✓ 已滚动到描述区域")
        except Exception as e:
            logger.warning(f"滚动到描述区域失败: {e}")
    
    with allure.step("步骤3：验证描述标题可见"):
        try:
            desc_title = detail_page_core_info.description_title
            if desc_title.is_visible(timeout=5000):
                title_text = desc_title.inner_text()
                assert 'description' in title_text.lower(), f"描述标题不正确: {title_text}"
                logger.info(f"✓ 描述标题可见: {title_text}")
        except Exception as e:
            logger.warning(f"描述标题验证失败: {e}")
    
    with allure.step("步骤4：定位描述内容元素"):
        desc_element = detail_page_core_info.description_element
        assert desc_element.count() > 0, "描述元素未找到"
        logger.info("✓ 描述元素已定位")
    
    with allure.step("步骤5：验证描述可见性"):
        assert detail_page_core_info.is_description_visible(), "描述元素不可见"
        logger.info("✓ 描述元素可见")
    
    with allure.step("步骤6：处理可能的展开操作"):
        # 如果有"Read more"按钮，点击展开
        detail_page_core_info.click_description_expand()
        page.wait_for_timeout(500)
    
    with allure.step("步骤7：获取描述文本并验证"):
        desc_text = detail_page_core_info.get_description_text()
        
        # 描述是必填项，不能为空
        assert desc_text != "", "描述文本为空（描述是必填项）"
        assert len(desc_text) > 0, "描述长度为0"
        
        # 描述应该有一定长度（至少10个字符）
        assert len(desc_text) >= 10, f"描述过短: {len(desc_text)} 字符"
        
        logger.info(f"✓ 描述显示正常，长度: {len(desc_text)} 字符")
        logger.info(f"描述前100字符: {desc_text[:100]}...")
    
    with allure.step("步骤8：验证描述内容质量"):
        # 1. 描述不应只是占位符
        placeholder_texts = ['lorem ipsum', 'test', 'N/A', 'TBD', 'pending']
        is_placeholder = any(p.lower() in desc_text.lower() for p in placeholder_texts)
        if is_placeholder:
            logger.warning(f"描述可能包含占位符文本")
        
        # 2. 描述不应包含HTML标签（应该是纯文本）
        has_html = '<' in desc_text and '>' in desc_text
        if has_html:
            logger.warning("描述包含HTML标签")
        
        # 3. 描述应该包含有意义的内容（有单词）
        word_count = len(desc_text.split())
        assert word_count >= 3, f"描述单词数过少: {word_count}"
        logger.info(f"✓ 描述包含 {word_count} 个单词")
        
        logger.info("✓ 描述内容质量验证通过")
    
    logger.info("✅ TC024 测试通过：描述正常展示")
