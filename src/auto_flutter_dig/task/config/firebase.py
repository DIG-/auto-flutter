from typing import Optional

from ...core.utils import _Dict, _Enum, _If
from ...model.platform import Platform
from ..firebase._const import FIREBASE_PROJECT_APP_ID_KEY
from ._base import *


class ConfigFirebase(_BaseConfigTask):
    __options = {
        "add": Option(
            None, "set-app-id", "Set app id for platform and/or flavor", True
        ),
        "remove": Option(
            None, "remove-app-id", "Remove app id from platform and/or flavor"
        ),
        "platform": Option(None, "platform", "Select platform to apply change", True),
        "flavor": Option(None, "flavor", "Select flavor to apply change", True),
    }

    identity = TaskIdentity(
        "firebase",
        "Update project firebase config",
        _Dict.flatten(__options),
        lambda: ConfigFirebase(),
    )

    def execute(self, args: Args) -> TaskResult:
        project = Project.current

        platform: Platform = _If.none(
            args.get_value(self.__options["platform"]),
            lambda: Platform.DEFAULT,
            _Enum.parse(Platform),
        )
        if platform != Platform.DEFAULT and platform not in project.platforms:
            raise ValueError(
                "Project does not support platform {}".format(str(platform))
            )

        flavor = args.get_value(self.__options["flavor"])
        if not flavor is None:
            if project.flavors is None or not flavor in project.flavors:
                raise ValueError("Project does not contains flavor {}".format(flavor))

        add_app_id = args.get_value(self.__options["add"])
        remove_app_id = args.contains(self.__options["remove"])
        if not add_app_id is None and remove_app_id:
            raise ValueError("Can not set and remove app id at same time")
        if add_app_id is None and not remove_app_id:
            raise ValueError("At least one operation is required")

        has_warning: Optional[BaseException] = None

        ## Remove app id section
        if remove_app_id:
            platform_config = project.get_platform_config(platform)
            if platform_config is None:
                raise KeyError(
                    "Project does not have config for platform {}".format(str(platform))
                )
            config = platform_config.get_config_by_flavor(flavor)
            if config is None:
                raise KeyError(
                    "Project does not have config for platform {} and flavor {}".format(
                        str(platform), flavor
                    )
                )
            if not config._remove_extra(FIREBASE_PROJECT_APP_ID_KEY.value):
                has_warning = Warning(
                    "Selected platform and flavor does not have app id"
                )

        ## Set app id section
        if not add_app_id is None:
            project.obtain_platform_cofig(platform).obtain_config_by_flavor(
                flavor
            )._add_extra(FIREBASE_PROJECT_APP_ID_KEY.value, add_app_id)

        self._add_save_project()
        return TaskResult(args, error=has_warning, success=True)
