from pathlib import Path, PurePosixPath
from re import compile as re_compile

from ........core.os import PathConverter
from ........model.error.silent_warning import SilentWarning
from ........model.platform import Platform
from ........model.project import Project
from ........model.result import Result
from ........model.task import *
from .base import BaseProjectInitFindFlavorIdentity, BaseProjectInitFindFlavorTask


class ProjectInitFindFlavorAndroidGradleTask(BaseProjectInitFindFlavorTask):
    identity = BaseProjectInitFindFlavorIdentity(
        "-project-init-find-flavor-1-android-gradle",
        "",
        [],
        lambda: ProjectInitFindFlavorAndroidGradleTask(),  # pylint: disable=unnecessary-lambda
    )

    def describe(self, args: Args) -> str:
        return "Detect flavor config via Android gradle"

    def execute(self, args: Args) -> TaskResult:
        project = Project.current
        if not Platform.ANDROID in project.platforms:
            self._uptade_description("")
            return TaskResult(args, E(SilentWarning("Project does not support android platform")).error, success=True)

        gradle = Path(PathConverter.from_posix(PurePosixPath("android/app/build.gradle")).to_machine())
        if not gradle.exists():
            self._uptade_description("", Result(E(FileNotFoundError("Can not found android app gradle file")).error))
            return TaskResult(args)
        found = False
        try:
            file = open(gradle, "r", encoding="utf-8")
            content = "".join(file.readlines())
            file.close()
            try:
                start = content.index("productFlavors")
                start = content.index("{", start)
            except BaseException as error:
                raise LookupError("Failed to find flavor section in build.gradle.") from error
            end = 0
            count = 0
            for i in range(start, len(content)):
                if content[i] == "{":
                    count += 1
                elif content[i] == "}":
                    count -= 1
                    if count <= 0:
                        end = i
                        break
            if end < start:
                raise LookupError("Failed to find flavor section in build.gradle.") from E(
                    IndexError("End of string is before start")
                ).error
            flavors = content[start + 1 : end]
            count = 0
            buffer = ""
            space = re_compile(r"\s")
            for i, char in enumerate(flavors):
                if not space.match(char) is None:
                    continue
                if char == "{":
                    count += 1
                    if count == 1:
                        found = True
                        self._append_flavor(project, Platform.ANDROID, buffer, None)
                        buffer = ""
                    continue
                if char == "}":
                    count -= 1
                elif count == 0:
                    buffer += char
        except BaseException as error:
            self._uptade_description("", Result(E(LookupError("Failed to find flavor")).caused_by(error)))
            return TaskResult(args)

        if not found:
            return TaskResult(args, error=E(LookupError("No flavor was found")).error, success=True)
        return TaskResult(args)
