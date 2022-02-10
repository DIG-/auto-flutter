from typing import Final, List

from ...model.platform import BuildType, MergePlatformConfigFlavored
from ...model.project import Project
from ...model.task import Task
from ..flutter.build.config import FlutterBuildConfig
from ..project.read import ProjectRead
from ._const import FIREBASE_PROJECT_APP_ID_KEY


class FirebaseBuildValidate(Task):
    identity = Task.Identity(
        "-firebase-build-validate",
        "Checking if project is able to upload to firebase",
        [],
        lambda: FirebaseBuildValidate(),
    )

    ARG_FIREBASE_GOOGLE_ID: Final = "FIREBASE_CONFIG_GOOGLE_ID"

    def require(self) -> List[Task.ID]:
        return [ProjectRead.identity.id, FlutterBuildConfig.identity.id]

    def execute(self, args: Task.Args) -> Task.Result:
        flavor: Final = args.get_value(FlutterBuildConfig.ARG_FLAVOR)
        build_type: Final = BuildType.from_flutter(
            args.get_value(FlutterBuildConfig.ARG_BUILD_TYPE)
        )
        project: Final = Project.current
        config = MergePlatformConfigFlavored(
            project.get_platform_config(Project.Platform.DEFAULT),
            project.get_platform_config(build_type.platform),
        )
        id = config.get_extra(flavor, FIREBASE_PROJECT_APP_ID_KEY.value)
        if id is None or len(id) <= 0:
            return Task.Result(
                args,
                error=ValueError("App id not found in aflutter.json"),
                success=False,
            )

        args.add_arg(FirebaseBuildValidate.ARG_FIREBASE_GOOGLE_ID, id)
        return Task.Result(args)
