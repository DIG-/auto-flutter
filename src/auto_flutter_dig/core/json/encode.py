from abc import ABC
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple, TypeVar, Union

from .serializable import Serializable
from .type import Json


class _JsonEncode(ABC):
    Input = TypeVar("Input", bound=Union[Serializable, Enum, Json])
    kInput = TypeVar("kInput", bound=Union[Enum, str])
    Encoder = Callable[[Input], Json]
    kEncoder = Callable[[kInput], Json]

    @staticmethod
    def encode_optional(value: Optional[Input], encoder: Optional[Encoder] = None) -> Optional[Json]:
        if value is None:
            return None
        return _JsonEncode.encode(value, encoder)

    @staticmethod
    def encode(value: Input, encoder: Optional[Encoder] = None) -> Json:
        if encoder is None:
            if isinstance(value, str):
                return value
            if isinstance(value, Serializable):
                return value.to_json()
            if isinstance(value, Enum):
                return value.value
            if isinstance(value, List):
                return _JsonEncode.encode_list(value, _JsonEncode.encode)
            if isinstance(value, Dict):
                return _JsonEncode.encode_dict(
                    value,
                    _JsonEncode.encode,
                    _JsonEncode.encode,
                )
            raise TypeError(f"Unknown encoder for {type(value).__name__}")
        if isinstance(value, List):
            return _JsonEncode.encode_list(value, encoder)
        if isinstance(value, Dict):
            raise TypeError("Can not encode Dict with only one encoder. Use encode_dict")

        return encoder(value)

    @staticmethod
    def encode_list(value: List[Input], encoder: Optional[Encoder] = None) -> List[Json]:
        return list(map(lambda x: _JsonEncode.encode(x, encoder), value))

    @staticmethod
    def encode_dict(
        value: Dict[kInput, Input],
        encoder_key: kEncoder,
        enoder_value: Encoder,
    ) -> Dict[str, Json]:
        return dict(
            map(
                lambda x: _JsonEncode.__encode_dict_tuple(x, encoder_key, enoder_value),
                value.items(),
            )
        )

    @staticmethod
    def __encode_dict_tuple(
        value: Tuple[kInput, Input],
        encoder_key: kEncoder,
        enoder_value: Encoder,
    ) -> Tuple[str, Json]:
        return (
            _JsonEncode.__encode_dict_key(value[0], encoder_key),
            _JsonEncode.encode(value[1], enoder_value),
        )

    @staticmethod
    def __encode_dict_key(key: kInput, encoder: kEncoder) -> str:
        output = encoder(key)
        if isinstance(output, str):
            return output
        raise ValueError(f'Can not accept "{type(output).__name__}" as dictionary key')

    @staticmethod
    def clear_nones(json: Json) -> Json:
        if isinstance(json, List):
            return [_JsonEncode.clear_nones(x) for x in json if x is not None]
        elif isinstance(json, Dict):
            return {key: _JsonEncode.clear_nones(val) for key, val in json.items() if val is not None}
        return json
