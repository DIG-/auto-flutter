from typing import List

from ....core.json import _JsonDecode
from ....core.string import SB
from ....core.utils import _Dict
from ....model.platform import BuildType, Platform
from ....model.platform.build_type import _BuildType_SerializeFlutter
from ....model.platform.config import BuildRunBefore
from ....model.platform.merge_config import MergePlatformConfigFlavored
from ....model.project import Project
from ....model.task import Task
from ...options import ParseOptions
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

    ARG_BUILD_TYPE = "FLUTTER_BUILD_CONFIG_TYPE"
    ARG_FLAVOR = "FLUTTER_BUILD_CONFIG_FLAVOR"
    ARG_DEBUG = "FLUTTER_BUILD_CONFIG_DEBUG"

    class Error(RuntimeError):
        ...

    def require(self) -> List[Task.ID]:
        return [ParseOptions.identity.id, ProjectRead.identity.id]

    def describe(self, args: Task.Args) -> str:
        return "Preparing flutter build"

    def execute(self, args: Task.Args) -> Task.Result:
        if not "-0" in args or len(args["-0"].argument) <= 0:
            raise FlutterBuildConfig.Error(
                "Build type not found. Usage is similar to pure flutter."
            )
        build_type: BuildType = _JsonDecode.decode(
            args["-0"].argument, _BuildType_SerializeFlutter
        )
        if build_type is None:
            raise FlutterBuildConfig.Error(
                "Unknown build type `{}`.".format(args["-0"].argument)
            )
        platform: Platform = build_type.platform
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
        else:
            merge = MergePlatformConfigFlavored(config_default, config_platform)
            before_build = merge.get_run_before(BuildRunBefore.BUILD, flavor)
            if len(before_build) > 0:
                from ....core.task import TaskManager

                TaskManager.instance().add_id(before_build)

        args.add_arg(FlutterBuildConfig.ARG_FLAVOR, flavor)
        args.add_arg(FlutterBuildConfig.ARG_BUILD_TYPE, build_type.flutter)
        if args.contains("debug"):
            args.add_arg(FlutterBuildConfig.ARG_DEBUG)
        elif args.contains(FlutterBuildConfig.ARG_DEBUG):
            args.pop(FlutterBuildConfig.ARG_DEBUG)
        return Task.Result(args)
