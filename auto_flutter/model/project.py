from typing import Dict, List, Optional

from ..core.json import _JsonDecode, _JsonEncode
from ..core.utils import _Ensure
from ..model._serializable import Serializable
from ..model.custom_task import CustomTask
from ..model.flavor import Flavor as mFlavor
from ..model.platform import Platform as mPlatform
from .platform.config import PlatformConfigFlavored


class Project(Serializable["Project"]):
    PlatformConfig = PlatformConfigFlavored
    Platform = mPlatform
    Flavor = mFlavor

    # Will be filled in `ProjectRead` task
    current: "Project" = None

    def __init__(
        self,
        name: str,
        platforms: List[mPlatform],
        flavors: Optional[List[mFlavor]],
        build_config: Dict[mPlatform, PlatformConfigFlavored],
        tasks: Optional[List[CustomTask]] = None,
    ) -> None:
        super().__init__()
        self.name: str = _Ensure.not_none(name, "name")
        self.platforms: List[mPlatform] = _Ensure.not_none(platforms, "platforms")
        self.flavors: Optional[List[mFlavor]] = flavors
        self.build_config: Dict[mPlatform, PlatformConfigFlavored] = _Ensure.not_none(
            build_config, "build-config"
        )
        self.tasks: Optional[List[CustomTask]] = tasks

    def to_json(self) -> Serializable.Json:
        return {
            "name": self.name,
            "platforms": _JsonEncode.encode(self.platforms),
            "flavors": _JsonEncode.encode_optional(self.flavors),
            "platform-config": _JsonEncode.encode(self.build_config),
            "tasks": _JsonEncode.encode_optional(self.tasks),
        }

    def from_json(json: Serializable.Json) -> Optional["Project"]:
        if not isinstance(json, Dict):
            return None
        name: Optional[str] = None
        platforms: Optional[List[mPlatform]] = None
        flavors: Optional[List[mFlavor]] = None
        build_config: Optional[Dict[mPlatform, PlatformConfigFlavored]]
        tasks: Optional[List[CustomTask]] = None
        for key, value in json.items():
            if not isinstance(key, str):
                continue
            if key == "name":
                name = _JsonDecode.decode(value, str)
            elif key == "platforms":
                platforms = _JsonDecode.decode_list(value, mPlatform)
            elif key == "flavors":
                flavors = _JsonDecode.decode_list(value, mFlavor)
            elif key == "platform-config":
                build_config = _JsonDecode.decode_dict(
                    value, mPlatform, PlatformConfigFlavored
                )
            elif key == "tasks":
                tasks = _JsonDecode.decode_list(value, CustomTask)

        return Project(name, platforms, flavors, build_config, tasks)
