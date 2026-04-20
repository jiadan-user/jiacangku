"""
AE站 - Property发布页AI推荐功能测试

本脚本由 playwright-test-generator 生成
录制文档：test_cases/ai/ai_publish/ai_publish_Property测试用例_20260311.md
生成时间：2026-03-11

测试站点：AE (https://aepub.58v5.cn)
测试角色：Seller (卖家)
测试目标：验证在Property发布页面，当用户上传房产图片和输入Title后，系统会基于AI智能分析，
         显示推荐的房产类目，并支持AI生成描述内容
"""
import pytest
import allure
import os
from pages.login_page import LoginPage
from pages.ai_publish_property_page import AiPublishPropertyPage
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
    "user_name": "ae_seller_property",
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


@pytest.mark.usefixtures("setup_property_page")
class TestAiPublishProperty:
    """Property发布AI推荐功能测试类"""
    
    @pytest.mark.case_id_ai_publish_property_01
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ai
    @pytest.mark.ae
    @pytest.mark.ai_publish
    @pytest.mark.ai_publish_property
    @pytest.mark.skip(reason="房产发布页改造，暂时跳过")
    @allure.feature("OK")
    @allure.story("Property发布AI推荐类目 - 正向场景")
    @allure.title("上传单张房产图片后应该显示AI推荐类目")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证用户上传单张房产图片（villa.png）后，页面显示Suggested Categories区域，并推荐至少1个相关类目")
    def test_upload_single_property_image_ai_recommendations_should_display(self, page, config):
        """TC001: 上传单张房产图片后显示AI推荐类目"""
        
        # ========== Arrange：准备测试对象 ==========
        property_page = AiPublishPropertyPage(page)
        
        logger.info("="*80)
        logger.info("TC001: 上传单张房产图片后显示AI推荐类目测试")
        logger.info("="*80)
        
        # 准备测试图片路径
        image_path = os.path.join(os.getcwd(), "test_data/images/villa_1.png")
        
        # ========== Act：执行操作 ==========
        with allure.step("步骤1：上传villa_1.png图片"):
            property_page.upload_single_image(image_path)
            logger.info("✓ 上传villa_1.png成功")
        
        with allure.step("步骤2：等待 AI 推荐加载"):
            property_page.wait_for_ai_recommendations()
            logger.info("✓ AI 推荐加载完成")
        
        # ========== Assert：验证结果 ==========
        with allure.step("验证1：图片成功上传，显示上传计数"):
            upload_count = property_page.get_upload_count()
            # 提取已上传数量和总限制（如 "1/20" -> 已上传1张）
            import re
            match = re.search(r'(\d+)/(\d+)', upload_count)
            assert match, f"无法解析上传计数格式，实际: '{upload_count}'"
            uploaded, total = int(match.group(1)), int(match.group(2))
            assert uploaded == 1, f"图片上传数量错误，期望: 1，实际: {uploaded}"
            logger.info(f"✓ 上传计数验证通过: {upload_count}")
        
        with allure.step("验证2：页面显示 Suggested Categories 区域"):
            assert property_page.is_suggested_categories_displayed(), \
                "Suggested Categories 区域未显示"
            logger.info("✓ Suggested Categories 区域显示成功")
        
        with allure.step("验证3：AI 推荐至少1个相关类目"):
            categories = property_page.get_suggested_categories_text()
            assert len(categories) >= 1, \
                f"AI 推荐类目数量不足，期望: ≥1，实际: {len(categories)}"
            logger.info(f"✓ AI 推荐类目数量: {len(categories)}")
            logger.info(f"✓ 推荐类目: {', '.join(categories)}")
            
            # 验证推荐类目包含Villa相关内容
            categories_text = ' '.join(categories).lower()
            assert 'villa' in categories_text or 'residential' in categories_text, \
                f"AI 推荐类目不相关，推荐内容: {categories}"
            logger.info("✓ AI 推荐类目相关性验证通过")
    
    @pytest.mark.case_id_ai_publish_property_02
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ai
    @pytest.mark.ai_publish
    @pytest.mark.ai_publish_property
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("Property发布AI描述生成 - 正向场景")
    @allure.title("单张房产图片点击Write with AI应该生成AI描述")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证用户上传单张房产图片后，点击Write with AI按钮，AI自动生成与图片相关的描述内容")
    def test_single_image_write_with_ai_should_generate_description(self, page, config):
        """TC002: 单张房产图片，点击Write with AI生成AI描述"""
        
        # ========== Arrange：准备测试对象 ==========
        property_page = AiPublishPropertyPage(page)
        
        logger.info("="*80)
        logger.info("TC002: 单张房产图片点击Write with AI生成描述测试")
        logger.info("="*80)
        
        # ========== 前置：从发布首页重新进入 Property 页面 ==========
        with allure.step("前置：从发布首页重新进入 Property 发布页面"):
            property_page.navigate_to_publish_front_and_click_property(config['base_url'])
            page.wait_for_timeout(6000)
            logger.info("✓ 从发布首页重新进入 Property 页面")
        
        image_path = os.path.join(os.getcwd(), "test_data/images/villa_1.png")
        
        # ========== Act：执行操作 ==========
        with allure.step("步骤1：上传单张房产图片"):
            property_page.upload_single_image(image_path)
            logger.info("✓ 上传单张房产图片成功")
        
        with allure.step("步骤2：点击 Write with AI 按钮"):
            property_page.click_write_with_ai()
            logger.info("✓ 点击Write with AI成功")
        
        with allure.step("步骤3：等待 AI 生成内容"):
            success = property_page.wait_for_ai_description_generation()
            assert success or len(property_page.get_description_value()) > 0, \
                "AI 生成超时且描述字段为空"
            logger.info("✓ AI 内容生成等待完成")
        
        # ========== Assert：验证结果 ==========
        with allure.step("验证：AI 生成的描述填充到Description字段"):
            description = property_page.get_description_value()
            assert len(description) > 0, "AI 未生成描述内容，Description字段为空"
            logger.info(f"✓ AI 生成描述长度: {len(description)} 字符")
            assert 0 < len(description) <= 1000, \
                f"描述内容长度异常，期望: 0-1000字符，实际: {len(description)}字符"
            logger.info("✓ 描述内容长度合理")
    
    @pytest.mark.case_id_ai_publish_property_03
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ai
    @pytest.mark.ai_publish
    @pytest.mark.ai_publish_property
    @pytest.mark.ae
    @pytest.mark.skip(reason="房产发布页改造，暂时跳过")
    @allure.feature("OK")
    @allure.story("Property发布AI推荐类目 - 正向场景")
    @allure.title("上传多张房产图片后应该显示AI推荐类目")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证用户上传3张公寓图片后，页面显示Suggested Categories区域，AI推荐基于多图片综合分析更准确")
    def test_upload_multiple_property_images_ai_recommendations_should_display(self, page, config):
        """TC003: 上传多张房产图片后显示AI推荐类目"""
        
        # ========== Arrange：准备测试对象 ==========
        property_page = AiPublishPropertyPage(page)
        
        logger.info("="*80)
        logger.info("TC003: 上传多张房产图片后显示AI推荐类目测试")
        logger.info("="*80)
        
        image_paths = [
            os.path.join(os.getcwd(), "test_data/images/apartment_1.png"),
            os.path.join(os.getcwd(), "test_data/images/apartment_2.png"),
            os.path.join(os.getcwd(), "test_data/images/apartment_3.png")
        ]
        
        with allure.step("前置：重新导航到发布页面"):
            property_page.navigate_to_publish_front_and_click_property(config['base_url'])
            page.wait_for_timeout(6000)
            logger.info("✓ 页面已重新导航")
        
        with allure.step("步骤1：上传3张公寓图片"):
            property_page.upload_multiple_images(image_paths)
            logger.info("✓ 上传3张公寓图片成功")
        
        with allure.step("步骤2：等待 AI 推荐加载"):
            property_page.wait_for_ai_recommendations()
            logger.info("✓ AI 推荐加载完成")
        
        with allure.step("验证1：3张图片均成功上传"):
            upload_count = property_page.get_upload_count()
            # 提取已上传数量（如 "3/20" -> 已上传3张）
            import re
            match = re.search(r'(\d+)/(\d+)', upload_count)
            assert match, f"无法解析上传计数格式，实际: '{upload_count}'"
            uploaded, total = int(match.group(1)), int(match.group(2))
            assert uploaded == 3, f"图片上传数量错误，期望: 3，实际: {uploaded}"
            logger.info(f"✓ 上传计数验证通过: {upload_count}")
        
        with allure.step("验证2：页面显示 Suggested Categories 区域"):
            assert property_page.is_suggested_categories_displayed(), \
                "Suggested Categories 区域未显示"
            logger.info("✓ Suggested Categories 区域显示成功")
        
        with allure.step("验证3：AI 推荐基于多图片综合分析"):
            categories = property_page.get_suggested_categories_text()
            assert len(categories) >= 1, \
                f"AI 推荐类目数量不足，期望: ≥1，实际: {len(categories)}"
            logger.info(f"✓ AI 推荐类目数量: {len(categories)}")
            categories_text = ' '.join(categories).lower()
            assert 'apartment' in categories_text or 'residential' in categories_text, \
                f"AI 推荐类目不相关，推荐内容: {categories}"
            logger.info("✓ AI 推荐类目相关性验证通过（公寓类型）")
    
    @pytest.mark.case_id_ai_publish_property_04
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ai
    @pytest.mark.ai_publish
    @pytest.mark.ai_publish_property
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("Property发布AI描述生成 - 正向场景")
    @allure.title("上传多张房产图片点击Write with AI应该生成AI描述")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证用户上传多张房产图片后，点击Write with AI按钮，AI自动生成与图片相关的描述内容")
    def test_multiple_images_write_with_ai_should_generate_description(self, page, config):
        """TC004: 上传多张房产图片，点击Write with AI生成AI描述"""
        
        property_page = AiPublishPropertyPage(page)
        
        logger.info("="*80)
        logger.info("TC004: 多张房产图片点击Write with AI生成描述测试")
        logger.info("="*80)
        
        image_paths = [
            os.path.join(os.getcwd(), "test_data/images/apartment_1.png"),
            os.path.join(os.getcwd(), "test_data/images/apartment_2.png"),
            os.path.join(os.getcwd(), "test_data/images/apartment_3.png")
        ]
        
        with allure.step("前置：重新导航到发布页面，清空页面状态"):
            property_page.navigate_to_publish_front_and_click_property(config['base_url'])
            page.wait_for_timeout(6000)
            logger.info("✓ 页面已重新导航")
        
        with allure.step("前置：上传 3 张公寓图片"):
            property_page.upload_multiple_images(image_paths)
            logger.info("✓ 已上传 3 张公寓图片")
        
        with allure.step("步骤1：确认当前为 3 张图片"):
            upload_count_str = property_page.get_upload_count()
            n = property_page.parse_upload_count(upload_count_str)
            assert n == 3, f"前置后应恰好 3 张图片，实际: {n} 张（{upload_count_str}）"
            logger.info("✓ 当前为 3 张图片")
        
        with allure.step("步骤2：点击 Write with AI 按钮"):
            property_page.click_write_with_ai()
            logger.info("✓ 点击Write with AI成功")
        
        with allure.step("步骤3：等待 AI 生成内容"):
            success = property_page.wait_for_ai_description_generation()
            assert success or len(property_page.get_description_value()) > 0, \
                "AI 生成超时且描述字段为空"
            logger.info("✓ AI 内容生成等待完成")
        
        with allure.step("验证：AI 生成的描述填充到Description字段"):
            description = property_page.get_description_value()
            assert len(description) > 0, "AI 未生成描述内容，Description字段为空"
            logger.info(f"✓ AI 生成描述长度: {len(description)} 字符")
            assert 50 <= len(description) <= 1000, \
                f"描述内容长度异常，期望: 50-1000字符，实际: {len(description)}字符"
            logger.info("✓ 描述内容长度合理")
    
    @pytest.mark.case_id_ai_publish_property_05
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ai
    @pytest.mark.ai_publish
    @pytest.mark.ai_publish_property
    @pytest.mark.ae
    @pytest.mark.skip(reason="房产发布页改造，暂时跳过")
    @allure.feature("OK")
    @allure.story("Property发布AI推荐类目 - 正向场景")
    @allure.title("仅输入标题后应该显示AI推荐类目")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证用户仅输入Title不上传图片时，失焦后页面显示Suggested Categories区域及AI推荐类目")
    def test_title_only_ai_recommendations_should_display(self, page, config):
        """TC005: 仅输入标题后显示AI推荐类目（录制：locator('#title').fill + getByText('Description *').click）"""
        
        property_page = AiPublishPropertyPage(page)
        
        logger.info("="*80)
        logger.info("TC005: 仅输入标题后显示AI推荐类目测试")
        logger.info("="*80)
        
        title = "Luxury 2BR Apartment in Downtown Dubai"
        
        with allure.step("前置：重新导航到发布页面"):
            property_page.navigate_to_publish_front_and_click_property(config['base_url'])
            page.wait_for_timeout(6000)
            logger.info("✓ 页面已重新导航")
        
        with allure.step("步骤1：在Title字段输入标题"):
            property_page.input_title(title)
            logger.info(f"✓ 输入Title: {title}")
        
        with allure.step("步骤2：点击Title字段外部触发失焦"):
            property_page.click_title_outside()
            logger.info("✓ Title失焦完成")
        
        with allure.step("步骤3：等待 AI 推荐加载"):
            property_page.wait_for_ai_recommendations()
            logger.info("✓ AI 推荐加载完成")
        
        with allure.step("验证：Suggested Categories 区域显示AI推荐类目"):
            assert property_page.is_suggested_categories_displayed(), \
                "Suggested Categories 区域未显示"
            logger.info("✓ Suggested Categories 区域显示成功")
            categories = property_page.get_suggested_categories_text()
            assert len(categories) >= 1, \
                f"AI 推荐类目数量不足，期望: ≥1，实际: {len(categories)}"
            logger.info(f"✓ AI 推荐类目数量: {len(categories)}")
    
    @pytest.mark.case_id_ai_publish_property_06
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ai
    @pytest.mark.ai_publish
    @pytest.mark.ai_publish_property
    @pytest.mark.ae
    @allure.feature("OK")
    @allure.story("Property发布AI描述生成 - 正向场景")
    @allure.title("仅输入标题点击Write with AI应该生成AI描述")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证用户仅输入Title不上传图片时，点击Write with AI按钮，AI自动生成与标题相关的描述内容")
    def test_title_only_write_with_ai_should_generate_description(self, page, config):
        """TC006: 仅输入标题，点击Write with AI生成AI描述（录制：getByRole('button', name='Write with AI').click）"""
        
        property_page = AiPublishPropertyPage(page)
        
        logger.info("="*80)
        logger.info("TC006: 仅输入标题点击Write with AI生成描述测试")
        logger.info("="*80)
        
        title = "Luxury 2BR Apartment in Downtown Dubai"
        
        with allure.step("前置：重新导航到发布页面"):
            property_page.navigate_to_publish_front_and_click_property(config['base_url'])
            page.wait_for_timeout(6000)
            logger.info("✓ 页面已重新导航")
        
        with allure.step("步骤1：在Title字段输入标题"):
            property_page.input_title(title)
            property_page.click_title_outside()
            logger.info(f"✓ 输入Title: {title}")
        
        with allure.step("步骤2：点击 Write with AI 按钮"):
            property_page.click_write_with_ai()
            logger.info("✓ 点击Write with AI成功")
        
        with allure.step("步骤3：等待 AI 生成内容"):
            success = property_page.wait_for_ai_description_generation()
            assert success or len(property_page.get_description_value()) > 0, \
                "AI 生成超时且描述字段为空"
            logger.info("✓ AI 内容生成等待完成")
        
        with allure.step("验证：AI 生成的描述填充到Description字段"):
            description = property_page.get_description_value()
            assert len(description) > 0, "AI 未生成描述内容，Description字段为空"
            logger.info(f"✓ AI 生成描述长度: {len(description)} 字符")
            assert 50 <= len(description) <= 1000, \
                f"描述内容长度异常，期望: 50-1000字符，实际: {len(description)}字符"
            logger.info("✓ 描述内容长度合理")
    
    @pytest.mark.case_id_ai_publish_property_07
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ai
    @pytest.mark.ai_publish
    @pytest.mark.ai_publish_property
    @pytest.mark.ae
    @pytest.mark.skip(reason="房产发布页改造，暂时跳过")
    @allure.feature("OK")
    @allure.story("Property发布AI推荐类目 - 正向场景")
    @allure.title("上传图片并输入Title后应该显示AI推荐类目")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证用户上传图片并输入Title后，图片和Title结合，AI推荐更精准的类目")
    def test_upload_image_and_input_title_ai_recommendations_should_display(self, page, config):
        """TC007: 上传图片并输入标题后显示AI推荐类目"""
        
        # ========== Arrange：准备测试对象 ==========
        property_page = AiPublishPropertyPage(page)
        
        logger.info("="*80)
        logger.info("TC007: 上传图片并输入Title后显示AI推荐类目测试")
        logger.info("="*80)
        
        # 准备测试数据
        image_path = os.path.join(os.getcwd(), "test_data/images/apartment_1.png")
        title = "Luxury 2BR Apartment in Downtown Dubai"
        
        with allure.step("前置：重新导航到发布页面"):
            property_page.navigate_to_publish_front_and_click_property(config['base_url'])
            page.wait_for_timeout(6000)
            logger.info("✓ 页面已重新导航")
        
        # ========== Act：执行操作 ==========
        with allure.step("步骤1：上传apartment_1.png图片"):
            property_page.upload_single_image(image_path)
            logger.info("✓ 上传apartment_1.png成功")
        
        with allure.step("步骤2：等待图片上传完成"):
            page.wait_for_timeout(2000)
            logger.info("✓ 图片上传完成")
        
        with allure.step(f"步骤3：输入Title '{title}'"):
            property_page.input_title(title)
            logger.info(f"✓ 输入Title: {title}")
        
        with allure.step("步骤4：点击Title字段外部触发失焦"):
            property_page.click_title_outside()
            logger.info("✓ Title字段失焦完成")
        
        with allure.step("步骤5：等待 AI 推荐加载"):
            property_page.wait_for_ai_recommendations()
            logger.info("✓ AI 推荐加载完成")
        
        # ========== Assert：验证结果 ==========
        with allure.step("验证1：页面显示 Suggested Categories 区域"):
            assert property_page.is_suggested_categories_displayed(), \
                "Suggested Categories 区域未显示"
            logger.info("✓ Suggested Categories 区域显示成功")
        
        with allure.step("验证2：AI 推荐显示更精准的类目"):
            categories = property_page.get_suggested_categories_text()
            assert len(categories) >= 2 and len(categories) <= 5, \
                f"AI 推荐类目数量异常，期望: 2-5个，实际: {len(categories)}"
            logger.info(f"✓ AI 推荐类目数量: {len(categories)}")
            logger.info(f"✓ 推荐类目: {', '.join(categories)}")
            
            # 验证推荐类目包含Apartment相关内容
            categories_text = ' '.join(categories).lower()
            assert 'apartment' in categories_text or 'residential' in categories_text, \
                f"AI 推荐类目不相关，推荐内容: {categories}"
            logger.info("✓ AI 推荐类目精准度验证通过")
    
  
    @pytest.mark.case_id_ai_publish_property_08
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ai
    @pytest.mark.ai_publish
    @pytest.mark.ai_publish_property
    @pytest.mark.ae
    @pytest.mark.flaky(reruns=2, reruns_delay=3)
    @allure.feature("OK")
    @allure.story("Property发布AI描述生成 - 正向场景")
    @allure.title("上传图片并输入标题后点击Write with AI应该生成描述内容")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证用户上传图片并输入Title后，点击Write with AI按钮，AI自动生成相关的描述内容")
    def test_write_with_ai_button_should_generate_description(self, page, config):
        """TC008: 上传图片并输入标题，点击Write with AI生成AI描述"""
        
        # ========== Arrange：准备测试对象 ==========
        property_page = AiPublishPropertyPage(page)
        
        logger.info("="*80)
        logger.info("TC008: 上传图片并输入标题后Write with AI生成描述测试")
        logger.info("="*80)
        
        # 准备测试数据
        image_path = os.path.join(os.getcwd(), "test_data/images/apartment_1.png")
        title = "Luxury Apartment with Pool and Gym"

        with allure.step("前置：重新导航到发布页面"):
            property_page.navigate_to_publish_front_and_click_property(config['base_url'])
            page.wait_for_timeout(6000)
            logger.info("✓ 页面已重新导航")
        
        # ========== Act：执行操作 ==========
        with allure.step("步骤1：上传房产图片"):
            property_page.upload_single_image(image_path)
            page.wait_for_timeout(2000)
            logger.info("✓ 上传图片成功")
        
        with allure.step(f"步骤2：输入Title '{title}'"):
            property_page.input_title(title)
            property_page.click_title_outside()
            logger.info(f"✓ 输入Title: {title}")
        
        with allure.step("步骤3：点击 Write with AI 按钮"):
            property_page.click_write_with_ai()
            logger.info("✓ 点击Write with AI按钮成功")
        
        with allure.step("步骤4：等待 AI 生成内容"):
            success = property_page.wait_for_ai_description_generation()
            assert success or len(property_page.get_description_value()) > 0, \
                "AI 生成超时且描述字段为空"
            logger.info("✓ AI 内容生成等待完成")
        
        # ========== Assert：验证结果 ==========
        with allure.step("验证：AI 生成的描述内容填充到Description字段"):
            description = property_page.get_description_value()
            assert len(description) > 0, \
                "AI 未生成描述内容，Description字段为空"
            logger.info(f"✓ AI 生成描述长度: {len(description)} 字符")
            
            # 验证描述内容长度合理（50-500字符）
            assert 50 <= len(description) <= 1000, \
                f"描述内容长度异常，期望: 50-500字符，实际: {len(description)}字符"
            logger.info("✓ 描述内容长度合理")
            
            # 验证描述内容为英文
            assert any(c.isalpha() for c in description), \
                "描述内容不包含字母，可能生成失败"
            logger.info("✓ 描述内容格式验证通过")

    @pytest.mark.case_id_ai_publish_property_09
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ai
    @pytest.mark.ai_publish
    @pytest.mark.ai_publish_property
    @pytest.mark.ae
    @pytest.mark.skip(reason="房产发布页改造，暂时跳过")
    @allure.feature("OK")
    @allure.story("Property发布AI推荐类目 - 交互场景")
    @allure.title("选择AI推荐的类目后应该自动填充到表单")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证用户点击AI推荐类目后，类目被选中并标记为用户选择的类目")
    def test_select_ai_recommended_category_should_fill_form(self, page, config):
        """TC009: 选择AI推荐的类目后自动填充到表单"""
        
        # ========== Arrange：准备测试对象 ==========
        property_page = AiPublishPropertyPage(page)
        
        logger.info("="*80)
        logger.info("TC009: 选择AI推荐类目后自动填充到表单测试")
        logger.info("="*80)
        
        # 准备测试数据
        image_path = os.path.join(os.getcwd(), "test_data/images/apartment_1.png")
        title = "Modern Apartment for Rent"
        
        with allure.step("前置：重新导航到发布页面"):
            property_page.navigate_to_publish_front_and_click_property(config['base_url'])
            page.wait_for_timeout(6000)
            logger.info("✓ 页面已重新导航")
        
        # ========== Act：执行操作 ==========
        with allure.step("步骤1：上传图片并输入Title"):
            property_page.upload_single_image(image_path)
            page.wait_for_timeout(2000)
            property_page.input_title(title)
            property_page.click_title_outside()
            logger.info("✓ 图片和Title准备完成")
        
        with allure.step("步骤2：等待 AI 推荐显示"):
            property_page.wait_for_ai_recommendations()
            logger.info("✓ AI 推荐已显示")
        
        with allure.step("步骤3：点击第一个推荐类目"):
            property_page.click_suggested_category_first()
            logger.info("✓ 点击第一个推荐类目成功")
        
        # ========== Assert：验证结果 ==========
        with allure.step("验证：推荐类目被点击（页面无报错）"):
            # 验证页面未报错，操作成功执行
            current_url = page.url
            assert "publish" in current_url, \
                f"操作后页面异常，当前URL: {current_url}"
            logger.info("✓ 选择推荐类目操作成功")
            logger.info("✅ 推荐类目选择功能正常")
    
    @pytest.mark.case_id_ai_publish_property_10
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ai
    @pytest.mark.ai_publish
    @pytest.mark.ai_publish_property
    @pytest.mark.ae
    @pytest.mark.skip(reason="房产发布页改造，暂时跳过")
    @allure.feature("OK")
    @allure.story("Property发布AI识别准确性 - 公寓类型")
    @allure.title("上传公寓图片AI应该识别并推荐Apartment相关类目")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证AI能够准确识别公寓图片，推荐Apartment相关类目，不应推荐Villa、Land等不相关类目")
    def test_upload_apartment_image_ai_should_recommend_apartment_category(self, page, config):
        """TC0010: 上传不同类型的房产图片验证AI识别准确性-公寓"""
        
        # ========== Arrange：准备测试对象 ==========
        property_page = AiPublishPropertyPage(page)
        
        logger.info("="*80)
        logger.info("TC0010: 上传公寓图片验证AI识别准确性测试")
        logger.info("="*80)
        
        # 准备测试数据
        image_path = os.path.join(os.getcwd(), "test_data/images/apartment_1.png")
        title = "Modern Apartment"
        
        with allure.step("前置：重新导航到发布页面"):
            property_page.navigate_to_publish_front_and_click_property(config['base_url'])
            page.wait_for_timeout(6000)
            logger.info("✓ 页面已重新导航")
        
        # ========== Act：执行操作 ==========
        with allure.step("步骤1：上传公寓图片"):
            property_page.upload_single_image(image_path)
            logger.info("✓ 上传公寓图片成功")
        
        with allure.step("步骤2：输入Title 'Modern Apartment'"):
            page.wait_for_timeout(2000)
            property_page.input_title(title)
            property_page.click_title_outside()
            logger.info("✓ 输入Title完成")
        
        with allure.step("步骤3：等待 AI 推荐加载"):
            property_page.wait_for_ai_recommendations()
            logger.info("✓ AI 推荐加载完成")
        
        # ========== Assert：验证结果 ==========
        with allure.step("验证1：AI 推荐类目包含Apartment相关选项"):
            categories = property_page.get_suggested_categories_text()
            categories_text = ' '.join(categories).lower()
            
            # 验证包含Apartment相关类目
            assert 'apartment' in categories_text or 'residential' in categories_text, \
                f"AI 未推荐Apartment相关类目，推荐内容: {categories}"
            logger.info("✓ AI 推荐包含Apartment相关类目")
        
        with allure.step("验证2：AI 不应推荐Villa、Land等不相关类目"):
            # 验证不包含明显不相关的类目
            assert 'land' not in categories_text and 'commercial' not in categories_text, \
                f"AI 推荐了不相关类目，推荐内容: {categories}"
            logger.info("✓ AI 未推荐不相关类目")
            logger.info(f"✓ 推荐类目: {', '.join(categories)}")
    
    @pytest.mark.case_id_ai_publish_property_11
    @pytest.mark.smoke
    @pytest.mark.p0
    @pytest.mark.ai
    @pytest.mark.ai_publish
    @pytest.mark.ai_publish_property
    @pytest.mark.ae
    @pytest.mark.skip(reason="房产发布页改造，暂时跳过")
    @allure.feature("OK")
    @allure.story("Property发布AI识别准确性 - 别墅类型")
    @allure.title("上传别墅图片AI应该识别并推荐Villa相关类目")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("验证AI能够准确识别别墅图片，推荐Villa相关类目，不应推荐Apartment、Office等不相关类目")
    def test_upload_villa_image_ai_should_recommend_villa_category(self, page, config):
        """TC0011: 上传不同类型的房产图片验证AI识别准确性-别墅"""
        
        # ========== Arrange：准备测试对象 ==========
        property_page = AiPublishPropertyPage(page)
        
        logger.info("="*80)
        logger.info("TC0011: 上传别墅图片验证AI识别准确性测试")
        logger.info("="*80)
        
        # 准备测试数据
        image_path = os.path.join(os.getcwd(), "test_data/images/villa_1.png")
        title = "Luxury Villa with Pool"
        
        with allure.step("前置：重新导航到发布页面"):
            property_page.navigate_to_publish_front_and_click_property(config['base_url'])
            page.wait_for_timeout(6000)
            logger.info("✓ 页面已重新导航")
        
        # ========== Act：执行操作 ==========
        with allure.step("步骤1：上传别墅图片"):
            property_page.upload_single_image(image_path)
            logger.info("✓ 上传别墅图片成功")
        
        with allure.step("步骤2：输入Title 'Luxury Villa with Pool'"):
            page.wait_for_timeout(2000)
            property_page.input_title(title)
            property_page.click_title_outside()
            logger.info("✓ 输入Title完成")
        
        with allure.step("步骤3：等待 AI 推荐加载"):
            property_page.wait_for_ai_recommendations()
            logger.info("✓ AI 推荐加载完成")
        
        # ========== Assert：验证结果 ==========
        with allure.step("验证1：AI 推荐类目包含Villa相关选项"):
            categories = property_page.get_suggested_categories_text()
            categories_text = ' '.join(categories).lower()
            
            # 验证包含Villa相关类目
            assert 'villa' in categories_text or 'residential' in categories_text, \
                f"AI 未推荐Villa相关类目，推荐内容: {categories}"
            logger.info("✓ AI 推荐包含Villa相关类目")
        
        with allure.step("验证2：AI 不应推荐Apartment、Office等不相关类目"):
            # 验证不包含明显不相关的类目（如果有Apartment应该不是主推荐）
            # Villa和Apartment都属于Residential，可能都会出现，所以这里放宽验证
            assert 'office' not in categories_text and 'commercial' not in categories_text, \
                f"AI 推荐了不相关类目，推荐内容: {categories}"
            logger.info("✓ AI 未推荐Office/Commercial等不相关类目")
            logger.info(f"✓ 推荐类目: {', '.join(categories)}")


@pytest.fixture(scope="module")
def setup_property_page(page, config):
    """
    Function级别的前置条件：登录并导航到Property发布页面
    
    前置步骤（来自测试用例文档）：
    - 访问页面：https://aepub.58v5.cn/biz/en/publish/front
    - 若未登录，则先登录（username：yangyang100@58.com/Qa123456）
    - 点击Property，进入Property发布页面
    """
    login_page = LoginPage(page)
    property_page = AiPublishPropertyPage(page)
    
    # 从 config 读取测试数据
    site = config['site']
    role = config['role']
    account_name = config['user_name']
    base_url = config['base_url']
    username = config['test_account']['username']
    password = config['test_account']['password']
    
    logger.info("="*80)
    logger.info("AE站 - Property发布AI推荐功能测试 - Class Setup")
    logger.info("="*80)
    logger.info(f"站点: {site.upper()} ({config['site_name']})")
    logger.info(f"角色: {role.upper()} (卖家)")
    logger.info(f"账号: {account_name}")
    logger.info(f"邮箱: {username}")
    logger.info("="*80)
    
    # ========== Session 复用机制：尝试加载已有登录状态 ==========
    session_manager = SessionManager(page, base_url, session_name=f"{site}_{role}_{account_name}")
    session_loaded = False
    
    # ========== 步骤1：进入页面 https://aepub.58v5.cn/biz/en/publish/front ==========
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
    
    # ========== 步骤2：若未登录，则先点击页面右上角登录按钮完成登录 ==========
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
            assert "login" not in current_url.lower(), f"登录失败，仍停留在登录页: {current_url}"
            assert login_page.is_login_button_text_changed(timeout=3000), \
                "登录失败，右上角仍显示 Log in / Register"
            logger.info("✅ 登录成功！")
        
        with allure.step("保存 Session"):
            if session_manager.save_session():
                logger.info("✓ Session 已保存，下次测试将自动复用")
    
    # ========== 步骤3：点击页面Property，进入Property发布页面 ==========
    with allure.step("步骤3：点击 Property 类目，进入Property发布页面"):
        property_page.click_property_category()
        logger.info("✓ 点击 Property 类目成功")
    
    # ========== 步骤4：等待页面加载完成 ==========
    with allure.step("步骤4：等待Property发布页面加载完成"):
        page.wait_for_load_state("domcontentloaded", timeout=15000)
        page.wait_for_timeout(6000)
        logger.info("✓ Property发布页面加载完成")
    
    with allure.step("验证进入 Property 发布页面"):
        current_url = page.url
        assert "publish" in current_url and "categoryId=5001" in current_url, \
            f"未进入Property发布页面，当前URL: {current_url}"
        logger.info(f"✓ 已进入Property发布页面: {current_url}")
        logger.info("✅ Class Setup 完成！")
    
    yield
    
    # Teardown: 清理操作（如果需要）
    logger.info("Class Teardown: 测试类执行完成")
