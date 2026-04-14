# OK UI 自动化稳定性整改计划

## 1. 目标

这份计划用于指导各模块负责人逐步清理不稳定模式，重点降低：

- 固定 sleep 过多
- 页面状态相互污染
- 隐式副作用修复
- 超大脚本和超大 Page Object
- 目录级 setup 复制蔓延

## 2. 统一约束

- 新用例禁止新增裸 `page.wait_for_timeout()`
- 旧用例仅允许保留少量动画/防抖等待，默认单次不超过 `300ms`
- 登录、Session、Redis/SQL、页面恢复逻辑必须收敛到 fixture/helper
- Page Object 只负责定位、动作、轻量状态读取，不承载大段断言
- 新增外部副作用动作必须显式命名且可开关

## 3. 框架侧已提供的支撑

- `BasePage.wait_for_any_selector(...)`
- `BasePage.wait_for_key_section(...)`
- `BasePage.wait_for_url_ready(...)`
- `BasePage.dismiss_modal_dialogs(...)`
- `tooling.ok_test doctor` 中的等待热点、超大文件、conftest 覆写扫描

## 4. 分批顺序

### 第一批

- `wallet`
- `marketplace_order`
- `test_tiyan/test_messages_complete`
- `kyc`
- `airwallex_recharge`
- `test_car`

治理重点：

- 登录和外部状态清理收敛
- 去掉长时间 `wait_for_timeout`
- 拆出副作用 helper

### 第二批

- `property_*`
- `zhaopin`
- `explore`

治理重点：

- 大 Page Object 拆分
- 列表页与筛选页等待策略统一
- Page 与断言职责拆分

### 第三批

- `ai/ai_publish`

治理重点：

- 合并高重复业务流
- 统一参数化模板
- 保持失败截图与目录级治理逻辑最小化

## 5. 每位负责人固定交付

- 本模块整改前后 `wait_for_timeout` 数量
- 改动文件清单
- 代表性子集重复跑 3 次结果
- 仍需保留的例外点说明

## 6. 验收口径

- 不依赖上一次残留状态
- `doctor` 能看到热点下降
- `collect-only` 正常
- 抽样 `run --dry-run` 可正常筛选到目标用例
