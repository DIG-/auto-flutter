from __future__ import annotations

from typing import Dict, List, Optional

from ...core.json import *
from ...core.utils import _Ensure
from ..build import BuildType
from ..task.id import TaskId
from .run_type import RunType

__all__ = ["PlatformConfig", "RunType", "BuildType", "TaskIdList", "TaskId"]


class TaskIdList(List[TaskId], Serializable["TaskIdList"]):
    def to_json(self) -> Json:
        output: List[str] = []
        output.extend(self)
        return output

    @staticmethod
    def from_json(json: Json) -> Optional[TaskIdList]:
        if json is None:
            return None
        if not isinstance(json, List):
            return None
        output = TaskIdList()
        output.extend(json)
        return output


class PlatformConfig(Serializable["PlatformConfig"]):
    def __init__(
        self,
        build_param: Optional[List[str]] = None,
        run_before: Optional[Dict[RunType, TaskIdList]] = None,
        output: Optional[str] = None,
        outputs: Optional[Dict[BuildType, str]] = None,
        extras: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__()
        self.build_param: Optional[List[str]] = build_param
        self.run_before: Optional[Dict[RunType, TaskIdList]] = run_before
        self.output: Optional[str] = output
        self.outputs: Optional[Dict[BuildType, str]] = outputs
        self.extras: Optional[Dict[str, str]] = extras

    def _append_build_param(self, param: str):
        if self.build_param is None:
            self.build_param = []
        self.build_param.append(_Ensure.instance(param, str, "build-param"))

    def _get_output(self, type: BuildType) -> Optional[str]:
        if not self.outputs is None:
            if type in self.outputs:
                return self.outputs[type]
        return self.output

    def _get_extra(self, key: str) -> Optional[str]:
        if self.extras is None:
            return None
        if key in self.extras:
            return self.extras[key]
        return None

    def _add_extra(self, key: str, value: str):
        if self.extras is None:
            self.extras = {}
        self.extras[key] = value

    def _remove_extra(self, key: str) -> bool:
        if self.extras is None:
            return False
        if not key in self.extras:
            return False
        self.extras.pop(key)
        if len(self.extras) <= 0:
            self.extras = None
        return True

    def _get_run_before(self, type: RunType) -> Optional[List[TaskId]]:
        _Ensure.type(type, RunType, "type")
        if self.run_before is None or type not in self.run_before:
            return None
        return self.run_before[type]

    def to_json(self) -> Json:
        extras = self.extras
        output = {
            "build-param": _JsonEncode.encode_optional(self.build_param),
            "run-before": _JsonEncode.encode_optional(self.run_before),
            "output": _JsonEncode.encode_optional(self.output),
            "outputs": None
            if self.outputs is None
            else _JsonEncode.encode_dict(self.outputs, lambda x: x.output, lambda x: x),
        }
        if extras is None:
            return output
        return {**output, **extras}

    @staticmethod
    def from_json(json: Json) -> Optional[PlatformConfig]:
        if not isinstance(json, Dict):
            return None
        output = PlatformConfig()
        for key, value in json.items():
            if not isinstance(key, str):
                continue
            if key == "build-param" and isinstance(value, List):
                output.build_param = _JsonDecode.decode_list(value, str)
            elif key == "run-before" and isinstance(value, Dict):
                output.run_before = _JsonDecode.decode_optional_dict(value, RunType, TaskIdList)
                pass
            elif key == "output" and isinstance(value, str):
                output.output = value
            elif key == "outputs" and isinstance(value, Dict):
                output.outputs = _JsonDecode.decode_optional_dict(value, BuildType, str, BuildType.from_output)
                pass
            elif isinstance(value, str):
                if output.extras is None:
                    output.extras = {key: value}
                else:
                    output.extras[key] = value
            pass
        return output
