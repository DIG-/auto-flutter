from ......model.error import E, SilentWarning
from ......model.task import *
from ......model.task.init.project_identity import InitProjectTaskIdentity
from ....identity import AflutterTaskIdentity

__all__ = ["ProjectInitGitIgnoreTask"]


class _ProjectInitGistIgnoreTaskIdentity(AflutterTaskIdentity, InitProjectTaskIdentity):
    ...


class ProjectInitGitIgnoreTask(Task):
    identity = _ProjectInitGistIgnoreTaskIdentity(
        "-project-init-git-ignore",
        "",
        [],
        lambda: ProjectInitGitIgnoreTask(),  # pylint: disable=unnecessary-lambda
    )

    def describe(self, args: Args) -> str:
        return "Configure .gitignore"

    def execute(self, args: Args) -> TaskResult:
        try:
            with open(".gitignore", "r+", encoding="utf-8") as file:
                found = False
                for line in file:
                    if not isinstance(line, str):
                        continue
                    line = line.strip("\n")
                    if line == "*.log" or line.startswith(("*.log ", "*.log#")):
                        found = True
                        break
                    if line == "aflutter.log" or line.startswith(("aflutter.log ", "aflutter.log#")):
                        found = True
                        break

                if found:
                    return TaskResult(args)

                file.writelines(("aflutter.log"))

        except BaseException as error:
            return TaskResult(
                args,
                error=E(SilentWarning(".gitignore can not be open")).caused_by(error),
                success=True,
            )

        return TaskResult(args)
