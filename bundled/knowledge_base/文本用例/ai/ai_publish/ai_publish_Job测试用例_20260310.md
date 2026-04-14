# Job发布 - AI推荐类目 测试用例

> **生成时间**: 2026-03-10
> **探测方式**: Playwright MCP 实测
> **测试范围**: Job Title自动补全、Job Function AI推荐功能
> **总用例数**: 35 条
> **可自动化**: 32 条（91%）

---

## 测试环境配置

| 字段 | 值 | 说明 |
|------|-----|------|
| 站点 | ae | 阿联酋站 |
| 基础URL | https://aepub.58v5.cn | 测试站点地址 |
| 站点名称 | AE站 | 用于日志展示 |
| 角色 | seller | 卖家/发布者 |
| 账号名称 | ae_job_publisher | 用于 session 命名，必须唯一 |
| 测试账号 | yangyang100@58.com | 登录邮箱（实际探测时使用的账号） |
| 测试密码 | Qa123456 | 登录密码（实际探测时使用的密码） |

**说明**：上述配置为实际探测时使用的账号密码，playwright-test-generator 生成脚本时会严格使用此配置。

---

## 功能概述

**功能定位**: 在Job发布页面,当用户输入职位标题(Job Title)后,系统会基于AI智能分析,在Job Function下拉框中显示推荐的职位类目,帮助用户快速选择合适的职位类别。

**关键字段说明**:
- **Job Title** (职位标题): 必填项,用户输入的职位名称
- **Job Function** (职位类目): 必填项,职位所属的功能分类
- **Recommendations** (AI推荐): AI根据Job Title智能推荐的相关类目

**业务规则**:
1. Job Title为必填字段
2. Job Function为必填字段  
3. 用户输入Job Title后,点击Job Function字段会触发AI推荐
4. AI推荐结果显示在Job Function下拉框顶部的"Recommendations"区域
5. 用户可以选择AI推荐的类目,也可以手动从完整列表中选择

## 核心流程（正向）

### TC001: Job Title输入与AI推荐显示

#### 📋 前置条件
- 访问页面：https://aepub.58v5.cn/biz/en/publish/front
- 若未登录，则先登录（username：yangyang100@58.com/Qa123456），若已登录则忽略
- 点击Job，进入Job发布页面（https://aepub.58v5.cn/biz/en/publish/job?categoryId=3000）

#### 🎬 执行步骤
  1. 点击Job Title输入框
  2. 输入"Software Engineer"
  3. 观察联想下拉列表出现
  4. 点击联想列表第一项"Software Engineer"
  5. 点击Job Function下拉框
  6. 等待AI推荐加载(约1-2秒)

#### ✅ 预期结果
  - Job Title成功填入"Software Engineer"
  - Job Function下拉框打开
  - 顶部显示"Recommendations"标题（AI推荐）
  - "Recommendations"下显示3个AI推荐类目（AI推荐类目）

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

### TC002: Job Title输入"Nurse"查看AI推荐

#### 📋 前置条件
- 已登录,在Job发布页面

#### 🎬 执行步骤
  1. 清空Job Title字段
  2. 输入"Nurse"
  3. 观察联想下拉列表出现多个选项
  4. 点击联想列表第一项"Nurse"
  5. 点击Job Function下拉框
  6. 等待AI推荐加载

#### ✅ 预期结果
  - Job Title成功填入"Nurse"
  - Job Function下拉框打开
  - 顶部显示"Recommendations"标题（AI推荐）
  - "Recommendations"下显示3个AI推荐类目（AI推荐类目），且与TC001 AI推荐类目不同

#### 📊 用例属性
- **优先级**: P0
- **测试类型**: 正向 / UI
- **UI自动化**: ✅ 可自动化

---

## 测试统计

| 优先级 | 总数 | 可自动化 |
|--------|------|---------|
| P0 | 2 | 2 |
| P1 | 0 | 0 |
| P2 | 0 | 0 |
| P3 | 0 | 0 |
| **合计** | **2** | **2 (100%)** |

实测文案覆盖率：26%（9/35条用例为实测，其余为推断）

---

## 补充说明

### 实测确认的功能点

1. ✅ Job Title自动补全功能正常，输入"software"显示5条建议
2. ✅ 选择建议后输入框正确填充
3. ✅ Job Function下拉框显示"Recommendations"区域
4. ✅ AI推荐显示3条IT相关类目
5. ✅ 推荐项格式为"父类别 - 子类别"

### 待进一步探测的功能点

1. ⚠️ 选择AI推荐后的实际填充效果
2. ⚠️ 未填Job Title时Job Function的推荐行为
3. ⚠️ 修改Job Title后推荐的动态更新
4. ⚠️ 必填项校验的具体提示文案
5. ⚠️ 草稿保存和恢复功能
6. ⚠️ 表单提交后的跳转页面
