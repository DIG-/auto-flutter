from typing import Optional

from ...core.json import _JsonDecode
from ...core.utils import _Ensure
from ...model.platform import PlatformConfigFlavored
from ._base import *


class ConfigPlatform(_BaseConfigTask):
    option_add = Task.Option(None, "add", "Add platform support to project", True)
    option_rem = Task.Option(
        None, "remove", "Remove platform support from project", True
    )
    identity = Task.Identity(
        "platform",
        "Manage platform support for project",
        [option_add, option_rem],
        lambda: ConfigPlatform(),
    )

    def describe(self, args: Task.Args) -> str:
        return "Updating project platform support"

    def execute(self, args: Task.Args) -> Task.Result:
        project = Project.current
        had_change = False

        platform_add = args.get_value(self.option_add)
        if not platform_add is None and len(platform_add) > 0:
            self.print("    Adding platform {}".format(platform_add))
            parsed_add = ConfigPlatform.__parse_platform(platform_add)
            if parsed_add is None:
                return Task.Result(
                    args,
                    error=ValueError("Unrecognized platform `{}`".format(platform_add)),
                )
            if parsed_add in project.platforms:
                return Task.Result(
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
            self.print("    Removing platform {}".format(platform_rem))
            parsed_rem = ConfigPlatform.__parse_platform(platform_rem)
            if parsed_rem is None:
                return Task.Result(
                    args,
                    error=ValueError("Unrecognized platform `{}`".format(platform_rem)),
                )
            if not parsed_rem in project.platforms:
                return Task.Result(
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
            return Task.Result(
                args, error=AssertionError("No change was made"), success=True
            )

        self._add_save_project()
        return Task.Result(args)

    def __parse_platform(platform: str) -> Optional[Project.Platform]:
        _Ensure.instance(platform, str, "platform")
        return _JsonDecode.decode(platform, Project.Platform)
