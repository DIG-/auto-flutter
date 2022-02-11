from abc import ABCMeta
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple, Type, TypeVar, Union

from .serializable import Serializable
from .type import Json


class _JsonEncode(metaclass=ABCMeta):
    Input = Union[Json, Serializable, Enum]
    Encoder = Union[Callable[[Input], Json], Type[Serializable[Input]], Type[str]]

    def encode_optional(
        input: Optional[Input], encoder: Optional[Encoder] = None
    ) -> Optional[Json]:
        if input is None:
            return None
        return _JsonEncode.encode(input, encoder)

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
        if isinstance(input, List):
            return _JsonEncode.encode_list(input, encoder)
        if isinstance(input, Dict):
            raise TypeError(
                "Can not encode Dict with only one encoder. Use encode_dict"
            )

        if encoder is str:
            return encoder(input)
        if isinstance(encoder, Type) and issubclass(encoder, Serializable):
            if isinstance(input, encoder):
                return input.to_json()
            return encoder(input).to_json()
        elif isinstance(encoder, Callable):
            return encoder(input)
        else:
            raise AssertionError("Invalid encoder `{}`".format(type(encoder)))

    def encode_list(
        input: List[Input], encoder: Optional[Encoder] = None
    ) -> List[Json]:
        return list(map(lambda x: _JsonEncode.encode(x, encoder), input))

    def encode_dict(
        input: Dict[Input, Input],
        encoder_key: Encoder,
        enoder_value: Encoder,
    ):
        return dict(
            map(
                lambda x: _JsonEncode.__encode_dict_tuple(x, encoder_key, enoder_value),
                input.items(),
            )
        )

    def __encode_dict_tuple(
        input: Tuple[Input, Input],
        encoder_key: Encoder,
        enoder_value: Encoder,
    ) -> Tuple[str, Json]:
        return (
            _JsonEncode.__encode_dict_key(input[0], encoder_key),
            _JsonEncode.encode(input[1], enoder_value),
        )

    def __encode_dict_key(key: Input, encoder: Encoder) -> str:
        output = _JsonEncode.encode(key, encoder)
        if isinstance(output, str):
            return output
        raise ValueError('Can not accept "{}" as dictionary key'.format(type(output)))

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
