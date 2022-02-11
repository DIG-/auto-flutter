from typing import Dict, List, Optional

from ...core.utils import _Dict
from ..flavor import Flavor
from . import PlatformConfigFlavored
from .build_type import BuildType
from .config import BuildRunBefore


class MergePlatformConfigFlavored(PlatformConfigFlavored):
    def __init__(
        self,
        default: Optional[PlatformConfigFlavored],
        platform: Optional[PlatformConfigFlavored],
    ) -> None:
        super().__init__()
        self.default = default
        self.platform = platform

    def get_build_param(self, flavor: Optional[Flavor]) -> List[str]:
        output: List[str] = []
        if not self.default is None:
            output.extend(self.default.get_build_param(flavor))
        if not self.platform is None:
            output.extend(self.platform.get_build_param(flavor))
        return output

    def get_output(self, flavor: Optional[Flavor], type: BuildType) -> Optional[str]:
        if not self.platform is None:
            output = self.platform.get_output(flavor, type)
            if not output is None:
                return output
        if not self.default is None:
            return self.default.get_output(flavor, type)
        return None

    def get_extra(self, flavor: Optional[Flavor], key: str) -> Optional[str]:
        if not self.platform is None:
            output = self.platform.get_extra(flavor, key)
            if not output is None:
                return output
        if not self.default is None:
            return self.default.get_extra(flavor, key)
        return None

    def get_run_before(
        self, type: BuildRunBefore, flavor: Optional[Flavor]
    ) -> List[str]:
        output: List[str] = []
        if not self.default is None:
            output.extend(self.default.get_run_before(type, flavor))
        if not self.platform is None:
            output.extend(self.platform.get_run_before(type, flavor))
        return output
