from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Generic, Optional, TypeVar

from .type import Json

T = TypeVar("T")

__all__ = ["Json", "Serializable"]


class Serializable(Generic[T], metaclass=ABCMeta):
    @abstractmethod
    def to_json(self) -> Json:
        raise NotImplementedError("to_json is not implemented")

    @staticmethod
    @abstractmethod
    def from_json(json: Json) -> Optional[T]:
        raise NotImplementedError("from_json is not implemented")
