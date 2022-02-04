from enum import Enum
from typing import Optional
from ..core.utils import _Iterable


class BuildType(Enum):
    AAR = "aar"
    APK = "apk"
    BUNDLE = "aab"
    IPA = "ipa"

    def to_FlutterBuildType(self) -> "FlutterBuildType":
        found = _Iterable.first_or_none(
            FlutterBuildType.__iter__, lambda other: other.name == self.name
        )
        if found is None:
            raise AttributeError("Can not find FlutterBuildType from BuildType")
        return found


class FlutterBuildType(Enum):
    AAR = "aar"
    APK = "apk"
    BUNDLE = "appbundle"
    IPA = "ipa"

    def to_BuildType(self) -> BuildType:
        found = _Iterable.first_or_none(
            BuildType.__iter__, lambda other: other.name == self.name
        )
        if found is None:
            raise AttributeError("Can not find BuildType from FlutterBuildType")
        return found

    def from_str(string: str) -> Optional["FlutterBuildType"]:
        return _Iterable.first_or_none(
            FlutterBuildType.__iter__, lambda it: it.value == string
        )