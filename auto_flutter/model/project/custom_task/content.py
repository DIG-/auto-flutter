from __future__ import annotations

from typing import Dict, List, Optional, Union

from ....core.json import Serializable


class CustomTaskContent(Dict[str, Union[str, List]], Serializable["CustomTaskContent"]):
    def to_json(self) -> Serializable.Json:
        return self

    def from_json(json: Serializable.Json) -> Optional[CustomTaskContent]:
        if not isinstance(json, Dict):
            return None
        return CustomTaskContent(json)
