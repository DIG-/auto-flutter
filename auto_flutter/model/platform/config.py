from enum import Enum
from re import I
from typing import Dict, List, Optional

from ...core.json import _JsonDecode, _JsonEncode
from ...core.utils import _Ensure
from .._serializable import Serializable
from .build_type import BuildType, _BuildType_SerializeOutput


class BuildRunBefore(Enum):
    BUILD = "build"


class TaskIdList(List[str], Serializable["TaskIdList"]):
    def to_json(self) -> Serializable.Json:
        return _JsonEncode.encode_list(self)

    def from_json(json: Serializable.Json) -> Optional["TaskIdList"]:
        if json is None:
            return None
        if not isinstance(json, List):
            return None
        return _JsonDecode.decode_list(json, str)


class PlatformConfig(Serializable["PlatformConfig"]):
    RunBefore = BuildRunBefore
    Type = BuildType

    def __init__(
        self,
        build_param: Optional[List[str]] = None,
        run_before: Optional[Dict[BuildRunBefore, TaskIdList]] = None,
        output: Optional[str] = None,
        outputs: Optional[Dict[BuildType, str]] = None,
        extras: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__()
        self.build_param: Optional[List[str]] = build_param
        self.run_before: Optional[Dict[BuildRunBefore, TaskIdList]] = run_before
        self.output: Optional[str] = output
        self.outputs: Optional[Dict[BuildType, str]] = outputs
        self.extras: Optional[Dict[str, str]] = extras

    def append_build_param(self, param: str):
        if self.build_param is None:
            self.build_param = []
        self.build_param.append(_Ensure.instance(param, str, "build-param"))

    def get_output(self, type: BuildType) -> Optional[str]:
        if not self.outputs is None:
            if type in self.outputs:
                return self.outputs[type]
        return self.output

    def get_extra(self, key: str) -> Optional[str]:
        if self.extras is None:
            return None
        if key in self.extras:
            return self.extras[key]
        return None

    def add_extra(self, key: str, value: str):
        if self.extras is None:
            self.extras = {}
        self.extras[key] = value

    def remove_extra(self, key: str) -> bool:
        if self.extras is None:
            return False
        if not key in self.extras:
            return False
        self.extras.pop(key)
        if len(self.extras) <= 0:
            self.extras = None
        return True

    def to_json(self) -> Serializable.Json:
        extras = self.extras
        output = {
            "build-param": _JsonEncode.encode_optional(self.build_param),
            "run-before": _JsonEncode.encode_optional(self.run_before),
            "output": _JsonEncode.encode_optional(self.output),
            "outputs": None
            if self.outputs is None
            else _JsonEncode.encode_dict(self.outputs, _BuildType_SerializeOutput, str),
        }
        if extras is None:
            return output
        return {**output, **extras}

    def from_json(json: Serializable.Json) -> Optional["PlatformConfig"]:
        if not isinstance(json, Dict):
            return None
        output = PlatformConfig()
        for key, value in json.items():
            if not isinstance(key, str):
                continue
            if key == "build-param" and isinstance(value, List):
                output.build_param = _JsonDecode.decode_list(value, str)
            elif key == "run-before" and isinstance(value, Dict):
                output.run_before = _JsonDecode.decode_optional_dict(
                    value, BuildRunBefore, TaskIdList
                )
                pass
            elif key == "output" and isinstance(value, str):
                output.output = value
            elif key == "outputs" and isinstance(value, Dict):
                output.outputs = _JsonDecode.decode_optional_dict(
                    value, _BuildType_SerializeOutput, str
                )
                pass
            elif isinstance(value, str):
                if output.extras is None:
                    output.extras = {key: value}
                else:
                    output.extras[key] = value
            pass
        return output
