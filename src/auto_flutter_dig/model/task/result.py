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

    def __repr__(self) -> str:
        return "{cls}(error={error}, success={success}, message={message}, args={args})".format(
            cls=type(self).__name__,
            error=self.error,
            success=self.success,
            message=self.message,
            args=self.args,
        )


class TaskResultHelp(TaskResult):  # Will be handled as error, but append Help at end
    ...
