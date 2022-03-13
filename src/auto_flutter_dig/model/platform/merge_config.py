from typing import Any, List, Optional

from ...core.json import Json
from .flavored_config import *

__all__ = [
    "PlatformConfigFlavored",
    "RunType",
    "BuildType",
    "TaskId",
    "Flavor",
]


class MergePlatformConfigFlavored(PlatformConfigFlavored):
    def __init__(
        self,
        default: Optional[PlatformConfigFlavored],
        platform: Optional[PlatformConfigFlavored],
    ) -> None:
        super().__init__()
        self.default = default
        self.platform = platform

    def append_build_param(self, flavor: Optional[Flavor], param: str):
        raise AssertionError(f"Can not append build param using {type(self).__name__}")

    def _append_build_param(self, param: str):
        raise AssertionError(f"Can not append build param using {type(self).__name__}")

    def add_extra(self, flavor: Optional[Flavor], key: str, value: str):
        raise AssertionError(f"Can not add extra using {type(self).__name__}")

    def _add_extra(self, key: str, value: str):
        raise AssertionError(f"Can not add extra using {type(self).__name__}")

    def remove_extra(self, flavor: Optional[Flavor], key: str) -> bool:
        raise AssertionError(f"Can not remove extra using {type(self).__name__}")

    def _remove_extra(self, key: str) -> bool:
        raise AssertionError(f"Can not remove extra using {type(self).__name__}")

    def to_json(self) -> Json:
        raise AssertionError(f"Can not serialize {type(self).__name__}")

    @staticmethod
    def from_json(json: Json) -> Optional[Any]:
        raise AssertionError(f"Can not parse {MergePlatformConfigFlavored.__name__}")

    def get_build_param(self, flavor: Optional[Flavor]) -> List[TaskId]:
        output: List[TaskId] = []
        if not self.default is None:
            output.extend(self.default.get_build_param(flavor))
        if not self.platform is None:
            output.extend(self.platform.get_build_param(flavor))
        return output

    def get_output(self, flavor: Optional[Flavor], build_type: BuildType) -> Optional[str]:
        if not self.platform is None:
            output = self.platform.get_output(flavor, build_type)
            if not output is None:
                return output
        if not self.default is None:
            return self.default.get_output(flavor, build_type)
        return None

    def get_extra(self, flavor: Optional[Flavor], key: str) -> Optional[str]:
        if not self.platform is None:
            output = self.platform.get_extra(flavor, key)
            if not output is None:
                return output
        if not self.default is None:
            return self.default.get_extra(flavor, key)
        return None

    def get_run_before(self, run_type: RunType, flavor: Optional[Flavor]) -> List[str]:
        output: List[str] = []
        if not self.default is None:
            output.extend(self.default.get_run_before(run_type, flavor))
        if not self.platform is None:
            output.extend(self.platform.get_run_before(run_type, flavor))
        return output
