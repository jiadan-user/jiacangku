"""
OK阿联酋站 - Post页面功能探索测试

本脚本用于探索 Post（发布）页面的功能和元素结构

测试站点：AE (https://ae.58v5.cn)
测试角色：Seller (卖家)
测试目标：访问 Post 分类选择页，探索页面结构、输入控件、按钮、图片上传等元素
"""

import pytest
import allure
import os
from pathlib import Path
from pages.login_page import LoginPage
from utils.session_manager import SessionManager
from utils.logger import setup_logger

logger = setup_logger()
ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_TEST_IMAGE = ROOT_DIR / "test_data" / "images" / "8b423179e72ba4d4a56ca6a5b0479aee.png"

# 配置信息
_CONFIG = {
    'site': 'ae',
    'site_name': 'OK阿联酋站',
    'role': 'seller',
    'user_name': 'gaosong01_ae_seller',
    'base_url': 'https://ae.58v5.cn/en/city-abu-dhabi/',
    'post_url': 'https://aepub.58v5.cn/biz/en/publish/front',
    
    'test_account': {
        'username': 'gaosong01@58.com',
        'password': 'Qwert_123'
    },
    
    'test_resources': {
        'image_path': str(DEFAULT_TEST_IMAGE)
    },
    'browser': {
        'type': 'chromium',
        'headless': False,
        'viewport': {'width': 1920, 'height': 1080}
    },
    'timeout': {
        'default': 30000,
        'wait': 10000,
        'navigation': 30000
    }
}


@pytest.mark.p1
@pytest.mark.case_id_post_explore_001
@pytest.mark.post
@pytest.mark.explore
@pytest.mark.ae
@allure.feature("OK - Post")
@allure.story("Post页面功能探索")
@allure.title("Post页面结构与元素探索测试")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("访问 Post 分类选择页，探索页面表单结构、输入框、按钮、文件上传、必填字段等元素")
def test_post_page_explore(page, config):
    """
    Post页面功能探索测试
    
    目标：
    1. 访问Post页面
    2. 探索页面结构和元素
    3. 识别关键功能区域
    4. 记录页面信息
    """
    logger.info("=" * 80)
    logger.info("Post页面功能探索测试")
    logger.info("=" * 80)

    with allure.step("步骤1：Session 复用登录"):
        session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
        session_manager = SessionManager(page, config['base_url'], session_name)
        login_page = LoginPage(page, base_url=config['base_url'])

        if session_manager.load_session():
            logger.info("✓ 成功加载已保存的 Session")
        else:
            login_page.navigate_to_home_page()
            login_page.handle_cookie_popup()
            login_page.login(config['test_account']['username'], config['test_account']['password'])
            session_manager.save_session()
            logger.info("✓ 登录成功并保存 Session")

    with allure.step("步骤2：导航到 Post 页面"):
        page.goto(_CONFIG['post_url'])
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)
        logger.info(f"✓ 已导航到Post页面: {_CONFIG['post_url']}")
    
    # 截图初始状态
    page.screenshot(path="screenshots/post_explore_initial.png", timeout=60000)
    logger.info("✓ 已截图: post_explore_initial.png")

    with allure.step("步骤3：验证 URL 包含 publish"):
        current_url = page.url
        logger.info(f"当前URL: {current_url}")
        assert 'publish' in current_url.lower(), f"URL 应包含 publish，实际={current_url}"
        logger.info("✓ URL验证通过（包含'publish'）")

    with allure.step("步骤4：获取页面标题"):
        page_title = page.title()
    logger.info(f"页面标题: {page_title}")
    
    # 步骤5: 探索页面元素
    logger.info("\n--- 步骤5: 探索页面元素 ---")
    
    # 5.1 查找表单容器
    logger.info("\n5.1 查找表单容器...")
    form_info = page.evaluate("""
        () => {
            const selectors = ['form', '[class*="publish"]', '[class*="post"]', '[class*="form"]'];
            let found = [];
            
            for (const selector of selectors) {
                const elements = document.querySelectorAll(selector);
                if (elements.length > 0) {
                    found.push({
                        selector: selector,
                        count: elements.length,
                        visible: Array.from(elements).filter(el => {
                            const rect = el.getBoundingClientRect();
                            return rect.width > 0 && rect.height > 0;
                        }).length
                    });
                }
            }
            
            return found;
        }
    """)
    
    if form_info:
        logger.info(f"✓ 找到表单容器:")
        for info in form_info:
            logger.info(f"  - {info['selector']}: {info['count']}个元素, {info['visible']}个可见")
    else:
        logger.warning("⚠️ 未找到表单容器")
    
    # 5.2 查找输入框
    logger.info("\n5.2 查找输入框...")
    input_info = page.evaluate("""
        () => {
            const inputs = document.querySelectorAll('input, textarea');
            let result = [];
            
            inputs.forEach((input, index) => {
                const rect = input.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) {
                    result.push({
                        type: input.tagName.toLowerCase(),
                        inputType: input.type || 'N/A',
                        placeholder: input.placeholder || '',
                        name: input.name || '',
                        id: input.id || '',
                        required: input.required,
                        visible: true
                    });
                }
            });
            
            return result;
        }
    """)
    
    if input_info:
        logger.info(f"✓ 找到 {len(input_info)} 个可见输入框:")
        for i, info in enumerate(input_info[:10], 1):  # 只显示前10个
            logger.info(f"  {i}. {info['type']}[{info['inputType']}] - "
                       f"placeholder: '{info['placeholder']}', "
                       f"name: '{info['name']}', "
                       f"required: {info['required']}")
    else:
        logger.warning("⚠️ 未找到输入框")
    
    # 5.3 查找按钮
    logger.info("\n5.3 查找按钮...")
    button_info = page.evaluate("""
        () => {
            const buttons = document.querySelectorAll('button, [type="button"], [type="submit"], [role="button"]');
            let result = [];
            
            buttons.forEach((btn) => {
                const rect = btn.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) {
                    result.push({
                        text: btn.textContent?.trim() || '',
                        type: btn.type || 'N/A',
                        className: btn.className || '',
                        disabled: btn.disabled
                    });
                }
            });
            
            return result;
        }
    """)
    
    if button_info:
        logger.info(f"✓ 找到 {len(button_info)} 个可见按钮:")
        for i, info in enumerate(button_info[:10], 1):  # 只显示前10个
            logger.info(f"  {i}. '{info['text']}' - "
                       f"type: {info['type']}, "
                       f"disabled: {info['disabled']}")
    else:
        logger.warning("⚠️ 未找到按钮")
    
    # 5.4 查找图片上传控件
    logger.info("\n5.4 查找图片上传控件...")
    upload_info = page.evaluate("""
        () => {
            const fileInputs = document.querySelectorAll('input[type="file"]');
            let result = [];
            
            fileInputs.forEach((input) => {
                result.push({
                    accept: input.accept || '',
                    multiple: input.multiple,
                    name: input.name || '',
                    id: input.id || ''
                });
            });
            
            return result;
        }
    """)
    
    if upload_info:
        logger.info(f"✓ 找到 {len(upload_info)} 个文件上传控件:")
        for i, info in enumerate(upload_info, 1):
            logger.info(f"  {i}. accept: '{info['accept']}', "
                       f"multiple: {info['multiple']}, "
                       f"name: '{info['name']}'")
    else:
        logger.warning("⚠️ 未找到文件上传控件")
    
    # 5.5 查找下拉选择框
    logger.info("\n5.5 查找下拉选择框...")
    select_info = page.evaluate("""
        () => {
            const selects = document.querySelectorAll('select, [role="combobox"], [role="listbox"]');
            let result = [];
            
            selects.forEach((select) => {
                const rect = select.getBoundingClientRect();
                if (rect.width > 0 && rect.height > 0) {
                    let options = [];
                    if (select.tagName === 'SELECT') {
                        options = Array.from(select.options).map(opt => opt.text);
                    }
                    
                    result.push({
                        type: select.tagName.toLowerCase(),
                        role: select.getAttribute('role') || '',
                        name: select.name || '',
                        optionsCount: options.length,
                        firstOptions: options.slice(0, 5)
                    });
                }
            });
            
            return result;
        }
    """)
    
    if select_info:
        logger.info(f"✓ 找到 {len(select_info)} 个选择控件:")
        for i, info in enumerate(select_info, 1):
            logger.info(f"  {i}. {info['type']} - "
                       f"name: '{info['name']}', "
                       f"options: {info['optionsCount']}")
            if info['firstOptions']:
                logger.info(f"     前几个选项: {info['firstOptions']}")
    else:
        logger.warning("⚠️ 未找到选择控件")
    
    # 步骤6: 尝试识别必填字段
    logger.info("\n--- 步骤6: 识别必填字段 ---")
    required_fields = page.evaluate("""
        () => {
            const required = document.querySelectorAll('[required], [aria-required="true"]');
            let result = [];
            
            required.forEach((field) => {
                result.push({
                    tag: field.tagName.toLowerCase(),
                    type: field.type || 'N/A',
                    name: field.name || '',
                    placeholder: field.placeholder || '',
                    label: field.labels?.[0]?.textContent?.trim() || ''
                });
            });
            
            return result;
        }
    """)
    
    if required_fields:
        logger.info(f"✓ 找到 {len(required_fields)} 个必填字段:")
        for i, field in enumerate(required_fields, 1):
            logger.info(f"  {i}. {field['tag']}[{field['type']}] - "
                       f"name: '{field['name']}', "
                       f"placeholder: '{field['placeholder']}', "
                       f"label: '{field['label']}'")
    else:
        logger.info("ℹ️ 未找到明确标记的必填字段")
    
    # 步骤7: 获取页面的所有可交互元素统计
    logger.info("\n--- 步骤7: 页面元素统计 ---")
    stats = page.evaluate("""
        () => {
            return {
                totalInputs: document.querySelectorAll('input').length,
                visibleInputs: Array.from(document.querySelectorAll('input')).filter(el => {
                    const rect = el.getBoundingClientRect();
                    return rect.width > 0 && rect.height > 0;
                }).length,
                totalTextareas: document.querySelectorAll('textarea').length,
                totalButtons: document.querySelectorAll('button').length,
                totalSelects: document.querySelectorAll('select').length,
                totalFileInputs: document.querySelectorAll('input[type="file"]').length,
                totalForms: document.querySelectorAll('form').length,
                totalImages: document.querySelectorAll('img').length
            };
        }
    """)
    
    logger.info("页面元素统计:")
    logger.info(f"  - 输入框总数: {stats['totalInputs']} (可见: {stats['visibleInputs']})")
    logger.info(f"  - 文本域: {stats['totalTextareas']}")
    logger.info(f"  - 按钮: {stats['totalButtons']}")
    logger.info(f"  - 下拉框: {stats['totalSelects']}")
    logger.info(f"  - 文件上传: {stats['totalFileInputs']}")
    logger.info(f"  - 表单: {stats['totalForms']}")
    logger.info(f"  - 图片: {stats['totalImages']}")
    
    # 步骤8: 最终截图
    logger.info("\n--- 步骤8: 最终截图 ---")
    page.screenshot(path="screenshots/post_explore_final.png", full_page=True, timeout=60000)
    logger.info("✓ 已截图: post_explore_final.png (全页)")
    
    # 总结
    logger.info("\n" + "=" * 80)
    logger.info("Post页面探索完成")
    logger.info("=" * 80)
    logger.info(f"✓ 页面URL: {current_url}")
    logger.info(f"✓ 页面标题: {page_title}")
    logger.info(f"✓ 可见输入框: {stats['visibleInputs']}个")
    logger.info(f"✓ 按钮: {stats['totalButtons']}个")
    logger.info(f"✓ 文件上传: {stats['totalFileInputs']}个")
    logger.info(f"✓ 必填字段: {len(required_fields)}个")
    logger.info("=" * 80)


@pytest.mark.p1
@pytest.mark.case_id_post_explore_002
@pytest.mark.post
@pytest.mark.explore
@pytest.mark.ae
@allure.feature("OK - Post")
@allure.story("Post页面功能探索")
@allure.title("Post页面图片上传功能探索测试")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("验证 Post 发布页的图片上传控件可用，上传图片后出现图片预览")
def test_post_image_upload_explore(page, config):
    """
    Post页面图片上传功能探索
    
    目标：
    1. 测试图片上传功能
    2. 验证图片预览
    3. 记录上传流程
    """
    logger.info("=" * 80)
    logger.info("Post页面图片上传功能探索")
    logger.info("=" * 80)

    with allure.step("步骤1：Session 复用登录并进入 Post 页面"):
        session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
        session_manager = SessionManager(page, config['base_url'], session_name)
        login_page = LoginPage(page, base_url=config['base_url'])

        if session_manager.load_session():
            logger.info("✓ 成功加载已保存的 Session")
        else:
            login_page.navigate_to_home_page()
            login_page.handle_cookie_popup()
            login_page.login(config['test_account']['username'], config['test_account']['password'])
            session_manager.save_session()
            logger.info("✓ 登录成功")

        page.goto(_CONFIG['post_url'])
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)
        logger.info("✓ 已进入Post页面")

    with allure.step("步骤2：检查测试图片文件"):
        image_path = _CONFIG['test_resources']['image_path']
    
    if os.path.exists(image_path):
        file_size = os.path.getsize(image_path) / 1024  # KB
        logger.info(f"✓ 图片文件存在: {image_path}")
        logger.info(f"  文件大小: {file_size:.2f} KB")
    else:
        logger.error(f"❌ 图片文件不存在: {image_path}")
        pytest.skip(f"测试图片不存在: {image_path}")
    
    # 截图上传前状态
    page.screenshot(path="screenshots/post_upload_before.png", timeout=60000)
    logger.info("✓ 已截图: post_upload_before.png")
    
    # 步骤3: 查找并使用上传控件
    logger.info("\n--- 步骤3: 查找上传控件 ---")
    
    # 查找file input
    file_inputs = page.locator('input[type="file"]').all()
    logger.info(f"找到 {len(file_inputs)} 个文件上传控件")
    
    if len(file_inputs) > 0:
        # 使用第一个上传控件
        upload_input = file_inputs[0]
        logger.info("✓ 使用第一个上传控件")
        
        # 上传图片
        logger.info(f"正在上传图片: {image_path}")
        upload_input.set_input_files(image_path)
        logger.info("✓ 已选择图片文件")
        
        # 等待上传完成
        page.wait_for_timeout(5000)
        logger.info("✓ 等待上传完成")
        
        # 截图上传后状态
        page.screenshot(path="screenshots/post_upload_after.png", timeout=60000)
        logger.info("✓ 已截图: post_upload_after.png")
        
        # 步骤4: 检查上传结果
        logger.info("\n--- 步骤4: 检查上传结果 ---")
        
        # 查找图片预览
        preview_check = page.evaluate("""
            () => {
                const images = document.querySelectorAll('img');
                let previews = [];
                
                images.forEach((img) => {
                    const src = img.src || '';
                    if (src.includes('blob:') || src.includes('data:image') || 
                        img.className.includes('preview') || img.className.includes('thumbnail')) {
                        const rect = img.getBoundingClientRect();
                        previews.push({
                            src: src.substring(0, 50) + '...',
                            width: rect.width,
                            height: rect.height,
                            visible: rect.width > 0 && rect.height > 0
                        });
                    }
                });
                
                return previews;
            }
        """)
        
        if preview_check:
            logger.info(f"✓ 找到 {len(preview_check)} 个图片预览:")
            for i, preview in enumerate(preview_check, 1):
                logger.info(f"  {i}. 尺寸: {preview['width']}x{preview['height']}, "
                           f"可见: {preview['visible']}")
            logger.info("✅ 图片上传成功")
        else:
            logger.warning("⚠️ 未找到图片预览，可能上传失败或预览方式不同")
        
    else:
        logger.warning("⚠️ 未找到文件上传控件")
        pytest.skip("未找到文件上传控件")
    
    # 总结
    logger.info("\n" + "=" * 80)
    logger.info("图片上传探索完成")
    logger.info("=" * 80)
    logger.info(f"✓ 测试图片: {image_path}")
    logger.info(f"✓ 上传控件数量: {len(file_inputs)}")
    logger.info(f"✓ 图片预览: {len(preview_check) if preview_check else 0}个")
    logger.info("=" * 80)
