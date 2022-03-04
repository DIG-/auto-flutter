from .....model.task.id import TaskId
from ..long_short import LongShortOptionWithValue
from ._decoder import _DecodedOption

__all__ = ["FlavorOption"]


class FlavorOption(LongShortOptionWithValue, _DecodedOption[TaskId]):
    def __init__(self, description: str) -> None:
        super().__init__("f", "flavor", description)

    def _convert(self, input: str) -> TaskId:
        return input
