from typing import List

from ...core.utils import _Ensure
from ...model.build import BuildType
from ...model.platform import MergePlatformConfigFlavored, Platform
from ...model.project import Project
from ...model.task import *
from ..flutter.build.config import FlutterBuildConfig
from ..project.read import ProjectRead
from ._const import FIREBASE_PROJECT_APP_ID_KEY


class FirebaseBuildValidate(Task):
    identity = TaskIdentity(
        "-firebase-build-validate",
        "Checking if project is able to upload to firebase",
        [],
        lambda: FirebaseBuildValidate(),
    )

    ARG_FIREBASE_GOOGLE_ID = "FIREBASE_CONFIG_GOOGLE_ID"

    def require(self) -> List[TaskId]:
        return [ProjectRead.identity.id, FlutterBuildConfig.identity.id]

    def execute(self, args: Args) -> TaskResult:
        flavor = args.get_value(FlutterBuildConfig.ARG_FLAVOR)
        build_type = BuildType.from_flutter(
            _Ensure.instance(
                args.get_value(FlutterBuildConfig.ARG_BUILD_TYPE), str, "build-type"
            )
        )
        project = Project.current
        config = MergePlatformConfigFlavored(
            project.get_platform_config(Platform.DEFAULT),
            project.get_platform_config(build_type.platform),
        )
        id = config.get_extra(flavor, FIREBASE_PROJECT_APP_ID_KEY.value)
        if id is None or len(id) <= 0:
            return TaskResult(
                args,
                error=ValueError("App id not found in aflutter.json"),
                success=False,
            )

        args.add_arg(FirebaseBuildValidate.ARG_FIREBASE_GOOGLE_ID, id)
        return TaskResult(args)
