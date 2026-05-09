# test_cases/体验/详情页/面包屑导航/conftest.py
"""
面包屑导航模块共享配置和fixture
"""

import pytest
from utils.logger import setup_logger

logger = setup_logger()

# ========== 测试配置 ==========
_CONFIG = {
    "site": "us",
    "site_name": "美国站 (US 58v5.cn)",
    "base_url": "https://us.58v5.cn",
    "role": "visitor",
    "user_name": "us_visitor_breadcrumb",
    "test_account": None,
    "list_url": "https://us.58v5.cn/en/city-washington1/cate/?lowestPrice=0&highestPrice=0",
    "browser": {
        "type": "chromium",
        "headless": True,
        "slow_mo": 0,
        "viewport": {"width": 1920, "height": 1080}
    }
}


@pytest.fixture(scope="module")
def config():
    """测试配置"""
    return _CONFIG


@pytest.fixture(scope="module")
def detail_url(page, config):
    """
    动态获取一个有效的详情页URL
    从列表页找到一个非招聘、非房产、非车的帖子详情页
    """
    list_url = config['list_url']
    base_url = config['base_url']
    
    logger.info("="*80)
    logger.info("开始获取有效的详情页链接...")
    logger.info(f"列表页URL: {list_url}")
    logger.info("="*80)
    
    # 访问您指定的列表页
    page.goto(list_url, timeout=60000, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)  # 等待列表内容加载
    
    # 排除关键词
    excluded_keywords = [
        'jobs', 'job', 'hiring', 'employment',
        'property', 'real-estate', 'apartment', 'house', 'rent', 'sale',
        'cars', 'car', 'vehicle', 'auto', 'motorbike', 'motorcycle',
        'find-a-job', 'real-estate-us'
    ]
    
    detail_url = None
    
    # 从列表页查找帖子详情页链接
    # 尝试多种可能的帖子链接选择器
    post_selectors = [
        'a[href*="/city-"][href*="/cate-"]',  # 包含city和cate的链接
        'article a',  # article标签内的链接
        '.post-item a, .item a',  # 帖子项中的链接
        '[class*="Card"] a',  # 卡片组件中的链接
        '[class*="List"] a[href*="/cate-"]',  # 列表中包含分类的链接
    ]
    
    for selector in post_selectors:
        links = page.locator(selector).all()
        logger.info(f"使用选择器 '{selector}', 找到 {len(links)} 个链接")
        
        for link in links[:50]:  # 检查前50个链接
            try:
                href = link.get_attribute('href')
                if not href:
                    continue
                
                # 补全相对路径
                if href.startswith('/'):
                    href = base_url + href
                
                # 必须包含完整域名
                if not href.startswith('http'):
                    continue
                
                # 排除关键词检查
                href_lower = href.lower()
                if any(keyword in href_lower for keyword in excluded_keywords):
                    logger.debug(f"跳过(包含排除关键词): {href}")
                    continue
                
                # 详情页URL特征:
                # 1. 必须包含 /city- 和 /cate-
                # 2. URL结构至少有6段: http://domain/en/city-xxx/cate-xxx/post-title-id/
                # 3. 最后一段包含短横线和数字(帖子标题+ID)
                # 4. **关键**: 最后一段不能只是 "cate-xxx" 格式(那是分类页)
                if '/city-' in href and '/cate-' in href:
                    url_parts = href.rstrip('/').split('/')
                    
                    # URL至少要有7段 (详情页比分类页多一段)
                    # http://domain/en/city-xxx/cate-xxx/post-title-id
                    if len(url_parts) >= 7:
                        last_part = url_parts[-1]
                        
                        # 排除纯分类页: 如果最后一段是空的,说明URL以 / 结尾且只到分类级别
                        if not last_part:
                            continue
                        
                        # 排除分类页: 分类页URL通常是 cate-name 或 cate-name123 这种简短格式
                        # 详情页URL最后一段通常是: "post-title-words-12345" 这种较长格式
                        # 判断依据: 包含短横线且有数字,但不是以 "cate-" 开头
                        if last_part.startswith('cate-'):
                            logger.debug(f"跳过(分类页): {href}")
                            continue
                        
                        # 详情页最后一段通常包含多个单词和数字ID
                        if '-' in last_part and any(char.isdigit() for char in last_part):
                            # 确保不是简单的 "name-123" 这种分类页格式
                            # 详情页通常至少有2个短横线: "some-title-12345"
                            if last_part.count('-') >= 2 or len(last_part) > 20:
                                detail_url = href
                                logger.info(f"✓ 找到符合条件的详情页: {detail_url}")
                                logger.info(f"  URL段数: {len(url_parts)}, 最后一段: {last_part}")
                                break
                        
            except Exception as e:
                logger.warning(f"处理链接时出错: {e}")
                continue
        
        if detail_url:
            break
    
    # 如果列表页没找到,记录详细信息并使用备用策略
    if not detail_url:
        logger.warning("="*80)
        logger.warning("未在列表页找到符合条件的详情页链接")
        logger.warning(f"列表页URL: {list_url}")
        logger.warning("可能原因:")
        logger.warning("  1. 列表页没有帖子")
        logger.warning("  2. 所有帖子都是招聘/房产/车类")
        logger.warning("  3. 页面结构与预期选择器不匹配")
        logger.warning("="*80)
        
        # 使用备用URL (一个通用的服务类详情页)
        detail_url = f"{base_url}/en/city-washington1/cate-others253/test-service-post-123456/"
        logger.warning(f"使用备用URL: {detail_url}")
    
    logger.info("="*80)
    logger.info(f"最终使用的详情页URL: {detail_url}")
    logger.info("="*80)
    
    config['detail_url'] = detail_url
    return detail_url
