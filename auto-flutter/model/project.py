from typing import Any, Dict, List, Optional
from ..model.platform import Platform as mPlatform
from ..model.build_config import BuildConfigFlavored
from ..model.flavor import Flavor as mFlavor
from ..model._serializable import Serializable
from ..core.utils import _JsonUtil


class Project(Serializable["Project"]):
    BuildConfig = BuildConfigFlavored
    Platform = mPlatform
    Flavor = mFlavor

    def __init__(
        self,
        name: str,
        platforms: List[mPlatform],
        flavors: Optional[List[mFlavor]],
        build_config: Dict[mPlatform, BuildConfigFlavored],
    ) -> None:
        super().__init__()
        self.name: str = name
        self.platforms: List[mPlatform] = platforms
        self.flavors: Optional[List[mFlavor]] = flavors
        self.build_config: Dict[mPlatform, BuildConfigFlavored] = build_config
        self.tasks: List[Any] = []

    def to_json(self) -> Serializable.Json:
        return {
            "name": self.name,
            "platforms": _JsonUtil.list_to_json(self.platforms),
            "flavors": _JsonUtil.optional_to_json(self.flavors),
            "build-config": _JsonUtil.map_to_json(self.build_config),
        }

    def from_json(json: Serializable.Json) -> Optional["Project"]:
        return None
