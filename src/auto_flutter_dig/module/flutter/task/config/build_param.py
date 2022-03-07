from .....model.argument.option import LongOptionWithValue, LongShortOption
from .....model.argument.option.common.flavor import FlavorOption
from .....model.argument.option.common.platform import PlatformOption
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
            __opt_list,
            __opt_list_recursive,
            __opt_platform,
            __opt_flavor,
        ],
        lambda: FlutterBuildParamConfigTask(),
    )

    def execute(self, args: Args) -> TaskResult:
        return super().execute(args)
