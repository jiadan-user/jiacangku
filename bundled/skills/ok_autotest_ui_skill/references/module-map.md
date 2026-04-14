# 模块与 Selector 映射

AI 选用例时，先查这张表，再自己核对文本用例和自动化脚本。

这张表是第一层导航，不是最终真相。如果文档映射和脚本现状不一致，以文本用例和脚本为准。

## 常用功能映射

| 开发常说的功能 | 推荐 selector | 说明 |
| --- | --- | --- |
| `wallet 提现` | `--module wallet --path test_cases/wallet/test_wallet_withdrawal.py` | 适合提现、余额、交易历史相关改动 |
| `wallet 银行账户` | `--module wallet --path test_cases/wallet/test_wallet_bank_account_binding.py` | 适合绑卡、解绑、账户状态相关改动；解绑类 case 命中前置时会自动先补跑绑定流程 |
| `wallet 解绑银行卡` | `--module wallet --path test_cases/wallet/test_wallet_bank_account_binding.py --nodeid TestBankAccountUnbinding` | 适合解绑、取消解绑、解绑异常等场景 |
| `publish_job step1` | `--module publish_job --feature publish_job_step1_validation` | Step1 校验与主字段输入 |
| `publish_job step2` | `--module publish_job --feature publish_job_step2_validation` | Step2 表单校验 |
| `publish_job step3` | `--module publish_job --feature publish_job_step3_navigation` | Step3 和导航相关 |
| `publish_job core flow` | `--module publish_job --feature publish_job_core_flow` | 职位发布主链路 |
| `car publish` | `--module car --feature car_publish --site ae` | AE 车发布主链路 |
| `car detail` | `--module car --path test_cases/test_car/test_ae_car_detail.py --site ae` | AE 车详情页 |
| `car list search/filter` | `--module car_list --feature car_list_nav_search` | 搜索入口和关键词搜索 |
| `car list location/filter` | `--module car_list --feature car_list_filter_location` | 城市、位置和筛选面板 |
| `car list sort` | `--module car_list --feature car_list_sort` | 排序能力 |
| `zhaopin ES search/filter` | `--module zhaopin --path test_cases/zhaopin/test_es_jobs_list_search_and_filter.py` | ES 招聘列表搜索筛选 |
| `zhaopin AE search/filter` | `--module zhaopin --path test_cases/zhaopin/test_ae_jobs_list_search_and_filter.py` | AE 招聘列表搜索筛选 |
| `zhaopin SG job preferences` | `--module zhaopin --path test_cases/zhaopin/test_sg_job_preferences.py` | SG Job Preferences |
| `search input` | `--module search_input --path test_cases/search_input/test_home_search_all_tc001_tc036.py` | 首页搜索输入框 |
| `tiyan messages` | `--module tiyan --path test_cases/test_tiyan/test_messages_complete.py` | Messages 功能探索 |
| `tiyan my post` | `--module tiyan --path test_cases/test_tiyan/test_my_post.py` | 我的帖子页 |
| `tiyan post category` | `--module tiyan --path test_cases/test_tiyan/test_post_category.py` | 发布分类选择页 |
| `tiyan post services` | `--module tiyan --path test_cases/test_tiyan/test_post_services.py` | 发布页主流程 |
| `tiyan browse navigation` | `--module tiyan --path test_cases/体验/首页/browse_navigation/` | 首页 Browse 导航 |
| `tiyan header function area` | `--module tiyan --path test_cases/体验/首页/顶部功能区/` | 首页右上角功能区 |
| `tiyan kingkong` | `--module tiyan --path test_cases/体验/首页/金刚位/` | 首页金刚位导航区 |
| `tiyan recommend cards` | `--module tiyan --path test_cases/体验/首页/推荐卡片/` | 首页推荐卡片 |
| `tiyan site selection` | `--module tiyan --path test_cases/体验/site_selection/` | 地区选择页 |
| `seo news` | `--module seo --path test_cases/ SEO/US/test_news_module.py` | US News 模块 |
| `seo qa database` | `--module seo --path test_cases/ SEO/US/test_qa_database_homepage.py` | Q&A Database 首页 |

## 目录级默认模块映射

| 目录 | 模块参数 |
| --- | --- |
| `test_cases/publish_job/` | `--module publish_job` |
| `test_cases/test_car/` | `--module car` |
| `test_cases/car_list/` | `--module car_list` |
| `test_cases/wallet/` | `--module wallet` |
| `test_cases/zhaopin/` | `--module zhaopin` |
| `test_cases/property_basics/` | `--module property_basics` |
| `test_cases/property_detail/` | `--module property_detail` |
| `test_cases/property_list/` | `--module property_list` |
| `test_cases/property_map/` | `--module property_map` |
| `test_cases/marketplace_post/` | `--module marketplace_post` |
| `test_cases/marketplace_order/` | `--module marketplace_order` |
| `test_cases/ai/` | `--module ai` |
| `test_cases/chat-ai/` | `--module chat_ai` |
| `test_cases/ SEO/` | `--module seo` |
| `test_cases/test_tiyan/` | `--module tiyan` |
| `test_cases/体验/` | `--module tiyan` |
| `test_cases/search_input/` | `--module search_input` |

## 使用规则

1. 优先选最具体的 selector
2. 不确定时先 `run --dry-run`
3. 映射命中后，继续回看文本用例和目标脚本，确认没有漏跑或错跑
4. 如果模块里没有稳定 `feature`，优先用 `--path`
5. 如果 selector 太宽，会把无关用例也带上，所以不要默认只写 `--module`
