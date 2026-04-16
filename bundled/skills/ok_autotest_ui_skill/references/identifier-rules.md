# 标识规则

每条进入治理的 case 都应具备：

- `@pytest.mark.p0`, `p1`, `p2`, or `p3`
- a stable `@pytest.mark.case_id_*`
- a resolvable `module_id`
- a resolvable `feature_id`

优先级推断规则：

- `p0`：smoke、登录、提交、发布成功、支付、提现、绑定、上传等主链路成功场景
- `p1`：核心校验、必填校验、安全、强业务规则、title/price/category/location 等关键验证
- `p2`：search、filter、sort、列表交互、分页、dropdown、session、card、tab、map、兼容性
- `p3`：长尾 UI 校验、弱业务影响、体验优化类场景

`case_id` 规则：

- 已稳定存在的 `case_id_*` 保持不变。
- 缺失时优先复用同文件最近的 `case_id` 前缀。
- 如果本地没有可复用前缀，则使用 `case_id_<module>_<feature>_<nnn>`。

执行流程：

1. Run `python3 scripts/ok_test.py ops audit-identifiers`.
2. 查看项目里的 `catalog/identifier_audit.md`，或导出 skill 后查看 `bundled/ok_autotest_ui_pc/catalog/identifier_audit.md`。
3. 如果建议合理，再运行 `python3 scripts/ok_test.py ops audit-identifiers --apply`。
4. 然后重新执行 `python3 scripts/ok_test.py ops catalog-build`。
