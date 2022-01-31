from enum import Enum
from typing import Dict, List, Optional
from ..model.build_type import BuildType
from ..model.flavor import Flavor


class BuildRunBefore(Enum):
    BUILD = "build"


class BuildConfig:
    build_param: Optional[str]
    run_before: Optional[Dict[BuildRunBefore, List[str]]]
    output: Optional[str]
    outputs: Optional[Dict[BuildType, str]]

    def get_output(self, type: BuildType) -> Optional[str]:
        if not self._outputs is None:
            if type in self._outputs:
                return self._outputs[type]
        return self._output


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
