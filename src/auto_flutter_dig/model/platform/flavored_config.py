from __future__ import annotations

from typing import Dict, List, Optional

from ...core.json import *
from ...core.utils import _If
from ..project import Flavor
from .config import *

__all__ = [
    "PlatformConfigFlavored",
    "PlatformConfig",
    "RunType",
    "BuildType",
    "TaskIdList",
    "TaskId",
    "Flavor",
]


class PlatformConfigFlavored(PlatformConfig, Serializable["PlatformConfigFlavored"]):
    def __init__(
        self,
        build_param: Optional[List[str]] = None,
        run_before: Optional[Dict[RunType, TaskIdList]] = None,
        output: Optional[str] = None,
        outputs: Optional[Dict[BuildType, str]] = None,
        extras: Optional[Dict[str, str]] = None,
        flavored: Optional[Dict[Flavor, PlatformConfig]] = None,
    ) -> None:
        super().__init__(build_param, run_before, output, outputs, extras)
        self.flavored: Optional[Dict[Flavor, PlatformConfig]] = flavored

    def get_build_param(self, flavor: Optional[Flavor]) -> List[str]:
        output = []
        if not self.build_param is None:
            output.extend(self.build_param)
        if not flavor is None:
            flavored = self.get_config_by_flavor(flavor)
            if (not flavored is None) and (not flavored.build_param is None):
                output.extend(flavored.build_param)
        return output

    def append_build_param(self, flavor: Optional[Flavor], param: str):
        self.obtain_config_by_flavor(flavor)._append_build_param(param)

    def get_run_before(self, type: RunType, flavor: Optional[Flavor]) -> List[TaskId]:
        output: List[TaskId] = list()
        _If.not_none(
            super()._get_run_before(type),
            lambda x: output.extend(x),
            lambda: None,
        )
        if not flavor is None:
            flavored = self.get_config_by_flavor(flavor)
            if not flavored is None:
                _If.not_none(
                    flavored._get_run_before(type),
                    lambda x: output.extend(x),
                    lambda: None,
                )
        return output

    def get_output(self, flavor: Optional[Flavor], type: BuildType) -> Optional[str]:
        if not flavor is None and not self.flavored is None and flavor in self.flavored:
            from_flavor = self.flavored[flavor]._get_output(type)
            if not from_flavor is None:
                return from_flavor
        return self._get_output(type)

    def get_extra(self, flavor: Optional[Flavor], key: str) -> Optional[str]:
        if not flavor is None and not self.flavored is None and flavor in self.flavored:
            from_flavor = self.flavored[flavor]._get_extra(key)
            if not from_flavor is None:
                return from_flavor
        return self._get_extra(key)

    def add_extra(self, flavor: Optional[Flavor], key: str, value: str):
        self.obtain_config_by_flavor(flavor)._add_extra(key, value)

    def remove_extra(self, flavor: Optional[Flavor], key: str) -> bool:
        return self.obtain_config_by_flavor(flavor)._remove_extra(key)

    def to_json(self) -> Json:
        parent = super().to_json()
        if not isinstance(parent, Dict):
            raise AssertionError("PlatformConfig must return Dict as json")
        if not self.flavored is None:
            flavored = {"flavored": _JsonEncode.encode(self.flavored)}
            return {**parent, **flavored}
        return parent

    @staticmethod
    def from_json(json: Json) -> Optional[PlatformConfigFlavored]:
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
                output.flavored = _JsonDecode.decode_optional_dict(json["flavored"], Flavor, PlatformConfig)
        return output

    def get_config_by_flavor(self, flavor: Optional[Flavor]) -> Optional[PlatformConfig]:
        if flavor is None:
            return self
        if self.flavored is None:
            return None
        if not flavor in self.flavored:
            return None
        return self.flavored[flavor]

    def obtain_config_by_flavor(self, flavor: Optional[Flavor]) -> PlatformConfig:
        if flavor is None:
            return self
        if self.flavored is None:
            self.flavored = {}
        if not flavor in self.flavored:
            self.flavored[flavor] = PlatformConfig()
        return self.flavored[flavor]
