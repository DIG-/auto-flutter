from abc import ABCMeta
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple, TypeVar, Union

from .serializable import Serializable
from .type import Json


class _JsonEncode(metaclass=ABCMeta):
    Input = TypeVar("Input", bound=Union[Serializable, Enum, Json])
    kInput = TypeVar("kInput", bound=Union[Enum, str])
    Encoder = Callable[[Input], Json]
    kEncoder = Callable[[kInput], Json]

    @staticmethod
    def encode_optional(input: Optional[Input], encoder: Optional[Encoder] = None) -> Optional[Json]:
        if input is None:
            return None
        return _JsonEncode.encode(input, encoder)

    @staticmethod
    def encode(input: Input, encoder: Optional[Encoder] = None) -> Json:
        if encoder is None:
            if isinstance(input, str):
                return input
            if isinstance(input, Serializable):
                return input.to_json()
            if isinstance(input, Enum):
                return input.value
            if isinstance(input, List):
                return _JsonEncode.encode_list(input, lambda x: _JsonEncode.encode(x))
            if isinstance(input, Dict):
                return _JsonEncode.encode_dict(
                    input,
                    lambda x: _JsonEncode.encode(x),
                    lambda x: _JsonEncode.encode(x),
                )
            raise TypeError("Unknown encoder for {}".format(type(input)))
        if isinstance(input, List):
            return _JsonEncode.encode_list(input, encoder)
        if isinstance(input, Dict):
            raise TypeError("Can not encode Dict with only one encoder. Use encode_dict")

        return encoder(input)

    @staticmethod
    def encode_list(input: List[Input], encoder: Optional[Encoder] = None) -> List[Json]:
        return list(map(lambda x: _JsonEncode.encode(x, encoder), input))

    @staticmethod
    def encode_dict(
        input: Dict[kInput, Input],
        encoder_key: kEncoder,
        enoder_value: Encoder,
    ) -> Dict[str, Json]:
        return dict(
            map(
                lambda x: _JsonEncode.__encode_dict_tuple(x, encoder_key, enoder_value),
                input.items(),
            )
        )

    @staticmethod
    def __encode_dict_tuple(
        input: Tuple[kInput, Input],
        encoder_key: kEncoder,
        enoder_value: Encoder,
    ) -> Tuple[str, Json]:
        return (
            _JsonEncode.__encode_dict_key(input[0], encoder_key),
            _JsonEncode.encode(input[1], enoder_value),
        )

    @staticmethod
    def __encode_dict_key(key: kInput, encoder: kEncoder) -> str:
        output = encoder(key)
        if isinstance(output, str):
            return output
        raise ValueError('Can not accept "{}" as dictionary key'.format(type(output)))

    @staticmethod
    def clear_nones(input: Json) -> Json:
        if isinstance(input, List):
            return [_JsonEncode.clear_nones(x) for x in input if x is not None]
        elif isinstance(input, Dict):
            return {key: _JsonEncode.clear_nones(val) for key, val in input.items() if val is not None}
        return input
