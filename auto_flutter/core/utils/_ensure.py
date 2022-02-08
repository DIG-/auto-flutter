from abc import ABC
from typing import Any, Optional, Type, TypeVar


class _Ensure(ABC):
    T = TypeVar("T")

    def not_none(input: Optional[T], name: Optional[str] = None) -> T:
        if input is None:
            if name is None:
                raise AssertionError("Field require valid value")
            else:
                raise AssertionError("Field `{}` require valid value".format(name))
        return input

    def type(
        input: Optional[T], cls: Type[T], name: Optional[str] = None
    ) -> Optional[T]:
        if input is None:
            return None
        if isinstance(input, cls):
            return input
        if name is None:
            raise AssertionError(
                "Field must be instance of `{}`, but `{}` was used".format(
                    cls.__name__, type(input)
                )
            )
        else:
            raise AssertionError(
                "Field `{}` must be instance of `{}`, but `{}` was used".format(
                    name, cls.__name__, type(input)
                )
            )

    def type_not_none(
        input: Optional[T], cls: Type[T], name: Optional[str] = None
    ) -> T:
        if not input is None and isinstance(input, cls):
            return input
        if name is None:
            raise AssertionError(
                "Field must be instance of `{}`, but `{}` was used".format(
                    cls.__name__, type(input)
                )
            )
        else:
            raise AssertionError(
                "Field `{}` must be instance of `{}`, but `{}` was used".format(
                    name, cls.__name__, type(input)
                )
            )

    def instance(input: Any, cls: Type[T], name: Optional[str] = None) -> T:
        if not input is None and isinstance(input, cls):
            return input
        if name is None:
            raise AssertionError(
                "Field must be intance of `{}`, but `{}` was used".format(
                    cls.__name__, type(input)
                )
            )
        else:
            raise AssertionError(
                "Field {} must be intance of `{}`, but `{}` was used".format(
                    name, cls.__name__, type(input)
                )
            )
