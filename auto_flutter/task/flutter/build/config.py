from typing import Final, List

from ....core.json import _JsonDecode
from ....core.string import SB
from ....core.utils import _Dict
from ....model.platform import BuildType, Platform
from ....model.platform.build_type import _BuildType_SerializeFlutter
from ....model.project import Project
from ....model.task import Task
from ...project.read import ProjectRead


class FlutterBuildConfig(Task):
    identity = Task.Identity(
        "-build-config",
        "",
        [
            Task.Identity.Option("f", "flavor", "Flavor to build", True),
            Task.Identity.Option(None, "debug", "Build a debug version", False),
        ],
        lambda: FlutterBuildConfig(),
    )

    ARG_BUILD_TYPE: Final = "FLUTTER_BUILD_CONFIG_TYPE"
    ARG_FLAVOR: Final = "FLUTTER_BUILD_CONFIG_FLAVOR"
    ARG_DEBUG: Final = "FLUTTER_BUILD_CONFIG_DEBUG"

    class Error(RuntimeError):
        ...

    def require(self) -> List[Task.ID]:
        return [ProjectRead.identity.id]

    def describe(self, args: Task.Args) -> str:
        return "Preparing flutter build"

    def execute(self, args: Task.Args) -> Task.Result:
        if not "-0" in args or len(args["-0"].argument) <= 0:
            raise FlutterBuildConfig.Error(
                "Build type not found. Usage is similar to pure flutter."
            )
        build_type: Final[BuildType] = _JsonDecode.decode(
            args["-0"].argument, _BuildType_SerializeFlutter
        )
        if build_type is None:
            raise FlutterBuildConfig.Error(
                "Unknown build type `{}`.".format(args["-0"].argument)
            )
        platform: Final[Platform] = build_type.platform
        project: Final = Project.current
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

        config_default = _Dict.get_or_none(project.platform_config, Platform.DEFAULT)
        config_platform = _Dict.get_or_none(project.platform_config, platform)
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

        args.add_arg(FlutterBuildConfig.ARG_FLAVOR, flavor)
        args.add_arg(
            FlutterBuildConfig.ARG_BUILD_TYPE,
            _BuildType_SerializeFlutter(build_type).to_json(),
        )
        if args.contains("debug"):
            args.add_arg(FlutterBuildConfig.ARG_DEBUG)
        return Task.Result(args)