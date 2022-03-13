from typing import Any, Dict, Optional

from ...core.json import Json
from .flavored_config import *

__all__ = [
    "MergePlatformConfigFlavored",
    "PlatformConfigFlavored",
    "RunType",
    "BuildType",
    "TaskId",
    "Flavor",
]


class _MergedPlatformConfig(PlatformConfig):
    def __init__(self, default: Optional[PlatformConfig], platform: Optional[PlatformConfig]) -> None:
        super().__init__(None, None, None, None, None)
        if not default is None:
            self._merge(default)
        if not platform is None:
            self._merge(platform)

    def append_build_param(self, param: str):
        raise AssertionError(f"{type(self).__name__} is read only")

    def add_extra(self, key: str, value: str):
        raise AssertionError(f"{type(self).__name__} is read only")

    def remove_extra(self, key: str) -> bool:
        raise AssertionError(f"{type(self).__name__} is read only")

    def to_json(self) -> Json:
        raise AssertionError(f"{type(self).__name__} is read only")

    @staticmethod
    def from_json(json: Json) -> Optional[Any]:
        raise AssertionError(f"{_MergedPlatformConfig.__name__} is read only")


class MergePlatformConfigFlavored(PlatformConfigFlavored):
    def __init__(
        self,
        default: Optional[PlatformConfigFlavored],
        platform: Optional[PlatformConfigFlavored],
    ) -> None:
        super().__init__()
        self.default = default
        self.platform = platform
        self.__cached: Dict[Flavor, _MergedPlatformConfig] = {}

    def append_build_param(self, param: str):
        raise AssertionError(f"{type(self).__name__} is read only")

    def add_extra(self, key: str, value: str):
        raise AssertionError(f"{type(self).__name__} is read only")

    def remove_extra(self, key: str) -> bool:
        raise AssertionError(f"{type(self).__name__} is read only")

    def to_json(self) -> Json:
        raise AssertionError(f"{type(self).__name__} is read only")

    @staticmethod
    def from_json(json: Json) -> Optional[Any]:
        raise AssertionError(f"{MergePlatformConfigFlavored.__name__} is read only")

    def get_config_by_flavor(self, flavor: Optional[Flavor]) -> PlatformConfig:
        key = self.__get_cache_key(flavor)
        if key in self.__cached:
            return self.__cached[key]

        config_default: Optional[PlatformConfig] = None
        config_platform: Optional[PlatformConfig] = None
        if not self.default is None:
            config_default = self.default.get_config_by_flavor(flavor)
        if not self.platform is None:
            config_default = self.platform.get_config_by_flavor(flavor)
        config = _MergedPlatformConfig(config_default, config_platform)
        self.__cached[key] = config
        return config

    def obtain_config_by_flavor(self, flavor: Optional[Flavor]) -> PlatformConfig:
        return self.get_config_by_flavor(flavor)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(default={self.default}, platform={self.platform})"

    @staticmethod
    def __get_cache_key(flavor: Optional[Flavor]) -> Flavor:
        if flavor is None:
            return "-#-#-"
        return flavor
