# OK.com AE站 - 首页底部公共跳转区域 - 测试用例

> **生成时间**: 2026-04-02  
> **测试站点**: AE站 (https://ae.ok.com)  
> **测试范围**: 首页底部 Footer 公共区域（About Us、Help、Cookie、App 下载等）  
> **总用例数**: 32条  
> **可自动化**: 28条 (88%)  
> **分析报告**: web-qa-brain/OK.com-首页底部公共区域-测试分析报告-20260402.md

---

## 测试环境配置

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | ae | 阿联酋站 |
| 基础URL | https://ae.ok.com | 测试站点地址 |
| 站点名称 | 阿联酋站 (AE OK.com) | 可选 |
| 角色 | visitor | 访客用户（主要测试） |
| 账号名称 | ae_visitor_footer | 用于 session 命名 |
| 测试账号 | shenchang@58.com | 仅权限对比用例需要 |
| 测试密码 | 123456Tt | 仅权限对比用例需要 |
| 浏览器类型 | chromium | Chrome/Edge |
| 视口大小 | 1920x1080 | 桌面端标准分辨率 |

**说明**：此配置将被 playwright-test-generator 用于生成自动化脚本。

---

## 📑 目录

- [测试概述](#测试概述)
- [模块 A：基础展示与定位](#模块-a基础展示与定位)
- [模块 B：About Us 相关链接](#模块-babout-us-相关链接)
- [模块 C：Help 相关链接](#模块-chelp-相关链接)
- [模块 D：Cookie 管理功能](#模块-dcookie-管理功能)
- [模块 E：应用下载引导](#模块-e应用下载引导)
- [模块 G：城市切换与 Cookie 持久化](#模块-g城市切换与-cookie-持久化)
- [测试统计](#测试统计)

---

## 测试概述

### 功能说明
首页底部 Footer 是全站通用的公共导航区域，提供以下功能入口：

1. **About Us** - Terms of Use、Privacy Policy
2. **Help** - Help、Contact Us、FAQ、Support and feedback、Return Policy、Refund Policy
3. **Cookie** - Cookie Policy、Cookie Settings、Cookie Information（点击单个 Cookie 选项后出现）
4. **Our Apps** - App Store、Google Play 下载引导
5. **城市切换与 Cookie 持久化** - 切换城市后的 URL 跳转及 Cookie 保留
6. **版权信息** - © 2025 Servanan International Pte. Ltd.

### 测试目标
1. 验证所有链接可点击且跳转正确
2. 验证外部链接在新标签页打开
3. 验证 Cookie 管理功能完整性（包括 Cookie Information 入口）
4. 验证应用下载引导流程
5. 验证城市切换后 Cookie 设置持久化，URL 正确跳转

### 测试策略
- **优先级分配**: 按功能影响面和用户使用频率
- **自动化策略**: 链接跳转、Cookie 操作、城市切换均可自动化
- **人工测试**: 应用商店实际下载（需手动验证）

**注意**：根据需求，模块 F（响应式与权限测试）不进行测试。

---

## 模块 A：基础展示与定位

### TC-FOOTER-A-001：Footer 区域基础展示

**优先级**: P0  
**类型**: 功能测试  
**UI自动化**: ✅ 可自动化  

**用例描述**  
验证首页底部 Footer 区域的基本展示元素是否完整。

**前置条件**  
- 浏览器已打开 https://ae.ok.com

**测试步骤**  
1. 访问首页
2. 滚动到页面底部
3. 检查 Footer 区域是否包含以下部分：
   - "About Us" 区块
   - "Help" 区块
   - "Cookie" 区块
   - "Our Apps" 区块
   - 版权信息 "© 2025 Servanan International Pte. Ltd."

**预期结果**  
- Footer 区域可见
- 所有区块标题清晰展示
- 版权信息显示正确年份和公司名称

**需求来源**: 页面结构分析  
**风险等级**: 高 - Footer 是全站公共区域  
**依赖关系**: 无

---

### TC-FOOTER-A-002：Footer 区域位置固定

**优先级**: P1  
**类型**: 布局测试  
**UI自动化**: ✅ 可自动化  

**用例描述**  
验证 Footer 始终位于页面最底部，不会被其他内容遮挡。

**前置条件**  
- 浏览器已打开 https://ae.ok.com

**测试步骤**  
1. 访问首页
2. 记录页面总高度
3. 滚动到页面底部
4. 检查 Footer 区域的纵向位置

**预期结果**  
- Footer 位于页面最底部
- Footer 下方无其他内容
- Footer 可见且未被遮挡

**需求来源**: UI 标准规范  
**风险等级**: 中  
**依赖关系**: 无

---

## 模块 B：About Us 相关链接

### TC-FOOTER-B-001：Terms of Use 链接跳转

**优先级**: P0  
**类型**: 功能测试  
**UI自动化**: ✅ 可自动化  

**用例描述**  
验证点击 "Terms of Use" 链接后，正确跳转到服务条款页面。

**前置条件**  
- 浏览器已打开 https://ae.ok.com
- 已滚动到 Footer 区域

**测试步骤**  
1. 定位 "About Us" 区块下的 "Terms of Use" 链接
2. 检查链接的 `href` 属性
3. 点击链接
4. 等待页面跳转
5. 检查新页面 URL 和标题

**预期结果**  
- 链接的 `href` 指向正确的服务条款页面
- 点击后在新标签页打开（`target="_blank"`）
- 新页面加载成功，标题包含 "Terms" 或 "服务条款"

**需求来源**: 法律合规要求  
**风险等级**: 高 - 法律文档入口  
**依赖关系**: 无

---

### TC-FOOTER-B-002：Privacy Policy 链接跳转

**优先级**: P0  
**类型**: 功能测试  
**UI自动化**: ✅ 可自动化  

**用例描述**  
验证点击 "Privacy Policy" 链接后，正确跳转到隐私政策页面。

**前置条件**  
- 浏览器已打开 https://ae.ok.com
- 已滚动到 Footer 区域

**测试步骤**  
1. 定位 "About Us" 区块下的 "Privacy Policy" 链接
2. 检查链接的 `href` 属性
3. 点击链接
4. 等待页面跳转
5. 检查新页面 URL 和标题

**预期结果**  
- 链接的 `href` 指向正确的隐私政策页面
- 点击后在新标签页打开（`target="_blank"`）
- 新页面加载成功，标题包含 "Privacy" 或 "隐私政策"

**需求来源**: 法律合规要求（GDPR、CCPA）  
**风险等级**: 高 - 隐私法律文档入口  
**依赖关系**: 无

---

## 模块 C：Help 相关链接

### TC-FOOTER-C-001：Help 链接跳转

**优先级**: P0  
**类型**: 功能测试  
**UI自动化**: ✅ 可自动化  

**用例描述**  
验证点击 "Help" 链接后，正确跳转到帮助中心页面。

**前置条件**  
- 浏览器已打开 https://ae.ok.com
- 已滚动到 Footer 区域

**测试步骤**  
1. 定位 "Help" 区块下的 "Help" 链接
2. 检查链接的 `href` 属性
3. 点击链接
4. 等待页面跳转
5. 检查新页面 URL 和内容

**预期结果**  
- 链接的 `href` 指向帮助中心页面
- 点击后在新标签页打开
- 新页面加载成功，显示帮助内容

**需求来源**: 用户支持流程  
**风险等级**: 高 - 用户求助主入口  
**依赖关系**: 无

---

### TC-FOOTER-C-002：Contact Us 链接跳转

**优先级**: P0  
**类型**: 功能测试  
**UI自动化**: ✅ 可自动化  

**用例描述**  
验证点击 "Contact Us" 链接后，正确跳转到联系我们页面。

**前置条件**  
- 浏览器已打开 https://ae.ok.com
- 已滚动到 Footer 区域

**测试步骤**  
1. 定位 "Help" 区块下的 "Contact Us" 链接
2. 检查链接的 `href` 属性
3. 点击链接
4. 等待页面跳转
5. 检查新页面是否包含联系表单或联系方式

**预期结果**  
- 链接的 `href` 指向联系页面
- 点击后在新标签页打开
- 新页面显示联系表单或客服信息

**需求来源**: 用户支持流程  
**风险等级**: 高 - 用户反馈入口  
**依赖关系**: 无

---

### TC-FOOTER-C-003：FAQ 链接跳转

**优先级**: P1  
**类型**: 功能测试  
**UI自动化**: ✅ 可自动化  

**用例描述**  
验证点击 "FAQ" 链接后，正确跳转到常见问题页面。

**前置条件**  
- 浏览器已打开 https://ae.ok.com
- 已滚动到 Footer 区域

**测试步骤**  
1. 定位 "Help" 区块下的 "FAQ" 链接
2. 检查链接的 `href` 属性
3. 点击链接
4. 等待页面跳转
5. 检查新页面是否包含常见问题列表

**预期结果**  
- 链接的 `href` 指向 FAQ 页面
- 点击后在新标签页打开
- 新页面显示问题列表或折叠面板

**需求来源**: 用户自助服务  
**风险等级**: 中  
**依赖关系**: 无

---

### TC-FOOTER-C-004：Support and feedback 链接跳转

**优先级**: P1  
**类型**: 功能测试  
**UI自动化**: ✅ 可自动化  

**用例描述**  
验证点击 "Support and feedback" 链接后，正确跳转到支持反馈页面。

**前置条件**  
- 浏览器已打开 https://ae.ok.com
- 已滚动到 Footer 区域

**测试步骤**  
1. 定位 "Help" 区块下的 "Support and feedback" 链接
2. 检查链接的 `href` 属性
3. 点击链接
4. 等待页面跳转
5. 检查新页面内容

**预期结果**  
- 链接的 `href` 指向支持反馈页面
- 点击后在新标签页打开
- 新页面显示反馈表单或支持选项

**需求来源**: 用户体验优化  
**风险等级**: 中  
**依赖关系**: 无

---

### TC-FOOTER-C-005：Return Policy 链接跳转

**优先级**: P1  
**类型**: 功能测试  
**UI自动化**: ✅ 可自动化  

**用例描述**  
验证点击 "Return Policy" 链接后，正确跳转到退货政策页面。

**前置条件**  
- 浏览器已打开 https://ae.ok.com
- 已滚动到 Footer 区域

**测试步骤**  
1. 定位 "Help" 区块下的 "Return Policy" 链接
2. 检查链接的 `href` 属性
3. 点击链接
4. 等待页面跳转
5. 检查新页面内容

**预期结果**  
- 链接的 `href` 指向退货政策页面
- 点击后在新标签页打开
- 新页面显示退货规则和流程

**需求来源**: 电商法律合规  
**风险等级**: 中 - 电商类目需要  
**依赖关系**: 无

---

### TC-FOOTER-C-006：Refund Policy 链接跳转

**优先级**: P1  
**类型**: 功能测试  
**UI自动化**: ✅ 可自动化  

**用例描述**  
验证点击 "Refund Policy" 链接后，正确跳转到退款政策页面。

**前置条件**  
- 浏览器已打开 https://ae.ok.com
- 已滚动到 Footer 区域

**测试步骤**  
1. 定位 "Help" 区块下的 "Refund Policy" 链接
2. 检查链接的 `href` 属性
3. 点击链接
4. 等待页面跳转
5. 检查新页面内容

**预期结果**  
- 链接的 `href` 指向退款政策页面
- 点击后在新标签页打开
- 新页面显示退款规则和流程

**需求来源**: 电商法律合规  
**风险等级**: 中 - 电商类目需要  
**依赖关系**: 无

---

## 模块 D：Cookie 管理功能

### TC-FOOTER-D-001：Cookie Policy 链接跳转

**优先级**: P0  
**类型**: 功能测试  
**UI自动化**: ✅ 可自动化  

**用例描述**  
验证点击 "Cookie Policy" 链接后，正确跳转到 Cookie 政策页面。

**前置条件**  
- 浏览器已打开 https://ae.ok.com
- 已滚动到 Footer 区域

**测试步骤**  
1. 定位 "Cookie" 区块下的 "Cookie Policy" 链接
2. 检查链接的 `href` 属性
3. 点击链接
4. 等待页面跳转
5. 检查新页面内容

**预期结果**  
- 链接的 `href` 指向 Cookie 政策页面
- 点击后在新标签页打开
- 新页面显示 Cookie 使用说明

**需求来源**: GDPR 合规要求  
**风险等级**: 高 - 法律合规  
**依赖关系**: 无

---

### TC-FOOTER-D-002：Cookie Settings 弹窗打开

**优先级**: P0  
**类型**: 功能测试  
**UI自动化**: ✅ 可自动化  

**用例描述**  
验证点击 "Cookie Settings" 后，正确打开 Cookie 设置弹窗。

**前置条件**  
- 浏览器已打开 https://ae.ok.com
- 已滚动到 Footer 区域

**测试步骤**  
1. 定位 "Cookie" 区块下的 "Cookie Settings" 链接
2. 点击链接
3. 等待弹窗出现
4. 检查弹窗内容

**预期结果**  
- 点击后弹窗打开
- 弹窗标题为 "Cookie Settings" 或 "Cookie 设置"
- 弹窗内显示多个 Cookie 类型选项（如必要 Cookie、分析 Cookie、营销 Cookie）
- 每个 Cookie 类型有描述和开关

**需求来源**: GDPR 合规要求  
**风险等级**: 高 - 用户隐私控制  
**依赖关系**: 无

---

### TC-FOOTER-D-003：Cookie Settings - 必要 Cookie 不可关闭

**优先级**: P0  
**类型**: 功能测试  
**UI自动化**: ✅ 可自动化  

**用例描述**  
验证必要 Cookie（Strictly Necessary Cookies）无法被用户关闭。

**前置条件**  
- 浏览器已打开 https://ae.ok.com
- 已打开 Cookie Settings 弹窗

**测试步骤**  
1. 在 Cookie Settings 弹窗中找到 "Strictly Necessary Cookies" 或 "必要 Cookie"
2. 检查其开关状态
3. 尝试点击开关

**预期结果**  
- 必要 Cookie 的开关处于开启状态
- 开关为禁用状态（灰色或无法点击）
- 或点击后无响应，保持开启

**需求来源**: GDPR 合规 - 必要 Cookie 不需用户同意  
**风险等级**: 高 - 法律合规  
**依赖关系**: TC-FOOTER-D-002

---

### TC-FOOTER-D-004：Cookie Settings - 可选 Cookie 可关闭

**优先级**: P0  
**类型**: 功能测试  
**UI自动化**: ✅ 可自动化  

**用例描述**  
验证可选 Cookie（如分析、营销类 Cookie）可以被用户关闭。

**前置条件**  
- 浏览器已打开 https://ae.ok.com
- 已打开 Cookie Settings 弹窗

**测试步骤**  
1. 在 Cookie Settings 弹窗中找到可选 Cookie（如 "Analytics Cookies"、"Marketing Cookies"）
2. 检查开关的初始状态
3. 点击开关关闭该类 Cookie
4. 检查开关状态变化
5. 保存设置
6. 刷新页面，重新打开 Cookie Settings
7. 检查之前关闭的 Cookie 状态是否保持

**预期结果**  
- 可选 Cookie 的开关可点击
- 点击后开关状态切换（开启/关闭）
- 保存后设置生效
- 刷新页面后设置保持

**需求来源**: GDPR 合规 - 用户隐私控制权  
**风险等级**: 高 - 用户隐私控制  
**依赖关系**: TC-FOOTER-D-002

---

### TC-FOOTER-D-005：Cookie Settings - 允许全部 Cookie

**优先级**: P0  
**类型**: 功能测试  
**UI自动化**: ✅ 可自动化  

**用例描述**  
验证点击 "Accept All" 或 "允许全部" 后，所有可选 Cookie 开启。

**前置条件**  
- 浏览器已打开 https://ae.ok.com
- 已打开 Cookie Settings 弹窗
- 部分可选 Cookie 处于关闭状态

**测试步骤**  
1. 在 Cookie Settings 弹窗中找到 "Accept All" 或 "允许全部" 按钮
2. 点击按钮
3. 检查所有可选 Cookie 的开关状态
4. 关闭弹窗
5. 刷新页面，重新打开 Cookie Settings
6. 检查所有 Cookie 状态

**预期结果**  
- 点击 "Accept All" 后，所有可选 Cookie 开关切换为开启
- 弹窗自动关闭或显示保存成功提示
- 刷新后设置保持

**需求来源**: GDPR 合规 - 用户便捷同意  
**风险等级**: 中  
**依赖关系**: TC-FOOTER-D-002

---

### TC-FOOTER-D-006：Cookie Information 入口 - 必要 Cookie

**优先级**: P1  
**类型**: 功能测试  
**UI自动化**: ✅ 可自动化  

**用例描述**  
验证点击 "Strictly Necessary Cookies" 或 "必要 Cookie" 选项后，出现 "Cookie Information" 入口，点击后可查看详细信息。

**前置条件**  
- 浏览器已打开 https://ae.ok.com
- 已打开 Cookie Settings 弹窗

**测试步骤**  
1. 在 Cookie Settings 弹窗中找到 "Strictly Necessary Cookies" 选项
2. 点击该选项（或选项旁的展开图标）
3. 检查是否出现 "Cookie Information" 入口或链接
4. 点击 "Cookie Information" 入口
5. 检查显示的详细信息内容

**预期结果**  
- 点击 Cookie 选项后，出现 "Cookie Information" 入口
- 点击入口后，展开或弹出详细信息
- 详细信息包含：Cookie 名称、用途、有效期、提供方等
- 信息清晰易读

**需求来源**: GDPR 合规 - 用户知情权  
**风险等级**: 中 - 透明度要求  
**依赖关系**: TC-FOOTER-D-002

---

### TC-FOOTER-D-007：Cookie Information 入口 - 分析 Cookie

**优先级**: P1  
**类型**: 功能测试  
**UI自动化**: ✅ 可自动化  

**用例描述**  
验证点击 "Analytics Cookies" 或 "分析 Cookie" 选项后，出现 "Cookie Information" 入口，点击后可查看详细信息。

**前置条件**  
- 浏览器已打开 https://ae.ok.com
- 已打开 Cookie Settings 弹窗

**测试步骤**  
1. 在 Cookie Settings 弹窗中找到 "Analytics Cookies" 选项
2. 点击该选项（或选项旁的展开图标）
3. 检查是否出现 "Cookie Information" 入口或链接
4. 点击 "Cookie Information" 入口
5. 检查显示的详细信息内容

**预期结果**  
- 点击 Cookie 选项后，出现 "Cookie Information" 入口
- 点击入口后，展开或弹出详细信息
- 详细信息包含：Cookie 名称、用途、有效期、提供方等
- 信息清晰易读

**需求来源**: GDPR 合规 - 用户知情权  
**风险等级**: 中 - 透明度要求  
**依赖关系**: TC-FOOTER-D-002

---

### TC-FOOTER-D-008：Cookie Information 入口 - 营销 Cookie

**优先级**: P1  
**类型**: 功能测试  
**UI自动化**: ✅ 可自动化  

**用例描述**  
验证点击 "Marketing Cookies" 或 "营销 Cookie" 选项后，出现 "Cookie Information" 入口，点击后可查看详细信息。

**前置条件**  
- 浏览器已打开 https://ae.ok.com
- 已打开 Cookie Settings 弹窗

**测试步骤**  
1. 在 Cookie Settings 弹窗中找到 "Marketing Cookies" 选项
2. 点击该选项（或选项旁的展开图标）
3. 检查是否出现 "Cookie Information" 入口或链接
4. 点击 "Cookie Information" 入口
5. 检查显示的详细信息内容

**预期结果**  
- 点击 Cookie 选项后，出现 "Cookie Information" 入口
- 点击入口后，展开或弹出详细信息
- 详细信息包含：Cookie 名称、用途、有效期、提供方等
- 信息清晰易读

**需求来源**: GDPR 合规 - 用户知情权  
**风险等级**: 中 - 透明度要求  
**依赖关系**: TC-FOOTER-D-002

---

### TC-FOOTER-D-009：Cookie Information 入口 - 所有 Cookie 类型

**优先级**: P1  
**类型**: 功能测试  
**UI自动化**: ✅ 可自动化  

**用例描述**  
批量验证所有 Cookie 类型选项均有 "Cookie Information" 入口。

**前置条件**  
- 浏览器已打开 https://ae.ok.com
- 已打开 Cookie Settings 弹窗

**测试步骤**  
1. 在 Cookie Settings 弹窗中列举所有 Cookie 类型选项
2. 逐一点击每个 Cookie 类型选项
3. 检查是否每个选项都出现 "Cookie Information" 入口
4. 随机抽样点击 2-3 个入口，验证信息正确展示

**预期结果**  
- 所有 Cookie 类型选项均有 "Cookie Information" 入口
- 每个入口点击后均能展开或弹出详细信息
- 信息内容与该 Cookie 类型匹配

**需求来源**: GDPR 合规 - 完整透明度  
**风险等级**: 中  
**依赖关系**: TC-FOOTER-D-002

---

## 模块 E：应用下载引导

### TC-FOOTER-E-001：App Store 下载引导

**优先级**: P1  
**类型**: 功能测试  
**UI自动化**: ⚠️ 部分自动化（跳转可自动化，实际下载需人工验证）  

**用例描述**  
验证点击 "Download on the App Store" 按钮后，正确跳转到 iOS App Store。

**前置条件**  
- 浏览器已打开 https://ae.ok.com
- 已滚动到 Footer 区域

**测试步骤**  
1. 定位 "Our Apps" 区块下的 "App Store" 按钮
2. 检查按钮的 `href` 属性
3. 点击按钮
4. 等待页面跳转
5. 检查新页面 URL 是否包含 `apps.apple.com` 或 `itunes.apple.com`

**预期结果**  
- 按钮的 `href` 指向正确的 App Store 链接
- 点击后在新标签页打开
- 新页面跳转到 App Store（iOS 设备）或 App Store 网页版（桌面端）

**需求来源**: 移动端用户引导  
**风险等级**: 中 - 用户获取入口  
**依赖关系**: 无

**备注**：实际下载安装需在 iOS 设备上手动验证。

---

### TC-FOOTER-E-002：Google Play 下载引导

**优先级**: P1  
**类型**: 功能测试  
**UI自动化**: ⚠️ 部分自动化（跳转可自动化，实际下载需人工验证）  

**用例描述**  
验证点击 "Get it on Google Play" 按钮后，正确跳转到 Google Play。

**前置条件**  
- 浏览器已打开 https://ae.ok.com
- 已滚动到 Footer 区域

**测试步骤**  
1. 定位 "Our Apps" 区块下的 "Google Play" 按钮
2. 检查按钮的 `href` 属性
3. 点击按钮
4. 等待页面跳转
5. 检查新页面 URL 是否包含 `play.google.com`

**预期结果**  
- 按钮的 `href` 指向正确的 Google Play 链接
- 点击后在新标签页打开
- 新页面跳转到 Google Play（Android 设备）或 Google Play 网页版（桌面端）

**需求来源**: 移动端用户引导  
**风险等级**: 中 - 用户获取入口  
**依赖关系**: 无

**备注**：实际下载安装需在 Android 设备上手动验证。

---

### TC-FOOTER-E-003：应用下载按钮图标正确性

**优先级**: P2  
**类型**: UI 测试  
**UI自动化**: ✅ 可自动化  

**用例描述**  
验证 App Store 和 Google Play 下载按钮的图标和文案正确。

**前置条件**  
- 浏览器已打开 https://ae.ok.com
- 已滚动到 Footer 区域

**测试步骤**  
1. 定位 "Our Apps" 区块
2. 检查 App Store 按钮：
   - 是否包含 Apple 图标
   - 文案是否为 "Download on the App Store"
3. 检查 Google Play 按钮：
   - 是否包含 Google Play 图标
   - 文案是否为 "Get it on Google Play"

**预期结果**  
- App Store 按钮包含 Apple 图标和正确文案
- Google Play 按钮包含 Google Play 图标和正确文案
- 图标清晰无损坏

**需求来源**: 品牌规范  
**风险等级**: 低  
**依赖关系**: 无

---

## 模块 G：城市切换与 Cookie 持久化

### TC-FOOTER-G-001：城市切换后 URL 自动跳转

**优先级**: P0  
**类型**: 功能测试  
**UI自动化**: ✅ 可自动化  

**用例描述**  
验证在首页设置了全部允许 Cookie 后，切换城市（如 Ajman），再次访问 https://ae.ok.com 时，自动跳转到 https://ae.ok.com/en/city-ajman/。

**前置条件**  
- 浏览器已打开 https://ae.ok.com
- 已允许全部 Cookie（通过 Cookie Settings）

**测试步骤**  
1. 在首页打开 Cookie Settings，点击 "Accept All"
2. 关闭 Cookie Settings 弹窗
3. 在首页顶部定位城市选择器（如下拉菜单或弹窗）
4. 切换城市为 "Ajman"
5. 等待页面跳转或刷新
6. 检查当前 URL
7. 关闭当前标签页
8. 新打开标签页，访问 https://ae.ok.com
9. 检查是否自动跳转到 https://ae.ok.com/en/city-ajman/

**预期结果**  
- 切换城市后，URL 包含 `/city-ajman/`
- 再次访问首页时，自动跳转到 https://ae.ok.com/en/city-ajman/
- Cookie 设置保持（所有 Cookie 仍为允许状态）

**需求来源**: 用户体验优化 - 记住用户偏好  
**风险等级**: 高 - 地理定位逻辑  
**依赖关系**: TC-FOOTER-D-005

---

### TC-FOOTER-G-002：城市切换后 Cookie 设置保持

**优先级**: P0  
**类型**: 功能测试  
**UI自动化**: ✅ 可自动化  

**用例描述**  
验证切换城市后，之前的 Cookie 设置保持不变。

**前置条件**  
- 浏览器已打开 https://ae.ok.com
- 已自定义 Cookie 设置（如关闭了营销 Cookie）

**测试步骤**  
1. 在首页打开 Cookie Settings
2. 关闭 "Marketing Cookies"
3. 保存设置并关闭弹窗
4. 在首页顶部切换城市为 "Ajman"
5. 等待页面跳转到 https://ae.ok.com/en/city-ajman/
6. 滚动到页面底部
7. 点击 "Cookie Settings"
8. 检查 "Marketing Cookies" 的状态

**预期结果**  
- 切换城市后，URL 跳转到 `/city-ajman/`
- 重新打开 Cookie Settings 后，"Marketing Cookies" 仍为关闭状态
- 其他 Cookie 设置保持不变

**需求来源**: GDPR 合规 - 用户选择持久化  
**风险等级**: 高 - 隐私设置保持  
**依赖关系**: TC-FOOTER-D-004

---

### TC-FOOTER-G-003：城市切换后 Footer 内容一致性

**优先级**: P1  
**类型**: 功能测试  
**UI自动化**: ✅ 可自动化  

**用例描述**  
验证切换城市后，Footer 区域的内容和链接保持一致。

**前置条件**  
- 浏览器已打开 https://ae.ok.com
- 已允许全部 Cookie

**测试步骤**  
1. 在首页滚动到 Footer 区域，记录所有链接
2. 在首页顶部切换城市为 "Ajman"
3. 等待页面跳转到 https://ae.ok.com/en/city-ajman/
4. 滚动到 Footer 区域
5. 对比 Footer 内容是否一致

**预期结果**  
- 切换城市后，Footer 的所有链接和区块保持一致
- "About Us"、"Help"、"Cookie"、"Our Apps" 等区块内容不变
- 所有链接的 `href` 属性不变（或正确适配新城市）

**需求来源**: 全站一致性  
**风险等级**: 中  
**依赖关系**: TC-FOOTER-G-001

---

### TC-FOOTER-G-004：多次城市切换后 Cookie 设置稳定

**优先级**: P1  
**类型**: 功能测试  
**UI自动化**: ✅ 可自动化  

**用例描述**  
验证多次切换城市后，Cookie 设置仍稳定保持。

**前置条件**  
- 浏览器已打开 https://ae.ok.com
- 已自定义 Cookie 设置

**测试步骤**  
1. 在首页打开 Cookie Settings，关闭 "Analytics Cookies"
2. 保存设置
3. 切换城市为 "Ajman"
4. 等待跳转到 https://ae.ok.com/en/city-ajman/
5. 再次切换城市为 "Dubai"
6. 等待跳转到 https://ae.ok.com/en/city-dubai/
7. 再次切换回默认城市（或刷新 https://ae.ok.com）
8. 打开 Cookie Settings
9. 检查 "Analytics Cookies" 状态

**预期结果**  
- 多次切换城市后，"Analytics Cookies" 仍为关闭状态
- Cookie 设置在各个城市页面间保持一致

**需求来源**: GDPR 合规 - 设置稳定性  
**风险等级**: 中  
**依赖关系**: TC-FOOTER-G-002

---

### TC-FOOTER-G-005：清除 Cookie 后城市选择重置

**优先级**: P2  
**类型**: 功能测试  
**UI自动化**: ✅ 可自动化  

**用例描述**  
验证清除浏览器 Cookie 后，城市选择重置为默认，不再自动跳转。

**前置条件**  
- 浏览器已打开 https://ae.ok.com
- 已切换城市为 "Ajman"，URL 为 https://ae.ok.com/en/city-ajman/

**测试步骤**  
1. 在当前页面，打开浏览器开发者工具
2. 清除所有 Cookie（Application > Cookies > Clear all）
3. 刷新页面
4. 检查 URL 是否仍为 https://ae.ok.com/en/city-ajman/
5. 在地址栏输入 https://ae.ok.com，访问首页
6. 检查是否自动跳转到 Ajman 页面

**预期结果**  
- 清除 Cookie 后，刷新页面可能跳转回默认首页（或保持当前 URL）
- 访问 https://ae.ok.com 时，不再自动跳转到 Ajman
- 城市选择重置为默认（或要求重新选择）

**需求来源**: Cookie 机制验证  
**风险等级**: 低  
**依赖关系**: TC-FOOTER-G-001

---

## 测试统计

### 按模块统计

| 模块 | 用例数 | 可自动化 | 不可自动化 | 条件自动化 |
|------|--------|----------|------------|------------|
| 模块 A：基础展示与定位 | 2 | 2 | 0 | 0 |
| 模块 B：About Us 相关链接 | 2 | 2 | 0 | 0 |
| 模块 C：Help 相关链接 | 6 | 6 | 0 | 0 |
| 模块 D：Cookie 管理功能 | 9 | 9 | 0 | 0 |
| 模块 E：应用下载引导 | 3 | 1 | 0 | 2 |
| 模块 G：城市切换与 Cookie 持久化 | 5 | 5 | 0 | 0 |
| **总计** | **27** | **25** | **0** | **2** |

### 按优先级统计

| 优先级 | 用例数 | 占比 |
|--------|--------|------|
| P0 | 13 | 48% |
| P1 | 12 | 44% |
| P2 | 2 | 8% |

### 自动化建议

**批次1（P0 核心功能）**：
- TC-FOOTER-A-001：Footer 区域基础展示
- TC-FOOTER-B-001：Terms of Use 链接跳转
- TC-FOOTER-B-002：Privacy Policy 链接跳转
- TC-FOOTER-C-001：Help 链接跳转
- TC-FOOTER-C-002：Contact Us 链接跳转
- TC-FOOTER-D-001：Cookie Policy 链接跳转
- TC-FOOTER-D-002：Cookie Settings 弹窗打开
- TC-FOOTER-D-003：必要 Cookie 不可关闭
- TC-FOOTER-D-004：可选 Cookie 可关闭
- TC-FOOTER-D-005：允许全部 Cookie
- TC-FOOTER-G-001：城市切换后 URL 自动跳转
- TC-FOOTER-G-002：城市切换后 Cookie 设置保持

**批次2（P1 扩展功能）**：
- TC-FOOTER-A-002：Footer 区域位置固定
- TC-FOOTER-C-003：FAQ 链接跳转
- TC-FOOTER-C-004：Support and feedback 链接跳转
- TC-FOOTER-C-005：Return Policy 链接跳转
- TC-FOOTER-C-006：Refund Policy 链接跳转
- TC-FOOTER-D-006：Cookie Information 入口 - 必要 Cookie
- TC-FOOTER-D-007：Cookie Information 入口 - 分析 Cookie
- TC-FOOTER-D-008：Cookie Information 入口 - 营销 Cookie
- TC-FOOTER-D-009：Cookie Information 入口 - 所有 Cookie 类型
- TC-FOOTER-E-001：App Store 下载引导（部分自动化）
- TC-FOOTER-E-002：Google Play 下载引导（部分自动化）
- TC-FOOTER-G-003：城市切换后 Footer 内容一致性
- TC-FOOTER-G-004：多次城市切换后 Cookie 设置稳定

**批次3（P2 补充验证）**：
- TC-FOOTER-E-003：应用下载按钮图标正确性
- TC-FOOTER-G-005：清除 Cookie 后城市选择重置

---

## 执行建议

1. **前置准备**：
   - 确认 https://ae.ok.com 可正常访问
   - 准备干净的浏览器环境（无缓存、无 Cookie）
   - 准备 iOS 和 Android 设备用于应用下载验证

2. **执行顺序**：
   - 先执行批次1（P0），确保核心功能可用
   - 再执行批次2（P1），覆盖扩展功能
   - 最后执行批次3（P2），补充边界验证

3. **注意事项**：
   - Cookie 相关用例建议每个用例前清除 Cookie，确保测试独立性
   - 城市切换用例需确认城市选择器位置和交互方式
   - Cookie Information 入口的具体展现形式需根据实际 UI 调整定位策略
   - 应用下载引导的实际安装需在真机上手动验证

4. **自动化脚本生成**：
   - 建议使用 Playwright 生成脚本
   - Cookie 操作建议使用 `context.add_cookies()` 和 `context.cookies()` API
   - 新标签页跳转建议使用 `page.context.wait_for_event('page')` 捕获
   - 城市切换逻辑需根据实际选择器编写

---

**文档版本**: v1.0  
**最后更新**: 2026-04-02  
**维护人**: 测试团队
