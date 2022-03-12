from .....core.utils import _Enum
from .....model.build.mode import BuildMode
from ..long import LongOptionWithValue
from ._decoder import _DecodedOption

__all__ = ["BuildModeOption"]


class BuildModeOption(LongOptionWithValue, _DecodedOption[BuildMode]):
    def __init__(self, description: str) -> None:
        LongOptionWithValue.__init__(self, "build-mode", description)
        _DecodedOption.__init__(self, description)

    def _convert(self, input: str) -> BuildMode:
        return _Enum.parse_value(BuildMode, input)
