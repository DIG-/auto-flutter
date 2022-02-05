import sys
from platform import system as platform_system
from .core.logger import log
from .model.config import Config
from .task._list import task_list
from .core.task import TaskManager
from .core.string_builder import SB


def main():
    # Enable color support on windows
    if platform_system() == "Windows":
        is_cp1252 = sys.stdout.encoding == "cp1252"
        # Bash from GIT does not use UTF-8 as default and colorama has conflit with them
        if is_cp1252:
            try:
                sys.stdout.reconfigure(encoding="utf-8")
                sys.stderr.reconfigure(encoding="utf-8")
                sys.stdin.reconfigure(encoding="utf-8")
            except AttributeError:
                from codecs import getwriter, getreader

                sys.stdout = getwriter("utf-8")(sys.stdout.detach())
                sys.stderr = getwriter("utf-8")(sys.stderr.detach())
                sys.stdin = getreader("utf-8")(sys.stdin.detach())
        else:
            from colorama import init

            init()

    manager = TaskManager.instance()

    if len(sys.argv) <= 1:
        print(
            SB().append("Auto-Flutter requires at least one task\n", SB.Color.RED).str()
        )
        manager.add_id("help")
        manager.execute()
        exit(1)

    log.debug("Loading config")
    if not Config.instance().load():
        print(
            SB()
            .append("Failed to read config. ", SB.Color.RED)
            .append("Using default values.", SB.Color.YELLOW)
            .str()
        )
        print(
            SB()
            .append("Use task ", end="")
            .append("setup", SB.Color.CYAN, True)
            .append(" to configure you environment\n")
            .str()
        )

    taskname = sys.argv[1]
    if taskname.startswith("-"):
        print(
            SB()
            .append("Unknown task ", SB.Color.RED)
            .append(taskname, SB.Color.CYAN, True, "\n")
            .str()
        )
        manager.add_id("help")
        manager.execute()
        exit(3)

    if taskname in task_list:
        manager.add(task_list[taskname].creator())
        if manager.execute():
            exit(0)
        else:
            exit(1)

    # TODO: Call read project task
    # TODO: Check if project constains that task
    # TODO: Call task

    print(
        SB()
        .append("No task found with name ", SB.Color.RED)
        .append(taskname, SB.Color.CYAN, True, "\n")
        .str()
    )
    manager.add_id("help")
    manager.execute()
