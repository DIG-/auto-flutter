from __future__ import annotations

from enum import Enum
from operator import itemgetter
from typing import Tuple

from ...core.utils import _Ensure
from .platform import Platform


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
