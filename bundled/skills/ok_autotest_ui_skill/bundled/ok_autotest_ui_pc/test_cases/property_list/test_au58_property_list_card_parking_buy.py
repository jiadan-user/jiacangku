"""
AU站 - 买房列表卡片 Parking 图标和数量功能测试

录制文档：test_plans/au58-Property-列表卡片parking图标和数量功能测试用例.md
生成时间：2026-03-13
测试目标：验证 Canberra 买房列表页卡片的 Parking（停车位）图标和数量展示

录制要点（MCP 录制结果）：
- 卡片定位器：a[href*="cate-property-for-sale-"]
- Parking 图标：img.room-distance-type-item-icon[src*="car.png"]
- Parking 数量：.room-distance-type-item > .room-distance-type-item-label
- card[0] 有停车位（数量: "14"），其余卡片无停车位图标
- 详情页 Parking 图标：img.MainInfo_icon__kiZFy[src*="parking_space_v1.png"]
- 详情页 Parking 数量：.MainInfo_item__ZNJ3X > .MainInfo_value__U8n3C（"14"，与列表一致）
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
    "list_url": "https://au.58v5.cn/en/city-canberra/cate-buy/?iconSource=buy",
    "browser": {
        "type": "chromium",
        "headless": True,
        "viewport": {"width": 1920, "height": 1080},
    },
    "timeout": {"default": 30000, "wait": 10000, "navigation": 30000},
}


def _goto_list(page, config):
    """直接打开买房列表页（无需登录）。"""
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
# TC001 列表卡片停车位图标和数量正常展示
# ============================================================
@pytest.mark.case_id_au58_list_card_parking_buy_001
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片Parking图标和数量-买房")
@allure.title("列表卡片停车位图标和数量正常展示")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("打开买房列表页，验证至少一张卡片展示停车位图标和数量")
def test_tc001_parking_icon_and_count_displayed(page, config):
    plp = _goto_list(page, config)

    with allure.step("步骤1：获取列表卡片数量"):
        card_count = plp.get_buy_card_count()
        assert card_count > 0, "买房列表页应至少有一张卡片"
        logger.info(f"✓ 卡片总数: {card_count}")

    with allure.step("步骤2：检查前20张卡片，至少一张有停车位图标和数量"):
        parking_counts = plp.get_all_parking_counts(max_cards=20)
        valid = [v for v in parking_counts if v is not None]
        if not valid:
            pytest.skip("当前买房列表无停车位信息卡片，跳过")
        logger.info(f"✓ 有停车位信息的卡片数: {len(valid)}，数量值: {valid}")

    with allure.step("步骤3：验证停车位数量非空"):
        for v in valid:
            assert v and len(v.strip()) > 0, f"停车位数量应非空，实际: {v!r}"
        logger.info(f"✓ 所有停车位数量均非空")


# ============================================================
# TC002 停车位数量取值合理
# ============================================================
@pytest.mark.case_id_au58_list_card_parking_buy_002
@pytest.mark.smoke
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片Parking图标和数量-买房")
@allure.title("停车位数量取值合理")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("停车位数量为合理格式：整数（1~100）或带+号（如 '2+'）")
def test_tc002_parking_count_value_valid(page, config):
    plp = _goto_list(page, config)

    with allure.step("步骤1：获取所有卡片停车位数量"):
        parking_counts = plp.get_all_parking_counts(max_cards=20)
        valid = [v for v in parking_counts if v is not None]
        if not valid:
            pytest.skip("当前买房列表无停车位信息，跳过")
        logger.info(f"✓ 停车位数量列表: {valid}")

    with allure.step("步骤2：验证每个数量取值格式"):
        for v in valid:
            v_stripped = v.strip()
            is_int = re.fullmatch(r'\d+', v_stripped) is not None
            is_plus = re.fullmatch(r'\d+(\.\d+)?\+', v_stripped) is not None
            assert is_int or is_plus, (
                f"停车位数量格式不合理: {v_stripped!r}，期望整数或带+号"
            )
        logger.info(f"✓ 所有停车位数量格式合理: {valid}")


# ============================================================
# TC003 停车位图标尺寸和可见性正常
# ============================================================
@pytest.mark.case_id_au58_list_card_parking_buy_003
@pytest.mark.p1
@allure.feature("OK")
@allure.story("AU站列表卡片Parking图标和数量-买房")
@allure.title("停车位图标尺寸和可见性正常")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("停车位图标在视口内可见，宽高 > 0")
def test_tc003_parking_icon_size_and_visibility(page, config):
    plp = _goto_list(page, config)

    with allure.step("步骤1：找到有停车位图标的卡片"):
        cards = plp.get_buy_cards()
        target_card = None
        for i in range(min(cards.count(), 20)):
            card = cards.nth(i)
            card.scroll_into_view_if_needed(timeout=3000)
            val = plp.get_parking_count_from_card(card)
            if val is not None:
                target_card = card
                logger.info(f"✓ card[{i}] 有停车位，数量: {val}")
                break
        if target_card is None:
            pytest.skip("当前买房列表无停车位图标，跳过")

    with allure.step("步骤2：验证图标尺寸和可见性"):
        icon_info = plp.get_parking_icon_visible(target_card)
        assert icon_info is not None, "应能获取到停车位图标信息"
        assert icon_info.get("width", 0) > 0, f"图标宽度应 > 0，实际: {icon_info}"
        assert icon_info.get("height", 0) > 0, f"图标高度应 > 0，实际: {icon_info}"
        logger.info(f"✓ 停车位图标尺寸: {icon_info['width']}x{icon_info['height']}")


# ============================================================
# TC004 停车位数量与详情页一致
# ============================================================
@pytest.mark.case_id_au58_list_card_parking_buy_004
@pytest.mark.p0
@allure.feature("OK")
@allure.story("AU站列表卡片Parking图标和数量-买房")
@allure.title("停车位数量与详情页一致")
@allure.severity(allure.severity_level.CRITICAL)
@allure.description("列表页停车位数量与详情页 MainInfo 区展示一致")
def test_tc004_parking_count_consistent_with_detail(page, config):
    plp = _goto_list(page, config)

    with allure.step("步骤1：找到有停车位的卡片，记录数量和 href"):
        cards = plp.get_buy_cards()
        list_parking = None
        target_href = None
        for i in range(min(cards.count(), 20)):
            val = plp.get_parking_count_from_card(cards.nth(i))
            if val is not None:
                list_parking = val.strip()
                target_href = cards.nth(i).get_attribute("href")
                logger.info(f"✓ card[{i}] 列表停车位: {list_parking}, href: {target_href[:60]}")
                break
        if list_parking is None:
            pytest.skip("当前买房列表无停车位信息，跳过")

    with allure.step("步骤2：点击进入详情页"):
        try:
            with page.context.expect_page(timeout=10000) as new_page_info:
                plp.click_buy_card_by_href(target_href)
            detail_page = new_page_info.value
            detail_page.wait_for_load_state("domcontentloaded", timeout=15000)
            detail_page.wait_for_timeout(2000)
            detail_parking = plp.get_parking_count_from_detail_page(detail_page)
            detail_page.close()
        except Exception:
            page.wait_for_load_state("domcontentloaded", timeout=15000)
            page.wait_for_timeout(2000)
            detail_parking = plp.get_parking_count_from_detail_page(page)

    with allure.step("步骤3：验证列表页与详情页停车位数量一致"):
        assert detail_parking is not None, "详情页应展示 Parking 数量"
        assert list_parking == detail_parking.strip(), (
            f"列表页 Parking 数量 '{list_parking}' 与详情页 '{detail_parking}' 不一致"
        )
        logger.info(f"✓ 列表页与详情页停车位数量一致: {list_parking}")


# ============================================================
# TC005 无停车位信息的卡片正常展示（不崩溃）
# ============================================================
@pytest.mark.case_id_au58_list_card_parking_buy_005
@pytest.mark.p1
@allure.feature("OK")
@allure.story("AU站列表卡片Parking图标和数量-买房")
@allure.title("无停车位信息的卡片正常展示")
@allure.severity(allure.severity_level.NORMAL)
@allure.description("无停车位图标的卡片仍应正常可见，不因缺少数据而报错或布局异常")
def test_tc005_card_without_parking_still_visible(page, config):
    plp = _goto_list(page, config)

    with allure.step("步骤1：找到无停车位图标的卡片"):
        page.evaluate("window.scrollTo(0, 0)")
        cards = plp.get_buy_cards()
        no_parking_cards = []
        for i in range(min(cards.count(), 20)):
            val = plp.get_parking_count_from_card(cards.nth(i))
            if val is None:
                no_parking_cards.append(i)
        if not no_parking_cards:
            pytest.skip("所有卡片均有停车位图标，跳过本用例")
        logger.info(f"✓ 无停车位图标的卡片索引: {no_parking_cards[:5]}")

    with allure.step("步骤2：验证无停车位卡片仍正常可见"):
        for idx in no_parking_cards[:3]:
            card = cards.nth(idx)
            try:
                card.scroll_into_view_if_needed(timeout=5000)
            except Exception:
                pass
            assert card.is_visible(), f"无 Parking 图标的 card[{idx}] 仍应可见"
            logger.info(f"✓ card[{idx}] 无停车位图标，卡片正常展示")
