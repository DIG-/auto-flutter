from typing import List

from ....core.utils import _Ensure
from ....model.build import BuildType
from ....model.platform import Platform
from ....model.platform.merge_config import MergePlatformConfigFlavored
from ....model.project import Project
from ....model.task import *
from ....task.flutter.build.config import FlutterBuildConfig
from ....task.project.read import ProjectRead
from ..identity import FirebaseTaskIdentity
from ..model._const import FIREBASE_PROJECT_APP_ID_KEY


class FirebaseBuildValidate(Task):
    identity = FirebaseTaskIdentity(
        "-firebase-build-validate",
        "Checking if project is able to upload to firebase",
        [],
        lambda: FirebaseBuildValidate(),
    )

    ARG_FIREBASE_GOOGLE_ID = "FIREBASE_CONFIG_GOOGLE_ID"

    def require(self) -> List[TaskId]:
        return [ProjectRead.identity.id, FlutterBuildConfig.identity.id]

    def execute(self, args: Args) -> TaskResult:
        flavor = args.group_get("flutter", FlutterBuildConfig.ARG_FLAVOR)
        build_type = BuildType.from_flutter(
            _Ensure.instance(
                args.group_get("flutter", FlutterBuildConfig.ARG_BUILD_TYPE),
                str,
                "build-type",
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
                error=E(ValueError("App id not found in aflutter.json")).error,
                success=False,
            )

        args.add(FirebaseBuildValidate.ARG_FIREBASE_GOOGLE_ID, id)
        return TaskResult(args)
