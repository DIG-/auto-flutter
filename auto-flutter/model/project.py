from typing import Any, Dict, List, Optional
from ..model.platform import Platform as mPlatform
from ..model.build_config import BuildConfigFlavored
from ..model.flavor import Flavor as mFlavor
from ..model._serializable import Serializable
from ..core.json import _JsonEncode, _JsonDecode


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
        self.tasks: Optional[List[Any]] = None

    def to_json(self) -> Serializable.Json:
        return {
            "name": self.name,
            "platforms": _JsonEncode.encode(self.platforms),
            "flavors": _JsonEncode.encode_optional(self.flavors),
            "build-config": _JsonEncode.encode(self.build_config),
            "tasks": _JsonEncode.encode_optional(self.tasks),
        }

    def from_json(json: Serializable.Json) -> Optional["Project"]:
        return None
