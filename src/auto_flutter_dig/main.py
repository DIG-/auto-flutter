def _main():
    import sys
    from platform import system as platform_system

    from .core.string import SB
    from .core.task import TaskManager
    from .model.error.formater import format_exception
    from .module.aflutter.task.init import AflutterInitTask

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

    TaskManager.start_printer()
    TaskManager.add(AflutterInitTask())

    try:
        has_error = not TaskManager.execute()
    except BaseException as error:
        has_error = True
        TaskManager.print(
            SB()
            .append("Unhandled error caught\n\n", SB.Color.RED)
            .append(format_exception(error), SB.Color.RED, True)
            .str()
        )

    TaskManager.stop_printer()
    exit(0 if not has_error else 3)
