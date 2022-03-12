from pathlib import Path, PurePosixPath

from .......core.os import OS
from .......core.string import SB
from .......core.utils import _Iterable
from .......model.error import SilentWarning
from .......model.platform import Platform
from .......model.project import Project
from .......model.result import Result
from .......model.task import *
from .......model.task.init.project_identity import InitProjectTaskIdentity
from .....identity import AflutterTaskIdentity
from ..create import ProjectInitCreateTask


class _Identity(AflutterTaskIdentity, InitProjectTaskIdentity):
    @property
    def require_before(self) -> List[TaskIdentity]:
        return [ProjectInitCreateTask.identity]


class ProjectInitFindPlatformTask(Task):
    identity = _Identity(
        "-project-init-find-platform",
        "",
        [],
        lambda: ProjectInitFindPlatformTask(),  # pylint: disable=unnecessary-lambda
    )

    def describe(self, args: Args) -> str:
        return "Detecting project platforms"

    def execute(self, args: Args) -> TaskResult:
        project = Project.current

        self._uptade_description("Detecting platform android")
        path = PurePosixPath("android/build.gradle")
        if Path(OS.posix_to_machine_path(path)).exists():
            project.platforms.append(Platform.ANDROID)
            self._reset_description(args, Result(success=True))
        else:
            self._reset_description(args, Result(error=SilentWarning()))

        self._uptade_description("Detecting platform ios")
        path = PurePosixPath("ios/Runner.xcodeproj")
        if Path(OS.posix_to_machine_path(path)).exists():
            project.platforms.append(Platform.IOS)
            self._reset_description(args, Result(success=True))
        else:
            self._reset_description(args, Result(error=SilentWarning()))

        self._uptade_description("Detecting platform web")
        path = PurePosixPath("web")
        real_path = Path(OS.posix_to_machine_path(path))
        if real_path.exists() and real_path.is_dir():
            if _Iterable.count(real_path.glob("*")) > 2:
                project.platforms.append(Platform.WEB)
                self._reset_description(args, Result(success=True))
            else:
                self._reset_description(args, Result(error=SilentWarning()))
        else:
            self._reset_description(args, Result(error=SilentWarning()))

        if len(project.platforms) <= 0:
            return TaskResult(
                args,
                error=Warning("No platform was found"),
                message=SB()
                .append("Don't worry, use task ")
                .append("config", SB.Color.CYAN, True)
                .append(" to manually add platform")
                .str(),
                success=True,
            )
        return TaskResult(
            args,
            message=SB()
            .append("  Found: ", SB.Color.GREEN)
            .append(
                " ".join(map(lambda x: x.value, project.platforms)),
                SB.Color.GREEN,
                True,
            )
            .str(),
        )
