from pathlib import Path, PurePosixPath
from typing import List

from ...core.os import OS
from ...core.process import Process
from ...model.config import Config
from ...model.task import *
from ..flutter.build.stub import FlutterBuildStub
from ._const import FIREBASE_DISABLE_INTERACTIVE_MODE, FIREBASE_ENV
from .check import FirebaseCheck
from .validate import FirebaseBuildValidate


class FirebaseBuildUpload(Task):
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

    def execute(self, args: Args) -> TaskResult:
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

        p = Process.create(
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
        output = p.try_run()
        if isinstance(output, BaseException):
            return TaskResult(args, error=output)

        return TaskResult(args, success=output)
