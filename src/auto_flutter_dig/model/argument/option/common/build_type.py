from .....model.build.type import BuildType
from ..long import LongOptionWithValue
from ._decoder import _DecodedOption

__all__ = ["BuildTypeFlutterOption", "BuildTypeOutputOption"]


class BuildTypeFlutterOption(LongOptionWithValue, _DecodedOption[BuildType]):
    def __init__(self, description: str) -> None:
        LongOptionWithValue.__init__(self, "build-type", description)
        _DecodedOption.__init__(self, description)

    def _convert(self, input: str) -> BuildType:
        return BuildType.from_flutter(input)


class BuildTypeOutputOption(LongOptionWithValue, _DecodedOption[BuildType]):
    def __init__(self, description: str) -> None:
        LongOptionWithValue.__init__(self, "build-type", description)
        _DecodedOption.__init__(self, description)

    def _convert(self, input: str) -> BuildType:
        return BuildType.from_output(input)
