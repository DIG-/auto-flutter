from .....core.utils import _Enum
from .....model.platform.platform import Platform
from ..long import LongOptionWithValue
from ._decoder import _DecodedOption

__all__ = ["PlatformOption"]


class PlatformOption(LongOptionWithValue, _DecodedOption[Platform]):
    def __init__(self, description: str) -> None:
        LongOptionWithValue.__init__(self, "platform", description)
        _DecodedOption.__init__(self, description)

    def _convert(self, input: str) -> Platform:
        return _Enum.parse_value(Platform, input)
