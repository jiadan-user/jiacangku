# Playwright Test Generator

从 Markdown 测试用例文档生成 Playwright Python 测试脚本，通过 playwright-cli 录制真实浏览器交互并转换为 Python 代码。**录制过程中严格验证预期结果，发现 bug 则记录到报告并跳过脚本生成**。

## 核心特性

- ✅ **100% 依赖真实录制**：使用 playwright-cli 录制浏览器交互，消除 AI 幻觉
- ✅ **实时验证预期结果**：录制过程中严格对照用例文档验证，发现 bug 立即记录
- ✅ **智能跳过失败用例**：验证失败的用例不生成脚本，只记录 bug 和截图
- ✅ **自动 Bug 报告**：每批次自动生成或追加 bug 清单（仅包含用例编号、复现步骤、截图）
- ✅ **5 阶段工作流**：解析配置 → CLI 录制+验证 → Python 生成 → Bug 报告 → 自测调试
- ✅ **严格证明存档**：每个通过验证的用例输出带 ref 和 JavaScript 代码的证明存档
- ✅ **自动批次管理**：每批最多处理 5 个用例，防止上下文超载

## 使用场景

当用户：
- 提供 Markdown 格式的测试用例文档
- 需要生成 UI 自动化测试脚本
- 需要在录制过程中发现产品 bug
- 提到 Playwright 测试开发、CLI 录制或脚本生成

## 依赖项

```bash
# Python 依赖
pip install pytest playwright allure-pytest

# Playwright 浏览器
playwright install chromium

# playwright-cli（必须全局安装）
npm install -g @playwright/cli@latest
```

## 工作流程

1. **阶段 1：解析与批次规划** - 从 Markdown 文档提取配置和预期结果，将用例分批（每批 ≤5 个）
2. **阶段 2：CLI 录制+验证** - 使用 `playwright-cli` 命令录制，每步执行后立即验证预期结果
   - ✅ 验证通过：输出证明存档，准备生成代码
   - ❌ 验证失败：截图、记录 bug、跳过代码生成
3. **阶段 3：Python 代码生成** - 仅针对通过验证的用例生成 Python Page Object + Test Case
4. **阶段 4：Bug 报告生成** - 如有失败用例，生成或追加 bug 清单（简洁格式）
5. **阶段 5：自测调试** - 运行 `pytest --collect-only` 和 `pytest` 验证生成的代码

## 技术特点

- **CLI 命令**：标准命令行工具，易于集成和自动化
- **YAML 快照**：结构清晰的元素引用格式
- **Token 友好**：简洁输出，降低上下文消耗
- **CI/CD 就绪**：可直接用于持续集成流程
- **实时验证**：录制过程中验证预期结果，及时发现 bug

## 最终交付

每个批次完成后交付：

### 1. 测试脚本（仅 PASSED 用例）
- `test_cases/test_module.py` - 通过验证的测试用例
- `pages/module_page.py` - Page Object 类（如需要）

### 2. Bug 清单报告（如有 FAILED 用例）
- `bug-report.md` - 简洁的 bug 清单（追加模式）
- `bug-tc{编号}.png` - 问题截图

### Bug 报告格式示例

```markdown
## TC006: 输入关键词点击 Search 执行搜索

**复现步骤**：
1. 打开浏览器，访问 https://example.com/search
2. 在搜索框输入 "Toyota"
3. 点击 "Search" 按钮

**预期结果**：页面跳转至搜索结果页，URL 包含 q=Toyota

**实际结果**：页面未跳转，URL 仍为 /search，搜索框清空但无任何反应

**问题截图**：`bug-tc006.png`

---
```

## 移动端支持

移动端测试脚本生成请使用专门的 skill：
- `playwright-mobile-test-generator` - 支持移动端设备配置、tap/swipe 等移动端 API

## 参考文档

核心工作流：
- `references/cli-recording-guide.md` - CLI 录制详细指南
- `references/result-validation-guide.md` - 预期结果验证指南（新增）
- `references/bug-report-template.md` - Bug 清单报告模板（新增）
- `references/enforcement-gates.md` - 证明存档格式定义
- `references/js-to-py-conversion.md` - JavaScript 到 Python 转换规则

特定场景：
- `references/login-flow-recording.md` - 登录流程录制防雷指南
- `references/search-input-debounce.md` - 搜索输入防抖处理
- `references/sticky-header-click.md` - 粘性头部遮挡处理

配置工具：
- `references/doc-env-config.md` - 测试环境配置解析
- `references/element-location-strategies.md` - 元素定位策略
- `references/auto-debug-strategy.md` - 自动调试策略
