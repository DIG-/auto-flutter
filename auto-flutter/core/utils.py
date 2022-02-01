from abc import ABCMeta
from enum import Enum
from typing import (
    Callable,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
)
from ..model._serializable import Serializable


class _Iterable:
    T = TypeVar("T")

    def first_or_none(
        iterable: Iterable[T], condition: Callable[[T], bool]
    ) -> Optional[T]:
        for it in iterable:
            if condition(it):
                return it
        return None

    def first_or_default(
        iterable: Iterable[T], condition: Callable[[T], bool], fallback: Callable[[], T]
    ) -> T:
        for it in iterable:
            if condition(it):
                return it
        return fallback()

    def flatten(iterable: Iterable[Iterable[T]]) -> List[T]:
        return [item for sublist in iterable for item in sublist]


class _JsonUtil(metaclass=ABCMeta):
    Input = Union[Serializable, Enum, Serializable.Json]

    def _map_key_to_json(key: Input) -> Serializable.Json:
        output = key
        if isinstance(key, Serializable):
            output = key.to_json()
        elif isinstance(key, Enum):
            output = key.value
        if not isinstance(output, (str, int)):
            raise ValueError("Can not use dictionary key as `{}`".format(type(output)))
        return output

    def optional_to_json(value: Optional[Input]) -> Optional[Serializable.Json]:
        if value is None:
            return None
        return _JsonUtil.value_to_json(value)

    def value_to_json(value: Input) -> Serializable.Json:
        if isinstance(value, Serializable):
            return value.to_json()
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, List):
            return _JsonUtil.list_to_json(value)
        if isinstance(value, Dict):
            return _JsonUtil.map_to_json(value)
        return value

    def map_to_json(
        input: Dict[Input, Input]
    ) -> Dict[Serializable.Json, Serializable.Json]:
        return dict(
            map(
                lambda it: (
                    _JsonUtil._map_key_to_json(it[0]),
                    _JsonUtil.value_to_json(it[1]),
                ),
                input.items(),
            )
        )

    def list_to_json(input: List[Input]) -> List[Serializable.Json]:
        return list(map(lambda it: _JsonUtil.value_to_json(it), input))

    CN = TypeVar("CN", Dict, List)

    def clear_nones(input: CN) -> CN:
        if isinstance(input, List):
            return [_JsonUtil.clear_nones(x) for x in input if x is not None]
        elif isinstance(input, Dict):
            return {
                key: _JsonUtil.clear_nones(val)
                for key, val in input.items()
                if val is not None
            }
        return input
