# 卡片完整内容读取：text= 层级误判陷阱

## 问题背景

在读取项目卡片的完整内容（如预算、周期）时，常见的写法：

```python
card_area = page.locator(f"text={project_name}").locator("xpath=ancestor::*[2]")
text = card_area.inner_text()
```

会只返回项目名称，不含描述/周期/预算。

---

## 根本原因

### Playwright `text=` 选择器的真实行为

`text=value` **不是**定位到包含该文字的最内层元素（文字节点的直接父元素），而是匹配**所有包含该文字内容的元素中最外层的那个**。

以 Optell 项目卡片的 DOM 结构为例：

```
generic [cursor=pointer]          ← 完整卡片（最外层）
  generic [class*=cardHeader]     ← header 区域
    generic: "项目名称文字"        ← 最内层名称元素
    img "more"
  generic                         ← body 区域（描述/周期/预算）
    generic: "项目描述..."
    generic: "2025-12-01 ~ 2025-12-25"
    generic: "USD:0"
```

当执行 `page.locator("text=项目名称文字")` 时：

- `[class*=cardHeader]` 包含该文字 ✓
- 完整卡片容器也包含该文字 ✓  
- Playwright 返回**最匹配（最外层有意义）的那个元素**：`[class*=cardHeader]`

从 `[class*=cardHeader]` 开始数层级：

```
ancestor::*[1] → 完整卡片 [cursor=pointer]
ancestor::*[2] → 卡片列表容器（多个卡片的父 div）
```

所以 `ancestor::*[2]` 定位到**卡片列表容器**，`inner_text()` 返回整个列表的所有项目名，字符串截断后看起来只有项目名。

---

## 正确写法

### 核心原则：语义 class + 相对导航

```python
# 1. 用有语义的 CSS class 定位到 header（确定的起始点）
card_header = page.locator("[class*='cardHeader']").filter(has_text=project_name)
expect(card_header).to_be_visible(timeout=5000)

# 2. 往上一级（xpath=..）= 完整卡片容器
full_card = card_header.locator("xpath=..")
text = full_card.inner_text()   # 包含名称 + 描述 + 周期 + 预算
```

### 为什么这样可靠

- `[class*='cardHeader']` 由 CLI snapshot 确认，是确定的卡片 header 类名
- `filter(has_text=project_name)` 精确锁定目标卡片的 header
- `xpath=..` 是**相对导航**，不依赖层级数字，header 的父节点永远是完整卡片

---

## 通用规则

| 场景 | 推荐写法 |
|------|---------|
| 读取卡片/行完整内容 | `card_header.locator("xpath=..")` |
| 读取卡片特定子区域 | `card_header.locator("xpath=..").locator("[class*='body']")` |
| 验证某文字在卡片内 | `expect(card_header.locator("xpath=..").get_by_text("USD:0")).to_be_visible()` |
| **禁止** | `page.locator(f"text={name}").locator("xpath=ancestor::*[n]")` |

---

## 识别信号

以下情况极可能触发此陷阱：

1. 断言 `assert "USD" in card_text` 失败，`card_text` 只含项目名
2. 断言 `assert "暂无周期" in text` 失败，`text` 只含项目名
3. 断言 `assert "2025-" in period_text` 失败，`period_text` 只含项目名

**快速诊断**：`print(repr(card_text))` — 如果结果只有一个字符串（项目名），说明层级错误。

---

## 修复检查清单

- [ ] 找到读取卡片内容的代码
- [ ] 将 `page.locator(f"text={name}").locator("xpath=ancestor::*[n]")` 全部替换
- [ ] 改为 `page.locator("[class*='cardHeader']").filter(has_text=name).locator("xpath=..")`
- [ ] 验证 `inner_text()` 结果包含预期的子内容（描述/周期/预算等）
