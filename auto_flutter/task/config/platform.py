from platform import platform
from typing import Final, List, Optional

from ...core.json import _JsonDecode
from ...core.utils import _Ensure
from ...model.platform import PlatformConfigFlavored
from ...model.task import Task
from ..options import ParseOptions
from ..project import Project, ProjectRead, ProjectSave


class ConfigPlatform(Task):
    option_add: Final = Task.Option(
        None, "add", "Add platform support to project", True)
    option_rem: Final = Task.Option(
        None, "remove", "Remove platform support from project", True)
    identity = Task.Identity("platform", "Manage platform support for project", [
        option_add, option_rem
    ],
        lambda: ConfigPlatform())

    def describe(self, args: Task.Args) -> str:
        return "Updating project platform support"

    def require(self) -> List[Task.ID]:
        return [ParseOptions.identity.id, ProjectRead.identity.id]

    def execute(self, args: Task.Args) -> Task.Result:
        project: Final = Project.current
        had_change = False

        platform_add: Final = args.get_value(self.option_add)
        if not platform_add is None and len(platform_add) > 0:
            self.print("    Adding platform {}".format(platform_add))
            parsed_add: Final = ConfigPlatform.__parse_platform(platform_add)
            if parsed_add is None:
                return Task.Result(args, error=ValueError("Unrecognized platform `{}`".format(platform_add)))
            if parsed_add in project.platforms:
                return Task.Result(args, error=Warning("Project already had platform `{}`".format(platform_add)), success=True)
            project.platforms.append(parsed_add)
            had_change = True
            if project.platform_config is None:
                project.platform_config = {}
            project.platform_config[parsed_add] = PlatformConfigFlavored()

        platform_rem: Final = args.get_value(self.option_rem)
        if not platform_rem is None and len(platform_rem) > 0:
            self.print("    Removing platform {}".format(platform_rem))
            parsed_rem: Final = ConfigPlatform.__parse_platform(platform_rem)
            if parsed_rem is None:
                return Task.Result(args, error=ValueError("Unrecognized platform `{}`".format(platform_rem)))
            if not parsed_rem in project.platforms:
                return Task.Result(args, error=Warning("Project do not have platform `{}`".format(platform_rem)), success=True)
            project.platforms.pop(parsed_rem)
            had_change = True
            if not project.platform_config is None and parsed_rem in project.platform_config:
                project.platform_config.pop(parsed_rem)

        if not had_change:
            return Task.Result(
                args, error=AssertionError("No change was made"), success=True
            )

        from ...core.task import TaskManager

        TaskManager.instance().add(ProjectSave())
        return Task.Result(args)

    def __parse_platform(platform: str) -> Optional[Project.Platform]:
        _Ensure.instance(platform, str, "platform")
        return _JsonDecode.decode(platform, Project.Platform)
