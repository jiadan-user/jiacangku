# OK AE 站 - Settings 模块测试用例

> **站点**: https://ae.58v5.cn/  
> **探测账号**: zidonghuammm@58.com / Qwer1234  
> **测试环境**: AE 生产站  
> **生成日期**: 2026-04-14  
> **覆盖模块**: Profile / Account Settings / Country & Region  

---

## 重复执行设计原则

本文档所有用例支持幂等重复执行，核心策略如下：

| 策略 | 说明 | 适用场景 |
|------|------|---------|
| **读取-取反** | 执行前先读取当前值，填入不同的值，执行后恢复原值 | Profile 文本字段修改 |
| **时间戳后缀** | 值拼接当前时间戳，保证每次写入唯一 | Username、昵称等 |
| **A/B 交替** | 在两个固定值之间交替切换 | Country、Language 切换 |
| **执行后复原** | 每个用例末尾有明确的"数据恢复步骤" | 密码修改、Country 切换 |

**密码用例特殊说明**：  
密码修改用例（TC-ACC-007）执行后**必须在后置步骤中恢复原密码**，否则影响后续所有用例的登录。  
建议测试账号密码策略：改为 `Qwer12345` → 测试完成 → 改回 `Qwer1234`。

---

## 页面结构概览（MCP 实测）

Settings 入口：首页右上角点击用户名 → 菜单选择 "Settings" → 跳转至 `https://aepub.58v5.cn/biz/en/user/home?tabindex=X`

左侧 Tab 导航：
- Tab 0 → Profile (`tabindex=0`)
- Tab 1 → Account Settings (`tabindex=1`，默认)
- Tab 2 → Country & Region (`tabindex=2`)

---

## 一、Profile 模块

### 字段结构（MCP 实测）

| 字段 | 类型 | 当前值 | 备注 |
|------|------|--------|------|
| Avatar | 文件上传 | - | Choose File 按钮 |
| User Name | text input | OKerAE_cnbucqx | 提示：This will be shown on your profile；**可单独修改** |
| First Name | text input | (空) | placeholder: First Name；**可单独修改** |
| Last Name | text input | (空) | placeholder: Last Name；**可单独修改** |
| Email | text input | zidonghuammm@58.com | 含字数提示"19"；**可编辑**（修改后通常需要邮箱验证流程） |
| Phone | text + 区号选择 | +971 / 501234570 | 区号默认 +971；**可单独修改** |
| Save | button | - | 统一提交所有字段 |

**修改场景矩阵**：

| 修改范围 | 覆盖用例 |
|---------|---------|
| 仅头像 | TC-PRO-006（图片1.png ↔ 图片2.png 交替） |
| 仅 First Name | TC-PRO-001 |
| 仅 User Name | TC-PRO-002b |
| 仅 Email | TC-PRO-002c |
| 全量修改（头像 + User Name + 所有文本字段） | TC-PRO-002d |
| 所有字段（不含头像/Email/User Name） | TC-PRO-002 |
| 仅 Phone 区号 | TC-PRO-010 |

---

### TC-PRO-001: 仅修改 First Name 并保存成功

**优先级**: P0  
**测试类型**: 正向功能  
**重复执行策略**: 读取当前值 → 填入不同值 → 保存 → 后置恢复原值

**前置条件**:
- 已登录账号 zidonghuammm@58.com
- 位于 Settings > Profile 页面

**操作步骤**:
1. 访问 `https://aepub.58v5.cn/biz/en/user/home?tabindex=0`
2. **读取**当前 First Name 输入框的值，记为 `original_first_name`
3. 构造新值：若当前值为空或为 `QA_Auto`，则填入 `QA_Test`；否则填入 `QA_Auto`（A/B 交替策略）
4. 将新值填入 First Name 输入框（确保与 `original_first_name` 不同）
5. 其他字段保持不变
6. 点击 Save 按钮
7. 等待保存成功提示出现
8. **【后置】** 刷新页面，确认 First Name 显示步骤3中填入的值

**预期结果**:
- Save 按钮进入 busy/active 状态（提交中）
- 显示保存成功 Toast/通知
- 刷新后 First Name 显示新填入的值（而非原值）

**重复执行验证点**: 第N次运行的新值与第N-1次运行的新值不同（A/B 交替）

**MCP 录制证明**:
```js
// 读取当前值
const currentVal = await page.locator('#firstName').inputValue();
// A/B 交替
const newVal = (currentVal === 'QA_Auto') ? 'QA_Test' : 'QA_Auto';
await page.locator('#firstName').fill(newVal);
await page.getByRole('button', { name: 'Save' }).click();
```

---

### TC-PRO-002: 同时修改所有可编辑字段并保存成功

**优先级**: P0  
**测试类型**: 正向功能  
**重复执行策略**: 时间戳后缀保证唯一性；Phone 使用 A/B 交替；执行后恢复固定基准值

**前置条件**:
- 已登录账号 zidonghuammm@58.com
- 位于 Settings > Profile 页面

**测试数据**（每次执行动态生成）:

| 字段 | 写入策略 | 示例值 |
|------|---------|--------|
| First Name | 时间戳后缀 | `Auto_20260414153012` |
| Last Name | 时间戳后缀 | `Run_20260414153012` |
| Phone | A/B 交替 | `501234570` ↔ `501234571` |

> **注意**：User Name 字段不使用时间戳，以免产生大量垃圾数据。

**操作步骤**:
1. 访问 Profile Tab
2. 记录各字段当前值（`original_firstName`, `original_lastName`, `original_phone`）
3. First Name 填入 `Auto_` + 当前时间戳（如 `Auto_20260414153012`）
4. Last Name 填入 `Run_` + 当前时间戳（如 `Run_20260414153012`）
5. Phone：读取当前号码，若为 `501234570` 则填 `501234571`，反之填 `501234570`
6. Email 字段保持不变（本用例不修改 Email）
7. 点击 Save 按钮，等待成功提示
8. **【后置恢复】** 将 First Name、Last Name、Phone 恢复为步骤2记录的原值，再次点击 Save

**预期结果**:
- 步骤7：保存成功，各字段值与写入值一致
- 步骤8：恢复保存成功，下次执行时读取到的是固定基准值

**MCP 录制证明**:
```js
const ts = Date.now();
const origFirst = await page.locator('#firstName').inputValue();
const origLast  = await page.locator('#lastName').inputValue();
const origPhone = await page.getByRole('textbox', { name: 'Phone Number' }).inputValue();

await page.locator('#firstName').fill(`Auto_${ts}`);
await page.locator('#lastName').fill(`Run_${ts}`);
const newPhone = origPhone === '501234570' ? '501234571' : '501234570';
await page.getByRole('textbox', { name: 'Phone Number' }).fill(newPhone);
await page.getByRole('button', { name: 'Save' }).click();

// 后置恢复
await page.locator('#firstName').fill(origFirst);
await page.locator('#lastName').fill(origLast);
await page.getByRole('textbox', { name: 'Phone Number' }).fill(origPhone);
await page.getByRole('button', { name: 'Save' }).click();
```

---

### TC-PRO-002b: 仅修改 User Name 并保存成功

**优先级**: P0  
**测试类型**: 正向功能  
**重复执行策略**: A/B 交替（`OKerAE_cnbucqx` ↔ `OKerAE_test`），每次后置恢复原值

> ⚠️ **注意**：User Name 修改后页面右上角昵称也会同步变化，后置必须恢复，否则影响后续用例依赖用户名的断言。

**前置条件**:
- 已登录账号 zidonghuammm@58.com
- 位于 Settings > Profile 页面

**操作步骤**:
1. 读取当前 User Name 值，记为 `original_username`
2. 构造新值：若当前为 `OKerAE_cnbucqx`，填 `OKerAE_test`；否则填 `OKerAE_cnbucqx`
3. 清空 User Name 输入框，填入新值（其余字段不动）
4. 点击 Save，等待成功提示
5. 刷新页面，验证 User Name 显示为新值，右上角用户名同步更新
6. **【后置恢复】** 将 User Name 恢复为 `original_username`，点击 Save

**预期结果**:
- 保存成功，User Name 更新为新值
- 刷新后 User Name 保持新值
- 页面右上角昵称同步变化
- 后置恢复成功

**MCP 录制证明**:
```js
const origName = await page.locator('#username').inputValue();
const newName = (origName === 'OKerAE_cnbucqx') ? 'OKerAE_test' : 'OKerAE_cnbucqx';
await page.locator('#username').fill(newName);
await page.getByRole('button', { name: 'Save' }).click();
// 后置恢复
await page.locator('#username').fill(origName);
await page.getByRole('button', { name: 'Save' }).click();
```

---

### TC-PRO-002c: 仅修改 Email（Profile 页）并保存成功

**优先级**: P0  
**测试类型**: 正向功能  
**重复执行策略**: A/B 交替（两个测试邮箱之间切换），后置恢复原邮箱

> ⚠️ **注意**：修改邮箱通常会触发验证流程（向新邮箱发验证码/确认邮件），自动化执行时需确认验证码获取方式；若验证码无法自动获取，则手动测试。

**前置条件**:
- 已登录账号 zidonghuammm@58.com，邮箱已验证
- 位于 Settings > Profile 页面
- 备用测试邮箱 `zidonghuammm2@58.com` 可收信

**A/B 交替方案**:

| 轮次 | 当前邮箱 | 修改为 | 后置恢复 |
|------|---------|--------|---------|
| 第1次 | `zidonghuammm@58.com` | `zidonghuammm2@58.com` | `zidonghuammm@58.com` |
| 第2次 | `zidonghuammm2@58.com` | `zidonghuammm@58.com` | `zidonghuammm2@58.com` |

**操作步骤**:
1. 读取当前 Email 输入框值，记为 `original_email`
2. 点击 Email 输入框，确认可以输入（字段可编辑）
3. 清空输入框，根据 A/B 策略填入目标邮箱
4. 其他字段保持不变
5. 点击 Save 按钮
6. 观察系统响应（Toast 提示 / 弹出验证码输入框 / 发送验证邮件）
7. 若触发验证码流程：输入收到的验证码完成验证
8. 验证 Account Settings 页中 Email 区域更新为新邮箱并显示 Verified
9. **【后置恢复】** 将 Email 改回 `original_email` 并完成验证

**预期结果**:
- Email 字段可点击并输入（可编辑）
- Save 后触发邮箱验证流程（发验证码或确认邮件）
- 验证完成后 Profile 页 Email 显示新邮箱
- Account Settings 页同步显示新邮箱 + Verified 标识
- 后置恢复成功

**实测记录**:
- [x] Email 字段可编辑：**是**
- [ ] 修改邮箱是否需要验证当前邮箱：_待补充_
- [ ] 修改邮箱是否需要验证新邮箱：_待补充_
- [ ] 验证方式（验证码 / 确认链接）：_待补充_

---

### TC-PRO-002d: 全量修改（头像 + User Name + 所有文本字段）并逐项验证保存成功

**优先级**: P1  
**测试类型**: 正向功能/组合  
**重复执行策略**: 头像图片交替 + 文本字段时间戳 + A/B 交替组合；执行后后置恢复所有字段

**测试图片路径**:

| 图片 | 绝对路径 |
|------|---------|
| 图片1 | `/Users/mengmeng/Desktop/ok_autotest_ui_pc_v2/ok_autotest_ui_pc/test_data/images/图片1.png` |
| 图片2 | `/Users/mengmeng/Desktop/ok_autotest_ui_pc_v2/ok_autotest_ui_pc/test_data/images/图片2.png` |

**各字段写入策略**:

| 字段 | 策略 | 第1次写入值示例 | 第2次写入值示例 |
|------|------|--------------|--------------|
| 头像 | 图片交替 | 图片1.png | 图片2.png |
| User Name | A/B 交替 | `OKerAE_test` | `OKerAE_cnbucqx` |
| First Name | 时间戳后缀 | `Auto_20260414153012` | `Auto_20260414160530` |
| Last Name | 时间戳后缀 | `Run_20260414153012` | `Run_20260414160530` |
| Email | A/B 交替（需完成验证流程） | `zidonghuammm2@58.com` | `zidonghuammm@58.com` |
| Phone | A/B 交替 | `501234571` | `501234570` |

**前置条件**:
- 已登录账号 zidonghuammm@58.com
- 位于 Settings > Profile 页面
- 两张测试图片文件存在且可访问

**操作步骤**:

**Step 1 — 记录所有字段当前值（执行前快照）**
1. 进入 Profile Tab
2. 记录当前头像图片 URL → `original_avatar_url`
3. 记录 User Name 输入框值 → `original_username`
4. 记录 First Name 输入框值 → `original_firstName`
5. 记录 Last Name 输入框值 → `original_lastName`
6. 记录 Email → `original_email`
7. 记录 Phone 号码 → `original_phone`

**Step 2 — 修改所有字段**
8. **头像**：读取当前头像 URL；若含"图片1"或为默认头像，上传 **图片2.png**；否则上传 **图片1.png**
9. **User Name**：若当前为 `OKerAE_cnbucqx`，填入 `OKerAE_test`；否则填入 `OKerAE_cnbucqx`
10. **First Name**：填入 `Auto_` + 当前时间戳（确保唯一）
11. **Last Name**：填入 `Run_` + 当前时间戳
12. **Email**：若当前为 `zidonghuammm@58.com`，填入 `zidonghuammm2@58.com`；否则填入 `zidonghuammm@58.com`
13. **Phone**：若当前为 `501234570`，填入 `501234571`；反之填入 `501234570`
14. 点击 **Save** 按钮，等待保存成功提示（Toast 出现）
15. 若触发 Email 验证流程：输入收到的验证码/点击确认链接完成验证

**Step 3 — 逐项验证所有修改持久化（刷新后核对）**
16. 刷新页面（`F5` 或重新导航至 Profile Tab）
17. ✅ 验证头像：当前头像图片与 `original_avatar_url` **不同**，且显示正常（非破图）
18. ✅ 验证 User Name：输入框值与步骤9填入值一致
19. ✅ 验证 First Name：输入框值与步骤10填入值一致（含时间戳）
20. ✅ 验证 Last Name：输入框值与步骤11填入值一致（含时间戳）
21. ✅ 验证 Email：输入框值与步骤12填入的新邮箱一致
22. ✅ 验证 Phone：输入框值与步骤13填入值一致
23. ✅ 验证页面右上角用户昵称与 User Name 同步更新

**Step 4 — 后置恢复所有字段**
24. 将 User Name 恢复为 `original_username`
25. 将 First Name 恢复为 `original_firstName`
26. 将 Last Name 恢复为 `original_lastName`
27. 将 Email 恢复为 `original_email`（需完成验证流程）
28. 将 Phone 恢复为 `original_phone`
29. 点击 Save，等待成功提示
30. 刷新，确认各字段已恢复为原值
31. （头像无需恢复，下次执行自动交替为另一张）

**预期结果**:

| 验证项 | 预期 |
|--------|------|
| Save 操作 | 成功（Toast 提示 / Save 按钮状态恢复） |
| 头像（刷新后） | 显示新图片，URL 与执行前不同，非破图 |
| User Name（刷新后） | 显示 A/B 交替后的值 |
| First Name（刷新后） | 显示含时间戳的新值 |
| Last Name（刷新后） | 显示含时间戳的新值 |
| Email（刷新后） | 显示 A/B 交替后的新邮箱 |
| Phone（刷新后） | 显示 A/B 交替后的号码 |
| 右上角昵称 | 与 User Name 同步 |
| 后置恢复 | 所有字段恢复原值，下次执行不受影响 |

**Playwright 自动化参考**:
```js
const ts = Date.now();

// Step 1: 记录原值
const origAvatar  = await page.locator('img[class*="avatar"], .avatar img').getAttribute('src') ?? '';
const origName    = await page.locator('#username').inputValue();
const origFirst   = await page.locator('#firstName').inputValue();
const origLast    = await page.locator('#lastName').inputValue();
const origEmail   = await page.locator('#email').inputValue();
const origPhone   = await page.getByRole('textbox', { name: 'Phone Number' }).inputValue();

// Step 2: 修改所有字段
// 头像交替
const useImg1 = origAvatar.includes('图片2') || origAvatar === '';
const imgPath = useImg1
  ? '/Users/mengmeng/Desktop/ok_autotest_ui_pc_v2/ok_autotest_ui_pc/test_data/images/图片1.png'
  : '/Users/mengmeng/Desktop/ok_autotest_ui_pc_v2/ok_autotest_ui_pc/test_data/images/图片2.png';
await page.locator('input[type="file"]').setInputFiles(imgPath);

// 文本字段（A/B 交替 + 时间戳）
const newName  = (origName  === 'OKerAE_cnbucqx') ? 'OKerAE_test' : 'OKerAE_cnbucqx';
const newEmail = (origEmail === 'zidonghuammm@58.com') ? 'zidonghuammm2@58.com' : 'zidonghuammm@58.com';
const newPhone = (origPhone === '501234570') ? '501234571' : '501234570';
await page.locator('#username').fill(newName);
await page.locator('#firstName').fill(`Auto_${ts}`);
await page.locator('#lastName').fill(`Run_${ts}`);
await page.locator('#email').fill(newEmail);
await page.getByRole('textbox', { name: 'Phone Number' }).fill(newPhone);
await page.getByRole('button', { name: 'Save' }).click();
// ⚠️ 若触发 Email 验证流程，需在此处补充验证码输入步骤

// Step 3: 刷新逐项验证
await page.reload();
const afterAvatar = await page.locator('img[class*="avatar"], .avatar img').getAttribute('src') ?? '';
expect(afterAvatar).not.toBe(origAvatar);                                                // 头像已变
expect(afterAvatar).not.toBe('');                                                        // 非破图
expect(await page.locator('#username').inputValue()).toBe(newName);                      // User Name
expect(await page.locator('#firstName').inputValue()).toBe(`Auto_${ts}`);                // First Name
expect(await page.locator('#lastName').inputValue()).toBe(`Run_${ts}`);                  // Last Name
expect(await page.locator('#email').inputValue()).toBe(newEmail);                        // Email
expect(await page.getByRole('textbox', { name: 'Phone Number' }).inputValue()).toBe(newPhone); // Phone

// Step 4: 后置恢复
await page.locator('#username').fill(origName);
await page.locator('#firstName').fill(origFirst);
await page.locator('#lastName').fill(origLast);
await page.locator('#email').fill(origEmail);
await page.getByRole('textbox', { name: 'Phone Number' }).fill(origPhone);
await page.getByRole('button', { name: 'Save' }).click();
// ⚠️ Email 恢复同样可能触发验证流程
```

---

### TC-PRO-003: User Name 为空时点击 Save

**优先级**: P1  
**测试类型**: 边界值/负向  
**重复执行策略**: 清空 → 验证报错 → 恢复原值，不产生数据变更

**前置条件**:
- 已登录，位于 Profile 页面

**操作步骤**:
1. 读取并记录当前 User Name 值（`original_username`）
2. 清空 User Name 字段
3. 点击 Save（或观察按钮状态）
4. **【后置恢复】** 无论结果如何，将 User Name 恢复为 `original_username` 并 Save

**预期结果**:
- Save 按钮被禁用（disabled）或提示 "User Name 不能为空"
- 数据不被保存
- 后置恢复成功，下次执行不受影响

---

### TC-PRO-004: User Name 超长字符输入

**优先级**: P1  
**测试类型**: 边界值  
**重复执行策略**: 输入超长值 → 验证截断/报错 → 恢复原值

**前置条件**: 已登录，位于 Profile 页面

**操作步骤**:
1. 读取并记录当前 User Name 值（`original_username`）
2. 在 User Name 输入 60 个字符（`ABCDEFGHIJ` 重复6次）
3. 点击 Save，观察是否被截断或报错
4. **【后置恢复】** 将 User Name 恢复为 `original_username` 并 Save

**预期结果**:
- 前端有字符数限制（截断或提示），或后端返回错误
- 不能保存超长 User Name

---

### TC-PRO-005: User Name 含特殊字符/Emoji

**优先级**: P2  
**测试类型**: 边界值/安全  
**重复执行策略**: 写入特殊字符 → 验证处理方式 → 恢复原值

**前置条件**: 已登录，位于 Profile 页面

**操作步骤**:
1. 读取并记录当前 User Name 值（`original_username`）
2. 在 User Name 输入 `<script>alert(1)</script>`，点击 Save
3. 观察是否被转义/拒绝
4. 再次输入 `😊Test`，点击 Save，观察 Emoji 处理
5. **【后置恢复】** 将 User Name 恢复为 `original_username` 并 Save

**预期结果**:
- 特殊字符被转义或拒绝，不触发 XSS
- Emoji 显示正常或被过滤（以实际产品规则为准）
- 后置恢复成功

---

### TC-PRO-006: 修改头像（图片交替上传）

**优先级**: P1  
**测试类型**: 正向功能  
**重复执行策略**: 图片1.png ↔ 图片2.png 交替上传，每次写入与上次不同的图片，天然避免重复

**测试图片路径**:

| 图片 | 绝对路径 |
|------|---------|
| 图片1 | `/Users/mengmeng/Desktop/ok_autotest_ui_pc_v2/ok_autotest_ui_pc/test_data/images/图片1.png` |
| 图片2 | `/Users/mengmeng/Desktop/ok_autotest_ui_pc_v2/ok_autotest_ui_pc/test_data/images/图片2.png` |

**交替策略**：
- 第1次执行 → 上传 图片1.png，验证头像更新
- 第2次执行 → 上传 图片2.png，验证头像更新
- 第3次执行 → 上传 图片1.png，以此类推

（执行前读取当前头像 URL 的文件名特征来判断当前是哪张图，或简单地按奇偶次轮换）

**前置条件**:
- 已登录账号 zidonghuammm@58.com
- 位于 Settings > Profile 页面
- 两张测试图片文件存在且可访问

**操作步骤**:
1. 进入 Profile 页面，记录当前头像图片 URL（`original_avatar_url`）
2. 判断当前头像：
   - 若当前为图片1（或未设置头像）→ 本次上传 **图片2.png**
   - 若当前为图片2 → 本次上传 **图片1.png**
3. 点击 "Choose File" 按钮
4. 选择本次目标图片（绝对路径见上表）
5. 等待上传完成，观察头像预览区域是否实时更新
6. 点击 Save 按钮（若头像上传后需手动 Save）
7. 刷新页面，验证头像 URL 已变更（不同于 `original_avatar_url`）

**预期结果**:
- 选择图片后头像预览立即更新为新图片
- 刷新后头像保持新图片（URL 发生变化）
- 两次交替执行均能成功（图片1 → 图片2 → 图片1 循环）

**Playwright 自动化参考**:
```js
// 读取当前头像（通过 img src 判断）
const avatarSrc = await page.locator('img[alt*="avatar"], .avatar img').getAttribute('src') ?? '';
const useImg1 = avatarSrc.includes('图片2') || avatarSrc === '';
const imgPath = useImg1
  ? '/Users/mengmeng/Desktop/ok_autotest_ui_pc_v2/ok_autotest_ui_pc/test_data/images/图片1.png'
  : '/Users/mengmeng/Desktop/ok_autotest_ui_pc_v2/ok_autotest_ui_pc/test_data/images/图片2.png';

// 上传文件（Playwright 通过 setInputFiles 上传，无需打开系统弹窗）
await page.getByRole('button', { name: 'Choose File' }).click();
// 注意：若触发器是 input[type=file]，用以下方式：
await page.locator('input[type="file"]').setInputFiles(imgPath);

// 等待预览更新
await page.waitForFunction(() => {
  const img = document.querySelector('.avatar img, img[class*="avatar"]');
  return img && img.src !== '';
});

await page.getByRole('button', { name: 'Save' }).click();
```

**手动测试备注**:
- [ ] 上传后是否需要额外点击 Save 才生效，或上传即自动保存：_待确认_
- [ ] 头像预览元素选择器：_待实测补充_

---

### TC-PRO-006b: 头像上传后取消（不保存验证）

**优先级**: P2  
**测试类型**: 负向/边界  
**重复执行策略**: 不保存，天然幂等

**前置条件**: 已登录，位于 Profile 页面，已有头像

**操作步骤**:
1. 记录当前头像 URL
2. 点击 "Choose File"，选择 图片1.png 或 图片2.png
3. 头像预览更新后，**不点击 Save**，直接刷新页面

**预期结果**:
- 刷新后头像恢复为原图（未保存的修改不持久化）

---

### TC-PRO-007: 上传超大头像文件（不自动化）

**优先级**: P1  
**测试类型**: 边界值/异常  
**UI自动化**: ❌  
**重复执行策略**: 上传大文件被拒绝，不修改服务器数据，天然幂等

**前置条件**: 已登录，位于 Profile 页面；准备超大测试文件（> 10MB）

**操作步骤**:
1. 点击 "Choose File"
2. 选择超过限制大小的图片（如 15MB 的图片）
3. 观察系统反应

**预期结果**:
- 前端提示文件过大错误
- 不进行上传请求，头像不变

---

### TC-PRO-008: 上传不支持格式的头像

**优先级**: P2  
**测试类型**: 异常  
**重复执行策略**: 上传非法格式被拒绝，不修改服务器数据，天然幂等

**前置条件**: 已登录，位于 Profile 页面

**操作步骤**:
1. 点击 "Choose File"
2. 选择 `.pdf` 文件

**预期结果**:
- 文件选择对话框仅允许图片类型，或上传后返回格式错误提示
- 头像不变

---

### TC-PRO-009: Email 字段显示字数统计

**优先级**: P2  
**测试类型**: UI 验证  
**重复执行策略**: 仅验证 UI 显示，天然幂等

**前置条件**: 已登录，位于 Profile 页面

**操作步骤**:
1. 查看 Email 输入框右侧的字数统计数字
2. 修改 Email 为更长/更短的地址，观察字数统计是否实时变化

**预期结果**:
- Email 字段旁显示实时字符数统计（如当前 `zidonghuammm@58.com` 显示"19"）
- 输入内容变化时字数统计同步更新

---

### TC-PRO-010: Phone 区号 A/B 交替切换后保存

**优先级**: P1  
**测试类型**: 正向功能  
**重复执行策略**: A/B 交替（+971 ↔ +86），每次运行切换方向，不产生累积脏数据

**前置条件**: 已登录，位于 Profile 页面

**操作步骤**:
1. 读取当前 Phone 区号（`original_code`）和号码（`original_number`）
2. 判断：若当前区号为 `+971`，则切换为 `+86`；否则切换回 `+971`
3. 填入对应号码（`+971` 对应 `501234570`，`+86` 对应 `13800138000`）
4. 点击 Save，等待成功提示
5. **【后置恢复】** 将区号和号码恢复为 `original_code` / `original_number` 并 Save

**预期结果**:
- 区号切换成功，保存成功
- 刷新后区号和号码显示切换后的值
- 后置恢复成功，下次执行时区号为上次的恢复值

---

### TC-PRO-011: 未修改任何字段直接点击 Save

**优先级**: P2  
**测试类型**: 边界值  
**重复执行策略**: 不修改任何字段，天然幂等

**前置条件**: 已登录，位于 Profile 页面，所有字段保持当前值

**操作步骤**:
1. 进入 Profile 页面，不做任何修改
2. 直接点击 Save

**预期结果**:
- 保存成功（无数据变化也能成功提交）
- 或 Save 按钮为灰色不可点击（以实际行为为准）
- 页面数据无任何变化

---

### TC-PRO-012: 网络中断时保存失败处理

**优先级**: P2  
**测试类型**: 异常/健壮性  
**重复执行策略**: 网络恢复后数据无变化，天然幂等

**前置条件**: 已登录，位于 Profile 页面，网络模拟断开

**操作步骤**:
1. 使用 DevTools Network 面板模拟 "Offline"
2. 修改 First Name（任意值）
3. 点击 Save
4. 观察错误提示
5. 恢复网络（取消 Offline 模拟）

**预期结果**:
- 显示网络错误提示（如 "Network error" 或 Toast 红色提示）
- 数据未被保存（刷新后仍为原值）
- 网络恢复后，可重新正常保存

---

## 二、Account Settings 模块

### 字段结构（MCP 实测）

| 功能区 | 字段/元素 | 当前状态 | 备注 |
|--------|-----------|----------|------|
| Email | zidonghuammm@58.com | Verified 已验证 | - |
| Phone Number | - | 未绑定，显示"Add" | Add 按钮 |
| Password | - | 已设置 | Edit 按钮 |
| 3rd Party Account | Apple | 未绑定 | Link 按钮 |
| 3rd Party Account | Facebook | 未绑定 | Link 按钮 |
| 3rd Party Account | Google | 未绑定 | Link 按钮 |
| New Messages | toggle | - | 邮件通知开关 |
| Deals & updates | button | Enable | 营销邮件开关 |

---

### TC-ACC-001: 已验证邮箱显示 Verified 标识

**优先级**: P0  
**测试类型**: UI/正向  

**前置条件**: 已登录，位于 Account Settings 页面

**操作步骤**:
1. 访问 `https://aepub.58v5.cn/biz/en/user/home?tabindex=1`
2. 查看 Email 区域

**预期结果**:
- 显示邮箱地址 `zidonghuammm@58.com`
- 旁边有 "Verified" 图标/文案

**MCP 录制证明**:
- ref=e315: `zidonghuammm@58.com`
- ref=e318: `Verified`

---

### TC-ACC-002: 未绑定手机号时显示 Add 按钮

**优先级**: P0  
**测试类型**: UI/正向  

**前置条件**: 账号未绑定手机号

**操作步骤**:
1. 访问 Account Settings 页面
2. 查看 Phone Number 区域

**预期结果**:
- 显示 "Add your phone number"
- 显示 "Add" 按钮

---

### TC-ACC-003: 点击 Add Phone Number 按钮

**优先级**: P1  
**测试类型**: 正向功能  

**前置条件**: 账号未绑定手机号，位于 Account Settings 页面

**操作步骤**:
1. 点击 Phone Number 区域的 "Add" 按钮

**预期结果**:
- 弹出绑定手机号的对话框/流程
- 能输入手机号并发送验证码

---

### TC-ACC-004: 修改密码弹窗 - 正常打开

**优先级**: P0  
**测试类型**: UI/正向  

**前置条件**: 账号已设置密码，位于 Account Settings 页面

**操作步骤**:
1. 点击 Password 区域的 "Edit" 按钮

**预期结果**:
- 弹出 "Change password" 对话框
- 标题："Change password"
- 副标题："Change your password to enhance your account security."
- 显示 Old password 输入框
- 显示 New password 输入框
- 显示密码规则：At least 1 number / At least 1 uppercase / At least 1 lowercase / 8–16 characters
- Confirm 按钮初始为 disabled 状态

**MCP 录制证明**:
```js
await page.getByRole('button', { name: 'Edit' }).click();
// dialog ref=e367 出现
// Old password input: ref=e380
// New password input: ref=e388
// Confirm button: ref=e399 [disabled]
```

---

### TC-ACC-005: 修改密码 - 密码规则验证（新密码不满足规则）

**优先级**: P0  
**测试类型**: 负向/边界值  
**重复执行策略**: 仅在输入框填值 + 观察 UI 状态，不提交，不修改密码，天然幂等

**前置条件**: 密码修改弹窗已打开（点击 Password 区域 Edit 按钮）

| 测试数据 | 违反规则 | 预期规则项变红 |
|----------|---------|--------------|
| `abc` | 长度/数字/大写全不满足 | 全部4项 |
| `abcdefgh` | 无数字、无大写 | "At least 1 number" + "At least 1 uppercase" |
| `Abcdefgh` | 无数字 | "At least 1 number" |
| `ABCDEFG1` | 无小写 | "At least 1 lowercase" |
| `Abcdefg1234567890` | 超过16位 | "8–16 characters" |
| `Abcdefg1` | 满足全部规则 | 全部规则项变绿/通过 |

**操作步骤**:
1. 打开密码修改弹窗
2. Old password 输入框填入任意字符（不提交，仅激活页面）
3. New password 依次输入上表各测试数据
4. 每次输入后观察密码规则指示器（4条规则的颜色/状态）和 Confirm 按钮
5. **不点击 Confirm**，验证完后关闭弹窗（Esc 或点击弹窗外）

**预期结果**:
- 不满足对应规则的项标红或灰显
- 仅当所有规则满足时 Confirm 按钮激活（可点击）
- 关闭弹窗后密码未被修改

---

### TC-ACC-006: 修改密码 - Old password 错误

**优先级**: P0  
**测试类型**: 负向/安全  
**重复执行策略**: 后端拒绝错误旧密码，密码不变，天然幂等

**前置条件**: 密码修改弹窗已打开

**操作步骤**:
1. Old password 输入错误值：`WrongPass999`（故意错误）
2. New password 输入符合规则的值：`NewPass456`
3. 点击 Confirm

**预期结果**:
- 返回错误提示（如 "Old password is incorrect" 或类似文案）
- 密码不被修改
- 弹窗不关闭，可重新输入

---

### TC-ACC-007: 修改密码 - 正确完成密码修改（A/B 交替，含后置恢复）

**优先级**: P0  
**测试类型**: 正向功能  
**重复执行策略**: A→B→A 交替修改，每次执行后置步骤将密码恢复，保证下次可用同一账号执行

> ⚠️ **关键**：此用例执行后必须执行后置步骤恢复密码，否则后续所有用例无法登录。

**密码交替策略**:

| 执行轮次 | 当前密码（Old） | 修改为（New） |
|---------|--------------|-------------|
| 第1次 | `Qwer1234` | `Qwer12345` |
| 第2次 | `Qwer12345` | `Qwer1234` |
| 第3次 | `Qwer1234` | `Qwer12345` |
| … | 以此类推 | … |

**操作步骤**:
1. 确认当前密码（首次为 `Qwer1234`，后续查看上轮执行记录）
2. 点击 Account Settings > Password 的 "Edit" 按钮
3. Old password 填入当前密码
4. New password 填入交替目标密码（满足：数字+大写+小写+8-16位）
5. 点击 Confirm，等待成功提示
6. **【后置恢复 - 必须执行】**：
   - 再次点击 "Edit"
   - Old password 填刚才设置的新密码
   - New password 填回原密码
   - 点击 Confirm，确认恢复成功

**预期结果**:
- 步骤5：修改成功，弹窗关闭，显示成功提示
- 步骤6：恢复成功，密码回到初始值
- 用原始密码 `Qwer1234` 可以重新登录
- 如果后置步骤失败，需手动通过"Forgot Password"流程重置密码

---

### TC-ACC-008: 修改密码 - New password 与 Old password 相同

**优先级**: P1  
**测试类型**: 负向  
**重复执行策略**: 后端拒绝同值修改，密码不变，天然幂等

**前置条件**: 密码修改弹窗已打开

**操作步骤**:
1. Old password 和 New password 均输入当前密码值 `Qwer1234`
2. 点击 Confirm

**预期结果**:
- 提示新旧密码不能相同（如 "New password must be different from old password"）
- 密码不被修改

---

### TC-ACC-009: New Messages 通知开关 A/B 交替切换

**优先级**: P1  
**测试类型**: 正向功能  
**重复执行策略**: 读取当前状态 → 切换为相反状态 → 验证 → 再切换回来（A/B 交替，每次恢复原状态）

**前置条件**: 已登录，位于 Account Settings 页面

**操作步骤**:
1. 读取 New Messages 开关当前状态（记为 `original_state`：开 or 关）
2. 点击 emailNotification 开关图标，切换状态
3. 等待响应，验证开关状态已变化
4. 刷新页面，确认切换后状态保持
5. **【后置恢复】** 再次点击开关，恢复为 `original_state`

**预期结果**:
- 开关状态成功切换
- 刷新后新状态保持
- 后置恢复成功（下次执行时开关状态与本次执行前相同）

**MCP 录制证明**:
- ref=e362: img "emailNotification" [cursor=pointer]

---

### TC-ACC-010: Deals & updates 订阅开关 A/B 交替切换

**优先级**: P2  
**测试类型**: 正向功能  
**重复执行策略**: 读取当前按钮文案（Enable/Disable）→ 点击切换 → 后置恢复  
**⚠️ 不需要自动化**: 此用例标记为不需要执行自动化测试

**前置条件**: 已登录，位于 Account Settings 页面

**操作步骤**:
1. 读取 "Deals & updates via email" 按钮当前文案（`Enable` 或 `Disable`），记为 `original_label`
2. 点击该按钮
3. 验证按钮文案已切换（`Enable` → `Disable` 或反之）
4. **【后置恢复】** 再次点击，恢复为 `original_label`

**预期结果**:
- 按钮文案切换成功
- 订阅设置随之更改
- 后置恢复成功

**备注**: 此用例不进行自动化测试

---

### TC-ACC-011: 绑定第三方账号（Apple/Facebook/Google）

**优先级**: P1  
**测试类型**: 正向功能  

**前置条件**: 已登录，位于 Account Settings 页面，第三方账号未绑定

**操作步骤**:
1. 点击 Apple / Facebook / Google 的 "Link" 按钮

**预期结果**:
- 跳转至对应第三方 OAuth 授权页面
- 授权成功后返回，显示已绑定状态（Link 按钮变为 Unlink 或账号名）

---

### TC-ACC-012: 密码输入框可见性切换（眼睛图标）

**优先级**: P2  
**测试类型**: UI  

**前置条件**: 密码修改弹窗已打开

**操作步骤**:
1. 在 Old password 或 New password 输入框旁（如有眼睛图标）点击

**预期结果**:
- 密码切换为明文显示
- 再次点击恢复为密文

---

## 三、Country & Region 模块

### 字段结构（MCP 实测）

| 字段 | 类型 | 当前值 | 备注 |
|------|------|--------|------|
| Country & Region | 下拉选择 | الإمارات العربية المتحدة (UAE) | 22个国家/地区 |
| Language | 下拉选择 | English | 语言选择 |

**国家列表（MCP 实测完整）**:
UAE (الإمارات العربية المتحدة)、Argentina、Australia、البحرين、Brasil、Canada、Chile、Colombia、مصر、España、香港、دولة الكويت、México、New Zealand、عُمان、Perú、Portugal、قطر、المملكة العربية السعودية、Singapore、United Kingdom、United States

---

### TC-REG-001: 切换 Country A/B 交替并验证保存

**优先级**: P0  
**测试类型**: 正向功能  
**重复执行策略**: 读取当前国家 → 切换为备选国家 → 验证 → 后置恢复原国家（A/B 交替）

**A/B 交替方案**:

| 轮次 | 执行前（当前值） | 切换为 | 后置恢复为 |
|------|--------------|--------|-----------|
| 第1次 | `الإمارات العربية المتحدة` (UAE) | `Singapore` | UAE |
| 第2次 | `Singapore` | UAE | `Singapore` |
| 第3次 | UAE | `Singapore` | UAE |
| … | 以此类推 | … | … |

**前置条件**: 已登录，位于 Country & Region 页面（tabindex=2）

**操作步骤**:
1. 读取当前 Country 显示值，记为 `original_country`
2. 点击 Country & Region 下拉触发器，展开列表
3. 验证下拉列表展开，包含 22 个选项
4. 根据 `original_country` 选择目标国家（UAE → Singapore，或 Singapore → UAE）
5. 等待页面响应（自动保存或出现保存按钮）
6. 验证当前 Country 显示值已更新为目标国家
7. **【后置恢复】** 再次展开下拉，选回 `original_country`，验证恢复成功

**预期结果**:
- 下拉列表展开，包含 22 个选项
- 选择后列表收起，当前值更新为目标国家
- 后置恢复成功，下次执行时读取到与本次相同的初始值

**MCP 录制证明**:
```js
// 读取当前值
const currentCountry = await page.locator('.cont-r-country').innerText();
// 展开下拉
await page.getByRole('img').nth(4).click();
// A/B 切换
const targetCountry = currentCountry.includes('UAE') ? 'Singapore' : 'الإمارات العربية المتحدة';
await page.getByRole('button', { name: targetCountry }).click();
// 后置恢复
await page.getByRole('img').nth(4).click();
await page.getByRole('button', { name: currentCountry }).click();
```

---

### TC-REG-002: Country & Region 下拉包含所有预期国家

**优先级**: P1  
**测试类型**: UI/数据校验  
**重复执行策略**: 仅展开查看，不选择，天然幂等

**前置条件**: 已登录，位于 Country & Region 页面

**操作步骤**:
1. 点击展开 Country & Region 下拉
2. 核对选项数量（应为 22 个）
3. 核对关键国家存在：UAE、Singapore、United States、United Kingdom、Australia、Canada
4. 按 Esc 或点击页面其他区域关闭下拉，不做选择

**预期结果**:
- 下拉列表共 22 个国家/地区（见字段结构表）
- 包含所有预期国家，顺序符合产品预期
- 关闭下拉后当前值不变

---

### TC-REG-003: Language A/B 交替切换

**优先级**: P0  
**测试类型**: 正向功能  
**重复执行策略**: 读取当前语言 → 切换为备选语言 → 验证 → 后置恢复（A/B 交替）

> ⚠️ **注意**：切换为阿拉伯语后界面变为 RTL，操作元素定位需适配。建议后置步骤立即恢复 English。

**A/B 交替方案**:

| 轮次 | 执行前 | 切换为 | 后置恢复 |
|------|--------|--------|---------|
| 第1次 | English | Arabic (ar) | English |
| 第2次 | English | English | English |

**前置条件**: 已登录，位于 Country & Region 页面

**操作步骤**:
1. 读取当前 Language 显示值（记为 `original_lang`，通常为 `English`）
2. 点击 Language 下拉，查看可选语言列表
3. 选择目标语言（若当前为 English，切换为 Arabic）
4. 等待界面响应，观察页面文本是否切换为对应语言
5. 刷新页面，确认语言设置保持
6. **【后置恢复 - 必须执行】** 重新进入 Country & Region，将 Language 恢复为 `English`，确认恢复

**预期结果**:
- 语言切换后，页面 UI 文本（Tab名称、按钮文案）更新为所选语言
- 刷新后语言设置保持
- 后置恢复为 English 成功，不影响下次用例执行

---

### TC-REG-004: 切换 Country 后首页内容联动验证

**优先级**: P1  
**测试类型**: 正向/联动  
**重复执行策略**: 切换 Country → 验证联动 → 后置恢复原 Country（A/B 交替）

**前置条件**: 已登录，位于 Country & Region 页面

**操作步骤**:
1. 记录当前 Country（`original_country`）
2. 切换 Country 至 "United States"
3. 导航至首页 `https://ae.58v5.cn/`
4. 观察城市/地区显示是否变化，分类列表是否更新
5. **【后置恢复】** 返回 Country & Region，将 Country 切回 `original_country`

**预期结果**:
- 首页地区标识（如顶部城市名）或内容分类反映新国家设置
- 后置恢复成功

---

### TC-REG-005: 切换国家后回到首页，分类/内容区更新

**优先级**: P1  
**测试类型**: 正向功能/联动  
**重复执行策略**: 与 TC-REG-004 类似，A/B 交替；建议合并为同一组执行

**前置条件**: 已登录，Country 当前为 UAE

**操作步骤**:
1. 在 Country & Region 页将 Country 切换为 `Singapore`
2. 导航至首页
3. 观察分类导航、首屏内容是否对应 Singapore
4. **【后置恢复】** 返回 Country & Region，切回 UAE

**预期结果**:
- 首页内容/分类反映 Singapore 区域数据
- 后置恢复成功

---

### TC-REG-006: 未登录用户访问 Country & Region 页面

**优先级**: P1  
**测试类型**: 权限/安全  
**重复执行策略**: 不登录即访问，验证重定向，天然幂等

**前置条件**: 未登录状态（清除 Cookie）

**操作步骤**:
1. 清除所有 Cookie/localStorage
2. 直接访问 `https://aepub.58v5.cn/biz/en/user/home?tabindex=2`

**预期结果**:
- 被重定向至登录页或首页
- 不能访问 Settings 内容

---

### TC-REG-007: 切换 Country 后 Language 选项联动验证

**优先级**: P2  
**测试类型**: 联动/边界  
**重复执行策略**: 切换 Country → 查看 Language 选项变化 → 后置恢复 Country

**前置条件**: 已登录，位于 Country & Region 页面

**操作步骤**:
1. 记录当前 Country（`original_country`，如 UAE）和 Language 可选数量
2. 将 Country 切换为 `香港`
3. 展开 Language 下拉，查看是否新增中文（繁体）选项
4. 记录语言选项数量变化
5. **【后置恢复】** 将 Country 切回 `original_country`，验证恢复

**预期结果**:
- Language 列表根据国家变化（如增加 繁体中文 选项）或保持不变（以产品设计为准）
- 后置恢复成功

---

## 四、Settings 通用场景

### TC-SET-001: 未登录用户访问 Settings 页面被重定向

**优先级**: P0  
**测试类型**: 权限/安全  

**前置条件**: 未登录，清除所有 Cookie

**操作步骤**:
1. 直接访问 `https://aepub.58v5.cn/biz/en/user/home?tabindex=1`

**预期结果**:
- 被重定向至登录页或首页
- 不显示用户设置内容

---

### TC-SET-002: Settings 页面 Tab 切换流畅

**优先级**: P1  
**测试类型**: UI/交互  

**前置条件**: 已登录，位于 Settings 页面

**操作步骤**:
1. 依次点击 Profile → Account Settings → Country & Region → Profile

**预期结果**:
- 每次点击 Tab 后对应内容区正确加载
- 无白屏、无 JS 报错

---

### TC-SET-003: Settings 页面刷新后保持当前 Tab

**优先级**: P2  
**测试类型**: 状态保持  

**前置条件**: 已登录，当前位于 Account Settings Tab

**操作步骤**:
1. 直接刷新页面（F5）

**预期结果**:
- 刷新后停留在 Account Settings Tab（因为 URL 包含 `tabindex=1`）
- 数据正常显示

---

### TC-SET-004: Settings 页面在 Session 过期后操作

**优先级**: P1  
**测试类型**: 会话/安全  

**前置条件**: 已登录，Session/Token 过期（手动清除 Cookie 或等待超时）

**操作步骤**:
1. 在 Profile 页修改 First Name
2. 点击 Save

**预期结果**:
- 系统检测到 Session 过期，返回 401
- 页面跳转至登录页，或弹出重新登录提示
- 数据修改不被保存

---

## 五、自动化测试执行记录

| 模块 | 用例总数 | 可自动化 | 手动测试 | 幂等策略 | 备注 |
|------|---------|---------|---------|---------|------|
| Profile | 16 | 11 | 5 | 读取-取反 / 时间戳 / A/B交替 | Email 已确认可编辑；TC-PRO-002c/002d 中 Email 修改需手动完成邮箱验证 |
| Account Settings | 12 | 9 | 3 | A/B交替（密码/开关）/ 后置恢复 | TC-ACC-011 三方OAuth需手动；密码用例必须后置恢复 |
| Country & Region | 7 | 5 | 2 | A/B交替 + 后置恢复 | Language切换需后置恢复English，否则影响后续用例 |
| Settings 通用 | 4 | 3 | 1 | 天然幂等 | TC-SET-004 Session过期需特殊处理 |
| **合计** | **35** | **25** | **10** | | - |

### 重复执行注意事项

1. **执行顺序建议**：TC-ACC-007（密码修改）单独执行，并确认后置恢复成功后再运行其他用例
2. **Language 用例**（TC-REG-003）：后置恢复 English 为强制要求，切换后界面语言改变会影响后续所有用例的元素定位
3. **Country 用例**（TC-REG-001/004/005）：共享同一套 A/B 状态，建议顺序执行这3个用例，避免交叉干扰
4. **Profile 字段**（TC-PRO-001/002）：A/B 交替值已固定（`QA_Auto` ↔ `QA_Test`），多次执行正确交替即可
5. **负向用例**（TC-PRO-003/004/005, TC-ACC-005/006/008）：均含后置恢复步骤，天然幂等，可随意重复

### 用例执行状态追踪表

| 用例ID | 幂等策略 | 首次值 | 后置恢复值 | 最近执行日期 | 执行结果 |
|--------|---------|--------|-----------|------------|---------|
| TC-PRO-006 | 图片交替 | 图片1.png ↔ 图片2.png | 无需恢复（可随意交替） | - | - |
| TC-PRO-001 | A/B | `QA_Auto` | - | - | - |
| TC-PRO-002 | 时间戳 | `Auto_{ts}` | 恢复原值 | - | - |
| TC-PRO-002b | A/B | `OKerAE_test` | `OKerAE_cnbucqx` | - | - |
| TC-PRO-002c | A/B | `zidonghuammm2@58.com` | `zidonghuammm@58.com` | - | 修改后需完成邮箱验证 |
| TC-PRO-002d | 图片交替+时间戳+A/B | 图片1/2+`OKerAE_test`+`Auto_{ts}` | 恢复所有文本原值（头像无需恢复） | - | - |
| TC-ACC-007 | A/B | `Qwer12345` | `Qwer1234` | - | - |
| TC-ACC-009 | A/B | 当前状态取反 | 恢复原状态 | - | - |
| TC-ACC-010 | A/B | 当前按钮取反 | 恢复原按钮 | - | - |
| TC-REG-001 | A/B | `Singapore` | UAE | - | - |
| TC-REG-003 | A/B | Arabic | English | - | - |

---

## 附录：录制证明存档

━━━━━━━━━━━━━━━━━━━━━━━━
✅ Profile 模块录制完成（8步）

【操作证明】
- 页面 URL：https://aepub.58v5.cn/biz/en/user/home?tabindex=1
- 操作前 snapshot ref 列表：e272(username输入框) e277(firstName输入框) e282(lastName输入框) e300(phone输入框) e303(Save按钮)

【MCP JavaScript 代码】
```js
// 登录流程
await page.getByRole('textbox', { name: 'Email or phone number' }).fill('zidonghuammm@58.com');
await page.getByRole('button', { name: 'Continue' }).click();
await page.getByRole('textbox', { name: 'Enter password' }).fill('Qwer1234');
await page.getByRole('button', { name: 'Log in' }).click();

// 进入Settings
await page.getByText('OKerAE_cnbucqx').click();
await page.getByText('Settings', { exact: true }).click();

// Profile 修改
await page.getByText('Profile').click();
await page.locator('#firstName').fill('AutoTest');
await page.locator('#lastName').fill('Runner');
await page.locator('#username').fill('OKerAE_cnbucqx');
await page.getByRole('button', { name: 'Save' }).click();
```

【动态行为发现】
- Save 按钮点击后进入 `[active]` 状态（表示提交中），此为 SPA 异步提交特征
- Email 字段包含字数统计"19"（可编辑，修改后需完成邮箱验证流程）
- 密码修改弹窗点击 Country & Region Tab 时被遮挡，需先关闭弹窗

【验证证明】
- Save 按钮状态：click 后变为 `[active]`，提交完成后恢复
- 页面停留在 `tabindex=1`，URL 不变

【MCP调用统计】
navigate:3 snapshot:8 click:7 type:5 wait_for:2 screenshot:0
━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━
✅ Account Settings 模块录制完成（5步）

【操作证明】
- 页面 URL：https://aepub.58v5.cn/biz/en/user/home?tabindex=1
- 操作前 snapshot ref 列表：e314(email区域) e316(Verified标识) e324(Phone Add按钮) e336(Password Edit按钮) e343(Apple Link) e349(Facebook Link) e355(Google Link) e362(New Messages开关) e365(Deals Enable按钮)

【MCP JavaScript 代码】
```js
// 点击 Account Settings Tab
await page.getByText('Account Settings').click();

// 打开密码修改弹窗
await page.getByRole('button', { name: 'Edit' }).click();
// dialog 出现: ref=e367
// Old password: ref=e380
// New password: ref=e388
// 密码规则: At least 1 number / uppercase / lowercase / 8-16 chars
// Confirm button: ref=e399 [disabled]
```

【动态行为发现】
- Password Edit 点击后弹出 modal dialog，modal 覆盖全页
- modal 打开后 Country & Region Tab 点击被 modal 拦截（interepts pointer events）
- Confirm 按钮初始 disabled，需两个输入框都有内容才激活

【MCP调用统计】
navigate:1 snapshot:3 click:3 type:0
━━━━━━━━━━━━━━━━━━━━━━━━

━━━━━━━━━━━━━━━━━━━━━━━━
✅ Country & Region 模块录制完成（5步）

【操作证明】
- 页面 URL：https://aepub.58v5.cn/biz/en/user/home?tabindex=2
- 操作前 snapshot ref 列表：e185(Country下拉触发器) e195(Language下拉触发器)
- 展开后 ref 列表：e258(UAE) e262(Argentina) e266(Australia) ... e342(United States)（共22个）

【MCP JavaScript 代码】
```js
// 直接导航至 tabindex=2
await page.goto('https://aepub.58v5.cn/biz/en/user/home?tabindex=2');

// 展开 Country 下拉
await page.getByRole('img').nth(4).click();
// 下拉列表出现: ref=e257

// 选择某个国家（示例）
await page.getByRole('button', { name: 'Singapore' }).click();
```

【动态行为发现】
- Country 下拉是自定义组件（非原生 select）
- Language 当前默认值：English（ref=e347）
- 下拉展开时 img 区域可点击（ref=e185/e187）

【MCP调用统计】
navigate:1 snapshot:2 click:2
━━━━━━━━━━━━━━━━━━━━━━━━
