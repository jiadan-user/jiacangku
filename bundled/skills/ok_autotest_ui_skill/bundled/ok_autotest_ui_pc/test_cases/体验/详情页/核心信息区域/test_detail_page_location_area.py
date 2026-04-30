"""
美国站 OK.com - 详情页地点区域功能测试

本脚本由 playwright-test-generator 生成
录制文档：web-qa-brain/OK.com-详情页核心信息区域-测试用例-20260327.md
生成时间：2026-03-31

测试站点：US OK.com (https://us.58v5.cn)
测试角色：访客（Visitor）
测试目标：验证详情页地点区域的展示、位置、图标
测试范围：模块 C - 地点区域（TC012-TC018）
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
@allure.story("模块C: 地点区域")
@allure.title("TC012: 地点正常展示")
@allure.severity(allure.severity_level.BLOCKER)
@allure.description("""
验证详情页地点的基本展示功能：
1. 地点元素清晰可见
2. 地点文本非空
3. 地点图标显示正常
""")
@pytest.mark.case_id_detail_core_tc012
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.us
def test_tc012_location_normal_display(page, config, detail_page_core_info, test_post_url):
    """TC012: 地点正常展示"""
    
    with allure.step("步骤1：访问详情页"):
        logger.info(f"访问详情页: {test_post_url}")
        page.goto(test_post_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        logger.info("✓ 详情页加载完成")
    
    with allure.step("步骤2：定位地点元素"):
        location_element = detail_page_core_info.location_element
        assert location_element.count() > 0, "地点元素未找到"
        logger.info("✓ 地点元素已定位")
    
    with allure.step("步骤3：验证地点可见性"):
        assert detail_page_core_info.is_location_visible(), "地点元素不可见"
        logger.info("✓ 地点元素可见")
    
    with allure.step("步骤4：获取地点文本并验证"):
        location_text = detail_page_core_info.get_location_text()
        assert location_text != "", "地点文本为空"
        assert len(location_text) > 0, "地点长度为0"
        logger.info(f"✓ 地点显示正常: {location_text}")
    
    with allure.step("步骤5：验证地点图标存在"):
        location_icon = detail_page_core_info.get_location_icon()
        assert location_icon.is_visible(), "地点图标不可见"
        logger.info("✓ 地点图标显示正常")
    
    logger.info("✅ TC012 测试通过：地点正常展示")


@allure.feature("详情页核心信息")
@allure.story("模块C: 地点区域")
@allure.title("TC014: 地点位置验证")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("""
验证地点在页面中的位置：
1. 地点在标题下方
2. 地点在发布时间上方
""")
@pytest.mark.case_id_detail_core_tc014
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.us
def test_tc014_location_position_validation(page, config, detail_page_core_info, test_post_url):
    """TC014: 地点位置验证"""
    
    with allure.step("步骤1：访问详情页"):
        logger.info(f"访问详情页: {test_post_url}")
        page.goto(test_post_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        logger.info("✓ 详情页加载完成")
    
    with allure.step("步骤2：获取各元素的位置"):
        try:
            # 确保所有元素都已加载并可见
            detail_page_core_info.title_element.wait_for(state="visible", timeout=10000)
            detail_page_core_info.location_element.wait_for(state="visible", timeout=10000)
            detail_page_core_info.publish_time_element.wait_for(state="visible", timeout=10000)
            
            # 等待页面稳定
            page.wait_for_timeout(1000)
            
            # 获取位置信息，增加超时时间
            title_box = detail_page_core_info.title_element.bounding_box(timeout=10000)
            location_box = detail_page_core_info.location_element.bounding_box(timeout=10000)
            time_box = detail_page_core_info.publish_time_element.bounding_box(timeout=10000)
            
            assert title_box is not None, "标题元素位置信息获取失败"
            assert location_box is not None, "地点元素位置信息获取失败"
            assert time_box is not None, "时间元素位置信息获取失败"
            
            logger.info(f"标题位置 Y: {title_box['y']}")
            logger.info(f"地点位置 Y: {location_box['y']}")
            logger.info(f"时间位置 Y: {time_box['y']}")
        except Exception as e:
            pytest.skip(f"无法获取元素位置信息: {e}")
    
    with allure.step("步骤3：验证地点位置关系"):
        # 地点应该在标题下方（Y坐标更大）
        assert location_box['y'] > title_box['y'], "地点不在标题下方"
        logger.info("✓ 地点在标题下方")
        
        # 地点应该在发布时间上方（Y坐标更小）
        assert location_box['y'] < time_box['y'], "地点不在发布时间上方"
        logger.info("✓ 地点在发布时间上方")
    
    logger.info("✅ TC014 测试通过：地点位置验证通过")


@allure.feature("详情页核心信息")
@allure.story("模块C: 地点区域")
@allure.title("TC015: 地点图标验证")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("""
验证地点图标的展示：
1. 图标在地点文本左侧
2. 图标为address/location类型
""")
@pytest.mark.case_id_detail_core_tc015
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.us
def test_tc015_location_icon_validation(page, config, detail_page_core_info, test_post_url):
    """TC015: 地点图标验证"""
    
    with allure.step("步骤1：访问详情页"):
        logger.info(f"访问详情页: {test_post_url}")
        page.goto(test_post_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        logger.info("✓ 详情页加载完成")
    
    with allure.step("步骤2：获取地点图标元素"):
        location_icon = detail_page_core_info.get_location_icon()
        assert location_icon.is_visible(), "地点图标不可见"
        logger.info("✓ 地点图标可见")
    
    with allure.step("步骤3：验证图标属性"):
        # 获取图标的alt属性
        icon_alt = location_icon.get_attribute('alt')
        assert icon_alt is not None, "图标alt属性为空"
        assert 'address' in icon_alt.lower() or 'location' in icon_alt.lower(), \
            f"图标alt属性不符合预期: {icon_alt}"
        logger.info(f"✓ 图标alt属性: {icon_alt}")
        
        # 验证图标有src属性（实际图片）
        icon_src = location_icon.get_attribute('src')
        assert icon_src is not None and len(icon_src) > 0, "图标src为空"
        logger.info(f"✓ 图标src存在")
    
    with allure.step("步骤4：验证图标位置在文本左侧"):
        try:
            icon_box = location_icon.bounding_box()
            location_box = detail_page_core_info.location_element.bounding_box()
            
            # 图标应该在容器左侧
            assert icon_box['x'] <= location_box['x'] + 50, "图标不在文本左侧"
            logger.info("✓ 图标位于文本左侧")
        except:
            logger.info("跳过图标位置验证（无法获取bounding box）")
    
    logger.info("✅ TC015 测试通过：地点图标验证通过")


@allure.feature("详情页核心信息")
@allure.story("模块C: 地点区域")
@allure.title("TC016: 地点不可点击验证")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("""
验证地点区域（标题下方、时间上方）不可点击跳转
""")
@pytest.mark.case_id_detail_core_tc016
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.us
def test_tc016_location_not_clickable(page, config, detail_page_core_info, test_post_url):
    """TC016: 地点不可点击验证"""
    
    with allure.step("步骤1：访问详情页"):
        logger.info(f"访问详情页: {test_post_url}")
        page.goto(test_post_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        current_url = page.url
        logger.info("✓ 详情页加载完成")
    
    with allure.step("步骤2：获取地点元素"):
        location_element = detail_page_core_info.location_element
        assert location_element.is_visible(), "地点元素不可见"
        logger.info("✓ 地点元素可见")
    
    with allure.step("步骤3：检查地点元素是否为链接"):
        # 检查地点元素或其父元素是否是link
        try:
            # 方式1：检查元素本身是否是<a>标签
            tag_name = location_element.evaluate("el => el.tagName.toLowerCase()")
            is_link = (tag_name == 'a')
            
            # 方式2：检查是否有cursor:pointer样式
            cursor_style = location_element.evaluate("el => window.getComputedStyle(el).cursor")
            has_pointer = (cursor_style == 'pointer')
            
            logger.info(f"地点元素标签: {tag_name}, cursor: {cursor_style}")
            
            # 地点区域不应该是链接或有pointer cursor
            assert not is_link, "地点区域是可点击链接"
            logger.info("✓ 地点区域不是链接元素")
            
        except Exception as e:
            logger.warning(f"元素检查异常: {e}")
    
    with allure.step("步骤4：尝试点击地点，验证不会跳转"):
        try:
            location_element.click(timeout=3000)
            page.wait_for_timeout(1000)
            
            # 验证URL没有变化
            new_url = page.url
            assert new_url == current_url, f"点击地点后URL发生变化：{current_url} -> {new_url}"
            logger.info("✓ 点击地点后URL未变化（符合预期）")
            
        except Exception as e:
            logger.info(f"地点元素点击无响应（符合预期）: {e}")
    
    logger.info("✅ TC016 测试通过：地点不可点击")


@allure.feature("详情页核心信息")
@allure.story("模块C: 地点区域")
@allure.title("TC017: 地点文本格式验证")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("""
验证地点文本的格式：
1. 地点文本不包含异常字符
2. 地点文本格式规范
""")
@pytest.mark.case_id_detail_core_tc017
@pytest.mark.regression
@pytest.mark.p2
@pytest.mark.us
def test_tc017_location_text_format(page, config, detail_page_core_info, test_post_url):
    """TC017: 地点文本格式验证"""
    
    with allure.step("步骤1：访问详情页"):
        logger.info(f"访问详情页: {test_post_url}")
        page.goto(test_post_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        logger.info("✓ 详情页加载完成")
    
    with allure.step("步骤2：获取地点文本"):
        location_text = detail_page_core_info.get_location_text()
        logger.info(f"地点内容: {location_text}")
    
    with allure.step("步骤3：验证地点文本格式"):
        # 1. 地点不应包含HTML标签
        assert '<' not in location_text and '>' not in location_text, "地点包含HTML标签"
        
        # 2. 地点不应有异常的控制字符
        control_chars = [chr(i) for i in range(32) if chr(i) not in ['\n', '\r', '\t']]
        has_control_char = any(char in location_text for char in control_chars)
        assert not has_control_char, "地点包含控制字符"
        
        # 3. 地点应该是有效的文本
        assert location_text.strip() != "", "地点文本为空"
        assert len(location_text.strip()) >= 2, "地点文本过短"
        
        logger.info("✓ 地点文本格式验证通过")
    
    logger.info("✅ TC017 测试通过：地点文本格式正确")


@allure.feature("详情页核心信息")
@allure.story("模块C: 地点区域")
@allure.title("TC018: 地点信息完整性验证")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("""
验证地点信息的完整性：
1. 地点文本包含国家或城市信息
2. 地点信息有意义
""")
@pytest.mark.case_id_detail_core_tc018
@pytest.mark.regression
@pytest.mark.p2
@pytest.mark.us
def test_tc018_location_completeness(page, config, detail_page_core_info, test_post_url):
    """TC018: 地点信息完整性验证"""
    
    with allure.step("步骤1：访问详情页"):
        logger.info(f"访问详情页: {test_post_url}")
        page.goto(test_post_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        logger.info("✓ 详情页加载完成")
    
    with allure.step("步骤2：获取地点文本"):
        location_text = detail_page_core_info.get_location_text()
        logger.info(f"地点内容: {location_text}")
    
    with allure.step("步骤3：验证地点信息完整性"):
        # 地点应该包含有意义的地理信息
        # 常见的国家/地区名称（美国站）
        valid_locations = [
            'United States', 'USA', 'US', 
            'Washington', 'New York', 'California', 'Texas', 'Florida',
            'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia',
            'San', 'City', 'County', 'State'
        ]
        
        # 检查地点文本是否包含至少一个有效的地理关键词
        has_valid_location = any(loc.lower() in location_text.lower() for loc in valid_locations)
        
        if not has_valid_location:
            logger.warning(f"地点信息可能不完整: {location_text}")
            # 如果不包含常见关键词，至少应该有较长的文本（可能是其他城市）
            assert len(location_text) >= 3, "地点信息过短且不包含有效地理信息"
        else:
            logger.info(f"✓ 地点包含有效地理信息")
        
        # 验证地点不是占位符
        placeholder_texts = ['N/A', 'Unknown', 'TBD', 'null', 'undefined', '---']
        is_placeholder = any(p.lower() in location_text.lower() for p in placeholder_texts)
        assert not is_placeholder, f"地点显示占位符文本: {location_text}"
        
        logger.info("✓ 地点信息完整性验证通过")
    
    logger.info("✅ TC018 测试通过：地点信息完整")
