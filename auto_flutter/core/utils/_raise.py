from __future__ import annotations

from typing import NoReturn


class _Raise:
    def __new__(cls: type[_Raise], error: BaseException) -> NoReturn:
        raise error
