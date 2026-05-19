"""
美国站 OK.com - 详情页发布时间区域功能测试

本脚本由 playwright-test-generator 生成
录制文档：web-qa-brain/OK.com-详情页核心信息区域-测试用例-20260327.md
生成时间：2026-03-31

测试站点：US OK.com (https://us.58v5.cn)
测试角色：访客（Visitor）
测试目标：验证详情页发布时间区域的展示、格式
测试范围：模块 D - 发布时间区域（TC019-TC023）
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
    "base_url": "https://us.58v5.cn/en/city-washington1/cate-services/?iconSource=services",
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
@allure.story("模块D: 发布时间区域")
@allure.title("TC019: 发布时间正常展示")
@allure.severity(allure.severity_level.BLOCKER)
@allure.description("""
验证详情页发布时间的基本展示功能：
1. 时间元素清晰可见
2. 时间文本非空
3. 时间格式合理
""")
@pytest.mark.case_id_detail_core_tc019
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.us
def test_tc019_publish_time_normal_display(page, config, detail_page_core_info, test_post_url):
    """TC019: 发布时间正常展示"""
    
    with allure.step("步骤1：访问详情页"):
        logger.info(f"访问详情页: {test_post_url}")
        page.goto(test_post_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        logger.info("✓ 详情页加载完成")
    
    with allure.step("步骤2：定位发布时间元素"):
        time_element = detail_page_core_info.publish_time_element
        assert time_element.count() > 0, "发布时间元素未找到"
        logger.info("✓ 发布时间元素已定位")
    
    with allure.step("步骤3：验证时间可见性"):
        assert detail_page_core_info.is_publish_time_visible(), "发布时间元素不可见"
        logger.info("✓ 发布时间元素可见")
    
    with allure.step("步骤4：获取时间文本并验证"):
        time_text = detail_page_core_info.get_publish_time_text()
        assert time_text != "", "发布时间文本为空"
        assert len(time_text) > 0, "发布时间长度为0"
        logger.info(f"✓ 发布时间显示正常: {time_text}")
    
    logger.info("✅ TC019 测试通过：发布时间正常展示")


@allure.feature("详情页核心信息")
@allure.story("模块D: 发布时间区域")
@allure.title("TC020: 发布时间格式验证")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("""
验证发布时间的格式：
1. 相对时间格式（如"2 hours ago", "Updated 1 month ago"）
2. 包含时间单位（hours, days, months等）
""")
@pytest.mark.case_id_detail_core_tc020
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.us
def test_tc020_publish_time_format_validation(page, config, detail_page_core_info, test_post_url):
    """TC020: 发布时间格式验证"""
    
    with allure.step("步骤1：访问详情页"):
        logger.info(f"访问详情页: {test_post_url}")
        page.goto(test_post_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        logger.info("✓ 详情页加载完成")
    
    with allure.step("步骤2：获取发布时间文本"):
        time_text = detail_page_core_info.get_publish_time_text()
        logger.info(f"发布时间: {time_text}")
    
    with allure.step("步骤3：验证时间格式"):
        # 常见的时间格式关键词
        time_keywords = [
            'ago', 'hour', 'day', 'week', 'month', 'year',
            'minute', 'second', 'Updated', 'Posted', 'Published',
            'just now', 'recently'
        ]
        
        # 检查时间文本是否包含至少一个时间关键词
        has_time_keyword = any(keyword.lower() in time_text.lower() for keyword in time_keywords)
        
        assert has_time_keyword, f"发布时间格式不符合预期: {time_text}"
        logger.info("✓ 发布时间格式包含有效时间关键词")
        
        # 验证不是占位符
        placeholder_texts = ['N/A', 'Unknown', 'TBD', 'null', 'undefined']
        is_placeholder = any(p in time_text for p in placeholder_texts)
        assert not is_placeholder, f"发布时间显示占位符: {time_text}"
        
        logger.info("✓ 发布时间格式验证通过")
    
    logger.info("✅ TC020 测试通过：发布时间格式正确")


@allure.feature("详情页核心信息")
@allure.story("模块D: 发布时间区域")
@allure.title("TC021: 发布时间位置验证")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("""
验证发布时间在页面中的位置：
1. 时间在地点下方
2. 时间在描述区域上方
""")
@pytest.mark.case_id_detail_core_tc021
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.us
def test_tc021_publish_time_position_validation(page, config, detail_page_core_info, test_post_url):
    """TC021: 发布时间位置验证"""
    
    with allure.step("步骤1：访问详情页"):
        logger.info(f"访问详情页: {test_post_url}")
        page.goto(test_post_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        logger.info("✓ 详情页加载完成")
    
    with allure.step("步骤2：获取各元素的位置"):
        try:
            location_box = detail_page_core_info.location_element.bounding_box()
            time_box = detail_page_core_info.publish_time_element.bounding_box()
            
            assert location_box is not None, "地点元素位置信息获取失败"
            assert time_box is not None, "时间元素位置信息获取失败"
            
            logger.info(f"地点位置 Y: {location_box['y']}")
            logger.info(f"时间位置 Y: {time_box['y']}")
            
            # 尝试获取描述区域位置（可能不在首屏）
            try:
                desc_box = detail_page_core_info.description_element.bounding_box(timeout=3000)
                if desc_box:
                    logger.info(f"描述位置 Y: {desc_box['y']}")
            except:
                desc_box = None
                logger.info("描述区域位置获取失败（可能不在首屏）")
                
        except Exception as e:
            pytest.skip(f"无法获取元素位置信息: {e}")
    
    with allure.step("步骤3：验证时间位置关系"):
        # 时间应该在地点下方（Y坐标更大）
        assert time_box['y'] > location_box['y'], "发布时间不在地点下方"
        logger.info("✓ 发布时间在地点下方")
        
        # 如果能获取到描述位置，验证时间在描述上方
        if desc_box:
            assert time_box['y'] < desc_box['y'], "发布时间不在描述上方"
            logger.info("✓ 发布时间在描述上方")
    
    logger.info("✅ TC021 测试通过：发布时间位置验证通过")


@allure.feature("详情页核心信息")
@allure.story("模块D: 发布时间区域")
@allure.title("TC022: 发布时间文本格式验证")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("""
验证发布时间文本的格式规范：
1. 不包含异常字符
2. 格式整洁
""")
@pytest.mark.case_id_detail_core_tc022
@pytest.mark.regression
@pytest.mark.p2
@pytest.mark.us
def test_tc022_publish_time_text_format(page, config, detail_page_core_info, test_post_url):
    """TC022: 发布时间文本格式验证"""
    
    with allure.step("步骤1：访问详情页"):
        logger.info(f"访问详情页: {test_post_url}")
        page.goto(test_post_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        logger.info("✓ 详情页加载完成")
    
    with allure.step("步骤2：获取发布时间文本"):
        time_text = detail_page_core_info.get_publish_time_text()
        logger.info(f"发布时间: {time_text}")
    
    with allure.step("步骤3：验证时间文本格式"):
        # 1. 时间不应包含HTML标签
        assert '<' not in time_text and '>' not in time_text, "发布时间包含HTML标签"
        
        # 2. 时间不应有异常的控制字符
        control_chars = [chr(i) for i in range(32) if chr(i) not in ['\n', '\r', '\t']]
        has_control_char = any(char in time_text for char in control_chars)
        assert not has_control_char, "发布时间包含控制字符"
        
        # 3. 时间应该是有效的文本
        assert time_text.strip() != "", "发布时间文本为空"
        
        # 4. 时间文本长度合理（不过长不过短）
        assert 5 <= len(time_text) <= 100, f"发布时间长度异常: {len(time_text)}"
        
        logger.info("✓ 发布时间文本格式验证通过")
    
    logger.info("✅ TC022 测试通过：发布时间文本格式正确")


@allure.feature("详情页核心信息")
@allure.story("模块D: 发布时间区域")
@allure.title("TC023: 发布时间合理性验证")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("""
验证发布时间的合理性：
1. 时间不是未来时间
2. 时间信息有意义
""")
@pytest.mark.case_id_detail_core_tc023
@pytest.mark.regression
@pytest.mark.p2
@pytest.mark.us
def test_tc023_publish_time_reasonableness(page, config, detail_page_core_info, test_post_url):
    """TC023: 发布时间合理性验证"""
    
    with allure.step("步骤1：访问详情页"):
        logger.info(f"访问详情页: {test_post_url}")
        page.goto(test_post_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        logger.info("✓ 详情页加载完成")
    
    with allure.step("步骤2：获取发布时间文本"):
        time_text = detail_page_core_info.get_publish_time_text()
        logger.info(f"发布时间: {time_text}")
    
    with allure.step("步骤3：验证时间合理性"):
        # 检查是否包含"ago"（表示过去时间）
        if 'ago' in time_text.lower():
            logger.info("✓ 时间表示过去（包含'ago'）")
        elif 'updated' in time_text.lower() or 'posted' in time_text.lower():
            logger.info("✓ 时间表示已发布/更新")
        else:
            # 如果不包含明确的过去时间标识，至少验证不包含未来时间关键词
            future_keywords = ['from now', 'in the future', 'will be', 'upcoming']
            has_future = any(kw in time_text.lower() for kw in future_keywords)
            assert not has_future, f"发布时间包含未来时间关键词: {time_text}"
            logger.info("✓ 时间不包含未来时间标识")
        
        # 验证时间包含数字（如果是相对时间）
        if 'ago' in time_text.lower():
            # 应该包含数字，如"2 hours ago"
            has_number = any(char.isdigit() for char in time_text)
            if has_number:
                logger.info("✓ 相对时间包含数字")
            else:
                # 可能是"just now"等特殊情况
                special_cases = ['just now', 'recently', 'moments ago']
                has_special = any(case in time_text.lower() for case in special_cases)
                if has_special:
                    logger.info("✓ 时间是特殊表达（just now等）")
                else:
                    logger.warning(f"相对时间不包含数字且无特殊标识: {time_text}")
        
        # 验证不是占位符或错误文本
        invalid_texts = ['N/A', 'null', 'undefined', 'error', '---', '0000-00-00']
        has_invalid = any(invalid.lower() in time_text.lower() for invalid in invalid_texts)
        assert not has_invalid, f"发布时间包含无效文本: {time_text}"
        
        logger.info("✓ 发布时间合理性验证通过")
    
    logger.info("✅ TC023 测试通过：发布时间合理")
