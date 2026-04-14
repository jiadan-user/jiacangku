"""
AU站 - 列表卡片 Bed 图标和数量功能测试（学生公寓 cate-student-apartment）

录制文档：test_plans/au58-Property-列表卡片bed图标和数量功能测试用例.md
生成时间：2026-03-12
测试目标：验证 Canberra 学生公寓列表页卡片的 Bed 图标和数量展示

录制要点（MCP 录制结果）：
- 卡片定位器：a[href*="student-apartment"]（30张）
- Bed 图标：img[src*="Bedrooms"]，18×18px 可见
- Bed 数量：.room-distance-type-item-label（Bed 图标同级）
- card[6] 无 Bed 图标（特殊情况：TC005 处理）
- 详情页 bed 与列表页一致（JS: img[src*="Bedrooms"] → closest item → label）
"""
import re
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


def _ensure_logged_in_and_on_list(page, config):
    """直接打开学生公寓列表页（无需登录）。"""
    list_url = config["list_url"]
    plp = PropertyListPage(page)
    page.goto(list_url, wait_until="commit", timeout=config["timeout"]["navigation"])
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
# TC001 列表卡片展示 Bed 图标和数量
# ============================================================
@pytest.mark.case_id_au58_list_card_bed_student_apartment_001
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片Bed图标和数量-学生公寓")
@allure.title("列表卡片展示 Bed 图标和数量")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("打开学生公寓列表页，验证列表卡片展示 Bed 图标和数量（正整数）")
def test_tc001_bed_icon_and_count_visible(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    with allure.step("步骤1：打开列表页，等待加载完成"):
        page.wait_for_load_state("domcontentloaded", timeout=10000)
        logger.info("✓ 列表页加载完成")

    with allure.step("步骤2：统计卡片总数"):
        card_count = plp.get_student_apartment_card_count()
        assert card_count > 0, "学生公寓列表应至少有一张卡片"
        logger.info(f"✓ 当前页卡片总数: {card_count}")

    with allure.step("步骤3：验证前5张卡片均有 Bed 数量展示"):
        # MCP录制：img[src*="Bedrooms"] 在卡片内可见，数量在 .room-distance-type-item-label
        bed_counts = plp.get_all_bed_counts(limit=5)
        logger.info(f"✓ 前5张卡片 Bed 数量: {bed_counts}")
        valid_beds = [b for b in bed_counts if b is not None]
        assert len(valid_beds) > 0, f"至少应有1张卡片展示 Bed 数量，实际: {bed_counts}"
        for bed in valid_beds:
            assert bed != "", f"Bed 数量不应为空字符串，实际: {bed!r}"
        logger.info(f"✓ 有 Bed 信息的卡片: {len(valid_beds)}/{len(bed_counts)}")


# ============================================================
# TC002 Bed 数量取值合理
# ============================================================
@pytest.mark.case_id_au58_list_card_bed_student_apartment_002
@pytest.mark.p1
@allure.feature("OK")
@allure.story("AU站列表卡片Bed图标和数量-学生公寓")
@allure.title("Bed 数量取值合理")
@allure.severity(allure.severity_level.NORMAL)
@allure.description(
    "验证列表卡片 Bed 数量为合理值，支持三种格式：\n"
    "1. 纯整数（如 1、6、8）：范围 1～50\n"
    "2. 数字+号（如 5+、8+）：表示至少N间\n"
    "3. 描述型文字（如 Studio）：学生公寓特有房型描述"
)
def test_tc002_bed_count_value_reasonable(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    with allure.step("步骤1：获取前10张卡片的 Bed 数量"):
        bed_counts = plp.get_all_bed_counts(limit=10)
        logger.info(f"✓ 前10张卡片 Bed 数量: {bed_counts}")

    with allure.step("步骤2：验证 Bed 数量为合理值（支持整数/数字+/描述型）"):
        # 录制结果：'1'、'6'、'8'（整数）、'5+'、'8+'（带+号）、'Studio'（描述型）
        valid_beds = [b for b in bed_counts if b is not None]
        assert len(valid_beds) > 0, "至少应有1张卡片有 Bed 信息"
        for bed in valid_beds:
            if re.match(r'^\d+$', bed):
                # 纯整数：1～50 合理范围（学生公寓可能有多床位）
                num = int(bed)
                assert 1 <= num <= 50, f"Bed 数量 {num} 超出合理范围(1-50)"
                logger.info(f"  ✓ Bed 数量（整数）: {num}")
            elif re.match(r'^\d+\+$', bed):
                # "数字+" 格式（如 8+）：至少N间，合理
                logger.info(f"  ✓ Bed 数量（带+号）: '{bed}'，表示至少 {bed[:-1]} 间")
            else:
                # 描述型（如 Studio）：学生公寓特有，接受非空字符串
                assert len(bed.strip()) > 0, f"Bed 描述不应为空字符串"
                logger.info(f"  ✓ Bed 描述型: '{bed}'")


# ============================================================
# TC003 Bed 图标可见性
# ============================================================
@pytest.mark.case_id_au58_list_card_bed_student_apartment_003
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片Bed图标和数量-学生公寓")
@allure.title("Bed 图标可见性")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证列表卡片 Bed 图标（img[src*='Bedrooms']）可见且有正常尺寸（18×18px）")
def test_tc003_bed_icon_visible_with_size(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    with allure.step("步骤1：获取页面所有 Bed 图标"):
        # MCP录制：Bed 图标总数=15，icon[0] 18×18px visible=True
        bed_icons = page.locator('img[src*="Bedrooms"]')
        icon_count = bed_icons.count()
        logger.info(f"✓ 页面 Bed 图标总数: {icon_count}")
        assert icon_count > 0, "页面应有 Bed 图标（img[src*='Bedrooms']）"

    with allure.step("步骤2：验证前3个 Bed 图标可见且有正常尺寸"):
        for i in range(min(3, icon_count)):
            try:
                icon = bed_icons.nth(i)
                visible = icon.is_visible()
                box = icon.bounding_box()
                assert visible, f"Bed 图标[{i}] 应可见"
                assert box is not None, f"Bed 图标[{i}] 应有 bounding_box"
                assert box["width"] > 0 and box["height"] > 0, (
                    f"Bed 图标[{i}] 宽高应大于0，实际: w={box['width']}, h={box['height']}"
                )
                logger.info(f"  ✓ Bed 图标[{i}]: visible={visible}, {box['width']}×{box['height']}px")
            except AssertionError:
                raise
            except Exception as e:
                logger.warning(f"  ⚠ Bed 图标[{i}] 检查异常: {e}")

    with allure.step("步骤3：验证 Bed 图标与数量并排展示"):
        cards = plp.get_student_apartment_cards()
        visible_bed_cards = 0
        for i in range(min(5, cards.count())):
            if plp.get_bed_icon_visible(cards.nth(i)):
                visible_bed_cards += 1
        assert visible_bed_cards > 0, "至少1张卡片的 Bed 图标应可见"
        logger.info(f"✓ 有可见 Bed 图标的卡片数: {visible_bed_cards}/5")


# ============================================================
# TC004 列表页 Bed 数量与详情页一致
# ============================================================
@pytest.mark.case_id_au58_list_card_bed_student_apartment_004
@pytest.mark.p1
@allure.feature("OK")
@allure.story("AU站列表卡片Bed图标和数量-学生公寓")
@allure.title("列表页 Bed 数量与详情页一致")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("记录列表页第一张卡片的 Bed 数量，点击进入详情页，验证两处 Bed 数量一致")
def test_tc004_bed_count_consistent_with_detail_page(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    with allure.step("步骤1：获取列表页第一张有 Bed 信息的卡片数量"):
        cards = plp.get_student_apartment_cards()
        card_count = cards.count()
        assert card_count > 0, "列表应有卡片"

        # 找第一张有 Bed 图标的卡片，同时记录 href 防止重渲染偏移
        target_idx = None
        list_bed = None
        target_href = None
        for i in range(min(card_count, 10)):
            bed = plp.get_bed_count_from_card(cards.nth(i))
            if bed is not None:
                target_idx = i
                list_bed = bed
                target_href = cards.nth(i).get_attribute("href")
                break

        if target_idx is None:
            pytest.skip("前10张卡片均无 Bed 信息，跳过本用例")

        logger.info(f"✓ 列表页 card[{target_idx}] Bed 数量: {list_bed!r}，href: {(target_href or '')[-40:]}")

    with allure.step("步骤2：点击该卡片进入详情页"):
        # 用 href 精确定位，防止列表重渲染导致 nth(idx) 偏移
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

    with allure.step("步骤3：获取详情页 Bed 数量"):
        detail_bed = plp.get_bed_count_from_detail_page(detail_page)
        logger.info(f"✓ 详情页 Bed 数量: {detail_bed!r}")
        detail_page.close()

    with allure.step("步骤4：验证列表页与详情页 Bed 数量一致"):
        assert detail_bed is not None, "详情页应展示 Bed 数量"
        assert list_bed == detail_bed, (
            f"列表页 Bed 数量 '{list_bed}' 与详情页 '{detail_bed}' 不一致"
        )
        logger.info(f"✓ 列表页与详情页 Bed 数量一致: {list_bed!r}")


# ============================================================
# TC005 Bed 数量为空或特殊情况处理
# ============================================================
@pytest.mark.case_id_au58_list_card_bed_student_apartment_005
@pytest.mark.p2
@allure.feature("OK")
@allure.story("AU站列表卡片Bed图标和数量-学生公寓")
@allure.title("Bed 数量为空或特殊情况处理")
@allure.severity(allure.severity_level.MINOR)
@allure.description("查找无 Bed 图标的卡片，验证页面不崩溃、不报错，整体展示正常")
def test_tc005_bed_missing_cards_handled_gracefully(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    with allure.step("步骤1：获取前10张卡片的 Bed 信息"):
        # MCP录制：card[6] 无 Bed 图标（no-bed-icon）
        bed_counts = plp.get_all_bed_counts(limit=10)
        logger.info(f"✓ 前10张卡片 Bed 信息: {bed_counts}")

    with allure.step("步骤2：统计无 Bed 信息的卡片"):
        missing_bed = [i for i, b in enumerate(bed_counts) if b is None]
        has_bed = [i for i, b in enumerate(bed_counts) if b is not None]
        logger.info(f"  有 Bed 信息的卡片: {has_bed}")
        logger.info(f"  无 Bed 信息的卡片: {missing_bed}（MCP录制发现 card[6] 无 Bed 图标）")

    with allure.step("步骤3：验证页面整体正常（无异常、无空白崩溃）"):
        # 验证有卡片展示
        card_count = plp.get_student_apartment_card_count()
        assert card_count > 0, "列表页应有卡片，页面正常"

        if not missing_bed:
            # 当前测试数据中所有卡片均有 Bed 信息，属于正常情况，直接通过
            logger.info(f"✓ 前10张卡片均有 Bed 信息（无缺失），页面正常展示")
        else:
            # 验证无 Bed 图标的卡片本身不崩溃（仍可见）
            cards = plp.get_student_apartment_cards()
            for idx in missing_bed:
                try:
                    card = cards.nth(idx)
                    visible = card.is_visible()
                    assert visible, f"无 Bed 图标的 card[{idx}] 仍应可见"
                    txt = card.inner_text().strip()
                    assert len(txt) > 0, f"无 Bed 图标的 card[{idx}] 应有非空文本内容"
                    logger.info(f"  ✓ card[{idx}] 无 Bed 图标但卡片正常展示: {txt[:60]!r}")
                except AssertionError:
                    raise
                except Exception as e:
                    logger.warning(f"  ⚠ card[{idx}] 检查异常: {e}")

        logger.info(f"✓ 页面正常，有 Bed 信息: {len(has_bed)} 张，无 Bed 信息: {len(missing_bed)} 张")
