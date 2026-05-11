"""
ES 简历联调多文件（test_es_resume_add / test_es_resume_submit）共用同一 test_user_id。

全目录「一线程一文件」并行时，若不做串行化，会出现：
- A 进程用例执行中 B 进程 teardown 删库 → 提交/断言超时或状态错乱。

通过 flock 将「清理 + 用例主体 + 再清理」包在同一互斥区内（跨进程生效）。
"""
from __future__ import annotations

import fcntl
import os
import time
from contextlib import contextmanager
from pathlib import Path

# 与 _CONFIG["test_user_id"] 一致，避免与其他项目/tmp 文件冲突
_DEFAULT_USER_ID = "796567146451408960"


@contextmanager
def es_resume_user_db_lock(
    *,
    user_id: str = _DEFAULT_USER_ID,
    timeout_sec: float = 900.0,
    poll_sec: float = 0.25,
):
    base = Path(os.environ.get("TMPDIR", "/tmp"))
    lock_path = base / f"qa_agent_es_resume_user_{user_id}.lock"
    fp = open(lock_path, "a+", encoding="utf-8")
    try:
        deadline = time.monotonic() + timeout_sec
        while True:
            try:
                fcntl.flock(fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() > deadline:
                    raise TimeoutError(
                        f"等待 ES 简历共享用户 DB 锁超时 ({timeout_sec}s)；"
                        "请减少同账号 ES 脚本的并行度。"
                    ) from None
                time.sleep(poll_sec)
        yield
    finally:
        try:
            fcntl.flock(fp.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        fp.close()
