from asyncio import tasks
from pathlib import Path
from typing import Optional

from ....core.string_builder import SB
from ....core.task.manager import TaskManager
from ....model.project import Project
from ....model.task import Task
from .find_platform import FindPlatform


class ProjectInit(Task):
    identity = Task.Identity(
        "init",
        "Initialize Auto-Flutter project",
        [
            Task.Option("n", "name", "Project name", True),
            Task.Option(None, "force", "Overwrite existent project", False),
        ],
        lambda: ProjectInit(),
    )

    def describe(self, args: Task.Args) -> str:
        return "Initializing project"

    def execute(self, args: Task.Args) -> Task.Result:
        if not Path("pubspec.yaml").exists():
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
        if not "name" in args or len(args["name"].value) <= 0:
            return Task.Result(args, error=Exception("Project name not informed"))

        Project.current = Project(
            name=args["name"].value,
            platforms=[],
            flavors=None,
            build_config={},
            tasks=None,
        )

        manager = TaskManager.instance()
        manager.add(FindPlatform())

        return Task.Result(args, error=overwrite, success=True)
