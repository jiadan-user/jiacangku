class PhaseBlockedError(RuntimeError):
    """当流程缺少外部输入、暂时无法继续时抛出。"""

    def __init__(self, message: str, run_id: str | None = None) -> None:
        super().__init__(message)
        self.run_id = run_id
