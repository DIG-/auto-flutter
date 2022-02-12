from traceback import TracebackException

from auto_flutter.core.session import Session
from auto_flutter.core.task import manager
from auto_flutter.model.error import TaskNotFound


def _main():
    import sys
    from platform import system as platform_system

    from .core.logger import log
    from .core.string import SB
    from .core.task import TaskManager
    from .model.config import Config
    from .task._list import task_list
    from .task.help_stub import HelpStub

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
                from codecs import getreader, getwriter

                sys.stdout = getwriter("utf-8")(sys.stdout.detach())
                sys.stderr = getwriter("utf-8")(sys.stderr.detach())
                sys.stdin = getreader("utf-8")(sys.stdin.detach())
        else:
            from colorama import init

            init()

    manager = TaskManager

    if len(sys.argv) <= 1:
        message = (
            SB().append("Auto-Flutter requires at least one task", SB.Color.RED).str()
        )
        manager.add(HelpStub(message=message))
        manager.execute()
        exit(1)

    log.debug("Loading config")
    if not Config.load():
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
    has_error = False
    was_handled = False
    if taskname.startswith("-"):
        was_handled = True
        if not taskname in ("-h", "--help"):
            has_error = True
            manager.add(HelpStub(taskname))
        else:
            manager.add(HelpStub())

    try:
        if not was_handled:
            manager.add_id(taskname)
    except TaskNotFound as error:
        manager.add(HelpStub(error.task_id))
    except BaseException as error:
        print(
            SB()
            .append("Error while creating task tree\n\n", SB.Color.RED)
            .append(
                "".join(TracebackException.from_exception(error).format()),
                SB.Color.RED,
                True,
            )
            .str()
        )
        exit(5)

    try:
        has_error = manager.execute() or has_error
    except BaseException as error:
        print(
            SB()
            .append("Unhandled error caught\n\n", SB.Color.RED)
            .append(Session.format_exception(error), SB.Color.RED, True)
            .str()
        )
        exit(6)

    exit(0 if not has_error else 3)
