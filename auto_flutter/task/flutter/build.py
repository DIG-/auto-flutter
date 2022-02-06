from typing import List, Optional

from ...core.utils import _Dict
from ...model.flavor import Flavor
from ...model.platform import BuildType, Platform, PlatformConfigFlavored
from ...model.platform.config import BuildRunBefore
from ...model.project import Project
from ...model.task import Task
from .exec import Flutter


class FlutterBuild(Flutter):
    def __init__(
        self,
        project: Project,
        platform: Platform,
        type: BuildType,
        flavor: Optional[Flavor],
        config: PlatformConfigFlavored,
        debug: bool = False,
    ) -> None:
        super().__init__(
            project=False,
            command=None,
            command_append_args=False,
            output_running=True,
            output_end=False,
            output_arg=True,
        )
        self.project = project
        self.platform = platform
        self.type = type
        self.flavor = flavor
        self.config = config
        self.debug = debug

    def require(self) -> List[Task.ID]:
        required = _Dict.get_or_none(self.config.get_run_before(), BuildRunBefore.BUILD)
        return [] if required is None else required

    def describe(self, args: Task.Args) -> str:
        BaseException()
        return "Building flutter {}".format(self.platform)

    def execute(self, args: Task.Args) -> Task.Result:
        command: List[str] = ["--no-version-check", "build", self.type.value]

        if not self.flavor is None:
            command.append("--flavor")
            command.append(self.flavor)

        if self.debug:
            command.append("--debug")
        else:
            command.append("--release")

        command.append(self.config.get_build_param(self.flavor))
        self._command = command

        process = super().execute(args)
        if not process.error is None:
            process.args.pop("output")
            return process

        if not process.success and self.platform == Platform.ANDROID:
            ## Check output to rebuild other flavors
            pass

        process.args.pop("output")
        if not process.success:
            return process

        output_file = self.config.get_output(self.flavor, self.type)
        if output_file is None:
            return Task.Result(
                args,
                error=Warning("Build success, but file output not defined"),
                success=True,
            )

        args["output"] = output_file
        return Task.Result(args, success=True)
