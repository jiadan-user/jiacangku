"""
AU58 - Property 房产发布功能测试
批次2：模块2 - 图片/视频/户型图上传（文档 TC001-TC005）

- TC001：单图上传 + Main。
- TC002：连续上传至 20 张边界 + 第 21 张拦截（耗时较长）。
- TC003：18 图 + 1 视频后，再传 1 图满 20，再传应失败。
- TC004/TC005：单视频上传；第二次传视频应被拒绝或提示。

样例视频：优先 test_data/videos/sample_publish.mp4；否则本机 ffmpeg 生成 1 秒黑场；再否则从 AU58_SAMPLE_MP4_URL（默认公开短视频）下载到该路径。
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import urllib.request
import pytest
import allure
from pathlib import Path

from pages.login_page import LoginPage
from pages.property_publish_page import PropertyPublishPage
from utils.session_manager import SessionManager
from utils.logger import setup_logger

logger = setup_logger()

_ROOT = Path(__file__).resolve().parents[2]
_SAMPLE_IMAGE = _ROOT / "test_data" / "images" / "apartment_1.png"
_SAMPLE_VIDEO = _ROOT / "test_data" / "videos" / "sample_publish.mp4"
# 无 ffmpeg 时用于拉取公开短视频（约 0.8MB，写入后缓存于本地路径）
_FALLBACK_SAMPLE_MP4_URL = os.getenv(
    "AU58_SAMPLE_MP4_URL",
    "https://www.w3schools.com/html/mov_bbb.mp4",
)


def _find_ffmpeg() -> str | None:
    w = shutil.which("ffmpeg")
    if w:
        return w
    for p in ("/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"):
        if Path(p).is_file():
            return p
    return None

_CONFIG = {
    "site": "au",
    "site_name": "澳洲站",
    "role": "seller",
    "user_name": "au_seller_liuyue",
    "base_url": "https://au.58v5.cn",
    "publish_url": "https://aupub.58v5.cn/biz/en",
    "test_account": {
        "username": "liuyue62@58.com",
        "password": "Xindemima1%",
    },
    "locale": "en-AU",
    "currency": "AUD",
    "browser": {
        "type": "chromium",
        "headless": True if os.getenv("CI") else False,
        "viewport": {"width": 1920, "height": 1080},
    },
    "timeout": {
        "default": 30000,
        "wait": 10000,
        "navigation": 30000,
    },
}


def _ensure_sample_video(path: Path) -> None:
    """确保存在可用短视频：本地文件 → ffmpeg 生成 → URL 下载兜底（缓存到 path）。"""
    if path.is_file():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = _find_ffmpeg()
    if ffmpeg:
        r = subprocess.run(
            [
                ffmpeg,
                "-y",
                "-f",
                "lavfi",
                "-i",
                "color=c=black:s=320x240:d=1",
                "-pix_fmt",
                "yuv420p",
                str(path),
            ],
            capture_output=True,
            timeout=120,
            text=True,
        )
        if r.returncode == 0 and path.is_file():
            return
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
    try:
        urllib.request.urlretrieve(_FALLBACK_SAMPLE_MP4_URL, str(path))
    except Exception as e:
        pytest.fail(
            f"无法准备样例视频 {path}（ffmpeg 不可用或失败，且下载失败: {e}）；"
            f"请安装 ffmpeg、设置 AU58_SAMPLE_MP4_URL，或将 mp4 放到该路径"
        )
    if not path.is_file():
        pytest.fail(f"样例视频仍不存在: {path}")


def _ensure_logged_in(page, config) -> None:
    session_name = f"{config['site']}_{config['role']}_{config['user_name']}"
    session_manager = SessionManager(page, config["base_url"], session_name)
    login_page = LoginPage(page)
    if session_manager.load_session():
        logger.info("✓ Session 已加载")
    else:
        login_page.navigate_to_home_page(config["base_url"])
        login_page.handle_cookie_popup()
        login_page.login(
            config["test_account"]["username"],
            config["test_account"]["password"],
        )
        session_manager.save_session()
        logger.info("✓ 登录并保存 Session")


def _open_property_rent_house_form(page, config) -> PropertyPublishPage:
    front = f"{config['publish_url']}/publish/front"
    page.goto(front, wait_until="domcontentloaded", timeout=config["timeout"]["navigation"])
    page.wait_for_timeout(2000)
    page.get_by_text("Property For Rent", exact=True).click()
    page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
    page.wait_for_timeout(1500)
    page.get_by_text("House").first.click()
    page.wait_for_load_state("domcontentloaded", timeout=config["timeout"]["navigation"])
    page.wait_for_timeout(2000)
    return PropertyPublishPage(page)


@pytest.fixture
def publish_form_rent_house(page, config):
    """已登录并进入「租房 - House」发布表单（含图片上传区域）。"""
    _ensure_logged_in(page, config)
    yield _open_property_rent_house_form(page, config)
    try:
        if page and not page.is_closed():
            page.goto(config["base_url"], wait_until="domcontentloaded", timeout=30000)
    except Exception:
        pass


def _tmpdir_unique_png_copies(base: Path, count: int, prefix: str) -> tuple[Path, list[str]]:
    """复制 base 为 count 个独立文件，返回 (临时目录, 绝对路径列表)。"""
    tmpdir = Path(tempfile.mkdtemp(prefix=prefix))
    paths: list[str] = []
    for i in range(count):
        p = tmpdir / f"copy_{i}.png"
        shutil.copy2(base, p)
        paths.append(str(p))
    return tmpdir, paths


def _assert_upload_cap_hint_visible(page) -> None:
    """第 21 张等场景：站点可能用 ant-message、notification 或英文/中文短句提示。"""
    toast = page.locator(
        ".ant-message-notice-message, .ant-message-notice-content, "
        ".ant-notification-notice-message, [role='alert']"
    )
    try:
        toast.first.wait_for(state="visible", timeout=8000)
        return
    except Exception:
        pass
    upper = page.get_by_text(
        re.compile(
            r"(20\s*(images|photos|files)|upload.*20|up to\s*20|"
            r"maximum|cannot\s+upload|too\s+many|"
            r"上限|最多|超出)",
            re.I,
        )
    )
    assert upper.first.is_visible(timeout=4000), "超出上限时应出现提示文案或 toast"


@pytest.mark.p0
@pytest.mark.case_id_au58_property_publish_m2_001
@allure.feature("AU站房产发布")
@allure.story("模块2：图片/视频/户型图上传")
@allure.title("TC001 图片正常上传（单张）")
@allure.severity(allure.severity_level.BLOCKER)
def test_m2_tc001_single_image_upload_shows_main(publish_form_rent_house, config):
    assert _SAMPLE_IMAGE.is_file(), f"缺少测试图片: {_SAMPLE_IMAGE}"
    ppp = publish_form_rent_house
    with allure.step("上传单张图片"):
        ppp.upload_single_image(str(_SAMPLE_IMAGE), wait_ms=3000)
    with allure.step("校验计数与 Main 标识"):
        count_text = ppp.get_upload_count_text()
        assert "1" in count_text and "20" in count_text, f"上传计数异常: {count_text!r}"
        assert ppp.is_main_label_visible(), "第一张图应显示 Main 标识"


@pytest.mark.p0
@pytest.mark.case_id_au58_property_publish_m2_002
@allure.feature("AU站房产发布")
@allure.story("模块2：图片/视频/户型图上传")
@allure.title("TC002 图片最大数量边界（20 张上限）")
@allure.severity(allure.severity_level.BLOCKER)
def test_m2_tc002_twenty_images_boundary(publish_form_rent_house, config):
    assert _SAMPLE_IMAGE.is_file(), f"缺少测试图片: {_SAMPLE_IMAGE}"
    ppp = publish_form_rent_house
    tmpdir, paths20 = _tmpdir_unique_png_copies(_SAMPLE_IMAGE, 20, "au58_m2_tc002_")
    try:
        with allure.step("逐张上传 20 份不同文件副本（避免同路径重复上传导致计数/状态异常）"):
            for idx, fp in enumerate(paths20, start=1):
                ppp.upload_single_image(fp, wait_ms=1400)
                logger.info("已上传 %s/20", idx)
            count_text = ""
            try:
                count_text = ppp.get_upload_count_text()
            except TimeoutError:
                pass
            if "20" not in count_text:
                thumbs = ppp.count_main_media_thumbnails()
                assert thumbs >= 20, (
                    f"满 20 张时期望计数含 20 或缩略图≥20: "
                    f"count_text={count_text!r}, thumbs={thumbs}"
                )
        with allure.step("第 21 张应被拒绝并出现上限类提示"):
            p21 = tmpdir / "boundary_21.png"
            shutil.copy2(_SAMPLE_IMAGE, p21)
            thumbs_before = ppp.count_main_media_thumbnails()
            ppp.upload_single_image(str(p21), wait_ms=3000)
            page = ppp.page
            page.wait_for_timeout(800)
            try:
                _assert_upload_cap_hint_visible(page)
            except AssertionError:
                thumbs_after = ppp.count_main_media_thumbnails()
                assert thumbs_after <= thumbs_before, (
                    "未出现 toast/文案时，第 21 张不应增加页内 img 峰值计数: "
                    f"before={thumbs_before}, after={thumbs_after}"
                )
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.mark.p0
@pytest.mark.case_id_au58_property_publish_m2_003
@allure.feature("AU站房产发布")
@allure.story("模块2：图片/视频/户型图上传")
@allure.title("TC003 图片+视频合计上限共享验证")
@allure.severity(allure.severity_level.BLOCKER)
def test_m2_tc003_image_video_combined_cap(publish_form_rent_house, config):
    assert _SAMPLE_IMAGE.is_file(), f"缺少测试图片: {_SAMPLE_IMAGE}"
    _ensure_sample_video(_SAMPLE_VIDEO)
    ppp = publish_form_rent_house
    tmpdir, paths18 = _tmpdir_unique_png_copies(_SAMPLE_IMAGE, 18, "au58_m2_tc003_")
    try:
        with allure.step("上传 18 张图片"):
            for i, fp in enumerate(paths18, start=1):
                ppp.upload_single_image(fp, wait_ms=1000)
                logger.info("TC003 已上传图 %s/18", i)
        with allure.step("上传 1 个视频（合计 19）"):
            ppp.upload_media_file(str(_SAMPLE_VIDEO), wait_ms=3500)
        with allure.step("再上传 1 张图应达到 20/20"):
            p19 = Path(paths18[0]).parent / "tc003_fill_20.png"
            shutil.copy2(_SAMPLE_IMAGE, p19)
            ppp.upload_single_image(str(p19), wait_ms=2500)
            ct = ""
            try:
                ct = ppp.get_upload_count_text()
            except TimeoutError:
                pass
            if "20" not in ct:
                thumbs = ppp.count_main_media_thumbnails()
                assert thumbs >= 20, (
                    f"合计满 20 时期望计数含 20 或缩略图≥20: "
                    f"count_text={ct!r}, thumbs={thumbs}"
                )
        with allure.step("再上传 1 张图应触发上限提示"):
            p20 = Path(paths18[0]).parent / "tc003_overflow.png"
            shutil.copy2(_SAMPLE_IMAGE, p20)
            thumbs_before = ppp.count_main_media_thumbnails()
            ppp.upload_single_image(str(p20), wait_ms=2000)
            page = ppp.page
            page.wait_for_timeout(800)
            try:
                _assert_upload_cap_hint_visible(page)
            except AssertionError:
                thumbs_after = ppp.count_main_media_thumbnails()
                assert thumbs_after <= thumbs_before, (
                    "未出现 toast/文案时，超出张数不应增加 img 峰值: "
                    f"before={thumbs_before}, after={thumbs_after}"
                )
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.mark.p0
@pytest.mark.case_id_au58_property_publish_m2_004
@allure.feature("AU站房产发布")
@allure.story("模块2：图片/视频/户型图上传")
@allure.title("TC004 视频上传（单个）")
@allure.severity(allure.severity_level.BLOCKER)
def test_m2_tc004_single_video_upload(publish_form_rent_house, config):
    _ensure_sample_video(_SAMPLE_VIDEO)
    ppp = publish_form_rent_house
    with allure.step("上传单个视频文件"):
        ppp.upload_media_file(str(_SAMPLE_VIDEO), wait_ms=4000)
    with allure.step("计数或页面应体现已上传媒体"):
        page = ppp.page
        ct = ""
        try:
            ct = ppp.get_upload_count_text()
        except TimeoutError:
            pass
        count_ok = "1" in ct and "20" in ct
        blob = page.evaluate("() => document.body.innerText || ''") or ""
        ok = bool(
            re.search(r"video|mp4|main|1\s*/\s*20", blob, re.I)
        )
        assert count_ok or ok or ppp.is_main_label_visible(), (
            f"上传视频后应有媒体计数或 Main/视频相关展示: count_text={ct!r}"
        )


@pytest.mark.p1
@pytest.mark.case_id_au58_property_publish_m2_005
@allure.feature("AU站房产发布")
@allure.story("模块2：图片/视频/户型图上传")
@allure.title("TC005 尝试上传第 2 个视频被拒绝")
@allure.severity(allure.severity_level.NORMAL)
def test_m2_tc005_second_video_rejected(publish_form_rent_house, config):
    _ensure_sample_video(_SAMPLE_VIDEO)
    ppp = publish_form_rent_house
    page = ppp.page
    with allure.step("先上传第 1 个视频"):
        ppp.upload_media_file(str(_SAMPLE_VIDEO), wait_ms=4000)
    with allure.step("再尝试上传第 2 个视频"):
        ppp.upload_media_file(str(_SAMPLE_VIDEO), wait_ms=3500)
    with allure.step("应出现仅允许单个视频或上限类提示"):
        body = page.evaluate("() => document.body.innerText || ''") or ""
        hit = bool(
            re.search(
                r"one\s+video|single\s+video|only\s+one|1\s*video|"
                r"second\s+video|another\s+video|最多|仅|一个视频|"
                r"20\s*(images|photos)|maximum|limit",
                body,
                re.I,
            )
        )
        toast = page.locator(
            ".ant-message-notice, [class*='toast'], [class*='notification'], [role='alert']"
        )
        assert hit or toast.count() > 0, (
            "第二次上传视频后应有文案或全局提示说明不可再传/已达上限"
        )
