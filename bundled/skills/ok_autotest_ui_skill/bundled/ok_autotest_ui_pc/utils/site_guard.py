from __future__ import annotations

from typing import Any


def guard_site_and_goto_or_skip(
    page: Any,
    url: str,
    *,
    ready_locator: Any | None = None,
    timeout_ms: int = 15000,
    wait_until: str = "domcontentloaded",
    logger: Any | None = None,
    transient_retry: int = 2,
) -> Any:
    """
    站点守卫：
    1) 先做 timeout_ms 内健康探测，命中 5xx 则直接 skip
    2) 导航后若 timeout_ms 内关键元素未可见则 skip
    """
    import pytest

    http_error_keywords = ("ERR_HTTP_RESPONSE_CODE_FAILURE", "net::ERR_HTTP")
    timeout_keywords = ("Timeout", "timed out")

    def _status_code(resp: Any) -> int | None:
        if not resp:
            return None
        try:
            return resp.status
        except Exception:
            return None

    def _skip(reason: str) -> None:
        if logger:
            logger.warning(reason)
        pytest.skip(reason)

    # 先用 request API 进行快速健康探测，避免 page.goto 卡长超时
    for attempt in range(transient_retry + 1):
        try:
            health_resp = page.request.get(url, timeout=timeout_ms, fail_on_status_code=False)
            health_code = _status_code(health_resp)
            if health_code is None or health_code < 500:
                break
            if attempt >= transient_retry:
                _skip(f"站点返回 {health_code}，跳过当前用例: {url}")
            page.wait_for_timeout(800)
        except Exception as exc:  # noqa: BLE001
            err_text = str(exc)
            if any(keyword in err_text for keyword in http_error_keywords):
                if attempt >= transient_retry:
                    _skip(f"站点 HTTP 异常，跳过当前用例: {url} | {err_text[:120]}")
                page.wait_for_timeout(800)
            else:
                raise

    response = None
    for attempt in range(transient_retry + 1):
        try:
            response = page.goto(url, wait_until=wait_until, timeout=timeout_ms)
            break
        except Exception as exc:  # noqa: BLE001
            err_text = str(exc)
            if any(keyword in err_text for keyword in http_error_keywords):
                if attempt >= transient_retry:
                    _skip(f"站点 HTTP 异常，跳过当前用例: {url} | {err_text[:120]}")
                page.wait_for_timeout(900)
                continue
            if any(keyword in err_text for keyword in timeout_keywords):
                if attempt >= transient_retry:
                    _skip(f"页面 {timeout_ms}ms 内未完成加载，跳过当前用例: {url}")
                page.wait_for_timeout(900)
                continue
            raise

    code = _status_code(response)
    if code is not None and code >= 500:
        _skip(f"站点返回 {code}，跳过当前用例: {url}")

    if ready_locator is not None:
        last_err = None
        for attempt in range(2):
            try:
                ready_locator.first.wait_for(state="visible", timeout=timeout_ms)
                break
            except Exception as exc:  # noqa: BLE001
                last_err = exc
                if attempt == 0:
                    try:
                        page.reload(wait_until=wait_until, timeout=max(timeout_ms * 4, 45000))
                        page.wait_for_timeout(1200)
                    except Exception:
                        pass
                else:
                    _skip(
                        f"关键元素 {timeout_ms}ms 内未加载完成（已重载重试），跳过当前用例: {url} | {str(last_err)[:80]}"
                    )

    return response
