from abc import ABC
from enum import Enum
from typing import Callable, Dict, Iterable, List, Optional, Tuple, Type, TypeVar, Union

from ..utils import _Ensure, _Enum, _Iterable
from .serializable import Serializable
from .type import Json


class _JsonDecode(ABC):
    T = TypeVar("T", bound=Union[str, Serializable, Enum, bool])
    K = TypeVar("K", bound=Union[str, Enum])
    Decoder = Callable[[Json], Optional[T]]
    KDecoder = Callable[[str], Optional[K]]

    @staticmethod
    def decode(
        json: Json,
        cls: Type[T],
        decoder: Optional[Decoder] = None,
    ) -> Optional[T]:
        if not decoder is None:
            return decoder(json)
        if cls is str:
            if isinstance(json, cls):
                return json
            return None
        elif issubclass(cls, Serializable):
            result = cls.from_json(json)
            if not result is None and not isinstance(result, cls):
                return _Ensure._raise_error_value(None, cls, type(result))
            return result  # type: ignore
        elif issubclass(cls, Enum):
            return _Enum.parse_value(cls, json)  # type:ignore
        raise ValueError("Unknown type to handle `{}`".format(type(json)))

    @staticmethod
    def decode_optional(json: Optional[Json], cls: Type[T], decoder: Optional[Decoder] = None) -> Optional[T]:
        if json is None:
            return None
        return _JsonDecode.decode(json, cls, decoder)

    @staticmethod
    def __decode_list(
        json: Union[Json, List[Json]], cls: Type[T], decoder: Optional[Decoder] = None
    ) -> Iterable[Optional[T]]:
        if not isinstance(json, List):
            return _Ensure._raise_error_instance("json", List, type(json))
        return map(lambda x: _JsonDecode.decode(x, cls, decoder), json)

    @staticmethod
    def decode_list(json: Union[Json, List[Json]], cls: Type[T], decoder: Optional[Decoder] = None) -> List[T]:
        return list(_Iterable.not_none(_JsonDecode.__decode_list(json, cls, decoder)))

    @staticmethod
    def decode_list_optional(
        json: Union[Json, List[Json]], cls: Type[T], decoder: Optional[Decoder] = None
    ) -> List[Optional[T]]:
        return list(_JsonDecode.__decode_list(json, cls, decoder))

    @staticmethod
    def decode_optional_list(
        json: Optional[Union[Json, List[Json]]],
        cls: Type[T],
        decoder: Optional[Decoder] = None,
    ) -> Optional[List[T]]:
        if json is None:
            return None
        return _JsonDecode.decode_list(json, cls, decoder)

    @staticmethod
    def decode_optional_list_optional(
        json: Optional[Union[Json, List[Json]]],
        cls: Type[T],
        decoder: Optional[Decoder] = None,
    ) -> Optional[List[Optional[T]]]:
        if json is None:
            return None
        return _JsonDecode.decode_list_optional(json, cls, decoder)

    @staticmethod
    def decode_dict(
        json: Union[Json, Dict[str, Json]],
        kcls: Type[K],
        tcls: Type[T],
        kDecoder: Optional[KDecoder] = None,
        tDecoder: Optional[Decoder] = None,
    ) -> Dict[K, T]:
        m = _JsonDecode.__decode_dict_to_map(json, kcls, tcls, kDecoder, tDecoder)
        f = _Iterable.tuple_not_none(m)
        return dict(f)

    @staticmethod
    def decode_dict_optional(
        json: Union[Json, Dict[str, Json]],
        kcls: Type[K],
        tcls: Type[T],
        kDecoder: Optional[KDecoder] = None,
        tDecoder: Optional[Decoder] = None,
    ) -> Dict[K, Optional[T]]:
        return dict(_JsonDecode.__decode_dict_to_map(json, kcls, tcls, kDecoder, tDecoder))

    @staticmethod
    def decode_optional_dict(
        json: Optional[Union[Json, Dict[str, Json]]],
        kcls: Type[K],
        tcls: Type[T],
        kDecoder: Optional[KDecoder] = None,
        tDecoder: Optional[Decoder] = None,
    ) -> Optional[Dict[K, T]]:
        if json is None:
            return None
        return _JsonDecode.decode_dict(json, kcls, tcls, kDecoder, tDecoder)

    @staticmethod
    def decode_optional_dict_optional(
        json: Optional[Union[Json, Dict[str, Json]]],
        kcls: Type[K],
        tcls: Type[T],
        kDecoder: Optional[KDecoder] = None,
        tDecoder: Optional[Decoder] = None,
    ) -> Optional[Dict[K, Optional[T]]]:
        if json is None:
            return None
        return _JsonDecode.decode_dict_optional(json, kcls, tcls, kDecoder, tDecoder)

    @staticmethod
    def __decode_dict_to_map(
        json: Union[Json, Dict[str, Json]],
        kcls: Type[K],
        tcls: Type[T],
        kDecoder: Optional[KDecoder] = None,
        tDecoder: Optional[Decoder] = None,
    ) -> Iterable[Tuple[K, Optional[T]]]:
        if not isinstance(json, Dict):
            return _Ensure._raise_error_instance("json", Dict, type(json))
        return map(
            lambda x: _JsonDecode.__decode_dict_tuple(x, kcls, tcls, kDecoder, tDecoder),
            json.items(),
        )

    @staticmethod
    def __decode_dict_tuple(
        input: Tuple[str, Json],
        kcls: Type[K],
        tcls: Type[T],
        kDecoder: Optional[KDecoder] = None,
        tDecoder: Optional[Decoder] = None,
    ) -> Tuple[K, Optional[T]]:
        return (
            _JsonDecode.__decode_dict_key(input[0], kcls, kDecoder),
            _JsonDecode.decode(input[1], tcls, tDecoder),
        )

    @staticmethod
    def __decode_dict_key(key: str, kcls: Type[K], kDecoder: Optional[KDecoder] = None) -> K:
        if kDecoder is None:
            decoded = _JsonDecode.decode(key, kcls, None)
        else:
            decoded = kDecoder(key)
        if decoded is None:
            raise ValueError('Unexpected dict key decode "{}" to `{}`'.format(key, kcls.__name__))
        if isinstance(decoded, kcls):
            return decoded
        raise ValueError('Invalid decoded key "{}" as `{}`'.format(key, type(key)))
