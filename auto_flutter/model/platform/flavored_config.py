from __future__ import annotations

from typing import Dict, List, Optional

from auto_flutter.model.task.task import Task

from ...core.json import *
from ...core.utils import _If
from ..project import Flavor
from .config import PlatformConfig, TaskIdList


class PlatformConfigFlavored(PlatformConfig, Serializable["PlatformConfigFlavored"]):
    def __init__(
        self,
        build_param: Optional[List[str]] = None,
        run_before: Optional[Dict[PlatformConfig.RunType, TaskIdList]] = None,
        output: Optional[str] = None,
        outputs: Optional[Dict[PlatformConfig.BuildType, str]] = None,
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

    def get_run_before(
        self, type: PlatformConfig.RunType, flavor: Optional[Flavor]
    ) -> List[Task.ID]:
        output: List[Task.ID] = list()
        _If.not_none(
            super().get_run_before(type),
            lambda x: output.extend(x),
            lambda: None,
        )
        if not flavor is None:
            flavored = self.get_config_by_flavor(flavor)
            if not flavored is None:
                _If.not_none(
                    flavored.get_run_before(type),
                    lambda x: output.extend(x),
                    lambda: None,
                )
        return output

    def get_output(
        self, flavor: Optional[Flavor], type: PlatformConfig.BuildType
    ) -> Optional[str]:
        if not flavor is None and not self.flavored is None and flavor in self.flavored:
            from_flavor = self.flavored[flavor].get_output(type)
            if not from_flavor is None:
                return from_flavor
        return super().get_output(type)

    def get_extra(self, flavor: Optional[Flavor], key: str) -> Optional[str]:
        if not flavor is None and not self.flavored is None and flavor in self.flavored:
            from_flavor = self.flavored[flavor].get_extra(key)
            if not from_flavor is None:
                return from_flavor
        return super().get_extra(key)

    def to_json(self) -> Serializable.Json:
        parent = super().to_json()
        if not self.flavored is None:
            flavored = {"flavored": _JsonEncode.encode(self.flavored)}
            return {**parent, **flavored}
        return parent

    def from_json(json: Serializable.Json) -> Optional[PlatformConfigFlavored]:
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

    def get_config_by_flavor(
        self, flavor: Optional[Flavor]
    ) -> Optional[PlatformConfig]:
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
