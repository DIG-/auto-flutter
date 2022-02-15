from pathlib import Path, PurePosixPath

from ...core.os import OS
from ...model.config import Config
from ...task.base.process import *
from ...task.firebase._const import FIREBASE_DISABLE_INTERACTIVE_MODE, FIREBASE_ENV
from ...task.firebase.check import FirebaseCheck
from ...task.firebase.validate import FirebaseBuildValidate
from ...task.flutter.build.stub import FlutterBuildStub


class FirebaseBuildUpload(BaseProcessTask):
    identity = TaskIdentity(
        "firebase",
        "Upload build to firebase",
        [],
        lambda: FirebaseBuildUpload(),
    )

    def require(self) -> List[TaskId]:
        return [
            FirebaseBuildValidate.identity.id,
            FirebaseCheck.identity.id,
            FlutterBuildStub.identity.id,
        ]

    def _create_process(self, args: Args) -> ProcessOrResult:
        filename = args.get_value("output")
        if filename is None or len(filename) <= 0:
            return TaskResult(
                args, AssertionError("Previous task does not have output")
            )

        file: Path = Path(OS.posix_to_machine_path(PurePosixPath(filename)))
        if not file.exists():
            return TaskResult(
                args, FileNotFoundError("Output not found: {}".format(str(file)))
            )

        file = file.absolute()
        google_id = args.get_value(FirebaseBuildValidate.ARG_FIREBASE_GOOGLE_ID)
        if google_id is None or len(google_id) <= 0:
            return TaskResult(args, AssertionError("Google app id not found"))

        return Process.create(
            Config.firebase,
            arguments=[
                FIREBASE_DISABLE_INTERACTIVE_MODE.value,
                "appdistribution:distribute",
                str(file),
                "--app",
                google_id,
            ],
            environment=FIREBASE_ENV.value,
            writer=self._print,
        )
