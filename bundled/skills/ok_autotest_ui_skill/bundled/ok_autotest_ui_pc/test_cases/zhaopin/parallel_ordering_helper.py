import os
import tempfile
import time


def _marker_path(marker_name: str) -> str:
    """
    生成顺序标记路径（跨 worker 共享，不按 testrun uid 隔离）。
    
    注意：不使用 PYTEST_XDIST_TESTRUNUID，因为标记需要跨 worker 可见。
    使用固定的 run_uid 保证同一次 pytest 调用的所有 worker 都能访问同一标记文件。
    """
    safe_name = marker_name.replace("/", "_")
    return os.path.join(tempfile.gettempdir(), f"{safe_name}_shared.flag")


def clear_order_marker(marker_name: str) -> None:
    """清理顺序标记（通常用于先行用例开始前）。"""
    marker = _marker_path(marker_name)
    if os.path.exists(marker):
        os.remove(marker)


def mark_order_done(marker_name: str) -> None:
    """写入顺序标记（通常用于先行用例完成后）。"""
    marker = _marker_path(marker_name)
    with open(marker, "w", encoding="utf-8") as f:
        f.write(str(time.time()))


def wait_order_done(marker_name: str, timeout_sec: int = 180, poll_sec: float = 0.5) -> bool:
    """
    等待顺序标记出现；返回 True 表示检测到标记，False 表示超时。
    """
    marker = _marker_path(marker_name)
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        if os.path.exists(marker):
            return True
        time.sleep(poll_sec)
    return False
