from typing import Dict, List, Optional

from ...core.json import _JsonDecode, _JsonEncode
from .._serializable import Serializable
from ..flavor import Flavor
from . import PlatformConfig
from .build_type import BuildType
from .config import BuildRunBefore, TaskIdList


class PlatformConfigFlavored(PlatformConfig, Serializable["PlatformConfigFlavored"]):
    def __init__(
        self,
        build_param: Optional[str] = None,
        run_before: Optional[Dict[BuildRunBefore, TaskIdList]] = None,
        output: Optional[str] = None,
        outputs: Optional[Dict[BuildType, str]] = None,
        extras: Optional[Dict[str, str]] = None,
        flavored: Optional[Dict[Flavor, PlatformConfig]] = None,
    ) -> None:
        super().__init__(build_param, run_before, output, outputs, extras)
        self.flavored: Optional[Dict[Flavor, PlatformConfig]] = flavored

    def get_build_param(self, flavor: Optional[Flavor]) -> str:
        output = ""
        if not self.build_param is None:
            output += self.build_param
        if not flavor is None and not self.flavored is None and flavor in self.flavored:
            flavored_param = self.flavored[flavor].build_param
            if not flavored_param is None:
                if len(output) > 0:
                    output += " "
                output += flavored_param
        return output

    def get_run_before(
        self, flavor: Optional[Flavor]
    ) -> Dict[BuildRunBefore, List[str]]:
        output: Dict[BuildRunBefore, List[str]] = dict()
        if not self.run_before is None:
            output = self.run_before
        if (
            (not flavor is None)
            and (not self.flavored is None)
            and (flavor in self.flavored)
            and (not self.flavored[flavor] is None)
            and (not self.flavored[flavor].run_before is None)
        ):
            for key, value in self.flavored[flavor].run_before.items():
                if not key in output:
                    output[key] = value
                else:
                    output[key] = [*output[key], *value]
        return output

    def get_output(self, flavor: Optional[Flavor], type: BuildType) -> Optional[str]:
        if not flavor is None and not self.flavored is None and flavor in self.flavored:
            from_flavor = self.flavored[flavor].get_output(type)
            if not from_flavor is None:
                return from_flavor
        return self.get_output(type)

    def get_extra(self, flavor: Optional[Flavor], key: str) -> Optional[str]:
        if not flavor is None and not self.flavored is None and flavor in self.flavored:
            from_flavor = self.flavored[flavor].get_extra(key)
            if not from_flavor is None:
                return from_flavor
        return self.get_extra(key)

    def to_json(self) -> Serializable.Json:
        parent = super().to_json()
        if not self.flavored is None:
            flavored = {"flavored": _JsonEncode.encode(self.flavored)}
            return {**parent, **flavored}
        return parent

    def from_json(json: Serializable.Json) -> Optional["PlatformConfigFlavored"]:
        output = PlatformConfigFlavored()
        other = PlatformConfig.from_json(json)
        if not other is None:
            output.build_param = other.build_param
            output.run_before = other.run_before
            output.output = other.output
            output.outputs = other.outputs
            output.extras = other.extras
        if isinstance(json, Dict):
            if "flavored" in json:
                output.flavored = _JsonDecode.decode_optional_dict(
                    json["flavored"], Flavor, PlatformConfig
                )
        return output
