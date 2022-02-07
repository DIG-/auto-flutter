from typing import Final, List

from auto_flutter.model import platform

from ....core.json import _JsonDecode
from ....core.task.manager import TaskManager
from ....core.utils import _Dict
from ....model.platform import BuildType, MergePlatformConfigFlavored, Platform
from ....model.platform.build_type import _BuildType_SerializeFlutter
from ....model.project import Project
from ....model.task import Task
from .build import FlutterBuild
from .config import FlutterBuildConfig


class FlutterBuildStub(Task):
    identity = Task.Identity(
        "build", "Build flutter app", [], lambda: FlutterBuildStub()
    )

    def require(self) -> List[Task.ID]:
        return [FlutterBuildConfig.identity.id]

    def describe(self, args: Task.Args) -> str:
        return ""

    def execute(self, args: Task.Args) -> Task.Result:
        flavor: Final = args.get_value(FlutterBuildConfig.ARG_FLAVOR)
        build_type: Final[BuildType] = _JsonDecode.decode(
            args.get_value(FlutterBuildConfig.ARG_BUILD_TYPE),
            _BuildType_SerializeFlutter,
        )
        debug: Final = args.contains(FlutterBuildConfig.ARG_DEBUG)
        project: Final = Project.current
        platform: Final = build_type.platform

        config_default = _Dict.get_or_none(project.platform_config, Platform.DEFAULT)
        config_platform = _Dict.get_or_none(project.platform_config, platform)
        config = MergePlatformConfigFlavored(config_default, config_platform)

        TaskManager.instance().add(
            FlutterBuild(project, platform, build_type, flavor, config, debug)
        )
        return Task.Result(args)
