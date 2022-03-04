from .....model.build.type import BuildType
from ..long import LongOptionWithValue
from ._decoder import _DecodedOption

__all__ = ["BuildTypeFlutterOption", "BuildTypeOutputOption"]


class BuildTypeFlutterOption(LongOptionWithValue, _DecodedOption[BuildType]):
    def __init__(self, description: str) -> None:
        super().__init__("build-type", description)

    def _convert(self, input: str) -> BuildType:
        return BuildType.from_flutter(input)


class BuildTypeOutputOption(LongOptionWithValue, _DecodedOption[BuildType]):
    def __init__(self, description: str) -> None:
        super().__init__("build-type", description)

    def _convert(self, input: str) -> BuildType:
        return BuildType.from_output(input)
