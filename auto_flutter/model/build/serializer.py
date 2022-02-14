from __future__ import annotations

from typing import Optional

from ...core.json.serializable import *
from ...core.utils import _Ensure
from .type import BuildType


class _BuildType_SerializeFlutter(Serializable[BuildType]):
    def __init__(self, value: BuildType) -> None:
        self.value = value

    def to_json(self) -> Json:
        return self.value.flutter

    @staticmethod
    def from_json(json: Json) -> Optional[BuildType]:
        return BuildType.from_flutter(_Ensure.instance(json, str, "json"))


class _BuildType_SerializeOutput(Serializable[BuildType]):
    def __init__(self, value: BuildType) -> None:
        self.value = value

    def to_json(self) -> Json:
        return self.value.output

    @staticmethod
    def from_json(json: Json) -> Optional[BuildType]:
        return BuildType.from_output(_Ensure.instance(json, str, "json"))
