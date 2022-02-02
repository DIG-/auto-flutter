from abc import ABCMeta
from enum import Enum
from typing import (
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
)
from ..core.utils import _Iterable
from ..model._serializable import Serializable

Json = Serializable.Json
Input = Union[Serializable.Json, Serializable, Enum]


class _JsonEncode(metaclass=ABCMeta):
    def encode(input: Input) -> Json:
        if isinstance(input, str):
            return input
        if isinstance(input, Serializable):
            return input.to_json()
        if isinstance(input, Enum):
            return input.value
        if isinstance(input, List):
            return _JsonEncode.encode_list(input)
        if isinstance(input, Dict):
            return _JsonEncode.encode_dict(input)

    def encode_list(input: List[Input]) -> List[Json]:
        return list(map(lambda x: _JsonEncode.encode(x), input))

    def encode_dict(input: Dict[Input, Input]) -> Dict[str, Json]:
        return dict(map(_JsonEncode.__encode_dict_tuple, input.items()))

    def __encode_dict_tuple(input: Tuple[Input, Input]) -> Tuple[str, Json]:
        return (_JsonEncode.__encode_dict_key(input[0]), _JsonEncode.encode(input[1]))

    def __encode_dict_key(key: Input) -> str:
        output = _JsonEncode.encode(key)
        if isinstance(output, str):
            return output
        raise ValueError('Can not accept "{}" as dictionary key'.format(output))

    C = TypeVar("C", Dict, List)

    def clear_nones(input: C) -> C:
        if isinstance(input, List):
            return [_JsonEncode.clear_nones(x) for x in input if x is not None]
        elif isinstance(input, Dict):
            return {
                key: _JsonEncode.clear_nones(val)
                for key, val in input.items()
                if val is not None
            }
        return input


class _JsonDecode(metaclass=ABCMeta):
    T = TypeVar("T", bound=Union[str, Serializable, Enum])
    K = TypeVar("K", bound=Union[str, Enum])

    def decode(json: Json, cls: Type[T]) -> Optional[T]:
        if cls is str:
            if isinstance(json, str):
                return json
        elif issubclass(cls, Serializable):
            return cls.from_json(json)
        elif issubclass(cls, Enum):
            return _Iterable.first_or_none(cls.__iter__(), lambda x: x.value == json)

    def decode_optional(json: Optional[Json], cls: Type[T]) -> Optional[T]:
        if json is None:
            return None
        return _JsonDecode.decode(json, cls)

    def decode_list(json: List[Json], cls: Type[T]) -> List[T]:
        return list(
            filter(None.__ne__, map(lambda x: _JsonDecode.decode(x, cls), json))
        )

    def decode_list_optional(json: List[Json], cls: Type[T]) -> List[Optional[T]]:
        return list(map(lambda x: _JsonDecode.decode(x, cls), json))

    def decode_optional_list(
        json: Optional[List[Json]], cls: Type[T]
    ) -> Optional[List[T]]:
        if json is None:
            return None
        return _JsonDecode.decode_list(json, cls)

    def decode_optional_list_optional(
        json: Optional[List[Json]], cls: Type[T]
    ) -> Optional[List[Optional[T]]]:
        if json is None:
            return None
        return _JsonDecode.decode_list_optional(json, cls)

    def decode_dict(json: Dict[str, Json], kcls: Type[K], tcls: Type[T]) -> Dict[K, T]:
        m = _JsonDecode.__decode_dict_to_map(json, kcls, tcls)
        f = filter(lambda x: not x[1] is None, m)
        return dict(f)

    def decode_dict_optional(
        json: Dict[str, Json], kcls: Type[K], tcls: Type[T]
    ) -> Dict[K, Optional[T]]:
        return dict(_JsonDecode.__decode_dict_to_map(json, kcls, tcls))

    def decode_optional_dict(
        json: Optional[Dict[str, Json]], kcls: Type[K], tcls: Type[T]
    ) -> Optional[Dict[K, T]]:
        if json is None:
            return None
        return _JsonDecode.decode_dict(json, kcls, tcls)

    def decode_optional_dict_optional(
        json: Optional[Dict[str, Json]], kcls: Type[K], tcls: Type[T]
    ) -> Optional[Dict[K, Optional[T]]]:
        if json is None:
            return None
        return _JsonDecode.decode_dict_optional(json, kcls, tcls)

    def __decode_dict_to_map(
        json: Dict[str, Json], kcls: Type[K], tcls: Type[T]
    ) -> Iterable[Tuple[K, Optional[T]]]:
        m = map(lambda x: _JsonDecode.__decode_dict_tuple(x, kcls, tcls), json.items())
        return m

    def __decode_dict_tuple(
        input: Tuple[str, Json], kcls: Type[K], tcls: Type[T]
    ) -> Tuple[K, Optional[T]]:
        return (
            _JsonDecode.__decode_dict_key(input[0], kcls),
            _JsonDecode.decode(input[1], tcls),
        )

    def __decode_dict_key(key: str, kcls: Type[K]) -> K:
        decoded = _JsonDecode.decode(key, kcls)
        if decoded is None:
            raise ValueError(
                'Unexpected dict key decode "{}" to `{}`'.format(key, kcls.__name__)
            )
        if isinstance(decoded, str) or isinstance(decoded, Enum):
            return decoded
        raise ValueError('Invalid decoded key "{}" as `{}`'.format(key, type(key)))
