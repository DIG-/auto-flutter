from enum import Enum
from typing import Dict, List, Optional
from ..model.build_type import BuildType
from ..model._serializable import Serializable
from ..model.flavor import Flavor
from ..core.utils import _JsonUtil


class BuildRunBefore(Enum):
    BUILD = "build"


class TaskIdList(list[str], Serializable["TaskIdList"]):
    def to_json(self) -> Serializable.Json:
        return _JsonUtil.list_to_json(self)

    def from_json(json: Serializable.Json) -> Optional["TaskIdList"]:
        if json is None:
            return None
        if not isinstance(json, List):
            return None
        return _JsonUtil.json_to_list(json, str)


class BuildConfig(Serializable["BuildConfig"]):
    RunBefore = BuildRunBefore
    Type = BuildType

    def __init__(
        self,
        build_param: Optional[str] = None,
        run_before: Optional[Dict[BuildRunBefore, TaskIdList]] = None,
        output: Optional[str] = None,
        outputs: Optional[Dict[BuildType, str]] = None,
        extras: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__()
        self.build_param: Optional[str] = build_param
        self.run_before: Optional[Dict[BuildRunBefore, TaskIdList]] = run_before
        self.output: Optional[str] = output
        self.outputs: Optional[Dict[BuildType, str]] = outputs
        self.extras: Optional[Dict[str, str]] = extras

    def get_output(self, type: BuildType) -> Optional[str]:
        if not self._outputs is None:
            if type in self._outputs:
                return self._outputs[type]
        return self._output

    def get_extra(self, key: str) -> Optional[str]:
        if self.extras is None:
            return None
        if key in self.extras:
            return self.extras[key]
        return None

    def to_json(self) -> Serializable.Json:
        extras = self.extras
        output = {
            "build-param": self.build_param,
            "run-before": _JsonUtil.optional_to_json(self.run_before),
            "output": _JsonUtil.optional_to_json(self.output),
            "outputs": _JsonUtil.optional_to_json(self.outputs),
        }
        if extras is None:
            return output
        return {**output, **extras}

    def from_json(json: Serializable.Json) -> Optional["BuildConfig"]:
        if not isinstance(json, Dict):
            return None
        output = BuildConfig()
        for key, value in json.items():
            if not isinstance(key, str):
                continue
            if key == "build-param" and isinstance(value, str):
                output.build_param = value
            elif key == "run-before" and isinstance(value, Dict):
                output.run_before = _JsonUtil.json_to_dict(
                    value, BuildRunBefore, TaskIdList
                )
                pass
            elif key == "output" and isinstance(value, str):
                output.output = value
            elif key == "outputs" and isinstance(value, Dict):
                output.outputs = _JsonUtil.json_to_dict(value, BuildType, str)
                pass
            elif isinstance(value, str):
                if output.extras is None:
                    output.extras = {key: value}
                else:
                    output.extras[key] = value
            pass
        return output


class BuildConfigFlavored(BuildConfig):
    flavored: Optional[Dict[Flavor, BuildConfig]]

    def get_build_param(self, flavor: Optional[Flavor]) -> str:
        output = ""
        if not self.build_param is None:
            output += self.build_param
        if not flavor is None and flavor in self.flavored:
            flavored_param = self.flavored[flavor].build_param
            if not flavored_param is None:
                if len(output) > 0:
                    output += " "
                output += flavored_param
        return output

    def get_run_before(
        self, flavor: Optional[Flavor]
    ) -> Dict[BuildRunBefore, List[str]]:
        output: Dict[BuildRunBefore, List[str]] = dict()
        if not self.run_before is None:
            output = self.run_before
        if (
            (not flavor is None)
            and (flavor in self.flavored)
            and (not self.flavored[flavor] is None)
        ):
            for key, value in self.flavored[flavor].run_before.items():
                if not key in output:
                    output[key] = value
                else:
                    output[key] = [*output[key], *value]
        return output

    def get_output(self, flavor: Optional[Flavor], type: BuildType) -> Optional[str]:
        if not flavor is None and flavor in self.flavored:
            from_flavor = self.flavored[flavor].get_output(type)
            if not from_flavor is None:
                return from_flavor
        return self.get_output(type)

    def get_extra(self, flavor: Optional[Flavor], key: str) -> Optional[str]:
        if not flavor is None and flavor in self.flavored:
            from_flavor = self.flavored[flavor].get_extra(key)
            if not from_flavor is None:
                return from_flavor
        return self.get_extra(key)
