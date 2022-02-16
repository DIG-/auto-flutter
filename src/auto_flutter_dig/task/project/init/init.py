from pathlib import Path
from typing import List, Optional

from ....core.string import SB
from ....model.project import Project
from ....model.task import *
from ...options import ParseOptions
from ..save import ProjectSave
from .common_config import CommonConfig
from .find_flavor import FindFlavor
from .find_platform import FindPlatform
from .gitignore import InitGitIgnore


class ProjectInit(Task):
    identity = TaskIdentity(
        "init",
        "Initialize Auto-Flutter project",
        [
            Option("n", "name", "Project name", True),
            Option(None, "force", "Overwrite existent project", False),
            FindFlavor.option_skip_idea,
            FindFlavor.option_skip_android,
            FindFlavor.option_skip_ios,
        ],
        lambda: ProjectInit(),
    )

    def require(self) -> List[TaskId]:
        return [ParseOptions.identity.id]

    def describe(self, args: Args) -> str:
        return "Initializing project"

    def execute(self, args: Args) -> TaskResult:
        pubspec = Path("pubspec.yaml")
        if not pubspec.exists():
            return TaskResult(
                args,
                error=FileNotFoundError("File pubspec.yaml not found"),
                message="Make sure to run this command on flutter project root",
                success=False,
            )
        overwrite: Optional[Warning] = None
        if Path("aflutter.json").exists():
            if "force" in args:
                overwrite = Warning("Current project will be overwritten")
            else:
                return TaskResult(
                    args,
                    error=Exception("Auto-Flutter project already initialized"),
                    message=SB()
                    .append("Use task ")
                    .append("config", SB.Color.CYAN, True)
                    .append(" to configure project.\n")
                    .append("Or retry with ")
                    .append("--force", SB.Color.MAGENTA)
                    .append(" option, to overwrite current project.")
                    .str(),
                    success=False,
                )
        name = ProjectInit._project_name_from_pubspec(pubspec)
        name_arg = args.get_value("name")
        if not name_arg is None and len(name_arg) > 0:
            name = name_arg
        elif name is None:
            return TaskResult(args, error=Exception("Project name not informed"))

        Project.current = Project(
            name=name,
            platforms=[],
            flavors=None,
            platform_config={},
            tasks=None,
        )

        # Remember, TaskManager is stack
        self._append_task(
            [
                ProjectSave(),
                InitGitIgnore(),
                CommonConfig(),
                FindFlavor(),
                FindPlatform(),
            ]
        )

        return TaskResult(args, error=overwrite, success=True)

    @staticmethod
    def _project_name_from_pubspec(pubspec: Path) -> Optional[str]:
        try:
            from yaml import safe_load as yaml_load  # type: ignore
        except ImportError as e:
            return None
        try:
            file = open(pubspec, "r")
            content = yaml_load(file)
            file.close()
            name = content["name"]
            if isinstance(name, str):
                return name
        except BaseException as e:
            pass
        return None
