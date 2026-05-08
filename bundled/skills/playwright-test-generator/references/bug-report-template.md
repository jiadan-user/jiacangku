# Bug 清单报告模板

> 阶段2A `playwright_bug_report.md` 的格式规范。

## 文件规则

- 固定文件名：`playwright_bug_report.md`
- 必须始终生成；没有 bug 时写：`本轮未发现 bug`
- 所有 `bug_recorded` 用例都必须能在本文件中通过 TC 编号或 BUG 编号追溯
- 不符合预期、页面缺失、流程阻塞、配置异常、接口异常都算 bug

## 推荐格式

```markdown
# Bug 清单报告

> 生成时间：YYYY-MM-DD HH:MM:SS
> 测试文档：[文档名称]

## BUG-001

- 用例编号：TC006
- 用例名称：输入关键词点击 Search 执行搜索
- 问题描述：点击 Search 后页面未跳转，搜索结果未更新
- 预期结果：页面跳转至搜索结果页，URL 包含关键词参数，搜索结果展示与 Toyota 相关的车辆
- 实际结果：页面未跳转，URL 仍为 /city-abu-dhabi/cate-car/，搜索框清空但无任何反应
- 截图 / proof：`bug-tc006.png`
```

## 禁止添加

- 不写原因猜测
- 不写修复建议
- 不写责任人
- 不写冗长环境说明
- 不把 AI 调试过程塞进 bug list
