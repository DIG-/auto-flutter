from __future__ import annotations

from abc import ABCMeta, abstractclassmethod
from enum import Enum
from typing import Any, Dict, Final, Generic, List, Optional, TypeVar, Union

T = TypeVar("T")


class Serializable(Generic[T], metaclass=ABCMeta):
    Json = Union[Dict, List, str, int, None]

    @abstractclassmethod
    def to_json(self) -> Serializable.Json:
        raise NotImplementedError("to_json is not implemented")

    @abstractclassmethod
    def from_json(json: Serializable.Json) -> Optional[T]:
        raise NotImplementedError("from_json is not implemented")


E = TypeVar("E", bound=Enum)


class SerializableEnum(Serializable[E]):
    def __init__(self, enum: E) -> None:
        super().__init__()
        self.enum: E = enum

    def __getattribute__(self, __name: str) -> Any:
        if __name in ("to_json", "from_json"):
            return object.__getattribute__(self, __name)
        enum: Final[E] = object.__getattribute__(self, "enum")
        return enum.__getattribute__(__name)
