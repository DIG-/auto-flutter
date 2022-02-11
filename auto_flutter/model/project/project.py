from typing import Dict, List, Optional

from ...core import VERSION
from ...core.json import _JsonDecode, _JsonEncode
from ...core.utils import _Ensure, _Iterable
from ...model._serializable import Serializable
from ...model.custom_task import CustomTask
from ...model.platform import Platform as mPlatform
from ...model.platform import PlatformConfigFlavored
from .flavor import Flavor as mFlavor


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
        platform_config: Dict[mPlatform, PlatformConfigFlavored],
        tasks: Optional[List[CustomTask]] = None,
    ) -> None:
        super().__init__()
        self.name: str = _Ensure.not_none(name, "name")
        self.platforms: List[mPlatform] = _Ensure.not_none(platforms, "platforms")
        self.flavors: Optional[List[mFlavor]] = flavors
        self.platform_config: Dict[
            mPlatform, PlatformConfigFlavored
        ] = _Ensure.not_none(platform_config, "platform-config")
        self.tasks: Optional[List[CustomTask]] = tasks

    def get_platform_config(
        self, platform: mPlatform
    ) -> Optional[PlatformConfigFlavored]:
        if self.platform_config is None or not platform in self.platform_config:
            return None
        return self.platform_config[platform]

    def obtain_platform_cofig(self, platform: mPlatform):
        if self.platform_config is None:
            self.platform_config = {}
        if not platform in self.platform_config:
            self.platform_config[platform] = PlatformConfigFlavored()
        return self.platform_config[platform]

    def add_task(self, task: CustomTask):
        if self.tasks is None:
            self.tasks = []
        self.tasks.append(task)

    def remove_task_id(self, id: CustomTask.ID) -> bool:
        if self.tasks is None:
            return False
        found = _Iterable.first_or_none(self.tasks, lambda x: x.id == id)
        if found is None:
            return False
        self.tasks.remove(found)
        if len(self.tasks) <= 0:
            self.tasks = None
        return True

    def to_json(self) -> Serializable.Json:
        return {
            "_creator": "Auto-Flutter " + VERSION,
            "name": self.name,
            "platforms": _JsonEncode.encode(self.platforms),
            "flavors": _JsonEncode.encode_optional(self.flavors),
            "platform-config": _JsonEncode.encode(self.platform_config),
            "tasks": _JsonEncode.encode_optional(self.tasks),
        }

    def from_json(json: Serializable.Json) -> Optional["Project"]:
        if not isinstance(json, Dict):
            return None
        name: Optional[str] = None
        platforms: Optional[List[mPlatform]] = None
        flavors: Optional[List[mFlavor]] = None
        platform_config: Optional[Dict[mPlatform, PlatformConfigFlavored]]
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
                platform_config = _JsonDecode.decode_dict(
                    value, mPlatform, PlatformConfigFlavored
                )
            elif key == "tasks":
                tasks = _JsonDecode.decode_list(value, CustomTask)

        return Project(name, platforms, flavors, platform_config, tasks)
