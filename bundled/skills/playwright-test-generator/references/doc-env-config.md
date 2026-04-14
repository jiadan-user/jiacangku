# MD 文档环境配置规范

> 用于 playwright-test-generator skill 解析测试环境配置

---

## 格式要求

在 MD 测试用例文档的**头部**（标题后、用例前）必须包含「测试环境配置」块：

```markdown
## 测试环境配置（必填）

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | us | ae/us/hk/br 等 |
| 基础URL | https://us.58v5.cn | 测试站点地址 |
| 站点名称 | 美国站 | 可选，用于日志展示 |
| 角色 | seller | seller/buyer |
| 账号名称 | dc_seller_us | 用于 session 命名，必须唯一 |
| 测试账号 | test_seller@example.com | 登录邮箱 |
| 测试密码 | Test@123456 | 登录密码 |

**说明**：录制和生成阶段必须使用上述账号密码；生成的脚本内包含此配置，运行时直接使用。
```

---

## 字段说明

| 字段 | 必填 | 说明 | 示例 |
|------|------|------|------|
| 站点 | ✅ | 站点代码 | ae / us / hk / br |
| 基础URL | ✅ | 测试站点地址 | https://us.58v5.cn |
| 站点名称 | 否 | 站点中文名，用于日志展示 | 美国站 / 阿联酋站 |
| 角色 | ✅ | 测试角色 | seller / buyer |
| 账号名称 | ✅ | 账号标识，用于 session 命名，必须全局唯一 | dc_seller_us |
| 测试账号 | ✅ | 登录邮箱或用户名 | test_seller@example.com |
| 测试密码 | ✅ | 登录密码 | Test@123456 |

---

## 解析规则

### 表格定位

1. 查找二级标题 `## 测试环境配置`（可选「必填」等后缀）
2. 提取该标题下的第一个表格
3. 按「字段 - 值」映射解析

### 字段映射

| MD 字段名 | 映射到 `_CONFIG` | 说明 |
|-----------|------------------|------|
| 站点 | `site` | 站点代码 |
| 基础URL | `base_url` | 站点地址 |
| 站点名称 | `site_name` | 可选，默认为站点代码大写 |
| 角色 | `role` | seller/buyer |
| 账号名称 | `user_name` | 用于 session 命名 |
| 测试账号 | `test_account.username` | 登录账号 |
| 测试密码 | `test_account.password` | 登录密码 |

### 默认值

| 字段 | 默认值 |
|------|--------|
| `locale` | 根据站点推导（us→en-US, ae→en-AE, hk→zh-HK） |
| `currency` | 根据站点推导（us→USD, ae→AED, hk→HKD） |
| `browser.type` | chromium |
| `browser.headless` | false |
| `browser.viewport` | {"width": 1920, "height": 1080} |
| `timeout.*` | {"default": 30000, "wait": 10000, "navigation": 30000} |

---

## 生成的 `_CONFIG` 结构

```python
_CONFIG = {
    "site": "us",                    # 来自「站点」
    "site_name": "美国站",            # 来自「站点名称」
    "role": "seller",                # 来自「角色」
    "user_name": "dc_seller_us",     # 来自「账号名称」
    "base_url": "https://us.58v5.cn",  # 来自「基础URL」
    "test_account": {
        "username": "test_seller@example.com",  # 来自「测试账号」
        "password": "Test@123456"               # 来自「测试密码」
    },
    "locale": "en-US",               # 根据站点推导
    "currency": "USD",               # 根据站点推导
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
```

---

## 错误处理与主动询问

| 情况 | 处理方式 |
|------|----------|
| 缺少「测试环境配置」块 | 询问用户："文档中未找到「测试环境配置」块，请问：<br>1) 无需登录，直接测试公开页面？<br>2) 需要登录，请提供站点、账号、密码？" |
| 必填字段缺失 | 列出缺失字段，询问用户补充 |
| 测试账号/密码为空或"无" | 询问用户："检测到测试账号为空，请问是否无需登录？" |
| 表格格式错误 | 停止，提示检查表格格式 |

**无需登录场景的处理**：
- 用户确认无需登录 → 生成 `_CONFIG` 时：
  - `role`: "visitor"
  - `user_name`: "guest"
  - `test_account`: None
- 跳过阶段3的登录步骤，直接录制业务操作

---

## 示例

完整示例见：`assets/test-case-example.md`
