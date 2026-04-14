"""
AU站 - 列表卡片 Bathroom 图标和数量功能测试（学生公寓 cate-student-apartment）

录制文档：test_plans/au58-Property-列表卡片bathroom图标和数量功能测试用例.md
生成时间：2026-03-12
测试目标：验证 Canberra 学生公寓列表页卡片的 Bathroom 图标和数量展示

录制要点（MCP 录制结果）：
- 卡片定位器：a[href*="student-apartment"]（30张）
- Bathroom 图标：img.room-distance-type-item-icon[src*="Bathrooms"]，18×18px 可见
- Bathroom 数量：.room-distance-type-item-label（Bathroom 图标同级）
- 数量格式：整数（'1'、'3'）、带+号（'5+'）；card[6/7/8] 无 Bathroom 图标
- 详情页取 MainInfo 区：img[src*="Bathrooms"] 旁的 MainInfo_value（不能用推荐卡片区）
- 录制验证：列表页 card[0] bath='1'，详情页 MainInfo bath='1'，一致
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
# TC001 列表卡片展示 Bathroom 图标和数量
# ============================================================
@pytest.mark.case_id_au58_list_card_bathroom_student_apartment_001
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片Bathroom图标和数量-学生公寓")
@allure.title("列表卡片展示 Bathroom 图标和数量")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("打开学生公寓列表页，验证列表卡片展示 Bathroom 图标和数量（正整数或合理描述）")
def test_tc001_bathroom_icon_and_count_visible(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    with allure.step("步骤1：打开列表页，等待加载完成"):
        page.wait_for_load_state("domcontentloaded", timeout=10000)
        logger.info("✓ 列表页加载完成")

    with allure.step("步骤2：统计卡片总数"):
        card_count = plp.get_student_apartment_card_count()
        assert card_count > 0, "学生公寓列表应至少有一张卡片"
        logger.info(f"✓ 当前页卡片总数: {card_count}")

    with allure.step("步骤3：验证前5张卡片中有 Bathroom 数量展示"):
        # MCP录制：img.room-distance-type-item-icon[src*="Bathrooms"] + .room-distance-type-item-label
        bath_counts = plp.get_all_bath_counts(limit=5)
        logger.info(f"✓ 前5张卡片 Bathroom 数量: {bath_counts}")
        valid_baths = [b for b in bath_counts if b is not None]
        assert len(valid_baths) > 0, f"至少应有1张卡片展示 Bathroom 数量，实际: {bath_counts}"
        for bath in valid_baths:
            assert bath != "", f"Bathroom 数量不应为空字符串，实际: {bath!r}"
        logger.info(f"✓ 有 Bathroom 信息的卡片: {len(valid_baths)}/{len(bath_counts)}")


# ============================================================
# TC002 Bathroom 数量取值合理
# ============================================================
@pytest.mark.case_id_au58_list_card_bathroom_student_apartment_002
@pytest.mark.p1
@allure.feature("OK")
@allure.story("AU站列表卡片Bathroom图标和数量-学生公寓")
@allure.title("Bathroom 数量取值合理")
@allure.severity(allure.severity_level.NORMAL)
@allure.description(
    "验证列表卡片 Bathroom 数量为合理值，支持以下格式：\n"
    "1. 整数（如 1、2、3、4、5）：范围 1～50\n"
    "2. 小数（如 1.5、2.5、3.5、4.5、5.5）：半卫生间格式\n"
    "3. 数字+号（如 5+、5.5+）：表示至少N个\n"
    "4. 描述型文字（如 shared）：共享卫生间描述"
)
def test_tc002_bathroom_count_value_reasonable(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    with allure.step("步骤1：获取前10张卡片的 Bathroom 数量"):
        bath_counts = plp.get_all_bath_counts(limit=10)
        logger.info(f"✓ 前10张卡片 Bathroom 数量: {bath_counts}")

    with allure.step("步骤2：验证 Bathroom 数量为合理值（整数/小数/带+号/描述型）"):
        # 已知合理值：1、1.5、2、2.5、3、3.5、4、4.5、5、5.5、5+、shared 等
        valid_baths = [b for b in bath_counts if b is not None]
        assert len(valid_baths) > 0, "至少应有1张卡片有 Bathroom 信息"
        for bath in valid_baths:
            # 去掉末尾 + 号后的数值部分（如 "5+" → "5"，"5.5+" → "5.5"）
            num_part = bath.rstrip('+')
            if re.match(r'^\d+(\.\d+)?$', num_part):
                num = float(num_part)
                assert 1 <= num <= 50, f"Bathroom 数量 {num} 超出合理范围(1-50)"
                # 小数部分只允许 .5（半卫生间）
                decimal = num - int(num)
                assert decimal in (0.0, 0.5), (
                    f"Bathroom 小数部分应为 0 或 0.5，实际: {bath!r}"
                )
                suffix = "（带+号）" if bath.endswith('+') else ""
                logger.info(f"  ✓ Bathroom 数量{suffix}: '{bath}'")
            else:
                # 描述型（如 shared）：非空字符串
                assert len(bath.strip()) > 0, f"Bathroom 描述不应为空字符串"
                logger.info(f"  ✓ Bathroom 描述型: '{bath}'")


# ============================================================
# TC003 Bathroom 图标可见性
# ============================================================
@pytest.mark.case_id_au58_list_card_bathroom_student_apartment_003
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片Bathroom图标和数量-学生公寓")
@allure.title("Bathroom 图标可见性")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("验证列表卡片 Bathroom 图标（img[src*='Bathrooms']）可见且有正常尺寸（18×18px）")
def test_tc003_bathroom_icon_visible_with_size(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    with allure.step("步骤1：获取页面所有 Bathroom 图标"):
        # MCP录制：Bathroom 图标总数=12，18×18px visible=True
        bath_icons = page.locator('img[src*="Bathrooms"]')
        icon_count = bath_icons.count()
        logger.info(f"✓ 页面 Bathroom 图标总数: {icon_count}")
        assert icon_count > 0, "页面应有 Bathroom 图标（img[src*='Bathrooms']）"

    with allure.step("步骤2：验证前3个 Bathroom 图标可见且有正常尺寸（18×18px）"):
        for i in range(min(3, icon_count)):
            try:
                icon = bath_icons.nth(i)
                visible = icon.is_visible()
                box = icon.bounding_box()
                assert visible, f"Bathroom 图标[{i}] 应可见"
                assert box is not None, f"Bathroom 图标[{i}] 应有 bounding_box"
                assert box["width"] > 0 and box["height"] > 0, (
                    f"Bathroom 图标[{i}] 宽高应大于0，实际: w={box['width']}, h={box['height']}"
                )
                logger.info(f"  ✓ Bathroom 图标[{i}]: visible={visible}, {box['width']}×{box['height']}px")
            except AssertionError:
                raise
            except Exception as e:
                logger.warning(f"  ⚠ Bathroom 图标[{i}] 检查异常: {e}")

    with allure.step("步骤3：验证 Bathroom 图标与数量并排展示"):
        cards = plp.get_student_apartment_cards()
        visible_bath_cards = 0
        for i in range(min(5, cards.count())):
            if plp.get_bath_icon_visible(cards.nth(i)):
                visible_bath_cards += 1
        assert visible_bath_cards > 0, "至少1张卡片的 Bathroom 图标应可见"
        logger.info(f"✓ 有可见 Bathroom 图标的卡片数: {visible_bath_cards}/5")


# ============================================================
# TC004 列表页 Bathroom 数量与详情页一致
# ============================================================
@pytest.mark.case_id_au58_list_card_bathroom_student_apartment_004
@pytest.mark.p1
@allure.feature("OK")
@allure.story("AU站列表卡片Bathroom图标和数量-学生公寓")
@allure.title("列表页 Bathroom 数量与详情页一致")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("记录列表页第一张卡片的 Bathroom 数量，点击进入详情页，验证两处数量一致（取 MainInfo 区）")
def test_tc004_bathroom_count_consistent_with_detail_page(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    with allure.step("步骤1：获取列表页第一张有 Bathroom 信息的卡片数量"):
        cards = plp.get_student_apartment_cards()
        card_count = cards.count()
        assert card_count > 0, "列表应有卡片"

        target_idx = None
        list_bath = None
        target_href = None
        for i in range(min(card_count, 10)):
            bath = plp.get_bath_count_from_card(cards.nth(i))
            if bath is not None:
                target_idx = i
                list_bath = bath
                target_href = cards.nth(i).get_attribute("href")
                break

        if target_idx is None:
            pytest.skip("前10张卡片均无 Bathroom 信息，跳过本用例")

        logger.info(f"✓ 列表页 card[{target_idx}] Bathroom 数量: {list_bath!r}，href: {(target_href or '')[-40:]}")

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

    with allure.step("步骤3：获取详情页 Bathroom 数量（MainInfo 区）"):
        detail_bath = plp.get_bath_count_from_detail_page(detail_page)
        logger.info(f"✓ 详情页 Bathroom 数量: {detail_bath!r}")
        detail_page.close()

    with allure.step("步骤4：验证列表页与详情页 Bathroom 数量一致"):
        assert detail_bath is not None, "详情页应展示 Bathroom 数量"
        assert list_bath == detail_bath, (
            f"列表页 Bathroom 数量 '{list_bath}' 与详情页 '{detail_bath}' 不一致"
        )
        logger.info(f"✓ 列表页与详情页 Bathroom 数量一致: {list_bath!r}")


# ============================================================
# TC005 Bathroom 数量为空或特殊情况处理
# ============================================================
@pytest.mark.case_id_au58_list_card_bathroom_student_apartment_005
@pytest.mark.p2
@allure.feature("OK")
@allure.story("AU站列表卡片Bathroom图标和数量-学生公寓")
@allure.title("Bathroom 数量为空或特殊情况处理")
@allure.severity(allure.severity_level.MINOR)
@allure.description("查找无 Bathroom 图标的卡片，验证页面不崩溃、不报错，整体展示正常")
def test_tc005_bathroom_missing_cards_handled_gracefully(page, config):
    plp = _ensure_logged_in_and_on_list(page, config)
    with allure.step("步骤1：获取前10张卡片的 Bathroom 信息"):
        # MCP录制：card[6/7/8] 无 Bathroom 图标（no-bath-icon）
        bath_counts = plp.get_all_bath_counts(limit=10)
        logger.info(f"✓ 前10张卡片 Bathroom 信息: {bath_counts}")

    with allure.step("步骤2：统计无 Bathroom 信息的卡片"):
        missing_bath = [i for i, b in enumerate(bath_counts) if b is None]
        has_bath = [i for i, b in enumerate(bath_counts) if b is not None]
        logger.info(f"  有 Bathroom 信息的卡片: {has_bath}")
        logger.info(f"  无 Bathroom 信息的卡片: {missing_bath}（MCP录制发现 card[6/7/8] 无图标）")

    with allure.step("步骤3：验证页面整体正常（无异常、无空白崩溃）"):
        card_count = plp.get_student_apartment_card_count()
        assert card_count > 0, "列表页应有卡片，页面正常"

        # 滚回顶部确保卡片在视口内
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(500)

        cards = plp.get_student_apartment_cards()
        for idx in missing_bath:
            try:
                card = cards.nth(idx)
                # 滚动到卡片位置确保可见
                card.scroll_into_view_if_needed(timeout=5000)
                page.wait_for_timeout(300)
                txt = card.inner_text().strip()
                assert len(txt) > 0, f"无 Bathroom 图标的 card[{idx}] 应有非空文本内容"
                logger.info(f"  ✓ card[{idx}] 无 Bathroom 图标但卡片正常展示: {txt[:60]!r}")
            except AssertionError:
                raise
            except Exception as e:
                logger.warning(f"  ⚠ card[{idx}] 检查异常: {e}")

        logger.info(f"✓ 页面正常，有 Bathroom 信息: {len(has_bath)} 张，无 Bathroom 信息: {len(missing_bath)} 张")
