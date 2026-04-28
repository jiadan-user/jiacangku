"""
保存登录状态工具
手动登录一次后保存 storage state，后续 pytest 可复用（见 test_cases/conftest.py 的 `page` fixture）。

默认写入本目录 `auth_state.json`；也可用环境变量 `MARKETPLACE_AUTH_STATE_OUT` 指定路径。
"""
import os
from pathlib import Path

from playwright.sync_api import sync_playwright


def save_login_state():
    """
    手动登录并保存 storage state

    使用方法：
    1. 在 ok_autotest_ui_pc 根目录执行: python3 test_cases/marketplace_post/save_auth_state.py
    2. 在打开的浏览器中手动完成登录（含 SMS 时用手机完成验证）
    3. 回到终端按 Enter 保存状态
    """
    out = os.environ.get("MARKETPLACE_AUTH_STATE_OUT", "").strip()
    storage_file = Path(out) if out else Path(__file__).resolve().parent / "auth_state.json"
    base = (os.environ.get("MARKETPLACE_BASE_URL") or "https://aepub.58v5.cn").rstrip("/")
    start_url = f"{base}/biz/en/publish/classified"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("正在打开发布页面...")
        page.goto(start_url)
        
        print("\n" + "="*60)
        print("请在浏览器中手动完成登录")
        print("完成后请在终端按Enter键保存登录状态...")
        print("="*60 + "\n")
        
        input("按Enter继续...")
        
        storage_file.parent.mkdir(parents=True, exist_ok=True)
        context.storage_state(path=str(storage_file))
        print(f"\n✅ 登录状态已保存到: {storage_file.resolve()}")
        print("后续跑测: 同目录下存在 auth_state.json 时，conftest 会自动注入；或设置 MARKETPLACE_STORAGE_STATE=该路径")
        
        browser.close()


if __name__ == "__main__":
    save_login_state()
