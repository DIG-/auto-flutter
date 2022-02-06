from ...core.json import _JsonDecode
from ...core.string import SB
from ...core.task.manager import TaskManager
from ...core.utils import _Dict
from ...model.platform import BuildType, MergePlatformConfigFlavored, Platform
from ...model.project import Project
from ...model.task import Task
from .build import FlutterBuild


class FlutterBuildConfig(Task):
    identity = Task.Identity(
        "build",
        "Build flutter app",
        [
            Task.Identity.Option("f", "flavor", "Flavor to build", True),
            Task.Identity.Option(None, "debug", "Build a debug version", False),
        ],
        lambda: FlutterBuildConfig(),
    )

    class Error(RuntimeError):
        ...

    def describe(self, args: Task.Args) -> str:
        return "Preparing flutter build"

    def execute(self, args: Task.Args) -> Task.Result:
        if not "-0" in args or len(args["-0"].argument) <= 0:
            raise FlutterBuildConfig.Error(
                "Build type not found. Usage is similar to pure flutter."
            )
        build_type = _JsonDecode.decode(args["-0"].argument, BuildType)
        if build_type is None:
            raise FlutterBuildConfig.Error(
                "Unknown build type `{}`.".format(args["-0"].argument)
            )
        platform = build_type.to_Platform()
        project = Project.current
        if project is None:
            raise FlutterBuildConfig.Error("Project was not initialized.")

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
                raise FlutterBuildConfig.Error(
                    "Build require flavor, nothing was passed."
                )
            if not flavor in project.flavors:
                raise FlutterBuildConfig.Error(
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

        TaskManager.instance().add(
            FlutterBuild(project, platform, build_type, flavor, config, "debug" in args)
        )
        return Task.Result(args)
