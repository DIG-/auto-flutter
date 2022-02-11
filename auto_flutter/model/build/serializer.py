from __future__ import annotations

from typing import Optional

from ...core.utils import _Ensure
from .._serializable import Serializable
from .type import BuildType


class _BuildType_SerializeFlutter(Serializable[BuildType]):
    def __init__(self, value: BuildType) -> None:
        self.value = value

    def to_json(self) -> Serializable.Json:
        return self.value.flutter

    def from_json(json: Serializable.Json) -> Optional[BuildType]:
        return BuildType.from_flutter(_Ensure.instance(json, str, "json"))


class _BuildType_SerializeOutput(Serializable[BuildType]):
    def __init__(self, value: BuildType) -> None:
        self.value = value

    def to_json(self) -> Serializable.Json:
        return self.value.output

    def from_json(json: Serializable.Json) -> Optional[BuildType]:
        return BuildType.from_output(_Ensure.instance(json, str, "json"))
