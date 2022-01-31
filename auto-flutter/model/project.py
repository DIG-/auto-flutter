from typing import Any, Dict, List
from ..model.platform import Platform
from ..model.build_config import BuildConfigFlavored
from ..model.flavor import Flavor


class Project:
    name: str
    platforms: List[Platform]
    flavors: List[Flavor]
    build_config: Dict[Platform, BuildConfigFlavored]
    tasks: List[Any]
