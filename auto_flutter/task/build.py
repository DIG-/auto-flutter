from ..core.json import _JsonDecode
from ..core.string_builder import SB
from ..core.utils import _Dict
from ..model.build_type import FlutterBuildType
from ..model.platform import MergePlatformConfigFlavored, Platform
from ..model.project import Project
from ..model.task import Task
from .flutter.exec import Flutter


class FlutterBuild(Flutter):
    identity = Task.Identity(
        "build",
        "Build flutter app",
        [
            Task.Identity.Option("f", "flavor", "Flavor to build", True),
            Task.Identity.Option(None, "debug", "Build a debug version", False),
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
                "Build type not found. Usage is similar to pure flutter."
            )
        build_type = _JsonDecode.decode(args["-0"].argument, FlutterBuildType)
        if build_type is None:
            raise FlutterBuild.Error(
                "Unknown build type `{}`.".format(args["-0"].argument)
            )
        platform = build_type.to_Platform()
        project = Project.current
        if project is None:
            raise FlutterBuild.Error("Project was not initialized.")

        flavor = args["flavor"].value if "flavor" in args else None
        if not project.flavors is None:
            if len(project.flavors) == 1:
                if flavor is None or len(flavor) == 0:
                    self.print(
                        SB()
                        .append(
                            "Flavor not informed, but project has only one. Assuming it.",
                            SB.Color.YELLOW,
                        )
                        .str()
                    )
                    flavor = project.flavors[0]
            if flavor is None:
                raise FlutterBuild.Error("Build require flavor, nothing was passed.")
            if not flavor in project.flavors:
                raise FlutterBuild.Error(
                    "Flavor {} was not found in project.".format(flavor)
                )

        config_default = _Dict.get_or_none(project.build_config, Platform.DEFAULT)
        config_platform = _Dict.get_or_none(project.build_config, platform)
        config = MergePlatformConfigFlavored(config_default, config_platform)
        if config_default is None and config_platform is None:
            self.print(
                SB()
                .append(
                    "Project does nos have platform config default and not for {}".format(
                        platform
                    ),
                    SB.Color.YELLOW,
                )
                .str()
            )

        ## TODO: Consume run before

        # Configure super to build
        self._command = ["build", build_type.value]
        if not flavor is None:
            self._command.append("--flavor")
            self._command.append(flavor)

        if "debug" in args:
            self._command.append("--debug")
        else:
            self._command.append("--release")

        self._command.append(config.get_build_param(flavor))

        process = super().execute(args)
        if not process.success:
            return process

        process.args.pop("output")

        output = config.get_output(flavor, build_type)
        if not output is None:
            ## TODO: Format output and check if exists
            pass

        return process
