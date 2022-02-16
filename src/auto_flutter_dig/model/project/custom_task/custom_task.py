from __future__ import annotations

from typing import List, Optional

from ....core.json import *
from ....core.utils import _Ensure
from ...task import TaskId
from .content import CustomTaskContent
from .type import CustomTaskType


class CustomTask(Serializable["CustomTask"]):
    def __init__(
        self,
        id: TaskId,
        name: str,
        type: CustomTaskType,
        require: Optional[List[str]] = None,
        content: Optional[CustomTaskContent] = None,
    ) -> None:
        super().__init__()
        self.id: TaskId = _Ensure.instance(id, TaskId, "id")
        self.name: str = _Ensure.instance(name, str, "name")
        self.type: CustomTaskType = _Ensure.instance(type, CustomTaskType, "type")
        self.require: Optional[List[str]] = require
        self.content: Optional[CustomTaskContent] = content

    def to_json(self) -> Json:
        return {
            "id": self.id,
            "name": self.name,
            "type": _JsonEncode.encode(self.type),
            "require": _JsonEncode.encode_optional(self.require),
            "content": _JsonEncode.encode_optional(self.content),
        }

    @staticmethod
    def from_json(json: Json) -> Optional[CustomTask]:
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
        return CustomTask(id, name, type, require, content)  # type: ignore[arg-type]
