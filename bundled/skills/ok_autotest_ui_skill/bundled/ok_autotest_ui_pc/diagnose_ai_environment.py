#!/usr/bin/env python3
"""
AI 模块测试环境诊断脚本
用于检查测试环境问题并提供修复建议
"""
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from playwright.sync_api import sync_playwright
import json

def diagnose_environment():
    """诊断测试环境"""
    print("=" * 80)
    print("AI 模块测试环境诊断")
    print("=" * 80)
    print()
    
    issues = []
    suggestions = []
    
    with sync_playwright() as p:
        # 1. 测试浏览器启动
        print("[1/5] 检查浏览器启动...")
        try:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = context.new_page()
            print("✅ 浏览器启动成功")
        except Exception as e:
            print(f"❌ 浏览器启动失败: {e}")
            issues.append("浏览器启动失败")
            suggestions.append("运行: playwright install chromium")
            return
        
        # 2. 测试页面访问
        print("\n[2/5] 检查页面访问...")
        try:
            page.goto("https://aepub.58v5.cn/biz/en/publish/front", timeout=30000)
            page.wait_for_load_state("domcontentloaded", timeout=15000)
            print(f"✅ 页面访问成功: {page.url}")
        except Exception as e:
            print(f"❌ 页面访问失败: {e}")
            issues.append("无法访问测试页面")
            suggestions.append("检查网络连接和VPN设置")
            browser.close()
            return
        
        # 3. 检查页面元素
        print("\n[3/5] 检查页面元素...")
        
        # 检查 Jobs 类目按钮
        print("  检查 Jobs 类目按钮...")
        jobs_found = False
        jobs_selector = None
        
        # 尝试多种定位方式
        selectors_to_try = [
            ('span:has-text("Jobs")', 'span标签包含"Jobs"文本'),
            ('button:has-text("Jobs")', 'button标签包含"Jobs"文本'),
            ('a:has-text("Jobs")', 'a标签包含"Jobs"文本'),
            ('[data-category="Jobs"]', 'data-category属性'),
            ('text=Jobs', 'Playwright text选择器'),
            ('.category-item:has-text("Jobs")', 'category-item类包含"Jobs"'),
        ]
        
        for selector, desc in selectors_to_try:
            try:
                element = page.locator(selector).first
                if element.is_visible(timeout=2000):
                    print(f"    ✅ 找到: {desc} -> {selector}")
                    jobs_found = True
                    jobs_selector = selector
                    break
            except:
                print(f"    ❌ 未找到: {desc}")
        
        if not jobs_found:
            print("  ⚠️  无法找到 Jobs 类目按钮")
            issues.append("Jobs 类目按钮定位失败")
            
            # 获取页面所有文本内容
            print("\n  页面上所有包含'Job'的文本:")
            try:
                all_text = page.content()
                if 'Job' in all_text or 'job' in all_text:
                    print("    ✅ 页面包含'Job'相关文本")
                else:
                    print("    ❌ 页面不包含'Job'相关文本")
            except:
                pass
            
            suggestions.append("更新 pages/ai_publish_job_page.py 中的 click_jobs_category() 方法的定位器")
        
        # 4. 测试登录状态
        print("\n[4/5] 检查登录状态...")
        try:
            # 检查是否有登录按钮
            login_button = page.locator('text=/Log in|Register|Sign in/i').first
            if login_button.is_visible(timeout=2000):
                print("  ⚠️  未登录状态")
                issues.append("需要登录")
                suggestions.append("确保测试账号 yangyang100@58.com 可用")
            else:
                print("  ✅ 可能已登录")
        except:
            print("  ✅ 可能已登录（未找到登录按钮）")
        
        # 5. 生成诊断报告
        print("\n[5/5] 生成页面快照...")
        try:
            screenshot_path = project_root / "reports" / "screenshots" / "diagnosis.png"
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"  ✅ 页面截图已保存: {screenshot_path}")
        except Exception as e:
            print(f"  ⚠️  截图保存失败: {e}")
        
        # 保存页面HTML
        try:
            html_path = project_root / "reports" / "screenshots" / "diagnosis.html"
            html_path.write_text(page.content(), encoding='utf-8')
            print(f"  ✅ 页面HTML已保存: {html_path}")
        except Exception as e:
            print(f"  ⚠️  HTML保存失败: {e}")
        
        browser.close()
    
    # 输出诊断总结
    print("\n" + "=" * 80)
    print("诊断总结")
    print("=" * 80)
    
    if not issues:
        print("✅ 未发现问题，环境配置正常")
    else:
        print(f"❌ 发现 {len(issues)} 个问题:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    
    if suggestions:
        print(f"\n💡 修复建议:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")
    
    # 生成修复脚本
    if jobs_selector and jobs_selector != 'span:has-text("Jobs")':
        print(f"\n📝 建议更新定位器:")
        print(f"   旧定位器: self.page.locator('span').filter(has_text='Jobs').click()")
        print(f"   新定位器: self.page.locator('{jobs_selector}').click()")
    
    print()


if __name__ == "__main__":
    try:
        diagnose_environment()
    except KeyboardInterrupt:
        print("\n\n诊断被用户中断")
    except Exception as e:
        print(f"\n\n诊断过程出错: {e}")
        import traceback
        traceback.print_exc()
