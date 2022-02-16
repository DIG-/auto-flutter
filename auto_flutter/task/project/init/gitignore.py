from ....model.error import E, SilentWarning
from ....model.task import *


class InitGitIgnore(Task):
    def describe(self, args: Args) -> str:
        return "Configure .gitignore"

    def execute(self, args: Args) -> TaskResult:
        try:
            file = open(".gitignore", "r+")
        except BaseException as e:
            return TaskResult(
                args,
                error=E(SilentWarning(".gitignore can not be open")).caused_by(e),
                success=True,
            )
        found = False
        for line in file:
            if not isinstance(line, str):
                continue
            line = line.strip("\n")
            if line == "*.log" or line.startswith(("*.log ", "*.log#")):
                found = True
                break
            if line == "aflutter.log" or line.startswith(
                ("aflutter.log ", "aflutter.log#")
            ):
                found = True
                break
            pass

        if found:
            file.close()
            return TaskResult(args)

        try:
            file.writelines(("aflutter.log"))
        except BaseException as e:
            file.close()
            return TaskResult(
                args,
                error=E(
                    SilentWarning("Failed to insert aflutter.log in .gitignore")
                ).caused_by(e),
                success=True,
            )
        file.close()
        return TaskResult(args)
