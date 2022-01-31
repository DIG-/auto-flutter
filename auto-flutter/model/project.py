from typing import Any, Dict, List
from ..model.platform import Platform
from ..model.build_config import BuildConfigFlavored


class Project:
    name: str
    platforms: List[Platform]
    flavors: List[str]
    build_config: Dict[Platform, BuildConfigFlavored]
    tasks: List[Any]
