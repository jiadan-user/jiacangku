"""
Property List 目录级公共配置

本 conftest 不覆盖父级 config fixture（仍由 test_cases/conftest.py 从各模块 _CONFIG 读取），
仅提供目录说明；各测试文件在模块顶部声明自己的 _CONFIG。

目录结构说明
───────────────────────────────────────────────────────
test_cases/property_basics/list/
│
│  ── Property For Rent 列表筛选（共享 _CONFIG / 独立 Class）
│  test_rent_sort.py                 8 条  Sort 排序
│  test_rent_price_filter.py        10 条  Price 价格筛选
│  test_rent_beds_filter.py          7 条  Beds 卧室筛选
│  test_rent_bathrooms_filter.py     7 条  Bathrooms 浴室筛选
│  test_rent_property_type_filter.py 9 条  Property Type 类型筛选
│  test_rent_filter_combo.py        23 条  Filter 综合筛选 & 多项组合
│  test_rent_robust.py              13 条  健壮性（分页/UI文案/URL安全/网络）
│
│  ── Property For Sale 搜索筛选（共享 _CONFIG_BUY / 独立 Class）
│  test_buy_search_basic.py         10 条  搜索框基础功能 & 特殊场景
│  test_buy_search_sug.py           11 条  地址 SUG 词
│  test_buy_search_category.py      12 条  二级类目切换
│  test_buy_search_history.py        5 条  搜索历史记录
│  test_buy_filter_combo.py          6 条  筛选组合
│  test_buy_view_navigation.py      17 条  模式切换 & 导航 & 翻页
│
│  ── 房产入口（金刚位 / All / Browse 下拉菜单）
│  test_property_entry_points.py    14 条  三大入口 & 异常边界
───────────────────────────────────────────────────────

原始文件：test_cases/test_property_rent_filter_sort.py（6781 行，152 条用例）
拆分时间：2026-03-13
"""
