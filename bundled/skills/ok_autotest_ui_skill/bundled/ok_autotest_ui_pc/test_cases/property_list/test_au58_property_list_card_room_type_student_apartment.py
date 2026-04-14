"""
AU站 - 列表卡片房间型号功能测试（学生公寓 cate-student-apartment）

录制文档：test_plans/au58-Property-列表卡片房间型号功能测试用例.md
生成时间：2026-03-13
测试目标：验证 Canberra 学生公寓列表页卡片的房间型号展示

录制要点（MCP 录制结果）：
- 卡片定位器：a[href*="student-apartment"]
- 房间型号：.room-distance-type-item（无 img 子元素）> .room-distance-type-item-label
- 常见取值：'Studio'、'1–3 Bedroom Apartment'、'Student Apartment'（兜底值）
- 详情页房间型号：.MainInfo_item__ZNJ3X（无 img.MainInfo_icon__kiZFy）> .MainInfo_value__U8n3C
"""
import pytest
import allure
from pages.property_list_page import PropertyListPage
from utils.logger import setup_logger

logger = setup_logger()

_CONFIG = {
    "site": "au",
    "site_name": "AU站（澳大利亚）",
    "role": "guest",
    "user_name": "guest_au",
    "base_url": "https://au.58v5.cn",
    "test_account": None,
    "list_url": "https://au.58v5.cn/en/city-canberra/cate-student-apartment/?iconSource=student-apartment",
    "browser": {
        "type": "chromium",
        "headless": True,
        "viewport": {"width": 1920, "height": 1080},
    },
    "timeout": {"default": 30000, "wait": 10000, "navigation": 30000},
}


def _goto_list(page, config):
    """直接打开学生公寓列表页（无需登录）。"""
    plp = PropertyListPage(page)
    page.goto(config["list_url"], wait_until="commit", timeout=config["timeout"]["navigation"])
    page.wait_for_load_state("domcontentloaded", timeout=10000)
    try:
        cookie_btn = page.locator("button:has-text('Accept all'), button:has-text('Accept')").first
        if cookie_btn.is_visible(timeout=2000):
            cookie_btn.click()
            page.wait_for_timeout(1000)
    except Exception:
        pass
    return plp


# ============================================================
# TC001 列表卡片房间型号正常展示
# ============================================================
@pytest.mark.case_id_au58_list_card_room_type_student_apartment_001
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片房间型号-学生公寓")
@allure.title("列表卡片房间型号正常展示")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("打开学生公寓列表页，验证列表卡片房间型号文案展示（非空）")
def test_tc001_room_type_visible(page, config):
    plp = _goto_list(page, config)
    with allure.step("步骤1：打开列表页，等待加载完成"):
        page.wait_for_load_state("domcontentloaded", timeout=10000)
        logger.info("✓ 列表页加载完成")

    with allure.step("步骤2：统计卡片总数"):
        card_count = plp.get_student_apartment_card_count()
        assert card_count > 0, "学生公寓列表应至少有一张卡片"
        logger.info(f"✓ 当前页卡片总数: {card_count}")

    with allure.step("步骤3：验证前5张卡片至少有一张展示房间型号"):
        # MCP录制：.room-distance-type-item（无 img）> .room-distance-type-item-label
        room_types = plp.get_all_room_types(max_cards=5)
        logger.info(f"✓ 前5张卡片房间型号: {room_types}")
        valid_types = [rt for rt in room_types if rt is not None]
        assert len(valid_types) > 0, f"至少应有1张卡片展示房间型号，实际: {room_types}"
        for rt in valid_types:
            assert rt != "", f"房间型号不应为空字符串，实际: {rt!r}"
        logger.info(f"✓ 有房间型号信息的卡片: {len(valid_types)}/{len(room_types)}")


# ============================================================
# TC002 房间型号取值合理
# ============================================================
@pytest.mark.case_id_au58_list_card_room_type_student_apartment_002
@pytest.mark.p1
@allure.feature("OK")
@allure.story("AU站列表卡片房间型号-学生公寓")
@allure.title("房间型号取值合理")
@allure.severity(allure.severity_level.NORMAL)
@allure.description(
    "验证列表卡片房间型号文案为合理英文字符串，长度在 1～100 字符之间，不含乱码或纯符号。\n"
    "录制样本：'Studio'、'1–3 Bedroom Apartment'、'Student Apartment'"
)
def test_tc002_room_type_value_reasonable(page, config):
    plp = _goto_list(page, config)
    with allure.step("步骤1：获取前10张卡片的房间型号"):
        room_types = plp.get_all_room_types(max_cards=10)
        logger.info(f"✓ 前10张卡片房间型号: {room_types}")

    with allure.step("步骤2：验证房间型号为合理英文字符串"):
        valid_types = [rt for rt in room_types if rt is not None]
        assert len(valid_types) > 0, "至少应有1张卡片有房间型号信息"
        for rt in valid_types:
            assert isinstance(rt, str), f"房间型号应为字符串，实际: {type(rt)}"
            assert 1 <= len(rt.strip()) <= 100, f"房间型号长度应在 1～100 之间，实际: {rt!r}"
            # 不应为纯空白或纯符号
            assert any(c.isalpha() or c.isdigit() for c in rt), (
                f"房间型号应包含字母或数字，实际: {rt!r}"
            )
            logger.info(f"  ✓ 房间型号: {rt!r}")


# ============================================================
# TC003 房间型号文本元素可见性
# ============================================================
@pytest.mark.case_id_au58_list_card_room_type_student_apartment_003
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片房间型号-学生公寓")
@allure.title("房间型号文本元素可见性")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证列表卡片房间型号文本元素在视口内可见，宽高大于 0")
def test_tc003_room_type_element_visible(page, config):
    plp = _goto_list(page, config)
    with allure.step("步骤1：找到第一张有房间型号的卡片"):
        cards = plp.get_student_apartment_cards()
        card_count = cards.count()
        assert card_count > 0, "列表应有卡片"

        target_idx = None
        for i in range(min(card_count, 10)):
            rt = plp.get_room_type_from_card(cards.nth(i))
            if rt is not None:
                target_idx = i
                logger.info(f"✓ 找到有房间型号的卡片 card[{i}]，型号: {rt!r}")
                break

        if target_idx is None:
            pytest.skip("前10张卡片均无房间型号字段，跳过本用例")

    with allure.step("步骤2：验证房间型号文本元素可见且有正常尺寸"):
        result = plp.get_room_type_element_visible(cards.nth(target_idx))
        assert result is not None, f"card[{target_idx}] 应有房间型号元素"
        assert result.get("visible"), (
            f"card[{target_idx}] 房间型号元素应可见，实际: {result}"
        )
        assert result.get("width", 0) > 0 and result.get("height", 0) > 0, (
            f"card[{target_idx}] 房间型号元素宽高应大于0，实际: {result}"
        )
        logger.info(f"✓ 房间型号元素: visible={result['visible']}, {result['width']}×{result['height']}px")


# ============================================================
# TC004 房间型号与详情页一致
# ============================================================
@pytest.mark.case_id_au58_list_card_room_type_student_apartment_004
@pytest.mark.p1
@allure.feature("OK")
@allure.story("AU站列表卡片房间型号-学生公寓")
@allure.title("房间型号与详情页一致")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("记录列表页第一张卡片的房间型号，点击进入详情页，验证两处房间型号一致")
def test_tc004_room_type_consistent_with_detail_page(page, config):
    plp = _goto_list(page, config)
    with allure.step("步骤1：获取列表页第一张有房间型号的卡片"):
        cards = plp.get_student_apartment_cards()
        card_count = cards.count()
        assert card_count > 0, "列表应有卡片"

        target_idx = None
        list_room_type = None
        target_href = None
        for i in range(min(card_count, 10)):
            rt = plp.get_room_type_from_card(cards.nth(i))
            if rt is not None:
                target_idx = i
                list_room_type = rt
                target_href = cards.nth(i).get_attribute("href")
                break

        if target_idx is None:
            pytest.skip("前10张卡片均无房间型号字段，跳过本用例")

        logger.info(f"✓ 列表页 card[{target_idx}] 房间型号: {list_room_type!r}")

    with allure.step("步骤2：点击该卡片进入详情页"):
        if target_href:
            card_loc = page.locator(f'a[href="{target_href}"]').first
        else:
            card_loc = plp.get_student_apartment_cards().nth(target_idx)
        with page.expect_popup() as popup_info:
            card_loc.click()
        detail_page = popup_info.value
        detail_page.wait_for_load_state("domcontentloaded", timeout=15000)
        detail_page.wait_for_timeout(1500)
        logger.info(f"✓ 详情页 URL: {detail_page.url[:80]}")

    with allure.step("步骤3：获取详情页房间型号"):
        detail_room_type = plp.get_room_type_from_detail_page(detail_page)
        logger.info(f"✓ 详情页房间型号: {detail_room_type!r}")
        detail_page.close()

    with allure.step("步骤4：验证列表页与详情页房间型号一致"):
        assert detail_room_type is not None, "详情页应展示房间型号"
        assert list_room_type == detail_room_type, (
            f"列表页房间型号 '{list_room_type}' 与详情页 '{detail_room_type}' 不一致"
        )
        logger.info(f"✓ 列表页与详情页房间型号一致: {list_room_type!r}")


# ============================================================
# TC005 无房间型号的卡片正常展示（不崩溃）
# ============================================================
@pytest.mark.case_id_au58_list_card_room_type_student_apartment_005
@pytest.mark.p2
@allure.feature("OK")
@allure.story("AU站列表卡片房间型号-学生公寓")
@allure.title("无房间型号的卡片正常展示")
@allure.severity(allure.severity_level.MINOR)
@allure.description("查找无独立房间型号字段的卡片，验证页面不崩溃、卡片仍正常展示")
def test_tc005_missing_room_type_cards_handled_gracefully(page, config):
    plp = _goto_list(page, config)
    with allure.step("步骤1：获取前10张卡片的房间型号信息"):
        room_types = plp.get_all_room_types(max_cards=10)
        logger.info(f"✓ 前10张卡片房间型号: {room_types}")

    with allure.step("步骤2：统计无房间型号的卡片"):
        missing = [i for i, rt in enumerate(room_types) if rt is None]
        has_type = [i for i, rt in enumerate(room_types) if rt is not None]
        logger.info(f"  有房间型号的卡片索引: {has_type}")
        logger.info(f"  无房间型号的卡片索引: {missing}")

    with allure.step("步骤3：验证页面整体正常（无崩溃）"):
        card_count = plp.get_student_apartment_card_count()
        assert card_count > 0, "列表页应有卡片，页面正常"

        cards = plp.get_student_apartment_cards()
        for idx in missing:
            try:
                card = cards.nth(idx)
                # 滚动到元素位置，确保不被视口遮挡
                try:
                    card.scroll_into_view_if_needed(timeout=3000)
                except Exception:
                    pass
                txt = card.inner_text().strip()
                assert len(txt) > 0, f"无房间型号的 card[{idx}] 应有非空文本内容"
                logger.info(f"  ✓ card[{idx}] 无房间型号但卡片正常展示: {txt[:60]!r}")
            except AssertionError:
                raise
            except Exception as e:
                logger.warning(f"  ⚠ card[{idx}] 检查异常: {e}")

        logger.info(f"✓ 页面正常，有房间型号: {len(has_type)} 张，无房间型号: {len(missing)} 张")
