from abc import ABCMeta, abstractclassmethod
from typing import Dict, Generic, Optional, TypeVar, Union

T = TypeVar("T")
Json = Union[Dict, str, int, None]


class Serializable(Generic[T], metaclass=ABCMeta):
    @abstractclassmethod
    def to_json(self) -> Json:
        raise NotImplementedError("to_json is not implemented")

    @abstractclassmethod
    def from_json(json: Json) -> Optional[T]:
        raise NotImplementedError("from_json is not implemented")
