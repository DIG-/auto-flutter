from __future__ import annotations

from typing import Dict, List, Optional

from ...core import VERSION
from ...core.json import *
from ...core.utils import _Ensure, _Iterable
from ...model.platform import Platform as mPlatform
from ...model.platform import PlatformConfigFlavored
from .custom_task import CustomTask as mCustomTask
from .flavor import Flavor as mFlavor


class Project(Serializable["Project"]):
    ## Start - Alias to reduce import
    CustomTask = mCustomTask
    Flavor = mFlavor
    Platform = mPlatform
    ## End - Alias to reduce import

    # Will be filled in `ProjectRead` task
    current: Project = None

    def __init__(
        self,
        name: str,
        platforms: List[Platform],
        flavors: Optional[List[Flavor]],
        platform_config: Dict[Platform, PlatformConfigFlavored],
        tasks: Optional[List[CustomTask]] = None,
    ) -> None:
        super().__init__()
        self.name: str = _Ensure.instance(name, str, "name")
        self.platforms: List[Project.Platform] = _Ensure.not_none(
            platforms, "platforms"
        )
        self.flavors: Optional[List[Project.Flavor]] = flavors
        self.platform_config: Dict[
            Project.Platform, PlatformConfigFlavored
        ] = _Ensure.not_none(platform_config, "platform-config")
        self.tasks: Optional[List[Project.CustomTask]] = tasks

    def get_platform_config(
        self, platform: Project.Platform
    ) -> Optional[PlatformConfigFlavored]:
        if self.platform_config is None or not platform in self.platform_config:
            return None
        return self.platform_config[platform]

    def obtain_platform_cofig(self, platform: Project.Platform):
        if self.platform_config is None:
            self.platform_config = {}
        if not platform in self.platform_config:
            self.platform_config[platform] = PlatformConfigFlavored()
        return self.platform_config[platform]

    def add_task(self, task: Project.CustomTask):
        if self.tasks is None:
            self.tasks = []
        self.tasks.append(task)

    def remove_task_id(self, id: Project.CustomTaskId) -> bool:
        if self.tasks is None:
            return False
        found = _Iterable.first_or_none(self.tasks, lambda x: x.id == id)
        if found is None:
            return False
        self.tasks.remove(found)
        if len(self.tasks) <= 0:
            self.tasks = None
        return True

    def to_json(self) -> Json:
        return {
            "_creator": "Auto-Flutter " + VERSION,
            "name": self.name,
            "platforms": _JsonEncode.encode(self.platforms),
            "flavors": _JsonEncode.encode_optional(self.flavors),
            "platform-config": _JsonEncode.encode(self.platform_config),
            "tasks": _JsonEncode.encode_optional(self.tasks),
        }

    @staticmethod
    def from_json(json: Json) -> Optional[Project]:
        if not isinstance(json, Dict):
            return None
        name: Optional[str] = None
        platforms: Optional[List[Project.Platform]] = None
        flavors: Optional[List[Project.Flavor]] = None
        platform_config: Optional[Dict[Project.Platform, PlatformConfigFlavored]]
        tasks: Optional[List[Project.CustomTask]] = None
        for key, value in json.items():
            if not isinstance(key, str):
                continue
            if key == "name":
                name = _JsonDecode.decode(value, str)
            elif key == "platforms":
                platforms = _JsonDecode.decode_list(value, Project.Platform)
            elif key == "flavors":
                flavors = _JsonDecode.decode_list(value, Project.Flavor)
            elif key == "platform-config":
                platform_config = _JsonDecode.decode_dict(
                    value, Project.Platform, PlatformConfigFlavored
                )
            elif key == "tasks":
                tasks = _JsonDecode.decode_list(value, Project.CustomTask)

        return Project(name, platforms, flavors, platform_config, tasks)
