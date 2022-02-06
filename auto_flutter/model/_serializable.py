from __future__ import annotations

from abc import ABCMeta, abstractclassmethod
from typing import Dict, Generic, List, Optional, TypeVar, Union

T = TypeVar("T")


class Serializable(Generic[T], metaclass=ABCMeta):
    Json = Union[Dict, List, str, int, None]

    @abstractclassmethod
    def to_json(self) -> Serializable.Json:
        raise NotImplementedError("to_json is not implemented")

    @abstractclassmethod
    def from_json(json: Serializable.Json) -> Optional[T]:
        raise NotImplementedError("from_json is not implemented")
