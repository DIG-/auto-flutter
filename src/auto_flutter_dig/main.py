from traceback import TracebackException


def _main():
    import sys
    from platform import system as platform_system

    from .core.config import Config
    from .core.logger import log
    from .core.string import SB
    from .core.task import TaskManager
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
            from colorama import init  # type: ignore[import]

            init()

    manager = TaskManager
    TaskManager.start_printer()

    if len(sys.argv) <= 1:
        message = (
            SB().append("Auto-Flutter requires at least one task", SB.Color.RED).str()
        )
        manager.add(HelpStub(message=message))
        manager.execute()
        TaskManager.stop_printer()
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

    if not was_handled:
        has_error = __add_task(taskname, False)

    has_error = __exec_task(has_error)
    TaskManager.stop_printer()
    exit(0 if not has_error else 3)


## Return true with error
def __add_task(taskname: str, already_not_found: bool = False) -> bool:
    from .core.string import SB
    from .core.task import TaskManager
    from .model.error import TaskNotFound
    from .task.help_stub import HelpStub

    try:
        TaskManager.add_id(taskname)
    except TaskNotFound as error:
        if already_not_found:
            TaskManager.add(HelpStub(error.task_id))
        else:
            TaskManager.add_id("-project-read")
            has_error = __exec_task(False)
            if has_error:
                return True
            else:
                return __add_task(taskname, True)
    except BaseException as error:
        TaskManager.print(
            SB()
            .append("Error while creating task tree\n\n", SB.Color.RED)
            .append(
                "".join(TracebackException.from_exception(error).format()),
                SB.Color.RED,
                True,
            )
            .str()
        )
        TaskManager.stop_printer()
        exit(5)
    return False


def __exec_task(has_error: bool) -> bool:
    from .core.session import Session
    from .core.string import SB
    from .core.task import TaskManager

    try:
        has_error = (not TaskManager.execute()) or has_error
    except BaseException as error:
        TaskManager.print(
            SB()
            .append("Unhandled error caught\n\n", SB.Color.RED)
            .append(Session.format_exception(error), SB.Color.RED, True)
            .str()
        )
        TaskManager.stop_printer()
        exit(6)
    return has_error
