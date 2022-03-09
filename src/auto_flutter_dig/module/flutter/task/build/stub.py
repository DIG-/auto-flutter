from .....model.argument.option import LongOption, LongPositionalOption
from .....model.argument.option.common.build_mode import BuildModeOption
from .....model.argument.option.common.build_type import BuildTypeFlutterOption
from .....model.argument.option.common.flavor import FlavorOption
from .....model.argument.option.hidden import HiddenOption
from .....model.build import BuildMode
from .....model.platform import Platform
from .....model.platform.merge_config import MergePlatformConfigFlavored
from .....model.project import Project
from .....model.task import *
from ...identity import FlutterTaskIdentity
from .build import FlutterBuildTaskIdentity


class _BuildTypeFlutterPositionalOption(BuildTypeFlutterOption, LongPositionalOption):
    def __init__(self, description: str) -> None:
        BuildTypeFlutterOption.__init__(self, description)
        LongPositionalOption.__init__(self, self.long, 0, description)


class _BuildModeHiddenOption(BuildModeOption, HiddenOption):
    def __init__(self, description: str) -> None:
        BuildModeOption.__init__(self, description)
        HiddenOption.__init__(self, description)


class FlutterBuildStub(Task):
    opt_build_type = _BuildTypeFlutterPositionalOption("Flutter build type")
    opt_flavor = FlavorOption("Flavor to build")
    opt_release = LongOption("release", "Build a release version (default)")
    opt_debug = LongOption("debug", "Build a debug version")
    opt_build_mode = _BuildModeHiddenOption("")
    identity = FlutterTaskIdentity(
        "build",
        "Build flutter app",
        [
            opt_build_type,
            opt_flavor,
            opt_release,
            opt_debug,
            opt_build_mode,
        ],
        lambda: FlutterBuildStub(),  # pylint: disable=unnecessary-lambda
    )

    def describe(self, args: Args) -> str:
        return "Prepare build"

    def execute(self, args: Args) -> TaskResult:
        try:
            build_type = self.opt_build_type.get_or_none(args)
        except BaseException as error:
            return TaskResult(
                args, E(ValueError(f'Failed to parse build type "{args.get(self.opt_build_type)}"')).caused_by(error)
            )
        if build_type is None:
            return TaskResult(
                args, E(ValueError("Build type not found. Usage is similar to pure flutter build.")).error
            )
        flavor = self.opt_flavor.get_or_none(args)

        try:
            build_mode = self.opt_build_mode.get_or_none(args)
        except BaseException as error:
            return TaskResult(
                args, E(ValueError(f'Failed to parse build mode "{args.get(self.opt_build_mode)}"')).caused_by(error)
            )
        if build_mode is None:
            if args.contains(self.opt_release):
                build_mode = BuildMode.RELEASE
            elif args.contains(self.opt_debug):
                build_mode = BuildMode.DEBUG
            else:
                build_mode = BuildMode.RELEASE
            args.add(self.opt_build_mode, build_mode.value)
        project = Project.current
        config_default = project.get_platform_config(Platform.DEFAULT)
        config_platform = project.get_platform_config(build_type.platform)
        config = MergePlatformConfigFlavored(config_default, config_platform)

        self._append_task(FlutterBuildTaskIdentity(project, build_type, flavor, config, build_mode))
        return TaskResult(args)
