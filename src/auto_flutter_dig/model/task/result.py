from __future__ import annotations

from typing import Optional

from ...core.utils import _Ensure
from ...model.result import Result
from ..argument import Args


class TaskResult(Result):
    def __init__(
        self,
        args: Args,
        error: Optional[BaseException] = None,
        message: Optional[str] = None,
        success: Optional[bool] = None,
    ) -> None:
        self.args: Args = _Ensure.instance(args, Args, "args")
        self.message: Optional[str] = _Ensure.type(message, str, "message")
        super().__init__(
            _Ensure.type(error, BaseException, "error"),
            _Ensure.type(success, bool, "success"),
        )
