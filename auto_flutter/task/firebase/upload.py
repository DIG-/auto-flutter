from typing import List

from ...model.task import Task
from ..flutter.build.stub import FlutterBuildStub
from .validate import FirebaseBuildValidate


class FirebaseBuildUpload(Task):
    identity = Task.Identity(
        "firebase",
        "Upload build to firebase",
        [],
        lambda: FirebaseBuildUpload(),
    )

    def require(self) -> List[Task.ID]:
        return [FirebaseBuildValidate.identity.id, FlutterBuildStub.identity.id]

    def execute(self, args: Task.Args) -> Task.Result:
        return Task.Result(args)
