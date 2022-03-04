from __future__ import annotations

from queue import Queue
from sys import stdout as sys_stdout
from threading import Lock, Thread
from time import sleep, time

from ....core.utils import _Ensure
from ....model.error import SilentWarning
from ....model.error.formater import format_exception
from ....model.task import TaskResult
from ...string import SB
from .operation import *


class TaskPrinter:
    __COUNTER = "⡀⡄⡆⡇⡏⡟⡿⣿⢿⢻⢹⢸⢰⢠⢀"
    __COUNTER_LEN = len(__COUNTER)

    def __init__(self) -> None:
        self.__thread = Thread(target=TaskPrinter.__run, args=[self])
        self._operations: Queue[Operation] = Queue()
        self.__stop_mutex = Lock()
        self.__stop = False
        self._current_description: str = ""

    def start(self):
        self.__thread.start()

    def stop(self):
        self.__stop_mutex.acquire()
        self.__stop = True
        self.__stop_mutex.release()
        self.__thread.join()

    def append(self, operation: Operation):
        self._operations.put(_Ensure.instance(operation, Operation, "operation"))
        pass

    def __run(self):
        while True:
            self.__stop_mutex.acquire()
            if self.__stop:
                self.__stop_mutex.release()
                if self._operations.empty():
                    break
            else:
                self.__stop_mutex.release()

            if not self._operations.empty():
                while not self._operations.empty():
                    self.__handle_operation(self._operations.get())

            else:
                TaskPrinter.__print_description(self._current_description)
                sleep(0.008)

    def __handle_operation(self, op: Operation):
        if isinstance(op, OpMessage):
            self.__handle_operation_message(op)
        elif isinstance(op, OpDescription):
            self.__handle_operation_description(op)
        elif isinstance(op, OpResult):
            self.__handle_operation_result(op)
        else:
            print(format_exception(TypeError("Unknown Operation type: {}".format(type(op).__name__))))
            pass

    def __handle_operation_result(self, op: OpResult):
        result = op.result
        has_description = len(self._current_description) > 0
        if not result.success:
            if has_description:
                TaskPrinter.__print_description(self._current_description, failure=True)
            if not result.error is None:
                print(
                    SB()
                    .append("\n")
                    .append(
                        format_exception(result.error),
                        SB.Color.RED,
                    )
                    .str()
                )
            elif has_description:
                print("")
        else:
            has_warning = not result.error is None
            print_warning = not result.error is None and not isinstance(result.error, SilentWarning)
            if has_description:
                TaskPrinter.__print_description(
                    self._current_description,
                    success=not has_warning,
                    warning=has_warning,
                )
                if not print_warning:
                    print("")
            if print_warning:
                assert not result.error is None
                print(
                    SB()
                    .append("\n")
                    .append(
                        format_exception(result.error),
                        SB.Color.YELLOW,
                    )
                    .str()
                )
        self._current_description = ""
        if isinstance(result, TaskResult):
            if not result.message is None:
                print(result.message)

    def __handle_operation_description(self, op: OpDescription):
        self.__clear_line(self._current_description)
        self._current_description = op.description
        TaskPrinter.__print_description(self._current_description)

    def __handle_operation_message(self, op: OpMessage):
        TaskPrinter.__clear_line(self._current_description)
        print(op.message)
        TaskPrinter.__print_description(self._current_description)

    @staticmethod
    def __clear_line(description: str):
        print("\r" + (" " * (len(description) + 8)), end="\r")

    @staticmethod
    def __print_description(
        description: str,
        success: bool = False,
        failure: bool = False,
        warning: bool = False,
    ):
        if description is None or len(description) == 0:
            return
        builder = SB()
        builder.append("\r")
        if success:
            builder.append("[√] ", SB.Color.GREEN, True)
        elif failure:
            builder.append("[X] ", SB.Color.RED, True)
        elif warning:
            builder.append("[!] ", SB.Color.YELLOW, True)
        else:
            icon = TaskPrinter.__COUNTER[int(time() * 10) % TaskPrinter.__COUNTER_LEN]
            builder.append("[" + icon + "] ", SB.Color.DEFAULT, True)

        print(builder.append(description).str(), end="")
        sys_stdout.flush()
