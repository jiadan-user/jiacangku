# OK UI 自动化用例编写规范

## 1. 适用范围

这份规范用于：

- 团队成员新增或重写 `bundled/ok_autotest_ui_pc/test_cases/` 下的自动化用例
- AI 根据规范直接生成可落到当前项目的测试脚本
- Code Review 时判断新用例是否符合当前 skill 和框架约定

默认原则：

- 优先复用现有 `page`、`config`、目录级 `conftest`
- 优先复用现有 `pages/`、`utils/`、已有 helper
- 新增脚本必须能通过 `doctor`、`collect-only`、`run --dry-run`

## 2. 文件放置规则

- 页面对象放：`bundled/ok_autotest_ui_pc/pages/`
- 测试工具放：`bundled/ok_autotest_ui_pc/utils/`
- 业务用例放：`bundled/ok_autotest_ui_pc/test_cases/<module>/`
- 目录级说明、模板、治理文档放：`bundled/ok_autotest_ui_pc/docs/`

新增测试文件命名要求：

- 文件名必须以 `test_` 开头，以 `.py` 结尾
- 文件名要表达“模块 + 功能”，不要使用 `test_temp.py`、`test_new.py`、`test_demo.py`
- 批次型脚本允许使用 `batch` 命名，但要表达批次含义，例如 `test_detail_page_share_batch2.py`

## 3. 标准文件骨架

每个新测试文件默认都应包含：

1. 文件头说明
2. 标准 imports
3. `_CONFIG`
4. 可选 helper / fixture
5. 测试类或测试函数

推荐顺序：

```python
"""
模块说明
"""
import pytest
import allure

from pages.xxx_page import XxxPage
from utils.logger import setup_logger

logger = setup_logger()

_CONFIG = {...}

# helper / fixture

# tests
```

## 4. `_CONFIG` 规则

### 4.1 必备字段

默认要求 `_CONFIG` 至少包含以下字段：

```python
_CONFIG = {
    "site": "us",
    "base_url": "https://example.com",
    "browser": {
        "type": "chromium",
        "headless": False,
        "viewport": {"width": 1920, "height": 1080},
    },
    "timeout": {
        "default": 30000,
    },
}
```

常用扩展字段：

- `site_name`
- `role`
- `user_name`
- `test_account`
- `target_page`
- `publish_url`
- `locale`
- `currency`
- `accounts`
- `data`

### 4.2 配置来源优先级

运行时配置按以下优先级合并：

1. 测试文件中的 `_CONFIG`
2. `bundled/ok_autotest_ui_pc/config/runtime_overrides.yaml`
3. 环境变量覆盖，例如 `OK_UI__...`、`HEADLESS`

要求：

- 测试文件里保留可读、可运行的默认 `_CONFIG`
- 本地差异配置放到 `runtime_overrides.yaml`
- 不要在测试代码里直接写“切换本地环境”的临时分支

### 4.3 允许没有 `_CONFIG` 的例外

只有目录级 `conftest.py` 明确提供 `default_config` 的模块，才允许测试文件不声明 `_CONFIG`。

当前已知例外：

- `test_cases/publish_job/`

除这个例外外，AI 生成新用例时必须显式生成 `_CONFIG`。

## 5. 标准 imports

默认 imports：

```python
import pytest
import allure

from utils.logger import setup_logger
```

按需 imports：

- 页面对象：`from pages.xxx_page import XxxPage`
- 会话管理：`from utils.session_manager import SessionManager`
- 正则：`import re`
- 时间戳：`from datetime import datetime`

要求：

- 只导入实际使用的对象
- 禁止把页面对象、数据库操作、HTTP 调用全部塞在同一文件头里

## 6. `pytest.mark` 与 `allure` 规则

### 6.1 每条测试必备标记

每条测试至少包含：

- 一个优先级：`@pytest.mark.p0 / p1 / p2 / p3`
- 一个稳定 `case_id`：`@pytest.mark.case_id_xxx`
- 一个站点标记：`@pytest.mark.us / sg / ae / au`
- 一个模块标记：如 `@pytest.mark.wallet`、`@pytest.mark.job_publish`
- `allure.feature(...)`
- `allure.story(...)`
- `allure.title(...)`

推荐结构：

```python
@pytest.mark.case_id_wallet_xxx
@pytest.mark.p1
@pytest.mark.wallet
@pytest.mark.ae
@allure.feature("OK")
@allure.story("钱包-提现")
@allure.title("输入非法金额时应提示校验错误")
def test_xxx(page, config):
    ...
```

### 6.2 命名要求

- `case_id` 要稳定，不要带时间戳
- `allure.story` 表达功能域，不要写成一句完整测试步骤
- `allure.title` 直接表达断言目标

## 7. Fixture 复用规则

### 7.1 默认规则

新用例默认直接复用全局 fixture：

- `config`
- `page`
- `reset_page_state_after_test`
- `geolocation_page`

不要为了“看起来完整”就在每个测试文件里重复声明 `config`、`page`。

### 7.2 允许自定义 fixture 的场景

只有下列场景允许新增目录级或文件级 fixture：

- 必须复用一次登录/会话准备
- 必须做目录级 flaky / 截图治理
- 必须注入地理位置、特殊权限、特殊上下文
- 必须做明确的前置数据准备或清理

要求：

- fixture 名称表达真实职责
- 状态性逻辑放 fixture / helper，不放到测试函数主体
- 如需目录级 `conftest.py`，文件头必须写“自定义原因”

### 7.3 不推荐模式

- 在测试函数中临时写登录流程
- 在测试函数中直接改 Redis / SQL / 外部状态
- 在测试函数中复制一整段目录级 setup/teardown

## 8. Page Object 使用边界

Page Object 负责：

- 选择器定位
- 单步动作
- 轻量状态读取
- 通用页面级等待

Page Object 不负责：

- 大段业务断言编排
- 跨页面流程编排
- 大量外部副作用
- 为单个测试硬编码一次性逻辑

要求：

- 一个 Page 文件只承载一个页面或一个清晰区块
- 超过约 `800-1000` 行时，优先考虑按页面区块拆分
- 复杂业务流放测试 helper，不要继续膨胀 Page 文件
- `LoginPage` 构造器可传可选参数 `base_url`：供后续无参 `navigate_to_home_page()` 时打开**对应站点**；未传时内部默认美国站基址。多站点用例中需与 `_CONFIG['base_url']` 一致。

## 9. 等待与断言规则

### 9.1 首选等待方式

优先级从高到低：

1. `expect(...)`
2. `locator.wait_for(...)`
3. `page.wait_for_url(...)`
4. `BasePage.wait_for_key_section(...)`
5. `BasePage.dismiss_modal_dialogs(...)`

### 9.2 禁止模式

AI 生成新用例时禁止新增裸 `page.wait_for_timeout()`。

允许保留的唯一例外：

- 动画收尾
- 防抖输入
- 浏览器自身过渡

例外要求：

- 单次默认不超过 `300ms`
- 行内写注释说明原因

合法例子：

```python
page.wait_for_timeout(200)  # 等待筛选面板收起动画完成，避免点击穿透
```

非法例子：

```python
page.wait_for_timeout(3000)
page.wait_for_timeout(5000)
```

### 9.3 断言要求

- 一个测试只验证一个清晰目标
- 断言失败信息要说明“期望”和“实际”
- 优先断言用户可见结果，不优先断言内部实现细节

## 10. 状态与副作用规则

要求：

- 登录、Session、Cookie、页面恢复统一收敛到 fixture/helper
- 外部副作用动作必须显式命名，且能看出开关点
- 禁止“监听 console 然后隐式改数据库”这类新模式继续扩散

新增副作用 helper 时，命名必须清晰，例如：

- `_prepare_bound_bank_account()`
- `_reset_withdrawal_lock_if_needed()`
- `_ensure_logged_in_session()`

不要使用：

- `_do_fix()`
- `_repair_state()`
- `_handle_issue()`

## 11. AI 生成流程

AI 新生成用例时必须执行下面流程：

1. 先读本规范
2. 再选用 `docs/templates/` 中最接近的模板
3. 尽量复用已有 Page / helper / fixture
4. 生成后执行自检

AI 生成时必须避免：

- 重新发明目录级 `conftest`
- 复制已有大段登录流程
- 新增长时间 `wait_for_timeout`
- 在 Page 文件里堆积一次性断言

## 12. 生成后自检

新增或修改用例后，至少执行：

```bash
cd <skill_root>/bundled/ok_autotest_ui_pc
./venv/bin/python -m tooling.ok_test doctor
./venv/bin/pytest --collect-only -q -p no:rerunfailures -o addopts=
```

如果要确认筛选映射，再执行：

```bash
cd <skill_root>
python3 scripts/ok_test.py run --path test_cases/<your_module>/<your_file>.py --dry-run
```

## 13. Review 清单入口

提交前必须再对照：

- `bundled/ok_autotest_ui_pc/docs/test-case-review-checklist.md`
- `bundled/ok_autotest_ui_pc/docs/stability-remediation-plan.md`

模板入口：

- `bundled/ok_autotest_ui_pc/docs/templates/standard-flow-template.py`
- `bundled/ok_autotest_ui_pc/docs/templates/stateful-session-template.py`
- `bundled/ok_autotest_ui_pc/docs/templates/component-batch-template.py`
