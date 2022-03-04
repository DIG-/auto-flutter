from abc import abstractmethod
from typing import Generic, TypeVar

from .....model.argument.arguments import Args
from .....model.argument.option.option import Option

T_co = TypeVar("T_co", covariant=True)

__all__ = ["_DecodedOption"]


class _DecodedOption(Option, Generic[T_co]):
    def get(self, args: Args) -> T_co:
        value = args.get(self)
        if value is None:
            raise ValueError("Check if option exists before getting")
        return self._convert(value)

    @abstractmethod
    def _convert(self, input: str) -> T_co:
        raise NotImplementedError()
