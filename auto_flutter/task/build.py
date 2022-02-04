from typing import List, Optional

from ..core.json import _JsonDecode
from ..core.task import Task
from ..model.build_type import BuildType, FlutterBuildType
from .flutter import Flutter


class FlutterBuild(Flutter):
    identity = Task.Identity(
        "build",
        "Build flutter app",
        [
            Task.Identity.Option("f", "flavor", "Flavor to build", True),
            Task.Identity.Option(None, "debug", "Build a debug version", True),
        ],
        lambda: FlutterBuild(),
    )

    class Error(RuntimeError):
        ...

    def __init__(self) -> None:
        super().__init__(
            project=True,
            command=None,
            command_append_args=None,
            output_running=True,
            output_end=False,
            output_arg=True,
        )

    def describe(self, args: Task.Args) -> str:
        return "Building flutter app"

    def execute(self, args: Task.Args) -> Task.Result:
        if not "-0" in args or len(args["-0"].argument) <= 0:
            raise FlutterBuild.Error(
                "Build type not found. Usage is similar to pure flutter"
            )
        build_type = _JsonDecode.decode(args["-0"].argument, FlutterBuildType)
        if build_type is None:
            raise FlutterBuild.Error(
                "Unknown build type `{}`".format(args["-0"].argument)
            )

        # return super().execute(args)
        return Task.Result(args, success=False)
