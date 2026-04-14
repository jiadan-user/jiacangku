# test_cases/property_basics/map/conftest.py
"""
Property Map 目录级公共配置

本 conftest 不覆盖父级 config fixture（仍由 test_cases/conftest.py 从各模块 _CONFIG 读取），
仅提供目录说明；各测试文件在模块顶部声明自己的 _CONFIG。

目录结构说明
───────────────────────────────────────────────────────
test_cases/property_basics/map/
│
│  ── Sydney Student Accommodation 地图筛选（共享 _CONFIG / 独立 Class）
│  test_map_view_switch.py          TC001–TC008  List/Map 视图切换
│  test_map_sort.py                 TC009–TC015  Sort 排序
│  test_map_price_filter.py         TC016–TC023  Price 价格筛选
│  test_map_beds_filter.py          TC024–TC028  Beds 卧室筛选
│  test_map_bathrooms_filter.py     TC029–TC033  Bathrooms 浴室筛选
│  test_map_property_type_filter.py TC034–TC043  Property Type + Filter 综合
│  test_map_combo_filter.py         TC047–TC051  组合筛选
│
│  ── Canberra Student Accommodation 地图综合（独立 _CONFIG）
│  test_canberra_card_pagination.py TC001–TC003/TC006–TC009/TC011–TC013 卡片+分页+视图
│  test_canberra_search.py          TC015–TC028 搜索+历史+SUG+鲁棒性
│
│  ── Pin 点展示 & 联动 & 类目切换（共享 _CONFIG / module 级 pin_page fixture）
│  test_pin_display.py              TC001–TC006e  Pin 点展示（颜色/类目）
│  test_pin_linkage.py              TC007–TC014   Pin 点与卡片列表联动
│  test_subcategory_switcher.py     TC015–TC023   二级类目切换器
───────────────────────────────────────────────────────
"""
