from ...core.utils import _Enum
from ...model.platform import Platform, PlatformConfigFlavored
from ._base import *


class ConfigPlatform(_BaseConfigTask):
    option_add = Option(None, "add", "Add platform support to project", True)
    option_rem = Option(None, "remove", "Remove platform support from project", True)
    identity = TaskIdentity(
        "platform",
        "Manage platform support for project",
        [option_add, option_rem],
        lambda: ConfigPlatform(),
    )

    def describe(self, args: Args) -> str:
        return "Updating project platform support"

    def execute(self, args: Args) -> TaskResult:
        project = Project.current
        had_change = False

        platform_add = args.get_value(self.option_add)
        if not platform_add is None and len(platform_add) > 0:
            self._print("    Adding platform {}".format(platform_add))
            parsed_add = _Enum.parse_value(Platform, platform_add)
            if parsed_add is None:
                return TaskResult(
                    args,
                    error=ValueError("Unrecognized platform `{}`".format(platform_add)),
                )
            if parsed_add in project.platforms:
                return TaskResult(
                    args,
                    error=Warning(
                        "Project already had platform `{}`".format(platform_add)
                    ),
                    success=True,
                )
            project.platforms.append(parsed_add)
            had_change = True
            if project.platform_config is None:
                project.platform_config = {}
            project.platform_config[parsed_add] = PlatformConfigFlavored()

        platform_rem = args.get_value(self.option_rem)
        if not platform_rem is None and len(platform_rem) > 0:
            self._print("    Removing platform {}".format(platform_rem))
            parsed_rem = _Enum.parse_value(Platform, platform_rem)
            if parsed_rem is None:
                return TaskResult(
                    args,
                    error=ValueError("Unrecognized platform `{}`".format(platform_rem)),
                )
            if not parsed_rem in project.platforms:
                return TaskResult(
                    args,
                    error=Warning(
                        "Project do not have platform `{}`".format(platform_rem)
                    ),
                    success=True,
                )
            project.platforms.remove(parsed_rem)
            had_change = True
            if (
                not project.platform_config is None
                and parsed_rem in project.platform_config
            ):
                project.platform_config.pop(parsed_rem)

        if not had_change:
            return TaskResult(args, error=Warning("No change was made"), success=True)

        self._add_save_project()
        return TaskResult(args)
