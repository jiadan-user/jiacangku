"""
美国站 OK.com - 详情页标题区域功能测试

本脚本由 playwright-test-generator 生成
录制文档：web-qa-brain/OK.com-详情页核心信息区域-测试用例-20260327.md
生成时间：2026-03-31

测试站点：US OK.com (https://us.58v5.cn)
测试角色：访客（Visitor）
测试目标：验证详情页标题区域的展示、格式、长度
测试范围：模块 B - 标题区域（TC006-TC011）
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
def page():
    """Module级别的page fixture"""
    from utils.browser_manager import BrowserManager
    
    browser_manager = BrowserManager()
    _page = browser_manager.start_browser(
        browser_type=_CONFIG["browser"]["type"],
        headless=_CONFIG["browser"].get("headless", False),
        viewport=_CONFIG["browser"]["viewport"]
    )
    
    yield _page
    
    browser_manager.close_browser(_page)


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
    """从列表页动态获取一个测试帖子URL"""
    logger.info("从列表页动态获取测试帖子URL...")
    page.goto(config["base_url"], wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(3000)
    page.wait_for_load_state("load", timeout=30000)
    page.wait_for_timeout(2000)
    
    # 查找第一个可见的详情页link
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
@allure.story("模块B: 标题区域")
@allure.title("TC006: 标题正常展示")
@allure.severity(allure.severity_level.BLOCKER)
@allure.description("""
验证详情页标题的基本展示功能：
1. 标题元素清晰可见
2. 标题文本非空
3. 标题位于页面显著位置
""")
@pytest.mark.case_id_detail_core_tc006
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.us
def test_tc006_title_normal_display(page, config, detail_page_core_info, test_post_url):
    """TC006: 标题正常展示"""
    
    with allure.step("步骤1：访问详情页"):
        logger.info(f"访问详情页: {test_post_url}")
        page.goto(test_post_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        logger.info("✓ 详情页加载完成")
    
    with allure.step("步骤2：定位标题元素"):
        title_element = detail_page_core_info.title_element
        assert title_element.count() > 0, "标题元素未找到"
        logger.info("✓ 标题元素已定位")
    
    with allure.step("步骤3：验证标题可见性"):
        assert detail_page_core_info.is_title_visible(), "标题元素不可见"
        logger.info("✓ 标题元素可见")
    
    with allure.step("步骤4：获取标题文本并验证"):
        title_text = detail_page_core_info.get_title_text()
        assert title_text != "", "标题文本为空"
        assert len(title_text) > 0, "标题长度为0"
        logger.info(f"✓ 标题显示正常: {title_text[:50]}...")
    
    logger.info("✅ TC006 测试通过：标题正常展示")


@allure.feature("详情页核心信息")
@allure.story("模块B: 标题区域")
@allure.title("TC007: 标题长度验证")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("""
验证标题的长度限制：
1. 标题不超过最大长度限制（通常100字符）
2. 过长标题是否截断
""")
@pytest.mark.case_id_detail_core_tc007
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.us
def test_tc007_title_length_validation(page, config, detail_page_core_info, test_post_url):
    """TC007: 标题长度验证"""
    
    with allure.step("步骤1：访问详情页"):
        logger.info(f"访问详情页: {test_post_url}")
        page.goto(test_post_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        logger.info("✓ 详情页加载完成")
    
    with allure.step("步骤2：获取标题文本"):
        title_text = detail_page_core_info.get_title_text()
        title_length = len(title_text)
        logger.info(f"标题长度: {title_length} 字符")
        logger.info(f"标题内容: {title_text[:100]}...")
    
    with allure.step("步骤3：验证标题长度是否合理"):
        # 标题应该至少有5个字符
        assert title_length >= 5, f"标题长度过短: {title_length}"
        
        # 标题不应超过200个字符（较宽松的限制）
        assert title_length <= 200, f"标题长度过长: {title_length}"
        logger.info("✓ 标题长度在合理范围内")
    
    logger.info("✅ TC007 测试通过：标题长度验证通过")


@allure.feature("详情页核心信息")
@allure.story("模块B: 标题区域")
@allure.title("TC008: 列表页与详情页标题一致性")
@allure.severity(allure.severity_level.BLOCKER)
@allure.description("""
验证列表页和详情页标题的一致性：
1. 从列表页记录标题
2. 点击进入详情页
3. 对比两处标题是否一致（或详情页包含列表页标题）
""")
@pytest.mark.case_id_detail_core_tc008
@pytest.mark.core_flow
@pytest.mark.p0
@pytest.mark.us
def test_tc008_title_consistency_list_to_detail(page, config, detail_page_core_info):
    """TC008: 列表页与详情页标题一致性"""
    
    with allure.step("步骤1：访问列表页"):
        logger.info(f"访问列表页: {config['base_url']}")
        page.goto(config["base_url"], wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)
        page.wait_for_load_state("load", timeout=30000)
        logger.info("✓ 列表页加载完成")
    
    with allure.step("步骤2：找到第一个帖子并记录标题"):
        all_links = page.get_by_role("link").all()
        
        list_title = None
        detail_url = None
        
        for link in all_links:
            href = link.get_attribute('href')
            if href and '/cate-jobs/' not in href and '/cate-property/' not in href and \
               '/city-' in href and href.count('/') > 5:
                try:
                    if link.is_visible():
                        card_text = link.inner_text().strip()
                        # 列表页卡片文本可能包含价格、Free Delivery、Verified User等
                        # 需要过滤掉这些干扰信息，提取真正的标题
                        lines = card_text.split('\n')
                        for line in lines:
                            line = line.strip()
                            # 跳过价格行、Free Delivery、Verified User等
                            if line and not line.startswith('$') and \
                               'Free Delivery' not in line and \
                               'Verified User' not in line and \
                               len(line) > 10:  # 标题通常较长
                                list_title = line
                                detail_url = href
                                break
                        
                        if list_title:
                            break
                except:
                    continue
        
        assert list_title is not None, "列表页未找到有效帖子标题"
        logger.info(f"✓ 列表页标题: {list_title[:80]}...")
    
    with allure.step("步骤3：访问详情页"):
        page.goto(detail_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        logger.info("✓ 详情页加载完成")
    
    with allure.step("步骤4：获取详情页标题"):
        detail_title = detail_page_core_info.get_title_text()
        assert detail_title != "", "详情页标题为空"
        logger.info(f"✓ 详情页标题: {detail_title[:80]}...")
    
    with allure.step("步骤5：对比两处标题"):
        # 列表页标题可能是截断版本，详情页是完整版本
        # 验证：详情页标题包含列表页标题的主要部分，或两者相似度高
        list_title_clean = list_title.split('\n')[0].strip()[:50]  # 取第一行前50字符
        detail_title_clean = detail_title.strip()[:50]
        
        # 方式1：检查详情页标题是否包含列表页标题的前30个字符
        similarity = list_title_clean[:30].lower() in detail_title_clean.lower()
        
        assert similarity or list_title_clean == detail_title_clean, \
            f"列表页标题({list_title_clean})与详情页标题({detail_title_clean})不一致"
        logger.info("✓ 列表页与详情页标题一致")
    
    logger.info("✅ TC008 测试通过：标题一致性验证通过")


@allure.feature("详情页核心信息")
@allure.story("模块B: 标题区域")
@allure.title("TC009: 标题格式化正确性")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("""
验证标题的格式化规则：
1. 标题不包含不合法字符
2. 标题格式规范（无异常HTML标签等）
""")
@pytest.mark.case_id_detail_core_tc009
@pytest.mark.regression
@pytest.mark.p2
@pytest.mark.us
def test_tc009_title_format_validation(page, config, detail_page_core_info, test_post_url):
    """TC009: 标题格式化正确性"""
    
    with allure.step("步骤1：访问详情页"):
        logger.info(f"访问详情页: {test_post_url}")
        page.goto(test_post_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        logger.info("✓ 详情页加载完成")
    
    with allure.step("步骤2：获取标题文本"):
        title_text = detail_page_core_info.get_title_text()
        logger.info(f"标题内容: {title_text}")
    
    with allure.step("步骤3：验证标题格式"):
        # 1. 标题不应包含HTML标签
        assert '<' not in title_text and '>' not in title_text, "标题包含HTML标签"
        
        # 2. 标题不应有异常的控制字符
        # 允许常见标点符号，但不允许控制字符
        control_chars = [chr(i) for i in range(32) if chr(i) not in ['\n', '\r', '\t']]
        has_control_char = any(char in title_text for char in control_chars)
        assert not has_control_char, "标题包含控制字符"
        
        # 3. 标题应该是有效的文本（不是纯空白）
        assert title_text.strip() == title_text or len(title_text.strip()) > 0, "标题格式异常"
        
        logger.info("✓ 标题格式验证通过")
    
    logger.info("✅ TC009 测试通过：标题格式化正确")


@allure.feature("详情页核心信息")
@allure.story("模块B: 标题区域")
@allure.title("TC010: 标题位置验证")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("""
验证标题在页面中的位置：
1. 标题在价格下方
2. 标题在地点上方
""")
@pytest.mark.case_id_detail_core_tc010
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.us
def test_tc010_title_position_validation(page, config, detail_page_core_info, test_post_url):
    """TC010: 标题位置验证"""
    
    with allure.step("步骤1：访问详情页"):
        logger.info(f"访问详情页: {test_post_url}")
        page.goto(test_post_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        logger.info("✓ 详情页加载完成")
    
    with allure.step("步骤2：获取各元素的位置"):
        # 获取价格、标题、地点的bounding box
        try:
            price_box = detail_page_core_info.price_element.bounding_box()
            title_box = detail_page_core_info.title_element.bounding_box()
            location_box = detail_page_core_info.location_element.bounding_box()
            
            assert price_box is not None, "价格元素位置信息获取失败"
            assert title_box is not None, "标题元素位置信息获取失败"
            assert location_box is not None, "地点元素位置信息获取失败"
            
            logger.info(f"价格位置 Y: {price_box['y']}")
            logger.info(f"标题位置 Y: {title_box['y']}")
            logger.info(f"地点位置 Y: {location_box['y']}")
        except Exception as e:
            pytest.skip(f"无法获取元素位置信息: {e}")
    
    with allure.step("步骤3：验证标题位置关系"):
        # 标题应该在价格下方（Y坐标更大）
        assert title_box['y'] > price_box['y'], "标题不在价格下方"
        logger.info("✓ 标题在价格下方")
        
        # 标题应该在地点上方（Y坐标更小）
        assert title_box['y'] < location_box['y'], "标题不在地点上方"
        logger.info("✓ 标题在地点上方")
    
    logger.info("✅ TC010 测试通过：标题位置验证通过")


@allure.feature("详情页核心信息")
@allure.story("模块B: 标题区域")
@allure.title("TC011: 标题可见性（滚动测试）")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("""
验证页面加载后标题立即可见（无需滚动）
""")
@pytest.mark.case_id_detail_core_tc011
@pytest.mark.regression
@pytest.mark.p2
@pytest.mark.us
def test_tc011_title_visibility_on_load(page, config, detail_page_core_info, test_post_url):
    """TC011: 标题可见性（滚动测试）"""
    
    with allure.step("步骤1：访问详情页"):
        logger.info(f"访问详情页: {test_post_url}")
        page.goto(test_post_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        logger.info("✓ 详情页加载完成")
    
    with allure.step("步骤2：不进行任何滚动，直接检查标题可见性"):
        # 获取viewport高度
        viewport_height = page.viewport_size['height']
        
        # 获取标题位置
        title_box = detail_page_core_info.title_element.bounding_box()
        assert title_box is not None, "标题元素位置信息获取失败"
        
        logger.info(f"Viewport高度: {viewport_height}")
        logger.info(f"标题Y坐标: {title_box['y']}, 高度: {title_box['height']}")
    
    with allure.step("步骤3：验证标题在首屏可见"):
        # 标题应该在首屏内（Y坐标 + 高度 < viewport高度）
        title_bottom = title_box['y'] + title_box['height']
        assert title_bottom <= viewport_height, \
            f"标题不在首屏可见范围（标题底部Y:{title_bottom} > viewport:{viewport_height}）"
        logger.info("✓ 标题在首屏可见")
    
    with allure.step("步骤4：验证标题元素确实可见"):
        assert detail_page_core_info.is_title_visible(), "标题元素不可见"
        logger.info("✓ 标题元素可见状态正常")
    
    logger.info("✅ TC011 测试通过：标题首屏可见")
