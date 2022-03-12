from typing import Optional

from ........model.platform import Platform
from ........model.project import Flavor, Project
from ........model.task import *
from ........model.task.init.project_identity import InitProjectTaskIdentity
from ......identity import AflutterTaskIdentity
from ..platform import ProjectInitFindPlatformTask


class BaseProjectInitFindFlavorIdentity(AflutterTaskIdentity, InitProjectTaskIdentity):
    @property
    def require_before(self) -> List[TaskIdentity]:
        return [ProjectInitFindPlatformTask.identity]


class BaseProjectInitFindFlavorTask(Task):
    @staticmethod
    def _append_flavor(
        project: Project,
        platform: Platform,
        flavor: Flavor,
        build_param: Optional[List[str]],
    ):
        if project.flavors is None:
            project.flavors = []
        if not flavor in project.flavors:
            project.flavors.append(flavor)

        if not build_param is None and len(build_param) > 0:
            project.obtain_platform_cofig(platform).obtain_config_by_flavor(flavor).build_param = build_param
