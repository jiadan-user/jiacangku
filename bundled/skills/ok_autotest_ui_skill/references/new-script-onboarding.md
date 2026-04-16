# 新增脚本接入说明

## 1. `bundled/ok_autotest_ui_pc` 里改过什么

这份 bundled 工程不是重写了一套新自动化，而是在原 UI 自动化基础上做了 3 类改动：

| 类别 | 改了什么 | 影响 |
| --- | --- | --- |
| 标识补齐 | 给原测试脚本补 `P0-P3`、`case_id_*`、必要的模块/功能标识 | 让 skill 能识别、筛选和统计 |
| 治理工具 | 新增 `tooling/ok_test`、`catalog/*` | 支持 `doctor/list/run/coverage/decide` |
| 少量兼容修正 | 修过极少量明显影响运行的细节 | 不是大规模业务逻辑重写 |

结论：

- 这套 bundled 工程仍然是你们正常的 UI 自动化脚本工程。
- 后续新脚本继续加在这里，不需要另外维护第二套自动化项目。
- 大多数场景不需要重新做整套 skill 适配。
- 新增或改写用例前，先读项目内规范文档：
  - `bundled/ok_autotest_ui_pc/docs/test-case-authoring-spec.md`
  - `bundled/ok_autotest_ui_pc/docs/test-case-review-checklist.md`
  - `bundled/ok_autotest_ui_pc/docs/stability-remediation-plan.md`
  - `bundled/ok_autotest_ui_pc/docs/templates/`

## 2. 后续新脚本加在哪里

继续加在这里：

```text
bundled/ok_autotest_ui_pc/test_cases/...
```

规则保持和原工程一致：

- 页面对象继续放 `pages/...`
- 测试工具继续放 `utils/...`
- 用例继续放 `test_cases/...`

## 3. 新脚本最少要补哪些标识

每个新 case 至少补齐这些内容：

| 必填项 | 作用 |
| --- | --- |
| `@pytest.mark.p0 / p1 / p2 / p3` | 告诉 skill 这是哪个优先级 |
| `@pytest.mark.case_id_xxx` | 给每条用例一个稳定标识 |
| 模块归属 | 让 `--module` 能筛选到它 |
| 功能归属 | 优先通过 `allure.story(...)` 表达 |

推荐做法：

- 模块统一用目录归属或文件级 `pytestmark`
- 功能统一优先用 `allure.story`
- 单文件多功能场景，再用 `catalog.overrides.yaml` 兜底

## 4. 新增脚本后要不要重新做适配

通常不用。

大多数情况下，你只需要：

1. 新增脚本
2. 补齐优先级和 `case_id`
3. 补 `allure.story`
4. 重新跑 catalog 和 audit

只有下面这些情况，才需要额外补 override：

- 新目录名不能直接看出属于哪个模块
- 同一个文件里混了多个功能，`allure.story` 不清晰
- 新模块的文本用例路径和现有模块映射对不上

## 5. 固定接入流程

```bash
# 从本 skill 根目录执行
python3 scripts/ok_test.py ops catalog-build
python3 scripts/ok_test.py ops audit-identifiers
python3 scripts/ok_test.py coverage --dashboard
```

推荐完整流程：

1. 新增或修改脚本
2. 补齐 `P0-P3`
3. 补齐 `case_id_*`
4. 补齐模块和功能标识
5. 运行 `python3 scripts/ok_test.py ops catalog-build`
6. 运行 `python3 scripts/ok_test.py ops audit-identifiers`
7. 如果 audit 通过，再运行 `python3 scripts/ok_test.py coverage --dashboard`

## 6. 如何判断接入已经完成

至少满足这几个结果：

- `python3 scripts/ok_test.py list --module <你的模块>` 能列出新用例
- `python3 scripts/ok_test.py ops audit-identifiers` 不再报缺优先级或缺 `case_id`
- `python3 scripts/ok_test.py coverage --dashboard` 能把这块文本用例统计进去
- 真实执行后，Allure 报告里能看到这批新用例

## 7. AI 生成用例时的固定入口

如果是让 AI 帮你直接生成新用例，固定顺序如下：

1. 先读 `bundled/ok_autotest_ui_pc/docs/test-case-authoring-spec.md`
2. 再读 `bundled/ok_autotest_ui_pc/docs/stability-remediation-plan.md`
3. 再选 `bundled/ok_autotest_ui_pc/docs/templates/` 中最接近的模板
4. 生成后对照 `bundled/ok_autotest_ui_pc/docs/test-case-review-checklist.md`
5. 最后执行 `doctor`、`collect-only`、`run --dry-run`
