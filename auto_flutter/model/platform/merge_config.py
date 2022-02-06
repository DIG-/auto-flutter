from typing import Dict, List, Optional

from ...core.utils import _Dict
from .build_type import BuildType
from ..flavor import Flavor
from . import PlatformConfigFlavored
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

    def get_build_param(self, flavor: Optional[Flavor]) -> str:
        output = ""
        if not self.default is None:
            output += self.default.get_build_param(flavor)
        output += " "
        if not self.platform is None:
            output += self.platform.get_build_param(flavor)
        return output.strip()

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
        self, flavor: Optional[Flavor]
    ) -> Dict[BuildRunBefore, List[str]]:
        output: Dict[BuildRunBefore, List[str]] = {}
        if not self.default is None:
            output = _Dict.merge_append(output, self.default.get_run_before(flavor))
        if not self.platform is None:
            output = _Dict.merge_append(output, self.platform.get_run_before(flavor))
        # Remove duplicated
        for k, v in output:
            output[k] = list(dict.fromkeys(v))
        return output
