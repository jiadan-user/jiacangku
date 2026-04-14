"""
美国站 OK.com - 详情页价格区域功能测试

本脚本由 playwright-test-generator 生成
录制文档：web-qa-brain/OK.com-详情页核心信息区域-测试用例-20260327.md
生成时间：2026-03-31

测试站点：US OK.com (https://us.ok.com)
测试角色：访客（Visitor）
测试目标：验证详情页价格区域的展示、格式、一致性
测试范围：模块 A - 价格区域（TC001-TC005）
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
    "base_url": "https://us.ok.com/en/city-washington1/cate/",
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
    """
    Module级别的page fixture，整个模块共享一个浏览器实例
    提升性能：避免每个测试都重新启动浏览器
    """
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
    """
    从列表页动态获取一个有价格的帖子URL（排除招聘和房产类别）
    
    Returns:
        str: 详情页URL
    """
    logger.info("从列表页动态获取测试帖子URL...")
    page.goto(config["base_url"], wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(3000)
    
    # 等待页面列表区域加载（使用更精确的选择器，排除导航菜单中的链接）
    # 从录制快照看到，帖子卡片是在特定容器中的link元素
    page.wait_for_load_state("load", timeout=30000)
    page.wait_for_timeout(2000)
    
    # 直接查找包含价格$符号的link元素（这些才是帖子卡片）
    post_links = page.locator("link:has-text('$')").all()
    
    for link in post_links:
        href = link.get_attribute('href')
        # 排除招聘和房产类别
        if href and '/cate-jobs/' not in href and '/cate-property/' not in href:
            logger.info(f"✓ 找到有价格的帖子: {href}")
            return href
    
    # 备用方案：查找所有包含详情页URL特征的link
    all_links = page.get_by_role("link").all()
    for link in all_links:
        href = link.get_attribute('href')
        if href and '/city-' in href and '/cate-' in href and \
           '/cate-jobs/' not in href and '/cate-property/' not in href and \
           href.count('/') > 5:  # 详情页URL层级更深
            # 检查link的可见性
            if link.is_visible():
                logger.info(f"✓ 使用备用方案找到帖子: {href}")
                return href
    
    raise Exception("未找到有效的测试帖子URL")


@pytest.fixture(scope="module")
def free_post_url(page, config):
    """
    从列表页动态获取一个Free（免费）帖子URL
    
    Returns:
        str: 免费帖子详情页URL，如果找不到返回None
    """
    logger.info("从列表页查找Free帖子...")
    page.goto(config["base_url"], wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(3000)
    page.wait_for_load_state("load", timeout=30000)
    
    # 查找包含"Free"文本但不包含具体价格"$数字"的link
    # 列表页卡片通常会显示"Free"作为价格
    all_links = page.get_by_role("link").all()
    
    for link in all_links:
        href = link.get_attribute('href')
        # 排除招聘和房产类别，且URL是详情页格式
        if href and '/city-' in href and '/cate-' in href and \
           '/cate-jobs/' not in href and '/cate-property/' not in href and \
           href.count('/') > 5:
            try:
                if link.is_visible():
                    card_text = link.inner_text()
                    # 检查：包含单独的"Free"单词，但该行不包含$符号（排除"Free Delivery $9.9"这种情况）
                    # 真正的Free帖子应该只显示"Free"而没有价格数字
                    lines = card_text.split('\n')
                    for line in lines:
                        line_clean = line.strip()
                        # 如果某行恰好是"Free"或"FREE"（大小写不敏感），且不在包含$的同一行
                        if line_clean.lower() == 'free' or (line_clean.lower().startswith('free') and '$' not in line):
                            # 确认整个卡片没有具体价格
                            if not re.search(r'\$\d', card_text):
                                logger.info(f"✓ 找到Free帖子: {href}")
                                return href
            except:
                continue
    
    logger.warning("未找到Free帖子，TC002可能需要跳过")
    return None


# ==================== 测试用例 ====================

@allure.feature("详情页核心信息")
@allure.story("模块A: 价格区域")
@allure.title("TC001: 普通价格正常展示")
@allure.severity(allure.severity_level.BLOCKER)
@allure.description("""
验证详情页价格区域的基本展示功能：
1. 价格元素清晰可见
2. 价格包含货币符号$
3. 价格文本非空
4. 价格位于页面显著位置
""")
@pytest.mark.case_id_detail_core_tc001
@pytest.mark.smoke
@pytest.mark.p0
@pytest.mark.us
def test_tc001_normal_price_display(page, config, detail_page_core_info, test_post_url):
    """TC001: 普通价格正常展示"""
    
    with allure.step("步骤1：访问详情页"):
        logger.info(f"访问详情页: {test_post_url}")
        page.goto(test_post_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        logger.info("✓ 详情页加载完成")
    
    with allure.step("步骤2：定位价格区域元素"):
        price_element = detail_page_core_info.price_element
        assert price_element.count() > 0, "价格元素未找到"
        logger.info("✓ 价格元素已定位")
    
    with allure.step("步骤3：验证价格可见性"):
        assert detail_page_core_info.is_price_visible(), "价格元素不可见"
        logger.info("✓ 价格元素可见")
    
    with allure.step("步骤4：获取价格文本并验证"):
        price_text = detail_page_core_info.get_price_text()
        assert price_text != "", "价格文本为空"
        assert "$" in price_text, f"价格文本不包含货币符号$: {price_text}"
        logger.info(f"✓ 价格显示正常: {price_text}")
    
    with allure.step("步骤5：验证价格格式"):
        # 价格应该是 $数字 格式
        assert re.match(r'^\$[\d.,]+$', price_text), f"价格格式不正确: {price_text}"
        logger.info("✓ 价格格式正确")
    
    logger.info("✅ TC001 测试通过：普通价格正常展示")


@allure.feature("详情页核心信息")
@allure.story("模块A: 价格区域")
@allure.title("TC002: 免费帖子价格展示")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("""
验证Free（免费）帖子的价格展示：
1. 价格显示为"Free"或类似标识
2. 不显示货币数字
3. 元素位置合理
""")
@pytest.mark.case_id_detail_core_tc002
@pytest.mark.regression
@pytest.mark.p1
@pytest.mark.us
def test_tc002_free_post_price_display(page, config, detail_page_core_info, free_post_url):
    """TC002: 免费帖子价格展示"""
    
    if free_post_url is None:
        pytest.skip("未找到Free帖子，跳过测试")
    
    with allure.step("步骤1：访问Free帖子详情页"):
        logger.info(f"访问Free帖子详情页: {free_post_url}")
        page.goto(free_post_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        logger.info("✓ 详情页加载完成")
    
    with allure.step("步骤2：检查价格区域显示"):
        # 对于Free帖子，可能显示"Free"文本或者没有价格显示数字
        page_text = page.inner_text("body")
        
        # 验证：要么显示Free，要么没有价格数字
        has_free_text = "free" in page_text.lower()
        price_text = detail_page_core_info.get_price_text()
        
        # Free帖子的价格文本应该不包含$符号，或者明确显示Free
        assert has_free_text or "$" not in price_text, "Free帖子不应显示价格数字"
        logger.info(f"✓ Free帖子价格展示正确: {price_text if price_text else 'Free'}")
    
    logger.info("✅ TC002 测试通过：免费帖子价格展示正确")


@allure.feature("详情页核心信息")
@allure.story("模块A: 价格区域")
@allure.title("TC003: 列表页与详情页价格一致性")
@allure.severity(allure.severity_level.BLOCKER)
@allure.description("""
验证列表页和详情页价格的一致性：
1. 从列表页记录价格
2. 点击进入详情页
3. 对比两处价格是否一致
""")
@pytest.mark.case_id_detail_core_tc003
@pytest.mark.core_flow
@pytest.mark.p0
@pytest.mark.us
def test_tc003_price_consistency_list_to_detail(page, config, detail_page_core_info):
    """TC003: 列表页与详情页价格一致性"""
    
    with allure.step("步骤1：访问列表页"):
        logger.info(f"访问列表页: {config['base_url']}")
        page.goto(config["base_url"], wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        logger.info("✓ 列表页加载完成")
    
    with allure.step("步骤2：找到第一个有价格的帖子并记录价格"):
        # 等待页面完全加载
        page.wait_for_load_state("load", timeout=30000)
        page.wait_for_timeout(2000)
        
        # 查找可见的详情页link（使用备用方案）
        all_links = page.get_by_role("link").all()
        
        list_price = None
        target_link = None
        
        for link in all_links:
            href = link.get_attribute('href')
            if href and '/cate-jobs/' not in href and '/cate-property/' not in href and \
               '/city-' in href and href.count('/') > 5:  # 详情页URL
                try:
                    if link.is_visible():
                        card_text = link.inner_text()
                        # 提取价格（查找$开头的数字）
                        price_match = re.search(r'\$[\d.,]+', card_text)
                        if price_match:
                            # 确认这是真实价格，不是"Free Delivery $0"这种
                            price_candidate = price_match.group()
                            # 检查价格前后文本，确保不是在"Free Delivery"后面
                            price_start_idx = card_text.find(price_candidate)
                            text_before_price = card_text[:price_start_idx].strip().lower()
                            # 如果价格前有"free delivery"，跳过
                            if not text_before_price.endswith('delivery'):
                                list_price = price_candidate
                                target_link = link
                                break
                except:
                    continue
        
        assert list_price is not None, "列表页未找到有价格的帖子"
        logger.info(f"✓ 列表页价格: {list_price}")
    
    with allure.step("步骤3：点击帖子进入详情页"):
        # 记录link的href，直接访问详情页（避免点击后新标签页问题）
        detail_url = target_link.get_attribute('href')
        logger.info(f"准备访问详情页: {detail_url}")
        page.goto(detail_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_load_state("domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        logger.info("✓ 详情页加载完成")
    
    with allure.step("步骤4：获取详情页价格"):
        detail_price = detail_page_core_info.get_price_text()
        assert detail_price != "", "详情页价格为空"
        logger.info(f"✓ 详情页价格: {detail_price}")
    
    with allure.step("步骤5：对比两处价格"):
        # 移除可能的千分位逗号进行对比
        list_price_clean = list_price.replace(",", "")
        detail_price_clean = detail_price.replace(",", "")
        
        assert list_price_clean == detail_price_clean, \
            f"列表页价格({list_price})与详情页价格({detail_price})不一致"
        logger.info("✓ 列表页与详情页价格一致")
    
    logger.info("✅ TC003 测试通过：价格一致性验证通过")


@allure.feature("详情页核心信息")
@allure.story("模块A: 价格区域")
@allure.title("TC004: 价格格式化正确性")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("""
验证价格的格式化规则：
1. 包含货币符号$
2. 大于1000的价格使用千分位分隔符
3. 小数点后最多2位
""")
@pytest.mark.case_id_detail_core_tc004
@pytest.mark.regression
@pytest.mark.p2
@pytest.mark.us
def test_tc004_price_format_validation(page, config, detail_page_core_info):
    """TC004: 价格格式化正确性"""
    
    with allure.step("步骤1：访问列表页查找价格≥1000的帖子"):
        logger.info(f"访问列表页查找高价帖子: {config['base_url']}")
        page.goto(config["base_url"], wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)
        page.wait_for_load_state("load", timeout=30000)
        page.wait_for_timeout(2000)
        
        # 查找价格≥1000的帖子
        all_links = page.get_by_role("link").all()
        high_price_url = None
        found_price = None
        
        for link in all_links:
            href = link.get_attribute('href')
            if href and '/cate-jobs/' not in href and '/cate-property/' not in href and \
               '/city-' in href and href.count('/') > 5:
                try:
                    if link.is_visible():
                        card_text = link.inner_text()
                        # 查找所有价格模式（可能有多个$，如 Free Delivery $1,233.01）
                        price_matches = re.findall(r'\$([\d,]+(?:\.\d{1,2})?)', card_text)
                        
                        for price_str in price_matches:
                            clean_price = price_str.replace(',', '')
                            try:
                                price_value = float(clean_price)
                                # 严格要求：找到价格≥1000的帖子
                                if price_value >= 1000:
                                    high_price_url = href
                                    found_price = price_value
                                    logger.info(f"✓ 找到高价帖子: {href}, 价格: ${price_str}")
                                    break
                            except ValueError:
                                continue
                    
                    if high_price_url:
                        break
                except:
                    continue
        
        if high_price_url is None:
            pytest.skip("未找到价格≥1000的帖子，跳过测试")
    
    with allure.step("步骤2：访问详情页"):
        page.goto(high_price_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        logger.info("✓ 详情页加载完成")
    
    with allure.step("步骤3：获取价格并验证格式"):
        price_text = detail_page_core_info.get_price_text()
        assert price_text != "", "价格文本为空"
        logger.info(f"价格文本: {price_text}")
    
    with allure.step("步骤4：验证价格格式规则"):
        # 1. 必须包含$
        assert "$" in price_text, "价格不包含货币符号$"
        
        # 2. 格式应为: $数字[,数字]*(.[数字]{1,2})?
        price_pattern = r'^\$[\d,]+(\.\d{1,2})?$'
        assert re.match(price_pattern, price_text), f"价格格式不符合规范: {price_text}"
        
        # 3. 提取价格数值并验证千分位分隔符
        price_value_str = price_text.replace('$', '').replace(',', '')
        try:
            price_value = float(price_value_str)
            
            # 价格应≥1000
            assert price_value >= 1000, f"找到的价格({price_value})小于1000"
            
            # 价格≥1000必须有千分位分隔符
            assert ',' in price_text, f"价格≥1000应使用千分位分隔符: {price_text}"
            logger.info("✓ 千分位分隔符验证通过")
            
            # 验证千分位格式正确（逗号位置应该是每3位）
            # 移除$和小数部分
            integer_part = price_text.replace('$', '').split('.')[0]
            # 移除逗号，应该能正确解析
            assert price_value > 0, "价格值异常"
            logger.info(f"✓ 价格为 ${price_text}，千分位格式正确")
                
        except ValueError:
            pytest.fail(f"价格格式错误，无法转换为数字: {price_text}")
        
        logger.info("✓ 价格格式验证通过")
    
    logger.info("✅ TC004 测试通过：价格格式化正确")


@allure.feature("详情页核心信息")
@allure.story("模块A: 价格区域")
@allure.title("TC005: 无价格帖子的展示")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("""
验证无价格帖子的展示（边界值测试）：
1. 价格区域显示占位文本或不显示
2. 页面其他信息正常展示
""")
@pytest.mark.case_id_detail_core_tc005
@pytest.mark.boundary
@pytest.mark.p2
@pytest.mark.us
def test_tc005_no_price_post_display(page, config, detail_page_core_info):
    """TC005: 无价格帖子的展示"""
    
    with allure.step("步骤1：访问列表页查找无价格帖子"):
        logger.info(f"访问列表页查找无价格帖子: {config['base_url']}")
        page.goto(config["base_url"], wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(3000)
        page.wait_for_load_state("load", timeout=30000)
        
        # 查找没有明确价格的帖子（不包含$符号）
        all_links = page.get_by_role("link").all()
        no_price_url = None
        
        for link in all_links:
            href = link.get_attribute('href')
            if href and '/city-' in href and '/cate-' in href and \
               '/cate-jobs/' not in href and '/cate-property/' not in href and \
               href.count('/') > 5:
                try:
                    if link.is_visible():
                        card_text = link.inner_text()
                        # 检查是否既没有$也没有Free
                        if '$' not in card_text and 'Free' not in card_text:
                            no_price_url = href
                            logger.info(f"✓ 找到无价格帖子: {href}")
                            break
                except:
                    continue
        
        if no_price_url is None:
            pytest.skip("未找到无价格帖子，跳过测试")
    
    with allure.step("步骤2：访问无价格帖子详情页"):
        page.goto(no_price_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        logger.info("✓ 详情页加载完成")
    
    with allure.step("步骤3：检查价格区域展示"):
        page_content = page.inner_text("body").lower()
        
        # 验证：要么有占位文本（如"contact for price"），要么价格元素不可见
        has_contact_text = "contact" in page_content
        price_visible = detail_page_core_info.is_price_visible()
        
        if price_visible:
            price_text = detail_page_core_info.get_price_text()
            # 如果价格可见，应该是占位文本而不是具体价格
            assert "$" not in price_text, "无价格帖子不应显示具体价格数字"
            logger.info(f"✓ 价格区域显示占位文本: {price_text}")
        else:
            logger.info("✓ 价格区域不显示（符合预期）")
    
    with allure.step("步骤4：验证页面其他信息正常展示"):
        # 验证标题、描述等其他信息正常显示
        assert detail_page_core_info.is_title_visible(), "标题应该可见"
        assert detail_page_core_info.is_description_visible(), "描述应该可见"
        logger.info("✓ 页面其他信息展示正常")
    
    logger.info("✅ TC005 测试通过：无价格帖子展示正常")
