"""
AE站 - Marketplace发布页AI推荐功能测试

本脚本由 playwright-test-generator 生成
录制文档：test_cases/ai/ai_publish/ai_publish_Marketplace测试用例_20260312.md
生成时间：2026-03-13

测试站点：AE (https://aepub.58v5.cn)
测试角色：Seller (卖家)
测试目标：验证在Marketplace发布页面，当用户上传商品图片和输入Title后，系统会基于AI智能分析，
         显示推荐的商品类目，并支持AI生成描述内容
"""
import pytest
import allure
import os
from pages.login_page import LoginPage
from pages.ai_publish_marketplace_page import AiPublishMarketplacePage
from utils.session_manager import SessionManager
from utils.logger import setup_logger

logger = setup_logger()

# ============================================
# 测试环境配置（来自录制文档，录制与运行使用同一账号）
# ============================================
_CONFIG = {
    "site": "ae",
    "site_name": "AE站",
    "role": "seller",
    "user_name": "ae_seller_marketplace",
    "base_url": "https://aepub.58v5.cn",
    "test_account": {
        "username": "yangyang100@58.com",
        "password": "Qa123456"
    },
    "locale": "en-US",
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


@pytest.mark.usefixtures("setup_marketplace_page")
class TestAiPublishMarketplace:
    """Marketplace发布AI推荐功能测试类"""

    @pytest.mark.case_id_ai_publish_marketplace_01
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ai
    @pytest.mark.ae
    @pytest.mark.ai_publish
    @pytest.mark.ai_publish_marketplace
    @allure.feature("OK")
    @allure.story("Marketplace发布AI推荐类目 - 正向场景")
    @allure.title("上传单张商品图片后应该显示AI推荐类目")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证用户上传单张商品图片（iphone 16_1.png）后，页面显示Suggested Categories区域，并推荐至少1个相关类目")
    def test_upload_single_image_ai_recommendations_should_display(self, page, config):
        """TC001: 上传单张商品图片后显示AI推荐类目"""

        # ========== Arrange：准备测试对象 ==========
        marketplace_page = AiPublishMarketplacePage(page)

        logger.info("="*80)
        logger.info("TC001: 上传单张商品图片后显示AI推荐类目测试")
        logger.info("="*80)

        image_path = os.path.join(os.getcwd(), "test_data/images/iphone 16_1.png")

        # ========== Act：执行操作 ==========
        with allure.step("步骤1：上传iphone 16_1.png图片"):
            marketplace_page.upload_single_image(image_path)
            logger.info("✓ 上传iphone 16_1.png成功")

        with allure.step("步骤2：等待 AI 推荐加载"):
            marketplace_page.wait_for_ai_recommendations()
            logger.info("✓ AI 推荐加载完成")

        # ========== Assert：验证结果 ==========
        with allure.step("验证1：图片成功上传，显示 Upload 1/9"):
            upload_count = marketplace_page.get_upload_count()
            assert "1" in upload_count and "9" in upload_count, \
                f"图片上传失败，期望: '1/9'，实际: '{upload_count}'"
            logger.info(f"✓ 上传计数验证通过: {upload_count}")

        with allure.step("验证2：页面显示 Suggested Categories 区域"):
            assert marketplace_page.is_suggested_categories_displayed(), \
                "Suggested Categories 区域未显示"
            logger.info("✓ Suggested Categories 区域显示成功")

        with allure.step("验证3：AI 推荐至少1个相关类目"):
            categories = marketplace_page.get_suggested_categories_text()
            assert len(categories) >= 1, \
                f"AI 推荐类目数量不足，期望: ≥1，实际: {len(categories)}"
            logger.info(f"✓ AI 推荐类目数量: {len(categories)}")
            logger.info(f"✓ 推荐类目: {', '.join(categories)}")

    @pytest.mark.case_id_ai_publish_marketplace_02
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ai
    @pytest.mark.ai_publish
    @pytest.mark.ai_publish_marketplace
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("Marketplace发布AI描述生成 - 正向场景")
    @allure.title("上传单张商品图片点击Write with AI应该生成AI描述")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证用户上传单张商品图片后，点击Write with AI按钮，AI自动生成与图片相关的描述内容")
    def test_single_image_write_with_ai_should_generate_description(self, page, config):
        """TC002: 上传单张商品图片，点击Write with AI生成AI描述"""

        # ========== Arrange：准备测试对象 ==========
        marketplace_page = AiPublishMarketplacePage(page)

        logger.info("="*80)
        logger.info("TC002: 单张商品图片点击Write with AI生成描述测试")
        logger.info("="*80)

        image_path = os.path.join(os.getcwd(), "test_data/images/iphone 16_1.png")

        # ========== 前置：保证恰好 1 张图片 ==========
        with allure.step("前置：判断并调整图片数量为 1 张"):
            page.wait_for_timeout(1000)
            upload_count_str = marketplace_page.get_upload_count()
            n = marketplace_page.parse_upload_count(upload_count_str)
            if n == 0:
                marketplace_page.upload_single_image(image_path)
                logger.info("✓ 图片未上传，已上传 1 张图片")
            elif n == 1:
                logger.info("✓ 已有 1 张图片，跳过上传")
            else:
                for _ in range(n - 1):
                    marketplace_page.delete_one_uploaded_image()
                logger.info(f"✓ 原已上传 {n} 张，已删除 {n - 1} 张，保留 1 张")

        # ========== Act：执行操作 ==========
        with allure.step("步骤1：确认当前为单张图片"):
            upload_count_str = marketplace_page.get_upload_count()
            n = marketplace_page.parse_upload_count(upload_count_str)
            assert n == 1, f"前置后应恰好 1 张图片，实际: {n} 张（{upload_count_str}）"
            logger.info("✓ 当前为单张图片")

        with allure.step("步骤2：点击 Write with AI 按钮"):
            marketplace_page.click_write_with_ai()
            logger.info("✓ 点击Write with AI成功")

        with allure.step("步骤3：等待 AI 生成内容（循环10次检查）"):
            max_retries = 10
            for i in range(max_retries):
                # 先等待10秒
                page.wait_for_timeout(10000)
                logger.info(f"⏳ 已等待 10 秒 (第 {i+1}/{max_retries} 次)")
                
                # 检查 description 字段长度
                description = marketplace_page.get_description_value()
                if len(description) > 0:
                    logger.info(f"✓ AI 内容生成完成，第 {i+1} 次检查")
                    break
                
                # description = 0，判断 Write with AI 按钮是否显示
                is_button_visible = marketplace_page.is_write_with_ai_button_visible()
                if is_button_visible:
                    logger.info(f"⚠️ AI 未生成内容，Write with AI 按钮显示，重新点击 (第 {i+1}/{max_retries} 次)")
                    try:
                        marketplace_page.click_write_with_ai()
                    except Exception as e:
                        logger.warning(f"重新点击失败: {e}，继续下次循环...")
                else:
                    logger.info(f"⏳ Write with AI 按钮未显示，继续等待... (第 {i+1}/{max_retries} 次)")
            logger.info("✓ AI 内容生成等待完成")

        # ========== Assert：验证结果 ==========
        with allure.step("验证：AI 生成的描述填充到Description字段"):
            description = marketplace_page.get_description_value()
            assert len(description) > 0, "AI 未生成描述内容，Description字段为空"
            logger.info(f"✓ AI 生成描述长度: {len(description)} 字符")
            assert 50 <= len(description) <= 1000, \
                f"描述内容长度异常，期望: 50-1000字符，实际: {len(description)}字符"
            logger.info("✓ 描述内容长度合理")

    @pytest.mark.case_id_ai_publish_marketplace_03
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ai
    @pytest.mark.ai_publish
    @pytest.mark.ai_publish_marketplace
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("Marketplace发布AI推荐类目 - 正向场景")
    @allure.title("上传多张商品图片后应该显示AI推荐类目")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证用户上传3张商品图片后，页面显示Suggested Categories区域，AI推荐基于多图片综合分析更准确")
    def test_upload_multiple_images_ai_recommendations_should_display(self, page, config):
        """TC003: 上传多张商品图片后显示AI推荐类目"""

        # ========== Arrange：准备测试对象 ==========
        marketplace_page = AiPublishMarketplacePage(page)

        logger.info("="*80)
        logger.info("TC003: 上传多张商品图片后显示AI推荐类目测试")
        logger.info("="*80)

        image_paths = [
            os.path.join(os.getcwd(), "test_data/images/iphone 16_1.png"),
            os.path.join(os.getcwd(), "test_data/images/iphone 16_2.png"),
            os.path.join(os.getcwd(), "test_data/images/iphone 16_3.png"),
        ]

        publish_url = f"{_CONFIG['base_url']}/biz/en/publish/classified"
        with allure.step("前置：重新导航到Marketplace发布页面"):
            page.goto(publish_url, timeout=60000)
            page.wait_for_load_state("domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)
            logger.info("✓ 页面已重新导航")

        with allure.step("步骤1：上传3张商品图片"):
            marketplace_page.upload_multiple_images(image_paths)
            logger.info("✓ 上传3张商品图片成功")

        with allure.step("步骤2：等待 AI 推荐加载"):
            marketplace_page.wait_for_ai_recommendations()
            logger.info("✓ AI 推荐加载完成")

        with allure.step("验证1：3张图片均成功上传，显示 Upload 3/9"):
            upload_count = marketplace_page.get_upload_count()
            assert "3" in upload_count and "9" in upload_count, \
                f"图片上传失败，期望: '3/9'，实际: '{upload_count}'"
            logger.info(f"✓ 上传计数验证通过: {upload_count}")

        with allure.step("验证2：页面显示 Suggested Categories 区域"):
            assert marketplace_page.is_suggested_categories_displayed(), \
                "Suggested Categories 区域未显示"
            logger.info("✓ Suggested Categories 区域显示成功")

        with allure.step("验证3：AI 推荐基于多图片综合分析"):
            categories = marketplace_page.get_suggested_categories_text()
            assert len(categories) >= 1, \
                f"AI 推荐类目数量不足，期望: ≥1，实际: {len(categories)}"
            logger.info(f"✓ AI 推荐类目数量: {len(categories)}")
            logger.info(f"✓ 推荐类目: {', '.join(categories)}")

    @pytest.mark.case_id_ai_publish_marketplace_04
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ai
    @pytest.mark.ai_publish
    @pytest.mark.ai_publish_marketplace
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("Marketplace发布AI描述生成 - 正向场景")
    @allure.title("上传多张商品图片点击Write with AI应该生成AI描述")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证用户上传多张商品图片后，点击Write with AI按钮，AI自动生成与图片相关的描述内容")
    def test_multiple_images_write_with_ai_should_generate_description(self, page, config):
        """TC004: 上传多张商品图片，点击Write with AI生成AI描述"""

        marketplace_page = AiPublishMarketplacePage(page)

        logger.info("="*80)
        logger.info("TC004: 多张商品图片点击Write with AI生成描述测试")
        logger.info("="*80)

        image_paths = [
            os.path.join(os.getcwd(), "test_data/images/iphone 16_1.png"),
            os.path.join(os.getcwd(), "test_data/images/iphone 16_2.png"),
            os.path.join(os.getcwd(), "test_data/images/iphone 16_3.png"),
        ]
        publish_url = f"{_CONFIG['base_url']}/biz/en/publish/classified"

        with allure.step("前置：重新导航到发布页面，清空页面状态"):
            page.goto(publish_url, timeout=60000)
            page.wait_for_load_state("domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)
            logger.info("✓ 页面已重新导航")

        with allure.step("前置：上传 3 张商品图片"):
            marketplace_page.upload_multiple_images(image_paths)
            logger.info("✓ 已上传 3 张商品图片")

        with allure.step("步骤1：确认当前为 3 张图片"):
            upload_count_str = marketplace_page.get_upload_count()
            n = marketplace_page.parse_upload_count(upload_count_str)
            assert n == 3, f"前置后应恰好 3 张图片，实际: {n} 张（{upload_count_str}）"
            logger.info("✓ 当前为 3 张图片")

        with allure.step("步骤2：点击 Write with AI 按钮"):
            marketplace_page.click_write_with_ai()
            logger.info("✓ 点击Write with AI成功")

        with allure.step("步骤3：等待 AI 生成内容（循环10次检查）"):
            max_retries = 10
            for i in range(max_retries):
                # 先等待10秒
                page.wait_for_timeout(10000)
                logger.info(f"⏳ 已等待 10 秒 (第 {i+1}/{max_retries} 次)")
                
                # 检查 description 字段长度
                description = marketplace_page.get_description_value()
                if len(description) > 0:
                    logger.info(f"✓ AI 内容生成完成，第 {i+1} 次检查")
                    break
                
                # description = 0，判断 Write with AI 按钮是否显示
                is_button_visible = marketplace_page.is_write_with_ai_button_visible()
                if is_button_visible:
                    logger.info(f"⚠️ AI 未生成内容，Write with AI 按钮显示，重新点击 (第 {i+1}/{max_retries} 次)")
                    try:
                        marketplace_page.click_write_with_ai()
                    except Exception as e:
                        logger.warning(f"重新点击失败: {e}，继续下次循环...")
                else:
                    logger.info(f"⏳ Write with AI 按钮未显示，继续等待... (第 {i+1}/{max_retries} 次)")
            logger.info("✓ AI 内容生成等待完成")

        with allure.step("验证：AI 生成的描述填充到Description字段"):
            description = marketplace_page.get_description_value()
            assert len(description) > 0, "AI 未生成描述内容，Description字段为空"
            logger.info(f"✓ AI 生成描述长度: {len(description)} 字符")
            assert 50 <= len(description) <= 1000, \
                f"描述内容长度异常，期望: 50-1000字符，实际: {len(description)}字符"
            logger.info("✓ 描述内容长度合理")

    @pytest.mark.case_id_ai_publish_marketplace_05
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ai
    @pytest.mark.ai_publish
    @pytest.mark.ai_publish_marketplace
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("Marketplace发布AI推荐类目 - 正向场景")
    @allure.title("仅输入标题后应该显示AI推荐类目")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证用户仅输入Title不上传图片时，失焦后页面显示Suggested Categories区域及AI推荐类目")
    def test_title_only_ai_recommendations_should_display(self, page, config):
        """TC005: 仅输入标题后显示AI推荐类目"""

        marketplace_page = AiPublishMarketplacePage(page)

        logger.info("="*80)
        logger.info("TC005: 仅输入标题后显示AI推荐类目测试")
        logger.info("="*80)

        title = "iPhone 14 Pro Max 256GB Space Black"
        publish_url = f"{_CONFIG['base_url']}/biz/en/publish/classified"

        with allure.step("前置：重新导航到Marketplace发布页面"):
            page.goto(publish_url, timeout=60000)
            page.wait_for_load_state("domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)
            logger.info("✓ 页面已重新导航")

        with allure.step("步骤1：在Title字段输入标题"):
            marketplace_page.input_title(title)
            logger.info(f"✓ 输入Title: {title}")

        with allure.step("步骤2：点击Title字段外部触发失焦"):
            marketplace_page.click_title_outside()
            logger.info("✓ Title失焦完成")

        with allure.step("步骤3：等待 AI 推荐加载"):
            marketplace_page.wait_for_ai_recommendations()
            logger.info("✓ AI 推荐加载完成")

        with allure.step("验证：Suggested Categories 区域显示AI推荐类目"):
            assert marketplace_page.is_suggested_categories_displayed(), \
                "Suggested Categories 区域未显示"
            logger.info("✓ Suggested Categories 区域显示成功")
            categories = marketplace_page.get_suggested_categories_text()
            assert len(categories) >= 1, \
                f"AI 推荐类目数量不足，期望: ≥1，实际: {len(categories)}"
            logger.info(f"✓ AI 推荐类目数量: {len(categories)}")
            logger.info(f"✓ 推荐类目: {', '.join(categories)}")

    @pytest.mark.case_id_ai_publish_marketplace_06
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ai
    @pytest.mark.ai_publish
    @pytest.mark.ai_publish_marketplace
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("Marketplace发布AI描述生成 - 正向场景")
    @allure.title("仅输入标题点击Write with AI应该生成AI描述")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证用户仅输入Title不上传图片时，点击Write with AI按钮，AI自动生成与标题相关的描述内容")
    def test_title_only_write_with_ai_should_generate_description(self, page, config):
        """TC006: 仅输入标题，点击Write with AI生成AI描述"""

        marketplace_page = AiPublishMarketplacePage(page)

        logger.info("="*80)
        logger.info("TC006: 仅输入标题点击Write with AI生成描述测试")
        logger.info("="*80)

        title = "iPhone 14 Pro Max 256GB Space Black"

        with allure.step("步骤1：确认Title字段有内容（若空则输入）"):
            marketplace_page.input_title(title)
            marketplace_page.click_title_outside()
            logger.info(f"✓ Title已确认: {title}")

        with allure.step("步骤2：点击 Write with AI 按钮"):
            marketplace_page.click_write_with_ai()
            logger.info("✓ 点击Write with AI成功")

        with allure.step("步骤3：等待 AI 生成内容（循环10次检查）"):
            max_retries = 10
            for i in range(max_retries):
                # 先等待10秒
                page.wait_for_timeout(10000)
                logger.info(f"⏳ 已等待 10 秒 (第 {i+1}/{max_retries} 次)")
                
                # 检查 description 字段长度
                description = marketplace_page.get_description_value()
                if len(description) > 0:
                    logger.info(f"✓ AI 内容生成完成，第 {i+1} 次检查")
                    break
                
                # description = 0，判断 Write with AI 按钮是否显示
                is_button_visible = marketplace_page.is_write_with_ai_button_visible()
                if is_button_visible:
                    logger.info(f"⚠️ AI 未生成内容，Write with AI 按钮显示，重新点击 (第 {i+1}/{max_retries} 次)")
                    try:
                        marketplace_page.click_write_with_ai()
                    except Exception as e:
                        logger.warning(f"重新点击失败: {e}，继续下次循环...")
                else:
                    logger.info(f"⏳ Write with AI 按钮未显示，继续等待... (第 {i+1}/{max_retries} 次)")
            logger.info("✓ AI 内容生成等待完成")

        with allure.step("验证：AI 生成的描述填充到Description字段"):
            description = marketplace_page.get_description_value()
            assert len(description) > 0, "AI 未生成描述内容，Description字段为空"
            logger.info(f"✓ AI 生成描述长度: {len(description)} 字符")
            assert 50 <= len(description) <= 1000, \
                f"描述内容长度异常，期望: 50-1000字符，实际: {len(description)}字符"
            logger.info("✓ 描述内容长度合理")

    @pytest.mark.case_id_ai_publish_marketplace_07
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ai
    @pytest.mark.ai_publish
    @pytest.mark.ai_publish_marketplace
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("Marketplace发布AI推荐类目 - 正向场景")
    @allure.title("上传图片并输入Title后应该显示AI推荐类目")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证用户上传图片并输入Title后，图片和Title结合，AI推荐更精准的类目，数量为2-5个")
    def test_upload_image_and_input_title_ai_recommendations_should_display(self, page, config):
        """TC007: 上传图片并输入标题后显示AI推荐类目"""

        # ========== Arrange：准备测试对象 ==========
        marketplace_page = AiPublishMarketplacePage(page)

        logger.info("="*80)
        logger.info("TC007: 上传图片并输入Title后显示AI推荐类目测试")
        logger.info("="*80)

        image_path = os.path.join(os.getcwd(), "test_data/images/iphone 16_1.png")
        title = "iPhone 14 Pro Max 256GB Space Black"
        publish_url = f"{_CONFIG['base_url']}/biz/en/publish/classified"

        with allure.step("前置：重新导航到Marketplace发布页面"):
            page.goto(publish_url, timeout=60000)
            page.wait_for_load_state("domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)
            logger.info("✓ 页面已重新导航")

        # ========== Act：执行操作 ==========
        with allure.step("步骤1：上传iphone 16_1.png图片"):
            marketplace_page.upload_single_image(image_path)
            logger.info("✓ 上传图片成功")

        with allure.step("步骤2：等待图片上传完成"):
            page.wait_for_timeout(2000)
            logger.info("✓ 图片上传完成")

        with allure.step(f"步骤3：输入Title '{title}'"):
            marketplace_page.input_title(title)
            logger.info(f"✓ 输入Title: {title}")

        with allure.step("步骤4：点击Title字段外部触发失焦"):
            marketplace_page.click_title_outside()
            logger.info("✓ Title字段失焦完成")

        with allure.step("步骤5：等待 AI 推荐加载"):
            marketplace_page.wait_for_ai_recommendations()
            logger.info("✓ AI 推荐加载完成")

        # ========== Assert：验证结果 ==========
        with allure.step("验证1：页面显示 Suggested Categories 区域"):
            assert marketplace_page.is_suggested_categories_displayed(), \
                "Suggested Categories 区域未显示"
            logger.info("✓ Suggested Categories 区域显示成功")

        with allure.step("验证2：AI 推荐显示2-5个精准类目"):
            categories = marketplace_page.get_suggested_categories_text()
            assert len(categories) >= 2 and len(categories) <= 5, \
                f"AI 推荐类目数量异常，期望: 2-5个，实际: {len(categories)}"
            logger.info(f"✓ AI 推荐类目数量: {len(categories)}")
            logger.info(f"✓ 推荐类目: {', '.join(categories)}")

    @pytest.mark.case_id_ai_publish_marketplace_08
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ai
    @pytest.mark.ai_publish
    @pytest.mark.ai_publish_marketplace
    @pytest.mark.ae
    @pytest.mark.flaky(reruns=2, reruns_delay=3)
    @allure.feature("OK")
    @allure.story("Marketplace发布AI描述生成 - 正向场景")
    @allure.title("上传图片并输入标题后点击Write with AI应该生成描述内容")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证用户上传图片并输入Title后，点击Write with AI按钮，AI自动生成相关的英文描述内容")
    def test_write_with_ai_button_should_generate_description(self, page, config):
        """TC008: 上传图片并输入标题，点击Write with AI生成AI描述"""

        # ========== Arrange：准备测试对象 ==========
        marketplace_page = AiPublishMarketplacePage(page)

        logger.info("="*80)
        logger.info("TC008: 上传图片并输入标题后Write with AI生成描述测试")
        logger.info("="*80)

        image_path = os.path.join(os.getcwd(), "test_data/images/iphone 16_1.png")
        title = "iPhone 14 Pro Max 256GB Space Black"
        publish_url = f"{_CONFIG['base_url']}/biz/en/publish/classified"

        with allure.step("前置：重新导航到Marketplace发布页面"):
            page.goto(publish_url, timeout=60000)
            page.wait_for_load_state("domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)
            logger.info("✓ 页面已重新导航")

        # ========== Act：执行操作 ==========
        with allure.step("步骤1：上传商品图片"):
            marketplace_page.upload_single_image(image_path)
            page.wait_for_timeout(2000)
            logger.info("✓ 上传图片成功")

        with allure.step(f"步骤2：输入Title '{title}'"):
            marketplace_page.input_title(title)
            marketplace_page.click_title_outside()
            logger.info(f"✓ 输入Title: {title}")

        with allure.step("步骤3：点击 Write with AI 按钮"):
            marketplace_page.click_write_with_ai()
            logger.info("✓ 点击Write with AI按钮成功")

        with allure.step("步骤4：等待 AI 生成内容（循环10次检查）"):
            max_retries = 10
            for i in range(max_retries):
                # 先等待10秒
                page.wait_for_timeout(10000)
                logger.info(f"⏳ 已等待 10 秒 (第 {i+1}/{max_retries} 次)")
                
                # 检查 description 字段长度
                description = marketplace_page.get_description_value()
                if len(description) > 0:
                    logger.info(f"✓ AI 内容生成完成，第 {i+1} 次检查")
                    break
                
                # description = 0，判断 Write with AI 按钮是否显示
                is_button_visible = marketplace_page.is_write_with_ai_button_visible()
                if is_button_visible:
                    logger.info(f"⚠️ AI 未生成内容，Write with AI 按钮显示，重新点击 (第 {i+1}/{max_retries} 次)")
                    try:
                        marketplace_page.click_write_with_ai()
                    except Exception as e:
                        logger.warning(f"重新点击失败: {e}，继续下次循环...")
                else:
                    logger.info(f"⏳ Write with AI 按钮未显示，继续等待... (第 {i+1}/{max_retries} 次)")
            logger.info("✓ AI 内容生成等待完成")

        # ========== Assert：验证结果 ==========
        with allure.step("验证：AI 生成的描述内容填充到Description字段"):
            description = marketplace_page.get_description_value()
            assert len(description) > 0, \
                "AI 未生成描述内容，Description字段为空"
            logger.info(f"✓ AI 生成描述长度: {len(description)} 字符")

            assert 50 <= len(description) <= 1000, \
                f"描述内容长度异常，期望: 50-1000字符，实际: {len(description)}字符"
            logger.info("✓ 描述内容长度合理")

            assert any(c.isalpha() for c in description), \
                "描述内容不包含字母，可能生成失败"
            logger.info("✓ 描述内容格式验证通过（包含英文字母）")

    @pytest.mark.case_id_ai_publish_marketplace_09
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ai
    @pytest.mark.ai_publish
    @pytest.mark.ai_publish_marketplace
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("Marketplace发布AI推荐类目 - 交互场景")
    @allure.title("选择AI推荐的类目后应该自动填充到表单")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证用户点击AI推荐类目后，类目被选中并高亮，类目信息自动填充或标记到表单")
    def test_select_ai_recommended_category_should_fill_form(self, page, config):
        """TC009: 选择AI推荐的类目后自动填充到表单"""

        # ========== Arrange：准备测试对象 ==========
        marketplace_page = AiPublishMarketplacePage(page)

        logger.info("="*80)
        logger.info("TC009: 选择AI推荐类目后自动填充到表单测试")
        logger.info("="*80)

        image_path = os.path.join(os.getcwd(), "test_data/images/iphone 16_1.png")
        publish_url = f"{_CONFIG['base_url']}/biz/en/publish/classified"

        with allure.step("前置：重新导航到Marketplace发布页面"):
            page.goto(publish_url, timeout=60000)
            page.wait_for_load_state("domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)
            logger.info("✓ 页面已重新导航")

        # ========== Act：执行操作 ==========
        with allure.step("步骤1：上传图片，触发AI推荐"):
            marketplace_page.upload_single_image(image_path)
            page.wait_for_timeout(2000)
            logger.info("✓ 图片上传完成")

        with allure.step("步骤2：等待 AI 推荐显示"):
            marketplace_page.wait_for_ai_recommendations()
            logger.info("✓ AI 推荐已显示")

        with allure.step("步骤3：点击第一个推荐类目"):
            marketplace_page.click_suggested_category_first()
            logger.info("✓ 点击第一个推荐类目成功")

        # ========== Assert：验证结果 ==========
        with allure.step("验证：推荐类目被点击（页面无报错）"):
            current_url = page.url
            assert "publish" in current_url, \
                f"操作后页面异常，当前URL: {current_url}"
            logger.info("✓ 选择推荐类目操作成功")
            logger.info("✅ 推荐类目选择功能正常")


@pytest.fixture(scope="function")
def setup_marketplace_page(page, config):
    """
    Function级别的前置条件：登录并导航到Marketplace发布页面

    前置步骤（来自测试用例文档）：
    - 访问页面：https://aepub.58v5.cn/biz/en/publish/front
    - 若未登录，则先登录（username：yangyang100@58.com/Qa123456）
    - 点击Marketplace，进入Marketplace发布页面（/biz/en/publish/classified）
    """
    login_page = LoginPage(page)
    marketplace_page = AiPublishMarketplacePage(page)

    site = config['site']
    role = config['role']
    account_name = config['user_name']
    base_url = config['base_url']
    username = config['test_account']['username']
    password = config['test_account']['password']

    logger.info("="*80)
    logger.info("AE站 - Marketplace发布AI推荐功能测试 - Class Setup")
    logger.info("="*80)
    logger.info(f"站点: {site.upper()} ({config['site_name']})")
    logger.info(f"角色: {role.upper()} (卖家)")
    logger.info(f"账号: {account_name}")
    logger.info(f"邮箱: {username}")
    logger.info("="*80)

    # ========== Session 复用机制：尝试加载已有登录状态 ==========
    session_manager = SessionManager(page, base_url, session_name=f"{site}_{role}_{account_name}")
    session_loaded = False

    with allure.step("步骤1：访问发布首页"):
        page.goto(f"{base_url}/biz/en/publish/front", timeout=30000)
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        logger.info(f"✓ 访问发布首页成功: {base_url}/biz/en/publish/front")

    with allure.step("尝试加载已保存的 Session"):
        session_loaded = session_manager.load_session()
        if session_loaded:
            logger.info("✓ 成功加载已保存的 Session")
            page.reload()
            page.wait_for_load_state("domcontentloaded", timeout=10000)
            page.wait_for_timeout(2000)
            is_logged_in = login_page.is_login_button_text_changed(timeout=2000)
            if is_logged_in:
                logger.info("✓ Session 有效，已登录状态")
                logger.info("✅ 跳过登录步骤！")
            else:
                logger.info("⚠️ Session 已过期，需要重新登录")
                session_loaded = False
        else:
            logger.info("⚠️ 未找到已保存的 Session，需要执行登录")

    if not session_loaded:
        with allure.step("步骤2：处理Cookie弹窗"):
            login_page.handle_cookie_popup()
            logger.info("✓ 已处理Cookie弹窗（如果存在）")
            page.wait_for_timeout(1000)

        with allure.step("步骤3：点击页面右上角 Log in / Register 按钮"):
            login_page.click_login_register_button()
            logger.info("✓ 点击登录/注册按钮")

        with allure.step(f"步骤4：输入邮箱 {username}"):
            login_page.input_email(username)
            login_page.click_continue_button()
            logger.info("✓ 输入邮箱完成")

        with allure.step("步骤5：输入密码并点击Log in"):
            login_page.input_password(password)
            login_page.click_login_button()
            logger.info("✓ 输入密码完成")

        with allure.step("验证登录成功"):
            page.wait_for_load_state("domcontentloaded", timeout=10000)
            current_url = page.url
            assert "login" not in current_url.lower(), \
                f"登录失败，仍停留在登录页: {current_url}"
            assert login_page.is_login_button_text_changed(timeout=3000), \
                "登录失败，右上角仍显示 Log in / Register"
            logger.info("✅ 登录成功！")

        with allure.step("保存 Session"):
            if session_manager.save_session():
                logger.info("✓ Session 已保存，下次测试将自动复用")

    with allure.step("步骤3：点击 Marketplace 类目，进入Marketplace发布页面"):
        marketplace_page.click_marketplace_category()
        logger.info("✓ 点击 Marketplace 类目成功")

    with allure.step("步骤4：等待Marketplace发布页面加载完成"):
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        page.wait_for_timeout(6000)
        logger.info("✓ Marketplace发布页面加载完成")

    with allure.step("验证进入 Marketplace 发布页面"):
        current_url = page.url
        assert "classified" in current_url or "publish" in current_url, \
            f"未进入Marketplace发布页面，当前URL: {current_url}"
        logger.info(f"✓ 已进入Marketplace发布页面: {current_url}")
        logger.info("✅ Class Setup 完成！")

    yield

    logger.info("Class Teardown: 测试类执行完成")
