from __future__ import annotations

from enum import Enum
from operator import attrgetter, itemgetter
from typing import Optional, Tuple

from ...core.utils import _Ensure, _Enum
from .._serializable import Serializable
from ..platform.platform import Platform


class _BuildTypeItem(Tuple[str, str, Platform]):
    def __new__(
        cls: type[_BuildTypeItem], flutter: str, output: str, platform: Platform
    ) -> _BuildTypeItem:
        _Ensure.type(flutter, str, "flutter")
        _Ensure.type(output, str, "output")
        _Ensure.type(platform, Platform, "platform")
        return super().__new__(_BuildTypeItem, (flutter, output, platform))

    flutter: str = property(itemgetter(0))
    output: str = property(itemgetter(1))
    platform: Platform = property(itemgetter(2))


class BuildType(Enum):
    AAR = _BuildTypeItem("aar", "aar", Platform.ANDROID)
    APK = _BuildTypeItem("apk", "apk", Platform.ANDROID)
    BUNDLE = _BuildTypeItem("appbundle", "aab", Platform.ANDROID)
    IPA = _BuildTypeItem("ios", "ipa", Platform.IOS)

    flutter: str = property(attrgetter("value.flutter"))
    output: str = property(attrgetter("value.output"))
    platform: Platform = property(attrgetter("value.platform"))

    @staticmethod
    def from_flutter(value: str) -> BuildType:
        _Ensure.not_none(value, "value")
        return _Enum.parse_value(BuildType, value, lambda x: x.flutter)

    @staticmethod
    def from_output(value: str) -> BuildType:
        _Ensure.not_none(value, "value")
        return _Enum.parse_value(BuildType, value, lambda x: x.output)


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
