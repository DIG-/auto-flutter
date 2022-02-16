from __future__ import annotations

from typing import Optional

from ...core.utils import _Ensure
from ..argument import Args


class TaskResult:
    def __init__(
        self,
        args: Args,
        error: Optional[BaseException] = None,
        message: Optional[str] = None,
        success: Optional[bool] = None,
    ) -> None:
        self.args: Args = _Ensure.instance(args, Args, "args")
        self.error: Optional[BaseException] = _Ensure.type(
            error, BaseException, "error"
        )
        self.message: Optional[str] = _Ensure.type(message, str, "message")
        success = _Ensure.type(success, bool, "success")
        self.success: bool = (
            success if not success is None else (True if error is None else False)
        )
