# 治理口径

V1 治理基于“自动化资产”，不是完整的人工业务场景分母。

dashboard 相关文档是 skill 发布时附带的静态参考资料，不在日常执行中自动更新。

AI 分析规则：

- 先参考 `module-map.md`
- 再核对文本用例和自动化脚本
- 不允许只凭映射文档直接下执行结论

输出指标：

- `治理覆盖率` = governed cases / scoped automated cases
- `基线执行覆盖率` = executed baseline cases / baseline cases
- `需求执行覆盖率` = executed recommended cases / recommended cases
- `本次通过率` = passed recommended cases / executed recommended cases

真实执行规则：

- `run --dry-run` 只预览，不算真实执行
- 如果目标 case 有已配置前置，CLI 会先自动补跑前置，再重新执行目标集合
- 如果前置失败，或前置后目标仍未真正执行，`run_status=blocked`
- `blocked` 不算验证通过，建议先处理前置、环境或数据问题后再重跑
- 真实 `run` 执行后会自动生成 Allure 静态报告，并启动本地服务输出 `allure_url`

测试资源规则：

- `bundled/ok_autotest_ui_pc/test_data/images` 是副本内必须保留的基础测试资源目录
- `car publish` 优先兼容外部目录 `/Users/vickymo/Pictures/公共配置图片/车图`
- 如果外部目录不存在，`car publish` 会自动 fallback 到副本内 `test_data/car_images`

基线规则：

1. Any case with `baseline_set`
2. Else any `p0`
3. Else any case carrying `smoke`, `core_flow`, or `validation`

风险建议：

- `中风险：先补前置再执行`
  触发条件：当前 run 被判定为 `blocked`

- `高风险：建议暂停上线并处理问题`
  触发条件：基线失败、治理覆盖率过低，或当前 scope 内存在未治理 case。
- `中风险：建议提测`
  触发条件：基线未跑齐、需求执行覆盖率不足，或非基线 `p0/p1` 失败。
- `低风险：建议可上线`
  触发条件：治理覆盖率达标、基线跑齐、推荐场景执行覆盖达标且结果通过。

`decide` 只是给开发的建议层，不替代 QA 结论。

维护说明：

- `coverage-dashboard.md` 和 `dashboard-modules/` 由 skill 版本维护，不属于运行时产物
- 若覆盖汇报需要更新，应在新一版 skill 中一起更新这些静态 reference 文件
