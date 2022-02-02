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
        if not isinstance(json, Dict):
            return None
        name: Optional[str] = None
        platforms: Optional[List[mPlatform]] = None
        flavors: Optional[List[mFlavor]] = None
        build_config: Optional[Dict[mPlatform, BuildConfigFlavored]]
        for key, value in json.items():
            if not isinstance(key, str):
                continue
            if key == "name":
                name = _JsonDecode.decode(value, str)
            elif key == "platforms":
                platforms = _JsonDecode.decode_list(value, mPlatform)
            elif key == "flavors":
                flavors = _JsonDecode.decode_list(value, mFlavor)
            elif key == "build-config":
                build_config = _JsonDecode.decode_dict(
                    value, mPlatform, BuildConfigFlavored
                )

        return Project(name, platforms, flavors, build_config)
