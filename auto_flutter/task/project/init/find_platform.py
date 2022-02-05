from pathlib import Path, PurePosixPath

from ....core.os import OS
from ....core.string_builder import SB
from ....core.utils import _Iterable
from ....model.project import Project
from ....model.task import Task


class FindPlatform(Task):
    def describe(self, args: Task.Args) -> str:
        return "Detecting project platforms"

    def execute(self, args: Task.Args) -> Task.Result:
        project = Project.current

        self.print("    Detecting platform android")
        path = PurePosixPath("android/build.gradle")
        if Path(OS.posix_to_machine_path(path)).exists():
            project.platforms.append(Project.Platform.ANDROID)

        self.print("    Detecting platform ios")
        path = PurePosixPath("ios/Runner.xcodeproj")
        if Path(OS.posix_to_machine_path(path)).exists():
            project.platforms.append(Project.Platform.IOS)

        self.print("    Detecting platform web")
        path = PurePosixPath("web")
        real_path = Path(OS.posix_to_machine_path(path))
        if real_path.exists() and real_path.is_dir():
            if _Iterable.count(real_path.glob("*")) > 2:
                project.platforms.append(Project.Platform.WEB)

        if len(project.platforms) <= 0:
            return Task.Result(
                args,
                error=Warning("No platform was found"),
                message=SB()
                .append("Don't worry, use task ")
                .append("config", SB.Color.CYAN, True)
                .append(" to manually add platform")
                .str(),
                success=True,
            )
        else:
            self.print(
                SB()
                .append("    Found: ", SB.Color.GREEN)
                .append(
                    " ".join(map(lambda x: x.value, project.platforms)),
                    SB.Color.GREEN,
                    True,
                )
                .str()
            )
            return Task.Result(args)
