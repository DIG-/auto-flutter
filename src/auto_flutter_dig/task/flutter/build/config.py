from typing import List

from ....core.string import SB
from ....core.utils import _Dict
from ....model.argument.option import (
    LongOption,
    LongPositionalOption,
    LongShortOptionWithValue,
)
from ....model.build import BuildType
from ....model.platform import Platform
from ....model.project import Project
from ....model.task import *
from ....task.identity import FlutterTaskIdentity
from ...project.read import ProjectRead


class FlutterBuildConfig(Task):
    __options = {
        "build-type": LongPositionalOption("build-type", 0, "Flutter build type"),
        "flavor": LongShortOptionWithValue("f", "flavor", "Flavor to build"),
        "debug": LongOption("debug", "Build a debug version"),
    }
    identity = FlutterTaskIdentity(
        "-build-config",
        "",
        _Dict.flatten(__options),
        lambda: FlutterBuildConfig(),
    )

    ARG_BUILD_TYPE = "FLUTTER_BUILD_CONFIG_TYPE"
    ARG_FLAVOR = "FLUTTER_BUILD_CONFIG_FLAVOR"
    ARG_DEBUG = "FLUTTER_BUILD_CONFIG_DEBUG"

    class Error(RuntimeError):
        ...

    def require(self) -> List[TaskId]:
        return [ProjectRead.identity.id]

    def describe(self, args: Args) -> str:
        return "Preparing flutter build"

    def execute(self, args: Args) -> TaskResult:
        build_type_arg = args.get(self.__options["build-type"])
        if build_type_arg is None or len(build_type_arg) <= 0:
            raise FlutterBuildConfig.Error(
                "Build type not found. Usage is similar to pure flutter."
            )
        build_type: BuildType = BuildType.from_flutter(build_type_arg)
        if build_type is None:
            raise FlutterBuildConfig.Error(
                "Unknown build type `{}`.".format(build_type_arg)
            )
        args.add("build-type", build_type.flutter)
        platform: Platform = build_type.platform
        project = Project.current
        if project is None:
            raise FlutterBuildConfig.Error("Project was not initialized.")

        flavor = args.get(self.__options["flavor"])
        if not project.flavors is None:
            if len(project.flavors) == 1:
                if flavor is None or len(flavor) == 0:
                    self._print(
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
            self._print(
                SB()
                .append(
                    "Project does nos have platform config default and not for {}".format(
                        platform
                    ),
                    SB.Color.YELLOW,
                )
                .str()
            )

        args.add(FlutterBuildConfig.ARG_FLAVOR, flavor)
        args.add(FlutterBuildConfig.ARG_BUILD_TYPE, build_type.flutter)
        if args.contains(self.__options["debug"]):
            args.add(FlutterBuildConfig.ARG_DEBUG)
        elif args.contains(FlutterBuildConfig.ARG_DEBUG):
            args.remove(FlutterBuildConfig.ARG_DEBUG)
        return TaskResult(args)
