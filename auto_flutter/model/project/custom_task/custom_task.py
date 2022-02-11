from __future__ import annotations

from typing import List, Optional

from ....core.json import *
from ....core.utils import _Ensure
from ...task import TaskId
from .content import CustomTaskContent
from .type import CustomTaskType


class CustomTask(Serializable["CustomTask"]):
    ## Start - Alias to reduce import
    ID = TaskId
    Type = CustomTaskType
    Content = CustomTaskContent
    ## End - Alias to reduce import

    def __init__(
        self,
        id: ID,
        name: str,
        type: Type,
        require: Optional[List[str]] = None,
        content: Optional[Content] = None,
    ) -> None:
        super().__init__()
        self.id: TaskId = _Ensure.instance(id, TaskId, "id")
        self.name: str = _Ensure.instance(name, str, "name")
        self.type: CustomTask.Type = _Ensure.instance(type, CustomTask.Type, "type")
        self.require: Optional[List[str]] = require
        self.content: Optional[CustomTask.Content] = content

    def to_json(self) -> Serializable.Json:
        return {
            "id": self.id,
            "name": self.name,
            "type": _JsonEncode.encode(self.type),
            "require": _JsonEncode.encode_optional(self.require),
            "content": _JsonEncode.encode_optional(self.content),
        }

    def from_json(json: Serializable.Json) -> Optional[CustomTask]:
        if not isinstance(json, dict):
            return None

        id: Optional[TaskId] = None
        name: Optional[str] = None
        type: Optional[CustomTaskType] = None
        require: Optional[List[str]] = None
        content: Optional[CustomTaskContent] = None

        for key, value in json.items():
            if not isinstance(key, str):
                continue
            if key == "id" and isinstance(value, str):
                id = value
            elif key == "name" and isinstance(value, str):
                name = value
            elif key == "type":
                type = _JsonDecode.decode(value, CustomTaskType)
            elif key == "require":
                require = _JsonDecode.decode_list(value, str)
            elif key == "content":
                content = _JsonDecode.decode(value, CustomTaskContent)
        return CustomTask(id, name, type, require, content)
