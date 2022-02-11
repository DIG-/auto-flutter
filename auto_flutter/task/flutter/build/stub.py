from typing import List

from ....core.task.manager import TaskManager
from ....core.utils import _Dict
from ....model.build import BuildType
from ....model.platform import MergePlatformConfigFlavored, Platform
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
        flavor = args.get_value(FlutterBuildConfig.ARG_FLAVOR)
        build_type = BuildType.from_flutter(
            args.get_value(FlutterBuildConfig.ARG_BUILD_TYPE)
        )
        debug = args.contains(FlutterBuildConfig.ARG_DEBUG)
        project = Project.current
        platform = build_type.platform

        config_default = _Dict.get_or_none(project.platform_config, Platform.DEFAULT)
        config_platform = _Dict.get_or_none(project.platform_config, platform)
        config = MergePlatformConfigFlavored(config_default, config_platform)

        TaskManager.instance().add(
            FlutterBuild(project, platform, build_type, flavor, config, debug)
        )
        return Task.Result(args)
