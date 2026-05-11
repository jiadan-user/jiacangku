# OK招聘 - B端职位发布功能简化（PC）测试用例

## 测试环境配置

| 配置项 | 值 |
| --- | --- |
| 站点 | SG (默认)；BR/MX/ES/AE/US/HK 等多站点 |
| Base URL | https://sgpub.58v5.cn |
| 发布入口 | https://sgpub.58v5.cn/biz/en/publish/front |
| 个人信息填写页 | https://sgpub.58v5.cn/biz/en/zpInfo/profile?fromUrl=%2Fpublish%2Fjob%3FcategoryId%3D6000 |
| 测试账号1 | wang@58.com / Qwer1234 (有UMC邮箱) |
| 测试账号2 | 91234567 / Qwer1234 (无UMC邮箱) |
| 测试账号3 | wangyongli@58.com / Qwer1234 (职位发布) |
| 测试账号4（公司信息模块实测） | wyl@58.com / Qwer1234 |
| Figma | https://www.figma.com/design/mJX31vs3bhzNlRRI43ym18/招聘?node-id=1296-2 |
| 总用例数 | 84条 |
| 可自动化 | 66条 (79%) |
| pytest 自动化标识 | 每条用例正文含 `case_id_sg_biz_job_publish_<tc>`（`<tc>` 为文档 TC 编号的小写形式，子编号如 TC011-1 映射为 `tc011_1`），对应 `@pytest.mark.case_id_*`，规则见 `ok_autotest_ui_skill/references/identifier-rules.md` |

## 一、个人信息 - 头像自动生成

### TC001: 头像自动生成-Last Name有值时取Last Name首字符

**自动化标识**：`case_id_sg_biz_job_publish_tc001`

**前置条件**：
- B端账号已注册，Last Name 为 "Garcia"，First Name 为 "Juan"
- 测试账号：wang@58.com / Qwer1234
- 首次发布触发个人信息填写页

**执行步骤**：
1. 登录账号，点击发布职位入口
2. 进入个人信息填写页,填写Last Name 为 "Garcia"，First Name 为 "Juan"
3. 从数据库查询该账号对应记录的 `head_pic_url` 字段值
4. 访问 `head_pic_url` 对应的图片链接，校验可访问性与图片元信息（HTTP 状态、`Content-Type`、尺寸可解析）

**预期结果**：
- `head_pic_url` **非空**，表示已生成头像图片并落库
- `head_pic_url` 链接可访问：HTTP 200，`Content-Type` 为 `image/*`，图片尺寸信息可正常解析
- 图片内容符合“文字头像”预期：展示字母 **"G"**（Last Name "Garcia" 的首字符），且字母为**大写**
- 背景色符合“uid尾号决定”的规则（同一账号多次查询/拉取图片，背景样式不应随机变化）

**优先级**：P0

**测试类型**：功能测试

**UI自动化**：⚠️ 半自动化

---

### TC004: 头像自动生成-小写字母强制转为大写

**自动化标识**：`case_id_sg_biz_job_publish_tc004`

**前置条件**：
- 账号 Last Name 为 "zhang"（全小写）
- 测试账号：yongli@58.com / Qwer1234

**执行步骤**：
1. 进入个人信息填写页，填写Last Name 为 "zhang"（全小写）
2. 从数据库查询该账号对应记录的 `head_pic_url` 字段值
3. 访问 `head_pic_url` 对应的图片链接，校验可访问性与图片元信息（HTTP 状态、`Content-Type`、尺寸可解析）

**预期结果**：
- `head_pic_url` **非空**，表示已生成头像图片并落库
- `head_pic_url` 链接可访问：HTTP 200，`Content-Type` 为 `image/*`，图片尺寸信息可正常解析
- 图片内容符合“文字头像”预期：展示字母 **"Z"**（由 "zhang" 首字符转大写），且字母为**大写**

**优先级**：P1

**测试类型**：功能测试

**UI自动化**：⚠️ 半自动化

---

### TC006: 头像自动生成-移除上传入口验证

**自动化标识**：`case_id_sg_biz_job_publish_tc006`

**前置条件**：
- 首次发布，进入个人信息填写页

**执行步骤**：
1. 观察头像区域是否存在上传按钮/点击上传入口

**预期结果**：
- 头像区域无上传入口
- 头像不可点击/不触发上传操作
  - 备注：该用例为 UI 交互验证；若当前版本“前端不展示头像/无头像入口”，可仅保留为回归检查项或标记为不适用（按实际页面形态执行）

**优先级**：P0

**测试类型**：UI测试

**UI自动化**：✅ 可自动化

---

### TC007: 头像背景色-相同uid尾号每次刷新颜色一致

**自动化标识**：`case_id_sg_biz_job_publish_tc007`

**前置条件**：
- 使用固定账号登录

**执行步骤**：
1. 从数据库查询该账号对应记录的 `head_pic_url` 字段值
2. 连续拉取同一 `head_pic_url` 图片至少 2 次（间隔 1-2s）
3. 对比两次返回图片内容的一致性（哈希一致/像素一致/人工比对其背景样式一致）

**预期结果**：
- 同一账号在同一规则下生成的头像背景样式应保持一致（不应随机变化）
- 若使用图片一致性校验：同一 `head_pic_url` 多次获取的图片内容应一致（允许服务端加时间戳参数导致 URL 不同，但最终展示效果需一致）

**优先级**：P1

**测试类型**：功能测试

**UI自动化**：⚠️ 半自动化

---

## 二、个人信息 - Email字段

### TC008: Email-UMC有email时自动同步

**自动化标识**：`case_id_sg_biz_job_publish_tc008`

**前置条件**：
- 账号在UMC中已存在邮箱：测试账号 wang@58.com / Qwer1234

**执行步骤**：
1. 首次发布，进入个人信息填写页
2. 观察Email字段

**预期结果**：
- Email字段已自动填写 wang@58.com
- 字段可见（首次填写页）

**优先级**：P0

**测试类型**：功能测试

**UI自动化**：✅ 可自动化

---

### TC009: Email-UMC无email时字段为必填且为空

**自动化标识**：`case_id_sg_biz_job_publish_tc009`

**前置条件**：
- 账号在UMC中无邮箱：测试账号 91234567 / Qwer1234

**执行步骤**：
1. 登录完成，进入个人信息填写页
2. 观察Email字段状态

**预期结果**：
- Email字段为空
- 字段标注必填
- 未填写时不允许提交

**优先级**：P0

**测试类型**：功能测试

**UI自动化**：✅ 可自动化

---

### TC010: Email-格式校验-无效格式提交

**自动化标识**：`case_id_sg_biz_job_publish_tc010`

**前置条件**：
- UMC无邮箱，需手动填写：测试账号 91234567 / Qwer1234

**执行步骤**：
1. Email字段输入 "test_invalid"（无@域名）
2. 点击确认按钮

**预期结果**：
- 提交失败，Email下方显示格式错误提示
- 不允许进入发布页

**优先级**：P0

**测试类型**：负向/功能

**UI自动化**：✅ 可自动化

---

### TC011: Email-修改email

**自动化标识**：`case_id_sg_biz_job_publish_tc011`

**前置条件**：
- 账号在UMC中已存在邮箱：测试账号 wang@58.com / Qwer1234

**执行步骤**：
1. 首次发布，进入个人信息填写页
2. 观察Email字段:Email字段已自动填写 wang@58.com
3. 点击邮箱后面的edit按钮

**预期结果**：
- 弹出Edit Your Email弹窗
- Email字段已自动填写 wang@58.com
- 邮箱可以被清空，重新填写
- 清空邮箱后，send按钮应该置灰不可点击，或者点击后提示先输入邮箱内容？

**优先级**：P0

**测试类型**：配置/功能

**UI自动化**：⚠️ 半自动化

---

### TC011-1: Email-修改email-验证码输入后confirm按钮高亮

**自动化标识**：`case_id_sg_biz_job_publish_tc011_1`

**前置条件**：
- 账号在UMC中已存在邮箱：测试账号 wang@58.com / Qwer1234
- 已进入 Edit Your Email 弹窗

**执行步骤**：
1. 首次发布，进入个人信息填写页
2. 点击邮箱后面的edit按钮，弹出Edit Your Email弹窗
3. 清空原邮箱，重新填写新邮箱（如 newemail@58.com）
4. 点击send按钮发送验证码
5. 输入收到的邮箱验证码

**预期结果**：
- 验证码输入完成后，confirm按钮从灰色变为高亮状态
- confirm按钮可点击

**优先级**：P0

**测试类型**：配置/功能

**UI自动化**：⚠️ 半自动化

---

### TC011-2: Email-修改email-确认后弹窗关闭并回显新邮箱

**自动化标识**：`case_id_sg_biz_job_publish_tc011_2`

**前置条件**：
- 账号在UMC中已存在邮箱：测试账号 wang@58.com / Qwer1234
- 已在 Edit Your Email 弹窗中填写新邮箱并输入验证码

**执行步骤**：
1. 首次发布，进入个人信息填写页
2. 点击邮箱后面的edit按钮，弹出Edit Your Email弹窗
3. 清空原邮箱，重新填写新邮箱（如 newemail@58.com）
4. 点击send按钮发送验证码
5. 输入收到的邮箱验证码
6. 点击confirm按钮

**预期结果**：
- 弹窗关闭
- 页面回显修改后的邮箱（newemail@58.com）
- Email字段显示最新的邮箱地址

**优先级**：P0

**测试类型**：配置/功能

**UI自动化**：⚠️ 半自动化

---

### TC011-3: Email-修改email

**自动化标识**：`case_id_sg_biz_job_publish_tc011_3`

**前置条件**：
- 账号在UMC中已存在邮箱：测试账号 wang@58.com / Qwer1234

**执行步骤**：
1. 首次发布，进入个人信息填写页
2. 观察Email字段:Email字段已自动填写 wang@58.com
3. 点击邮箱后面的edit按钮，弹出Edit Your Email弹窗后，修改邮箱内容，不点击confirm，直接点击叉号关闭弹窗

**预期结果**：
- 弹窗关闭
- Email内容不变，还是 wang@58.com

**优先级**：P0

**测试类型**：配置/功能

**UI自动化**：✅ 可自动化

---

## 三、个人信息 - WhatsApp模块

### TC012: WhatsApp-巴西站点可见-模块正常显示

**自动化标识**：`case_id_sg_biz_job_publish_tc012`

**前置条件**：
- 使用巴西站点（brpub.58v5.cn）
- 首次发布，进入个人信息填写页
- 测试账号：

**执行步骤**：
1. 观察WhatsApp输入框与勾选框是否展示

**预期结果**：
- WhatsApp输入框可见
- 勾选框及文案"Check this to reply to candidates via WhatsApp"可见

**优先级**：P0

**测试类型**：配置/功能

**UI自动化**：✅ 可自动化

---

### TC014: WhatsApp-非BR/MX站点不可见且内容上移

**自动化标识**：`case_id_sg_biz_job_publish_tc014`

**前置条件**：
- 使用sg站点，访问https://sgpub.58v5.cn/biz/en/zpInfo/profile?fromUrl=%2Fpublish%2Fjob%3FcategoryId%3D6000

**执行步骤**：
1. 进入个人信息填写页
2. 观察WhatsApp模块是否存在

**预期结果**：
- WhatsApp输入框和勾选框均不可见
- 下方内容自动上移，无空白区域

**优先级**：P0

**测试类型**：配置/负向

**UI自动化**：✅ 可自动化

---

### TC015: WhatsApp勾选框-输入框为空时不可点击

**自动化标识**：`case_id_sg_biz_job_publish_tc015`

**前置条件**：
- 巴西站，WhatsApp输入框为空

**执行步骤**：
1. 点击WhatsApp勾选框
2. 观察勾选框状态变化

**预期结果**：
- 勾选框为不可点击状态（disabled/灰色）
- 点击无响应

**优先级**：P0

**测试类型**：交互/功能

**UI自动化**：✅ 可自动化

---

### TC016: WhatsApp勾选框-输入框有值时可点击且默认勾选

**自动化标识**：`case_id_sg_biz_job_publish_tc016`

**前置条件**：
- 巴西站，WhatsApp输入框已输入有效号码
- 该国家需要配置WhatsApp勾选框默认勾选

**执行步骤**：
1. 输入WhatsApp号码
2. 观察勾选框状态

**预期结果**：
- 勾选框变为可点击状态
- 处于勾选状态

**优先级**：P0

**测试类型**：交互/功能

**UI自动化**：✅ 可自动化

---

### TC017: WhatsApp勾选框-输入号码后再清空，勾选框恢复不可点击

**自动化标识**：`case_id_sg_biz_job_publish_tc017`

**前置条件**：
- 巴西站，WhatsApp已输入号码（勾选框可用）

**执行步骤**：
1. 清空WhatsApp输入框
2. 观察勾选框状态

**预期结果**：
- 勾选框恢复为不可点击状态

**优先级**：P1

**测试类型**：交互/边界

**UI自动化**：✅ 可自动化

---

### TC018: WhatsApp-勾选框文案完整性验证

**自动化标识**：`case_id_sg_biz_job_publish_tc018`

**前置条件**：
- 巴西站，WhatsApp模块可见

**执行步骤**：
1. 观察勾选框下方说明文案

**预期结果**：
- 主文案：Check this to reply to candidates via WhatsApp
- 副文案：Once selected, you will receive instant notifications on WhatsApp and can reply directly. You can update this setting in your profile.
- 文案完整，无截断

**优先级**：P1

**测试类型**：UI/文案

**UI自动化**：✅ 可自动化

---

### TC019: WhatsApp-号码格式校验-无效格式

**自动化标识**：`case_id_sg_biz_job_publish_tc019`

**前置条件**：
- 巴西站，WhatsApp输入框可输入
- 测试账号：wangyongli@58.com / Qwer1234（与批次2 WhatsApp 用例一致）

**执行步骤**：
1. 登录后访问雇主信息页：`https://brpub.58v5.cn/biz/en/zpInfo/profile?fromUrl=%2Fpublish%2Fjob%3FcategoryId%3D6000`
2. 填写必填项：First name、Last name、公司全名（可搜索并选择 `+58.com` 等联想项）
3. 在 WhatsApp（+55）输入框输入无效号码如 `123456789099`（位数超长）
4. 点击 Confirm 提交

**预期结果**：
- 提交失败，显示格式错误提示
- 同手机号校验逻辑

**实测记录**：
- **2026-05-09 首轮补录**：按上述步骤实测 **提交未失败**，直接进入 `/publish/job?categoryId=6000`，**未出现** WhatsApp 格式错误提示；已记为缺陷登记，见 run `run-biz-job-publish-20260508` 之 `bug_list.md` / `proofs/tc019-recording-rerun-proof.yml`。
- **2026-05-09 二次重录（playwright-cli，会话 `tc019-biz-job-publish-rerun`）**：使用账号 `wangyongli@58.com` 登录 BR 站后复现相同步骤（无效 WA `123456789099` + Confirm），**结果一致**：URL 变为 `https://brpub.58v5.cn/biz/en/publish/job?categoryId=6000`，页面为 Job Basics（Post），**仍无** WhatsApp 格式校验失败提示。证明：`recordings/tc019-rerun-20260509-after-confirm.png`、`recordings/tc019-rerun-20260509-post-submit-page.yml`（相对本 Markdown 所在目录 `zhaopin/`）。

**优先级**：P1

**测试类型**：负向/边界

**UI自动化**：✅ 可自动化

---

### TC072: WhatsApp勾选框默认状态-配置为默认不勾选时验证

**自动化标识**：`case_id_sg_biz_job_publish_tc072`

**前置条件**：
- 西班牙站，WhatsApp模块可见
- 该国家需要配置WhatsApp勾选框为不默认勾选
- 测试账号：wang@58.com / Qwer1234

**执行步骤**：
1. 访问：https://espub.58v5.cn/biz/en/zpInfo/profile?fromUrl=%2Fpublish%2Fjob%3FcategoryId%3D4000
2. 进入个人信息填写页
3. 输入有效 WhatsApp 号码（使勾选框进入可点击状态）
4. 不手动操作勾选框
5. 断言 `[data-testid="whatsapp-checkbox"]` 的 `checked` 属性为 `false`

**预期结果**：
- 勾选框初始状态为未勾选（`checked === false`）

**优先级**：P1

**测试类型**：配置

**UI自动化**：✅ 可自动化

---

### TC088: 非必填

**自动化标识**：`case_id_sg_biz_job_publish_tc088`

**前置条件**：
- 使用未提交过雇主信息的新账号（或可用于首次雇主信息提交的账号）
- ES 站（WhatsApp 模块可见，便于确认未填 WA 仍可提交）
- 测试账号：wang1@58.com / Qwer1234 （userid=796582628244985888）

**执行步骤**：
1. 访问雇主信息填写页：https://espub.58v5.cn/biz/en/zpInfo/profile?fromUrl=%2Fpublish%2Fjob%3FcategoryId%3D6000（未登录则通过页头「Log in / Register」使用 wang1@58.com / Qwer1234 完成登录）
2. 填写必填字段：First Name、Last Name；在「Search the full name of the company」中输入并选择匹配公司（实测可选用 `+58.com` 联想项）
3. **不填写 WhatsApp 号码**（保持空白，不勾选 WA 勾选框）
4. 点击 Confirm 按钮提交

**预期结果**：
- 提交成功，跳转到职位发布页（`/publish/job?categoryId=6000`，与 `fromUrl` 一致）
- 无 WhatsApp 必填校验错误
- WhatsApp 字段确认为非必填项

**优先级**：P1

**测试类型**：配置/功能

**UI自动化**：✅ 可自动化

---

## 四、公司信息模块

> **实测说明（SG，`zpInfo/profile`，账号 wyl@58.com / Qwer1234，2026-05-09 playwright-cli 录制）**：页面在同一屏展示 **Recruiter Information** 与 **Company Information**。公司区块文案为 *「By searching for the company's full name, you can join an existing company or create a new one.」*；可见字段为 **Search the full name of the company**（必填，`#companyFullName`）与 **Company Logo**（Choose File，格式 PNG/JPG/SVG）。输入关键字后出现下拉联想；可选已有公司行，或点击 **`+{关键字}`** 创建新公司（创建后展示 Logo 上传区）。**未发现独立「Display Name」输入框**——若其他站点/版本仍有展示名能力，请按环境拆分用例，勿与本条 SG 实测混写。

### TC021: 公司信息-联想选择已有公司后全称回填

**自动化标识**：`case_id_sg_biz_job_publish_tc021`

**前置条件**：
- 已登录 SG B 端（示例：`wyl@58.com` / `Qwer1234`）
- 已进入雇主信息页：`https://sgpub.58v5.cn/biz/en/zpInfo/profile?fromUrl=%2Fpublish%2Fjob%3FcategoryId%3D6000`

**执行步骤**：
1. 定位 **Company Information** 区块
2. 在公司全称搜索框（label：`Search the full name of the company`）输入可命中联想的片段（实测示例：`+58`）
3. 在下拉列表中点击一条已有公司（实测示例：`58 RECRUITMENT PTE. LTD.`）

**预期结果**：
- 搜索框回填所选公司的**完整法定名称**（与列表项一致）
- **Company Logo** 区域展示（含 Choose File / 占位图），上传格式提示为 `PNG, JPG, or SVG`

**优先级**：P0

**测试类型**：功能

**UI自动化**：✅ 可自动化

---

### TC022: 公司信息-通过「+关键字」创建新公司并展示 Logo

**自动化标识**：`case_id_sg_biz_job_publish_tc022`

**前置条件**：
- 同 TC021 登录与入口

**执行步骤**：
1. 在公司全称搜索框输入**尚未存在/可创建**的名称（实测示例：`TestCompanyWYL`）
2. 点击下拉中的 **`+TestCompanyWYL`** 按钮（按钮文案为 `+` 与输入关键字拼接）

**预期结果**：
- 搜索框保留该新建公司名称
- **Company Logo** 上传区可见，且提示格式为 `PNG, JPG, or SVG`

**优先级**：P1

**测试类型**：功能

**UI自动化**：✅ 可自动化

---

### TC023: 公司信息-公司全称搜索必填（HTML5 校验）

**自动化标识**：`case_id_sg_biz_job_publish_tc023`

**前置条件**：
- 同 TC021；Recruiter Information 中 First/Last name 为空（或与下列步骤一致保持未填）

**执行步骤**：
1. 保持 **First name**、**Last name** 为空（或未满足必填）
2. 保持 **Search the full name of the company** 为空（清空或未选择）
3. 点击 **Confirm**

**预期结果**：
- 页面不跳转，停留在当前雇主信息页
- First name / Last name / 公司搜索框下方出现校验提示（实测为 **`Please fill out this field.`**，公司行旁有 **error** 图标）
- 交互层表现为浏览器原生必填校验（非异步 toast 亦可接受，以线上为准）

**优先级**：P0

**测试类型**：负向/功能

**UI自动化**：✅ 可自动化

---

### TC024: 再次编辑-公司全称可重新搜索并更换

**自动化标识**：`case_id_sg_biz_job_publish_tc024`

**前置条件**：
- 账号已完成**首次**雇主信息提交（Recruiter + Company Information 已 Confirm 成功）
- 可通过发布入口或其他雇主信息编辑路径进入 **再次编辑**（与「七、再次编辑个人信息和公司信息」、TC091 入口一致；页面仍为 `zpInfo/profile` 或线上等价雇主信息页）

**执行步骤**：
1. 进入雇主信息**再次编辑**页，定位 **Company Information**
2. 在公司全称搜索框（`#companyFullName`）内重新输入关键字，**更换绑定实体**：  
   - 从联想列表选择**与首次不同的**已有公司；或  
   - 使用 **`+关键字`** 创建/绑定另一家新公司（关键字与首次已选公司区分）
3. （可选）更新 **Company Logo**
4. 点击 **Confirm** 保存

**预期结果**：
- 提交成功，无因「仅首次允许填写」类逻辑错误阻断（若业务禁止更换主体，应以线上明确拦截文案为准，并单独记录为缺陷或拆分反向用例）
- 再次进入同一编辑页：`Search the full name of the company` 展示**最近一次保存**的公司全称（与步骤 2 所选一致）
- 若可从职位列表/详情核对雇主展示名：应与更新后的公司信息一致（口径与业务展示字段一致即可）

**优先级**：P1

**测试类型**：功能/持久化

**UI自动化**：✅ 可自动化

---

### TC024-1: 公司信息-公司 Logo 真实选择文件并预览更新

**自动化标识**：`case_id_sg_biz_job_publish_tc024_1`

**前置条件**：
- 同 TC021 登录与入口
- 已选/已创建公司，**Company Logo** 区域已展示（含 **Choose File** 与 `input.upload-input`；参见 TC021、TC022）
- 准备符合格式的本地图片用于上传（**录制/自动化夹具**见：`bundled/knowledge_base/文本用例/zhaopin/company_info_recording_20260509/fixtures/logo_upload_fixture.png`，可替换为同类型其它 `PNG`/`JPG`/`SVG`）

**执行步骤**：
1. 在 **Company Information** 中完成公司选择，使 **Company Logo** 区域出现
2. **必须**通过以下任一方式将**真实本地文件**绑定到上传控件（不得省略本步）：
   - 手工：点击 **Choose File** 或点击 Logo 预览区，在系统文件选择器中选择一张 `PNG`/`JPG`/`SVG`
   - 自动化脚本：对 `input.upload-input` 使用 `setInputFiles(绝对路径)`（与 Playwright 规范一致；夹具路径见前置条件）
3. 观察 Logo 预览区 **src/预览图已更新**（与所选文件一致或经上传后返回的 URL）
4. 填写 **First name**、**Last name** 等其余必填项后，点击 **Confirm** 保存（完成当前雇主信息表单允许的提交路径）

**预期结果**：
- 步骤 2 执行后，页面出现**新文件对应**的 Logo 预览（非仅层级拦截/无反馈）
- **Confirm** 保存成功或进入下一流程后，Logo 预览与线上展示与本次上传一致（允许 CDN 地址变化，**文件名/资源**可区分于默认占位图）

**优先级**：P1

**测试类型**：功能/UI

**UI自动化**：✅ 可自动化

---

## 五、首次填写提交与状态持久化

### TC025: 首次提交成功后再次点击发布不弹出个人/公司信息页

**自动化标识**：`case_id_sg_biz_job_publish_tc025`

**前置条件**：
- 已完成首次个人信息+公司信息提交

**执行步骤**：
1. 再次点击发布职位入口
2. 观察是否弹出个人/公司信息填写页

**预期结果**：
- 直接进入职位发布页（Job Basic）
- 不再弹出个人/公司信息填写页

**优先级**：P0

**测试类型**：功能/会话

**UI自动化**：✅ 可自动化

---

### TC026: 首次提交成功后刷新页面再点击发布仍不弹出

**自动化标识**：`case_id_sg_biz_job_publish_tc026`

**前置条件**：
- 已完成首次提交

**执行步骤**：
1. 刷新页面
2. 再次点击发布职位
3. 观察跳转

**预期结果**：
- 直接进入职位发布页

**优先级**：P1

**测试类型**：会话/持久化

**UI自动化**：✅ 可自动化

---

### TC027: 未完成首次提交中途退出后再次点击发布仍弹出填写页

**自动化标识**：`case_id_sg_biz_job_publish_tc027`

**前置条件**：
- 进入个人信息页未提交，直接关闭弹窗/返回

**执行步骤**：
1. 再次点击发布职位入口

**预期结果**：
- 仍弹出个人/公司信息填写页

**优先级**：P1

**测试类型**：异常流/会话

**UI自动化**：✅ 可自动化

---

## 六、职位发布-Job Basic（页面1）

### TC034: Job Basic-默认值-Workplace Type默认Onsite

**自动化标识**：`case_id_sg_biz_job_publish_tc034`

**前置条件**：
- 测试账号：wangyongli@58.com / Qwer1234
- 进入职位发布 Job Basic 页面

**执行步骤**：
1. 观察 Workplace type 字段默认选中项

**预期结果**：
- Workplace type 默认选中 "Onsite"

**优先级**：P0

**测试类型**：功能/默认值

**UI自动化**：✅ 可自动化

---

### TC035: Job Basic-默认值-Job Type默认Full-time

**自动化标识**：`case_id_sg_biz_job_publish_tc035`

**前置条件**：
- 测试账号：wangyongli@58.com / Qwer1234
- 进入职位发布 Job Basic 页面

**执行步骤**：
1. 观察 Job type 字段默认选中项

**预期结果**：
- Job type 默认选中 "Full-time"

**优先级**：P0

**测试类型**：功能/默认值

**UI自动化**：✅ 可自动化

---

### TC036: Job Basic-Job title必填校验

**自动化标识**：`case_id_sg_biz_job_publish_tc036`

**前置条件**：
- 测试账号：wangyongli@58.com / Qwer1234
- 进入 Job Basic 页面

**执行步骤**：
1. 不填写 Job title
2. 点击下一步/提交

**预期结果**：
- 校验失败，Job title 必填提示

**优先级**：P0

**测试类型**：负向/功能

**UI自动化**：✅ 可自动化

---

### TC037: Job Basic-Workplace type三选项均可选中

**自动化标识**：`case_id_sg_biz_job_publish_tc037`

**前置条件**：
- 测试账号：wangyongli@58.com / Qwer1234
- 进入 Job Basic 页面

**执行步骤**：
1. 依次点击 Onsite、Hybrid、Remote
2. 观察选中状态变化

**预期结果**：
- 每个选项均可单独选中
- 选中后样式高亮，其他选项取消选中

**优先级**：P1

**测试类型**：功能/交互

**UI自动化**：✅ 可自动化

---

### TC038: Job Basic-Job type四选项均可选中

**自动化标识**：`case_id_sg_biz_job_publish_tc038`

**前置条件**：
- 测试账号：wangyongli@58.com / Qwer1234
- 进入 Job Basic 页面

**执行步骤**：
1. 依次点击 Full-time、Part-time、Contract、Internship、Temporary
2. 观察选中状态

**预期结果**：
- 各选项均可选中，单选逻辑正常

**优先级**：P1

**测试类型**：功能

**UI自动化**：✅ 可自动化

---

### TC039: Job Basic-Salary range选填必填

**自动化标识**：`case_id_sg_biz_job_publish_tc039`

**前置条件**：
- 测试账号：wangyongli@58.com / Qwer1234
- Job title、job function、workplace type、location、job type 已填写
- Salary range 不填

**执行步骤**：
1. 点击continue

**预期结果**：
- 无法提交，Salary range 下方有红色提示文案

**优先级**：P1

**测试类型**：功能/边界

**UI自动化**：✅ 可自动化

---

## 七、职位发布-Requirement（页面1）

### TC040: Requirement-Experience默认选中"All levels"

**自动化标识**：`case_id_sg_biz_job_publish_tc040`

**前置条件**：
- 测试账号：wangyongli@58.com / Qwer1234
- 进入职位发布 Requirement 区域

**执行步骤**：
1. 观察 Experience 字段默认值

**预期结果**：
- Experience 默认选中 "All levels"

**优先级**：P0

**测试类型**：功能/默认值

**UI自动化**：✅ 可自动化

---

### TC041: Requirement-Education默认选中"All levels"

**自动化标识**：`case_id_sg_biz_job_publish_tc041`

**前置条件**：
- 测试账号：wangyongli@58.com / Qwer1234
- 进入 Requirement 区域

**执行步骤**：
1. 观察 Education 字段默认值

**预期结果**：
- Education 默认选中 "All levels"

**优先级**：P0

**测试类型**：功能/默认值

**UI自动化**：✅ 可自动化

---

### TC042: Requirement-Experience全部6个选项可选

**自动化标识**：`case_id_sg_biz_job_publish_tc042`

**前置条件**：
- 测试账号：wangyongli@58.com / Qwer1234
- 进入 Requirement 区域

**执行步骤**：
1. 点击 Experience 下拉/选项
2. 依次验证：All levels / <1 year / 1–2 years / 3–5 years / 6–10 years / 10+ years

**预期结果**：
- 6个选项完整显示
- 每个选项均可选中

**优先级**：P1

**测试类型**：功能/枚举

**UI自动化**：✅ 可自动化

---

### TC043: Requirement-Education全部8个选项可选

**自动化标识**：`case_id_sg_biz_job_publish_tc043`

**前置条件**：
- 测试账号：wangyongli@58.com / Qwer1234
- 进入 Requirement 区域

**执行步骤**：
1. 验证Education选项：All levels / Secondary Education / High school or equivalent / Associate's degree / Bachelor's degree / Master's degree / Doctorate / Other

**预期结果**：
- 8个选项完整显示，均可选中

**优先级**：P1

**测试类型**：功能/枚举

**UI自动化**：✅ 可自动化

---

### TC044: Requirement-Experience必填，不选无法下一步

**自动化标识**：`case_id_sg_biz_job_publish_tc044`

**前置条件**：
- 测试账号：wangyongli@58.com / Qwer1234
- 进入 Requirement 区域

**执行步骤**：
1. 清空 Experience（若可清空）
2. 点击下一步

**预期结果**：
- 校验失败，提示 Experience 必填

**优先级**：P0

**测试类型**：负向/功能

**UI自动化**：✅ 可自动化

---

### TC045: Requirement-Education必填，不选无法下一步

**自动化标识**：`case_id_sg_biz_job_publish_tc045`

**前置条件**：
- 测试账号：wangyongli@58.com / Qwer1234
- 进入 Requirement 区域

**执行步骤**：
1. 清空 Education
2. 点击下一步

**预期结果**：
- 校验失败，提示 Education 必填

**优先级**：P0

**测试类型**：负向/功能

**UI自动化**：✅ 可自动化

---

## 八、职位发布-Job Detail（页面2）

### TC047: Job Detail-页面完整加载

**自动化标识**：`case_id_sg_biz_job_publish_tc047`

**前置条件**：
- 测试账号：wangyongli@58.com / Qwer1234
- 完成 Job Basic + Requirement 填写，进入 Job Detail 页面

**执行步骤**：
1. 观察 Job Detail 页面是否正常加载

**预期结果**：
- 页面正常显示，无白屏/报错

**优先级**：P0

**测试类型**：功能

**UI自动化**：✅ 可自动化

---

### TC048: Job Detail-底部按钮变更

**自动化标识**：`case_id_sg_biz_job_publish_tc048`

**前置条件**：
- 测试账号：wangyongli@58.com / Qwer1234
- 进入 Job Detail 页面（新版简化流程）

**预期结果**：
- 从Continue 变为 Post

**需求来源**：PRD-按钮逻辑同原招聘发布最后一步

**优先级**：P1

**测试类型**：功能/回归

**UI自动化**：✅ 可自动化

---

### TC049: Job Detail-完整发布职位全流程成功

**自动化标识**：`case_id_sg_biz_job_publish_tc049`

**前置条件**：
- 测试账号：wangyongli@58.com / Qwer1234
- 所有必填信息已完成（个人信息、公司信息、Job Basic、Requirement）

**执行步骤**：
1. 在 Job Detail 页填写职位描述
2. 点击发布
3. 观察发布结果

**预期结果**：
- 职位发布成功
- 跳转到发布成功页或职位管理页

**优先级**：P0

**测试类型**：功能/主流程

**UI自动化**：✅ 可自动化

---

## 九、多语言与国际化

### TC050: 多语言-英语站(espub)-雇主信息页i18n验证

**自动化标识**：`case_id_sg_biz_job_publish_tc050`

**前置条件**：
- 测试账号：wangyongli@58.com / Qwer1234
- ES站英语版（espub.58v5.cn/biz/en），language: en

**执行步骤**：
1. 登录并访问雇主信息页
2. 验证以下关键字段的英文文案：
   - Employer Info (主标题)
   - Recruiter Information (子标题)
   - First name, Last name, Email (字段标签)
   - Company Information (子标题)
   - Search the full name of the company (字段标签)
   - WhatsApp 相关文案

**预期结果**：
- 所有字段标签显示正确的英文文案
- 无乱码或语言混用

**实际测试结果**：✅ 通过 (TC-L-EN)
- 证据：`proofs/tc-l-en-proof.yml`

**优先级**：P1

**测试类型**：国际化

**UI自动化**：✅ 可自动化

---

### TC051: 多语言-英语站(espub)-发布流程13字段i18n验证

**自动化标识**：`case_id_sg_biz_job_publish_tc051`

**前置条件**：
- 测试账号：wangyongli@58.com / Qwer1234
- ES站英语版，发布流程页面

**执行步骤**：
1. 进入职位发布流程（Job Basics页面）
2. 验证以下13个字段的英文文案（对应多语言文档行2757-2772，不含已排除字段）：
   - **雇主信息**：First name, Last name, Email, Search the full name of the company
   - **基本信息**：Basic Information (标题), Job Title, Job Function, Workplace Type, Job Location, Job Type, Salary Range
   - **职位要求**：Experience, Education

**预期结果**：
- 所有测试范围内的字段显示正确的英文文案

**实际测试结果**：⚠️ 部分通过 (TC-L2-EN)
- ✅ 已验证通过 11个字段：First name, Last name, Email, Search company, Basic Information, Job Title, Job Function, Workplace Type, Job Location, Job Type, Salary Range, Experience, Education
- 🚫 已排除字段：Job title (as employer) - 该字段已从测试范围移除
- ⏸️ 待验证：Job Description - 需进入Job Details页面（第二步）才能验证
- 证据：`proofs/tc-l2-en-proof.md`, `proofs/tc-l2-en-two-keys-recheck.md`

**优先级**：P1

**测试类型**：国际化

**UI自动化**：✅ 可自动化

---

### TC052: 多语言-西班牙语站(espub)-雇主信息页i18n验证

**自动化标识**：`case_id_sg_biz_job_publish_tc052`

**前置条件**：
- 测试账号：wangyongli@58.com / Qwer1234
- ES站西班牙语版（espub.58v5.cn/biz/es），language: es

**执行步骤**：
1. 登录并访问雇主信息页
2. 验证西班牙语文案：Información del empleador, Editar, WhatsApp相关文案等

**预期结果**：
- 所有字段标签显示正确的西班牙语文案

**实际测试结果**：✅ 通过 (TC-L-ES)
- 证据：`proofs/tc-l-es-proof.yml`

**优先级**：P1

**测试类型**：国际化

**UI自动化**：✅ 可自动化

---

### TC053: 多语言-西班牙语站(espub)-发布流程13字段i18n验证

**自动化标识**：`case_id_sg_biz_job_publish_tc053`

**前置条件**：
- 测试账号：wangyongli@58.com / Qwer1234
- ES站西班牙语版，发布流程页面

**执行步骤**：
1. 进入职位发布流程
2. 验证以下13个字段的西班牙语文案：
   - Nombre, Apellidos, Correo, Buscar empresa
   - Información básica, Título del puesto, Función laboral
   - Tipo de lugar de trabajo, Ubicación, Tipo de empleo
   - Rango salarial, Experiencia, Educación

**预期结果**：
- 所有13个字段显示正确的西班牙语文案

**实际测试结果**：✅ 通过 13/13 (TC-L2-ES)
- 证据：`proofs/tc-l2-es-proof.md`, `proofs/tc-l2-es-*-proof.yml`

**优先级**：P1

**测试类型**：国际化

**UI自动化**：✅ 可自动化

---

### TC054: 多语言-阿拉伯语站(aepub)-雇主信息页i18n+RTL验证

**自动化标识**：`case_id_sg_biz_job_publish_tc054`

**前置条件**：
- 测试账号：wangyongli@58.com / Qwer1234
- AE站阿拉伯语版（aepub.58v5.cn/biz/ar），language: ar

**执行步骤**：
1. 登录并访问雇主信息页
2. 验证阿拉伯语文案：معلومات صاحب العمل, تعديل, واتساب相关文案等
3. 验证RTL布局：检查 `<html dir="rtl">` 属性

**预期结果**：
- 所有字段标签显示正确的阿拉伯语文案
- RTL布局正确

**实际测试结果**：✅ 通过 (TC-L-AR, 含RTL验证)
- 证据：`proofs/tc-l-ar-proof.yml`

**优先级**：P1

**测试类型**：国际化/兼容性

**UI自动化**：✅ 可自动化

---

### TC055: 多语言-阿拉伯语站(aepub)-发布流程13字段i18n+RTL验证

**自动化标识**：`case_id_sg_biz_job_publish_tc055`

**前置条件**：
- 测试账号：wangyongli@58.com / Qwer1234
- AE站阿拉伯语版，发布流程页面

**执行步骤**：
1. 进入职位发布流程
2. 验证以下13个字段的阿拉伯语文案：
   - الاسم الأول, اسم العائلة, البريد الإلكتروني, ابحث عن الاسم الكامل للشركة
   - المعلومات الأساسية, اسم الوظيفة, نوع الوظيفة
   - نوع مكان العمل, موقع العمل, نطاق الراتب
   - الخبرة, المؤهل الدراسي
3. 验证RTL布局

**预期结果**：
- 所有13个字段显示正确的阿拉伯语文案
- RTL布局正确

**实际测试结果**：✅ 通过 13/13 (TC-L2-AR, 含RTL验证)
- 证据：`proofs/tc-l2-ar-proof.md`, `proofs/tc-l2-ar-*-proof.yml`

**优先级**：P1

**测试类型**：国际化/兼容性

**UI自动化**：✅ 可自动化

---

### TC056: 多语言-葡萄牙语站(ptpub)-雇主信息页i18n验证

**自动化标识**：`case_id_sg_biz_job_publish_tc056`

**前置条件**：
- 测试账号：wangyongli@58.com / Qwer1234
- PT站葡萄牙语版（ptpub.58v5.cn/biz/pt），language: pt

**执行步骤**：
1. 登录并访问雇主信息页
2. 验证葡萄牙语文案：Informações do empregador, Editar, WhatsApp相关文案等

**预期结果**：
- 所有字段标签显示正确的葡萄牙语文案

**实际测试结果**：✅ 通过 (TC-L-PT)
- 证据：`proofs/tc-l-pt-proof.yml`

**优先级**：P1

**测试类型**：国际化

**UI自动化**：✅ 可自动化

---

### TC057: 多语言-葡萄牙语站(ptpub)-发布流程13字段i18n验证

**自动化标识**：`case_id_sg_biz_job_publish_tc057`

**前置条件**：
- 测试账号：wangyongli@58.com / Qwer1234
- PT站葡萄牙语版，发布流程页面

**执行步骤**：
1. 进入职位发布流程
2. 验证以下13个字段的葡萄牙语文案：
   - Nome, Sobrenome, Email, Pesquisar empresa
   - Informações básicas, Nome do cargo, Categoria funcional
   - Tipo de local, Local, Tipo de vaga
   - Faixa salarial, Experiência, Educação

**预期结果**：
- 所有13个字段显示正确的葡萄牙语文案

**实际测试结果**：✅ 通过 13/13 (TC-L2-PT)
- 证据：`proofs/tc-l2-pt-proof.md`, `proofs/tc-l2-pt-*-proof.yml`
- 备注：线上部分标签（如Nome do cargo, Categoria funcional）与Excel用词可能略有差异，以页面实际为准

**优先级**：P1

**测试类型**：国际化

**UI自动化**：✅ 可自动化

---

### TC058: 多语言-繁体中文站(hkpub)-雇主信息页i18n验证

**自动化标识**：`case_id_sg_biz_job_publish_tc058`

**前置条件**：
- 测试账号：wangyongli@58.com / Qwer1234
- HK站繁体中文版（hkpub.58v5.cn/biz/zh），language: zh

**执行步骤**：
1. 登录并访问雇主信息页
2. 验证繁体中文文案：雇主資訊, 編輯, WhatsApp相关文案等

**预期结果**：
- 所有字段标签显示正确的繁体中文文案
- 使用繁体字而非简体字

**实际测试结果**：✅ 通过 (TC-L-ZH)
- 证据：`proofs/tc-l-zh-proof.yml`

**优先级**：P1

**测试类型**：国际化

**UI自动化**：✅ 可自动化

---

### TC059: 多语言-繁体中文站(hkpub)-发布流程13字段i18n验证

**自动化标识**：`case_id_sg_biz_job_publish_tc059`

**前置条件**：
- 测试账号：wangyongli@58.com / Qwer1234
- HK站繁体中文版，发布流程页面

**执行步骤**：
1. 进入职位发布流程
2. 验证以下13个字段的繁体中文文案：
   - 名字, 姓氏, 電子郵件, 搜尋公司全名
   - 基本資料, 職位名稱, 職能類別
   - 工作地點型態, 工作地點, 職位類型
   - 薪資範圍, 經歷, 學歷

**预期结果**：
- 所有13个字段显示正确的繁体中文文案

**实际测试结果**：✅ 通过 13/13 (TC-L2-ZH)
- 证据：`proofs/tc-l2-zh-proof.md`, `proofs/tc-l2-zh-*-proof.yml`
- 备注：HK站加载时有console errors，但未阻断字段展示验证

**优先级**：P1

**测试类型**：国际化

**UI自动化**：✅ 可自动化

---

### TC060: 多语言-巴西站点pt语言-个人信息页文案

**自动化标识**：`case_id_sg_biz_job_publish_tc060`

**前置条件**：
- 巴西站（brpub.58v5.cn），language: pt
- 维护多语言预期值映射文件 `i18n_expected/pt.json`，包含关键文案的预期值

**执行步骤**：
1. 访问巴西站个人信息填写页
2. 读取页面上以下关键元素的文本内容：
3. 与 `pt.json` 中对应预期值做精确匹配断言

**预期结果**：
- 各元素文本与 `pt.json` 预期值完全一致
- WhatsApp勾选框主文案已正确翻译为葡语

**优先级**：P2

**测试类型**：国际化

**UI自动化**：✅ 可自动化

---

### TC061: 多语言-美国站点en语言-发布页文案及选项完整性

**自动化标识**：`case_id_sg_biz_job_publish_tc061`

**前置条件**：
- 美国站（uspub.58v5.cn），language: en

**执行步骤**：
1. 进入职位发布 Requirement 区域
2. 获取 Experience 所有选项文本列表，断言与 PRD 定义完全一致：
`["All levels", "< 1 year", "1–2 years", "3–5 years", "6–10 years", "10+ years"]`
3. 获取 Education 所有选项文本列表，断言与 PRD 定义完全一致
4. 获取 Workplace type 选项列表，断言包含 `["Onsite", "Hybrid", "Remote"]`
5. 获取 Job type 选项列表，断言包含 `["Full-time", "Part-time", "Contract", "Internship", "Temporary"]`

**预期结果**：
- 所有枚举选项文案与 PRD 定义完全匹配
- 无多余或缺少的选项

**优先级**：P2

**测试类型**：国际化/功能

**UI自动化**：✅ 可自动化

---

### TC062: 多语言-阿拉伯语站点-RTL布局深度验证

**自动化标识**：`case_id_sg_biz_job_publish_tc062`

**前置条件**：
- AE站（aepub.58v5.cn），language: ar

**执行步骤**：
1. 访问AE站个人信息填写页
2. 断言 `<html>` 元素的 `dir` 属性值为 `"rtl"`
3. 断言 `<body>` 或页面根容器 CSS `direction` 属性计算值为 `"rtl"`
4. 断言确认按钮（`[data-testid="submit-btn"]`）的 `offsetLeft` 值小于页面宽度的50%（即按钮靠左，RTL布局中"靠左"等于视觉上靠右）
5. 重复步骤2-4，验证职位发布页

**预期结果**：
- `<html dir="rtl">` 存在
- 页面 CSS direction 为 rtl
- 按钮/文字布局方向符合RTL规则（通过DOM属性和CSS计算值断言）

**备注**：基础RTL验证已在TC054-TC055中覆盖

**优先级**：P2

**测试类型**：国际化/兼容性

**UI自动化**：✅ 可自动化

---

### TC063: 多语言-头像生成-阿拉伯语姓名首字符提取

**自动化标识**：`case_id_sg_biz_job_publish_tc063`

**前置条件**：
- AE站，账号姓名为阿拉伯语字符

**执行步骤**：
1. 进入个人信息页，观察自动生成头像

**预期结果**：
- 正确提取阿拉伯字符作为头像文字，或显示兜底头像
- 不崩溃、不乱码

**备注**：当前轮次按需求不需要覆盖（可不执行/不录制）

**优先级**：P2

**测试类型**：国际化/边界

**UI自动化**：✅ 可自动化

---

### TC064: 多语言-香港站点zh语言-文案非简体且无乱码深度验证

**自动化标识**：`case_id_sg_biz_job_publish_tc064`

**前置条件**：
- HK站（hkpub.58v5.cn），language: zh

**执行步骤**：
1. 访问HK站职位发布页
2. 获取页面标题、确认按钮、字段标签等关键元素文本
3. 断言各文本不含 `?` 或 `□`（乱码标志字符）
4. 断言各文本通过正则 `/[\u4e00-\u9fa5]/.test(text)` 包含中文字符
5. 断言文本不完全等于英文版默认值（如不等于 "Post Job"、"Confirm" 等）
6. 断言使用繁体字而非简体字（如：資訊 vs 资讯）

**预期结果**：
- 关键文案包含繁体中文字符
- 无乱码字符（? 或方块）
- 文案不为英文默认值（说明多语言加载正常）

**备注**：基础繁体中文验证已在TC058-TC059中覆盖

**优先级**：P2

**测试类型**：国际化

**UI自动化**：✅ 可自动化

---

## 十、网络健壮性

### TC065: 断网状态下填写个人信息点击提交

**自动化标识**：`case_id_sg_biz_job_publish_tc065`

**前置条件**：
- 进入个人信息填写页，已填写完整信息

**执行步骤**：
1. 填写姓名、Email、公司名等必填字段
2. 使用 Playwright `context.setOffline(true)` 模拟断网
3. 点击确认提交按钮
4. 等待错误提示出现（最多5s）
5. 断言表单字段内容未被清空
6. 使用 `context.setOffline(false)` 恢复网络

**预期结果**：
- 页面显示网络错误提示（toast/inline错误文案出现）
- 页面不崩溃（无JavaScript错误抛出）
- 已填写的姓名、Email字段内容保留

**优先级**：P1

**测试类型**：健壮性/异常

**UI自动化**：✅ 可自动化

---

### TC066: 重复点击提交按钮-防重复提交

**自动化标识**：`case_id_sg_biz_job_publish_tc066`

**前置条件**：
- 个人信息填写完整

**执行步骤**：
1. 快速连续点击确认按钮3次
2. 观察接口调用次数和数据

**预期结果**：
- 仅提交一次，无重复数据
- 按钮在提交中状态下不可重复点击（loading态）

**优先级**：P1

**测试类型**：健壮性/幂等

**UI自动化**：✅ 可自动化

---

## 十一、边界值与组合场景

### TC073: First name与Last name均填写最大长度（80字符）后提交

**自动化标识**：`case_id_sg_biz_job_publish_tc073`

**前置条件**：
- 使用 **UMC 已绑定邮箱** 的 B 端账号（Email 可自动回显，避免 Email 必填阻塞）：测试账号 **wang@58.com** / Qwer1234（见上文「测试环境配置」）
- 先访问发布入口触发登录态，再进入个人信息填写页（保证 Biz 登录成功、Email 同步）：  
  1）`https://sgpub.58v5.cn/biz/en/publish/job?categoryId=6000`  
  2）`https://sgpub.58v5.cn/biz/en/zpInfo/profile?fromUrl=%2Fpublish%2Fjob%3FcategoryId%3D6000`

**执行步骤**：
1. 将 **First name**（`#firstName`）、**Last name**（`#lastName`）均填写为 **恰好 80 个字符**（与页面 `maxlength=80` 一致）
2. **公司全名**等其余必填项按页面规则填写合法取值（公司名字段无 80 字符限制时按联想检索选择合法公司，见 TC021 / TC022）
3. 点击 **Confirm** 提交个人信息

**预期结果**：
- 提交成功：跳转回职位发布流程（例如 URL 进入 `/biz/en/publish/job?categoryId=6000` 的 Step1），无截断乱码、无服务端错误提示

**优先级**：P1

**测试类型**：边界值

**UI自动化**：✅ 可自动化

---

### TC074: First name与Last name输入超出最大长度

**自动化标识**：`case_id_sg_biz_job_publish_tc074`

**前置条件**：
- 同 TC073：UMC 有邮箱账号 + 先发布页登录再进入个人信息页（`zpInfo/profile`）

**执行步骤**：
1. 在 **First name** 中通过 `fill` 等方式尝试输入 **超过 80** 个字符（如 100 个相同字符）
2. 在 **Last name** 中重复上述操作
3. 观察输入框实际保留字符数与计数展示（如 `80/80`）

**预期结果**：
- 两字段均受 `maxlength=80` 约束：**实际值长度不超过 80**，无法保留第 81 个及以后字符；无乱码
- （说明：XMind 原稿中「公司名称」步骤与标题不一致，已按 **First/Last name** 与线上 `id=firstName`/`id=lastName` 校正）

**优先级**：P1

**测试类型**：边界值

**UI自动化**：✅ 可自动化

---

### TC075: 首次填写-公司信息为空直接提交

**自动化标识**：`case_id_sg_biz_job_publish_tc075`

**前置条件**：
- 进入公司信息填写页，不填写任何内容

**执行步骤**：
1. 直接点击确认按钮

**预期结果**：
- 必填字段均报错，不提交

**优先级**：P0

**测试类型**：负向/边界

**UI自动化**：✅ 可自动化




