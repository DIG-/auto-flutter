from typing import List

from ....core.utils import _Dict, _Ensure
from ....model.build import BuildType
from ....model.platform import MergePlatformConfigFlavored, Platform
from ....model.project import Project
from ....model.task import *
from .build import FlutterBuildTask
from .config import FlutterBuildConfig


class FlutterBuildStub(Task):
    identity = TaskIdentity(
        "build", "Build flutter app", [], lambda: FlutterBuildStub()
    )

    def require(self) -> List[TaskId]:
        return [FlutterBuildConfig.identity.id]

    def describe(self, args: Args) -> str:
        return ""

    def execute(self, args: Args) -> TaskResult:
        flavor = args.get_value(FlutterBuildConfig.ARG_FLAVOR)
        build_type = BuildType.from_flutter(
            _Ensure.not_none(
                args.get_value(FlutterBuildConfig.ARG_BUILD_TYPE), "build-type"
            )
        )
        debug = args.contains(FlutterBuildConfig.ARG_DEBUG)
        project = Project.current
        platform = build_type.platform

        config_default = _Dict.get_or_none(project.platform_config, Platform.DEFAULT)
        config_platform = _Dict.get_or_none(project.platform_config, platform)
        config = MergePlatformConfigFlavored(config_default, config_platform)

        self._append_task(FlutterBuildTask(project, build_type, flavor, config, debug))
        return TaskResult(args)
