from typing import Optional

from .....core.string import SB
from .....model.argument.option import LongOptionWithValue, LongShortOption
from .....model.argument.option.common.flavor import Flavor, FlavorOption
from .....model.argument.option.common.platform import Platform, PlatformOption
from .....model.platform.merge_config import MergePlatformConfigFlavored, PlatformConfigFlavored
from .....model.result import Result
from .....model.task import *
from .....module.aflutter.task.config.base import *
from ...identity import FlutterTaskIdentity


class FlutterBuildParamConfigTask(BaseConfigTask):
    __opt_add = LongOptionWithValue("add", "Add build param to project, platform and/or flavor")
    __opt_rem = LongOptionWithValue("remove", "Remove build param from project, platform and/or flavor")
    __opt_list = LongShortOption("l", "list", "List build params for project, platform and/or flavor")
    __opt_list_recursive = LongShortOption(
        "r",
        "list-all",
        "List all build params (recursively) for platform and flavor. (require both, except flavor if project does not have flavor)",
    )
    __opt_platform = PlatformOption("Platform to update build param (optional)")
    __opt_flavor = FlavorOption("Flavor to update build param (optional)")
    identity = FlutterTaskIdentity(
        "build-param",
        "Configure build params for project, platform and/or flavor",
        [
            __opt_add,
            __opt_rem,
            __opt_platform,
            __opt_flavor,
            __opt_list,
            __opt_list_recursive,
        ],
        lambda: FlutterBuildParamConfigTask(),
    )

    def execute(self, args: Args) -> TaskResult:
        project = Project.current
        platform = self.__opt_platform.get_or_default(args, lambda: Platform.DEFAULT)
        flavor = self.__opt_flavor.get_or_none(args)

        had_change: bool = False
        had_change = self._add_build_param(args, project, platform, flavor) or had_change
        had_change = self._remove_build_param(args, project, platform, flavor) or had_change

        if args.contains(self.__opt_list) or args.contains(self.__opt_list_recursive):
            result: TaskResult
            if args.contains(self.__opt_list):
                result = self._show_build_params(args, project, platform, flavor)
            else:
                result = self._show_recursive_build_params(args, project, platform, flavor)
            if not had_change:
                return result
            self._uptade_description(self.describe(args), result)

        if not had_change:
            return TaskResult(args, error=E(Warning("No change was made")).error, success=True)
        self._uptade_description("")  # To not write default description since had change
        self._add_save_project()
        return TaskResult(args)

    def _add_build_param(self, args: Args, project: Project, platform: Platform, flavor: Optional[Flavor]) -> bool:
        add_param = args.get(self.__opt_add)
        if add_param is None or len(add_param) <= 0:
            return False
        if flavor is None:
            self._uptade_description(f"Add build param to {platform}")
        else:
            self._uptade_description(f"Add build param to {platform} and flavor {flavor}")

        add_param = add_param.strip()
        if len(add_param) <= 0:
            self._reset_description(args, Result(E(ValueError("Can not add empty build param")).error))
            return False

        invalid = self._validate_platform(project, platform)
        if not invalid is None:
            self._reset_description(args, invalid)
            return False

        invalid = self._validate_flavor(project, flavor)
        if not invalid is None:
            self._reset_description(args, invalid)
            return False

        config = project.obtain_platform_cofig(platform).obtain_config_by_flavor(flavor)
        if config.build_param is None:
            config.build_param = []
        config.build_param.append(add_param)
        self._reset_description(args, Result(success=True))
        return True

    def _remove_build_param(self, args: Args, project: Project, platform: Platform, flavor: Optional[Flavor]) -> bool:
        rem_param = args.get(self.__opt_rem)
        if rem_param is None or len(rem_param) <= 0:
            return False
        if flavor is None:
            self._uptade_description(f"Remove build param from {platform}")
        else:
            self._uptade_description(f"Remove build param from {platform} and flavor {flavor}")

        rem_param = rem_param.strip()
        if len(rem_param) <= 0:
            self._reset_description(args, Result(E(ValueError("Can not remove empty build param")).error))
            return False

        invalid = self._validate_platform(project, platform)
        if not invalid is None:
            self._reset_description(args, invalid)
            return False

        invalid = self._validate_flavor(project, flavor)
        if not invalid is None:
            self._reset_description(args, invalid)
            return False

        p_config = project.get_platform_config(platform)
        if p_config is None:
            self._reset_description(
                args, Result(E(Warning(f"{platform} does not have build config")).error, success=True)
            )
            return False

        f_config = p_config.get_config_by_flavor(flavor)
        if f_config is None:
            self._reset_description(
                args,
                Result(E(Warning(f"{platform} with flavor {flavor} does not have build config")).error, success=True),
            )
            return False

        if f_config.build_param is None or not rem_param in f_config.build_param:
            self._reset_description(args, Result(E(ValueError("Build param not found to be removed")).error))
            return False
        f_config.build_param.remove(rem_param)
        self._reset_description(args, Result(success=True))
        return True

    def _validate_platform(self, project: Project, platform: Platform) -> Optional[Result]:
        if platform != Platform.DEFAULT and not platform in project.platforms:
            return Result(E(ValueError(f"Project does not have support to {platform}")).error)
        return None

    def _validate_flavor(self, project: Project, flavor: Optional[Flavor]) -> Optional[Result]:
        if project.flavors is None or len(project.flavors) <= 0:
            if not flavor is None:
                return Result(E(ValueError("Project does not have flavors")).error)
            return None
        if flavor is None:
            return None
        if not flavor in project.flavors:
            return Result(E(ValueError(f"Project does not have flavor {flavor}")).error)
        return None

    def _show_build_params(
        self,
        args: Args,
        project: Project,
        platform: Platform,
        flavor: Optional[Flavor],
    ) -> TaskResult:
        if flavor is None:
            self._uptade_description(f"Showing build params for {platform}")
        else:
            self._uptade_description(f"Showing build params for {platform} and flavor {flavor}")

        invalid = self._validate_platform(project, platform)
        if not invalid is None:
            return TaskResult(args, error=invalid.error, success=invalid.success)

        invalid = self._validate_flavor(project, flavor)
        if not invalid is None:
            return TaskResult(args, error=invalid.error, success=invalid.success)

        p_config = project.get_platform_config(platform)
        if p_config is None:
            return TaskResult(args, error=Warning(f"Project has no config for {platform}"), success=True)

        f_config = p_config.get_config_by_flavor(flavor)
        if f_config is None:
            return TaskResult(args, error=Warning(f"Project has no config for {platform} {flavor}"), success=True)

        if f_config.build_param is None or len(f_config.build_param) <= 0:
            return TaskResult(args, message=SB().append("  No build params found", SB.Color.YELLOW).str(), success=True)

        builder = SB().append(" Build params:")
        for param in f_config.build_param:
            builder.append("\n  ").append(param, SB.Color.GREEN)
        return TaskResult(args, message=builder.str())

    def _show_recursive_build_params(
        self,
        args: Args,
        project: Project,
        platform: Platform,
        flavor: Optional[Flavor],
    ) -> TaskResult:
        if flavor is None:
            self._uptade_description(f"Showing all build params for {platform}")
        else:
            self._uptade_description(f"Showing all build params for {platform} and flavor {flavor}")

        invalid = self._validate_platform(project, platform)
        if not invalid is None:
            return TaskResult(args, error=invalid.error, success=invalid.success)

        invalid = self._validate_flavor(project, flavor)
        if not invalid is None:
            return TaskResult(args, error=invalid.error, success=invalid.success)

        if not project.flavors is None and len(project.flavors) > 0 and flavor is None:
            return TaskResult(args, error=E(ValueError("Flavor is required")).error)

        config: PlatformConfigFlavored
        if platform == Platform.DEFAULT:
            config = project.obtain_platform_cofig(platform)
        else:
            config = MergePlatformConfigFlavored(
                project.get_platform_config(Platform.DEFAULT),
                project.get_platform_config(platform),
            )

        builder = SB().append(" All build params:")
        for param in config.get_build_param(flavor):
            builder.append("\n  ").append(param, SB.Color.GREEN)
        return TaskResult(args, message=builder.str(), success=True)
