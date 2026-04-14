# OK UI 自动化用例评审检查清单

## 基础结构

- 文件路径是否放在正确模块目录下
- 文件名是否表达模块和功能
- 是否声明 `_CONFIG`，或明确属于允许无 `_CONFIG` 的目录例外
- imports 是否只包含实际使用对象

## 标识与可筛选性

- 每条测试是否有 `p0/p1/p2/p3`
- 每条测试是否有稳定 `case_id`
- 是否有正确站点标记
- 是否有正确模块标记
- 是否补齐 `allure.feature/story/title`

## Fixture 与状态

- 是否优先复用了全局 `config/page`
- 是否把登录、Session、外部状态准备收敛到了 fixture/helper
- 是否新增了不必要的目录级 `conftest`
- 如有自定义 fixture，文件头是否写明原因

## 等待与断言

- 是否新增了裸 `page.wait_for_timeout()`
- 例外等待是否不超过 `300ms` 且有注释
- 是否优先用了 `expect` / locator wait / URL wait / BasePage helper
- 断言是否表达明确的用户可见结果

## Page Object 边界

- Page Object 是否只承载定位、动作、轻量状态读取
- 是否把大段流程断言塞进了 Page 文件
- 是否复用了已有 Page / helper，而不是重新复制一套

## 运行校验

- 是否执行过 `doctor`
- 是否执行过 `pytest --collect-only`
- 是否执行过 `run --dry-run` 或等价筛选验证
- 生成内容是否无需人工重写框架约定
