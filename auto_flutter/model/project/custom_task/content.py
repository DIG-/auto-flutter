from __future__ import annotations

from typing import Dict, List, Optional

from ....core.json import *
from ....core.utils import _Ensure


class CustomTaskContent(Serializable["CustomTaskContent"]):
    def __init__(self, command: str, args: Optional[List[str]]) -> None:
        self.command: str = _Ensure.instance(command, str, "command")
        self.args: Optional[List[str]] = args

    @classmethod
    def to_json(self) -> Serializable.Json:
        return {
            "command": self.command,
            "args": None
            if self.args is None
            else _JsonEncode.encode_list(self.args, lambda x: x),
        }

    @staticmethod
    def from_json(json: Serializable.Json) -> Optional[CustomTaskContent]:
        if not isinstance(json, Dict):
            return None
        command: Optional[str] = None
        args: Optional[List[str]] = None
        for key, value in json.items():
            if not isinstance(key, str):
                continue
            if key == "command":
                command = _JsonDecode.decode(value, str)
            elif key == "args":
                args = _JsonDecode.decode_list(value, str)
        return CustomTaskContent(command, args)
