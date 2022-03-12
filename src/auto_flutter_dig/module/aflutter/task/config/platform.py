from .....core.string import SB
from .....model.argument.option import LongOption
from .....model.argument.option.common.platform import PlatformOption
from .....model.platform import Platform
from .....model.task import *
from .base import *
from .project import ProjectConfigTaskIdentity


class _PlatformOption(PlatformOption):
    def __init__(self, long: str, description: str) -> None:
        super().__init__(description)
        self.long = long


class AflutterPlatformConfigTask(BaseConfigTask):
    __opt_add = _PlatformOption("add", "Add platform support to project")
    __opt_rem = _PlatformOption("remove", "Remove platform support from project")
    __opt_lst = LongOption("list", "List current project platforms")
    identity = ProjectConfigTaskIdentity(
        "platform",
        "Manage platform support for project",
        [__opt_add, __opt_rem, __opt_lst],
        lambda: AflutterPlatformConfigTask(),
    )

    def describe(self, args: Args) -> str:
        return "Updating project platform support"

    def execute(self, args: Args) -> TaskResult:
        project = Project.current
        had_change = False

        add_platform = self.__opt_add.get_or_none(args)
        if not add_platform is None:
            self._uptade_description("Adding platform")
            if add_platform in project.platforms:
                self._uptade_description(
                    self.describe(args),
                    TaskResult(
                        args, E(Warning(f"Project already have platform {add_platform.value}")).error, success=True
                    ),
                )
            else:
                project.platforms.append(add_platform)
                project.obtain_platform_cofig(add_platform)
                had_change = True
                self._uptade_description(
                    self.describe(args),
                    TaskResult(args),
                )

        rem_platform = self.__opt_rem.get_or_none(args)
        if not rem_platform is None:
            self._uptade_description("Removing platform")
            if rem_platform == Platform.DEFAULT:
                self._uptade_description(
                    self.describe(args), TaskResult(args, E(Warning("Can not remove platform DEFAULT")).error)
                )
            elif rem_platform not in project.platforms:
                self._uptade_description(
                    self.describe(args),
                    TaskResult(
                        args, E(Warning(f'Project does not have platform "{rem_platform.value}"')).error, success=True
                    ),
                )
            else:
                project.platforms.remove(rem_platform)
                if rem_platform in project.platform_config:
                    project.platform_config.pop(rem_platform)
                had_change = True
                self._uptade_description(
                    self.describe(args),
                    TaskResult(args),
                )

        if args.contains(self.__opt_lst):
            self._uptade_description("Showing current platform")
            builder = SB()
            builder.append(" Supported platform:")
            for platform in project.platforms:
                builder.append("\n  ").append(platform.value, SB.Color.GREEN)
            list_result = TaskResult(args, message=builder.str())
            if not had_change:
                return list_result
            else:
                self._uptade_description(self.describe(args), list_result)

        if not had_change:
            return TaskResult(args, E(Warning("No change was made")).error, success=True)

        self._add_save_project()
        return TaskResult(args)
