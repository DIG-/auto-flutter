from typing import List, Optional, Union
from ..model._serializable import Serializable


class CustomTaskContent(dict[Union[str, List]], Serializable["CustomTaskContent"]):
    def to_json(self) -> Serializable.Json:
        return self

    def from_json(json: Serializable.Json) -> Optional["CustomTaskContent"]:
        if not isinstance(json, dict):
            return None
        return CustomTaskContent(json)
