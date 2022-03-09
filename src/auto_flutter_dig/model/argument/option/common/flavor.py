from .....model.project.flavor import Flavor
from ..long_short import LongShortOptionWithValue
from ._decoder import _DecodedOption

__all__ = ["FlavorOption"]


class FlavorOption(LongShortOptionWithValue, _DecodedOption[Flavor]):
    def __init__(self, description: str) -> None:
        LongShortOptionWithValue.__init__(self, "f", "flavor", description)
        _DecodedOption.__init__(self, description)

    def _convert(self, input: str) -> Flavor:
        return input
