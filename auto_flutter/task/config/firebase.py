from collections import namedtuple
from pprint import pprint
from typing import Final

from ...core.utils import _Dict, _Enum, _If
from ._base import *


class ConfigFirebase(_BaseConfigTask):
    __options: Final = {
        "add": Task.Option(
            None, "set-app-id", "Set app id for platform and/or flavor", True
        ),
        "remove": Task.Option(
            None, "remove-app-id", "Remove app id from platform and/or flavor"
        ),
        "platform": Task.Option(
            None, "platform", "Select platform to apply change", True
        ),
        "flavor": Task.Option(None, "flavor", "Select flavor to apply change", True),
    }

    identity = Task.Identity(
        "firebase",
        "Update project firebase config",
        _Dict.flatten(__options),
        lambda: ConfigFirebase(),
    )

    def execute(self, args: Task.Args) -> Task.Result:
        project: Final = Project.current

        platform: Final[Project.Platform] = _If.none(
            args.get_value(self.__options["platform"]),
            lambda: Project.Platform.DEFAULT,
            _Enum.parse(Project.Platform),
        )
        if platform != Project.Platform.DEFAULT and platform not in project.platforms:
            raise ValueError(
                "Project does not support platform {}".format(str(platform))
            )

        flavor: Final = args.get_value(self.__options["flavor"])
        if not flavor is None:
            if project.flavors is None or not flavor in project.flavors:
                raise ValueError("Project does not contains flavor {}".format(flavor))

        add_app_id: Final = args.get_value(self.__options["add"])
        remove_app_id: Final = args.contains(self.__options["remove"])
        if not add_app_id is None and remove_app_id:
            raise ValueError("Can not set and remove app id at same time")

        raise NotImplementedError()
