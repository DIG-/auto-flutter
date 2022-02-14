from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Generic, Optional, TypeVar

from .type import Json

T = TypeVar("T")


class Serializable(Generic[T], metaclass=ABCMeta):
    Json = Json

    @abstractmethod
    def to_json(self) -> Serializable.Json:
        raise NotImplementedError("to_json is not implemented")

    @staticmethod
    @abstractmethod
    def from_json(json: Serializable.Json) -> Optional[T]:
        raise NotImplementedError("from_json is not implemented")
