from pathlib import Path
from typing import Final, Optional

from ....core.string import SB
from ....core.task.manager import TaskManager
from ....model.project import Project
from ....model.task import Task
from ..save import ProjectSave
from .common_config import CommonConfig
from .find_flavor import FindFlavor
from .find_platform import FindPlatform


class ProjectInit(Task):
    identity = Task.Identity(
        "init",
        "Initialize Auto-Flutter project",
        [
            Task.Option("n", "name", "Project name", True),
            Task.Option(None, "force", "Overwrite existent project", False),
            FindFlavor.option_skip_idea,
            FindFlavor.option_skip_android,
            FindFlavor.option_skip_ios,
        ],
        lambda: ProjectInit(),
    )

    def describe(self, args: Task.Args) -> str:
        return "Initializing project"

    def execute(self, args: Task.Args) -> Task.Result:
        pubspec: Final = Path("pubspec.yaml")
        if not pubspec.exists():
            return Task.Result(
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
                return Task.Result(
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
        if "name" in args and len(args["name"].value) > 0:
            name = args["name"].value
        elif name is None:
            return Task.Result(args, error=Exception("Project name not informed"))

        Project.current = Project(
            name=name,
            platforms=[],
            flavors=None,
            platform_config={},
            tasks=None,
        )

        # Remember, TaskManager is stack
        manager = TaskManager.instance()
        manager.add(ProjectSave())
        manager.add(CommonConfig())
        manager.add(FindFlavor())
        manager.add(FindPlatform())

        return Task.Result(args, error=overwrite, success=True)

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
