from typing import List

from ...model.task import Task
from ..flutter.build.config import FlutterBuildConfig
from ..project.read import ProjectRead


class FirebaseBuildValidate(Task):
    identity = Task.Identity(
        "-firebase-build-validate",
        "Checking if project is able to upload to firebase",
        [],
        lambda: FirebaseBuildValidate(),
    )

    def require(self) -> List[Task.ID]:
        return [ProjectRead.identity.id, FlutterBuildConfig.identity.id]

    def execute(self, args: Task.Args) -> Task.Result:
        return Task.Result(args)
