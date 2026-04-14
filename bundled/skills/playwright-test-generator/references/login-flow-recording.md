# 登录流程录制指南（高频违规防范）

## 为什么登录流程必须录制

手写登录代码会遗漏以下关键信息，这些信息只有通过 playwright-cli 录制才能观察到：

| 手写时的盲点 | 实际录制才能确认 |
|------------|----------------|
| 页面是否自动弹出登录 Modal | 导航到目标 URL 后拍快照才可见 |
| Cookie 弹窗是否出现及时机 | 只在真实浏览器中出现 |
| "Continue" 按钮是否被内部覆层遮挡 | ValidAccount overlay 只在特定状态出现 |
| 导航 URL 是否 404 或跳转 | 需要实际导航确认 |

## 强制规定

1. 登录流程**必须通过 playwright-cli 命令完整录制一遍**，不允许凭经验手写。
2. 录制时覆盖完整链路：
   ```
   导航到目标 URL (playwright-cli open)
     → 获取快照 (playwright-cli snapshot)
     → Cookie 弹窗处理 (playwright-cli click)
     → 登录入口（自动弹出？还是需要点击按钮？）
     → 邮箱输入 (playwright-cli fill) → Continue 按钮 (playwright-cli click)
     → 密码输入 (playwright-cli fill) → Login 按钮 (playwright-cli click)
     → 登录成功后 URL 变化
   ```
3. 录制完成后，将登录步骤封装进 `LoginPage`，配合 `SessionManager` 做 session 复用。

## 标准 `_ensure_logged_in` 模板

> ⚠️ **优先遵守项目 SCRIPT_SPEC.md**：若项目的 SCRIPT_SPEC.md 中有 config 结构、SessionManager 用法、账号来源等规范，**必须以 SCRIPT_SPEC 为准**，使用 `config['test_account']['username']`、`config['base_url']` 等，禁止硬编码。以下模板中的占位符（BASE_URL、USERNAME、PASSWORD、SESSION_NAME）应替换为从 config 读取。

基于录制结果填充以下模板，不得在未录制的情况下填充具体实现：

```python
def _ensure_logged_in(page, config):
    # 从 config 读取（若 SCRIPT_SPEC 有 config 规范，必须以 config 为准，禁止硬编码）
    base_url = config.get('base_url') or BASE_URL
    test_account = config.get('test_account') or {}
    username = test_account.get('username') or USERNAME
    password = test_account.get('password') or PASSWORD
    site, role, account_name = config.get('site'), config.get('role'), config.get('user_name')
    session_name = f"{site}_{role}_{account_name}" if all([site, role, account_name]) else SESSION_NAME

    session_manager = SessionManager(page, base_url, session_name=session_name)

    if session_manager.load_session():
        page.goto(TARGET_URL)  # 录制确认的目标页 URL，或 base_url + path
        page.wait_for_load_state("domcontentloaded", timeout=30000)
        login_page = LoginPage(page)
        login_page.handle_cookie_popup()          # 录制时观察到的 Cookie 弹窗
        if not page.locator('text="Log in / Register"').is_visible():
            return  # session 有效，无需重新登录

    # 导航到真实目标页（录制确认的 URL，非推测）
    page.goto(TARGET_URL, timeout=30000)
    page.wait_for_load_state("domcontentloaded", timeout=30000)
    login_page = LoginPage(page)
    login_page.handle_cookie_popup()

    # 判断登录 Modal 是否已自动弹出（录制确认的逻辑）
    if not page.locator("input[placeholder='placeholder']").is_visible():
        login_page.click_login_register_button()

    login_page.input_email(username)   # 使用从 config 读取的 username
    login_page.click_continue_button()
    login_page.input_password(password)  # 使用从 config 读取的 password
    login_page.click_login_button()
    session_manager.save_session()
```

## LoginPage 方法必须限定 Modal 容器

登录弹窗内的操作（邮箱输入、Continue、密码、Login）全部需要在 Modal 容器内定位，
避免与主页面同名元素冲突（详见 `sticky-header-click.md`）：

```python
class LoginPage(BasePage):
    LOGIN_MODAL = "[role='dialog'][aria-modal='true']"

    def _modal(self):
        return self.page.locator(self.LOGIN_MODAL)

    def input_email(self, email: str):
        modal = self._modal()
        modal.wait_for(state="visible", timeout=10000)
        modal.locator(self.EMAIL_INPUT).fill(email)

    def click_continue_button(self):
        modal = self._modal()
        modal.wait_for(state="visible", timeout=10000)
        btn = modal.locator(self.CONTINUE_BUTTON)
        btn.wait_for(state="visible", timeout=10000)
        btn.click()
```

## CLI 录制时的检查点

录制登录流程时，依次确认以下快照节点已记录：

- [ ] `browser_navigate` 到目标 URL 后立即 `browser_snapshot`（确认 Cookie 弹窗/登录Modal 状态）
- [ ] Cookie 弹窗出现时记录其选择器和关闭操作
- [ ] 登录 Modal 的容器选择器（`role=dialog` 或具体类名）
- [ ] 邮箱输入框的完整 ref 和 placeholder
- [ ] Continue 按钮进入"可点击"状态的时机（有无 loading/disabled 状态）
- [ ] 密码输入框出现的时机（是否在 Continue 点击后异步渲染）
- [ ] Login 按钮状态（disabled → enabled 的触发条件）
- [ ] 登录成功后的 URL 或页面状态变化
