from __future__ import annotations

from queue import Queue
from sys import stdout as sys_stdout
from threading import Lock, Thread
from time import sleep, time
from typing import Optional

from ...model.error import SilentWarning
from ...model.task import TaskResult
from ..session import Session
from ..string import SB


class TaskPrinter:
    __COUNTER = "⡀⡄⡆⡇⡏⡟⡿⣿⢿⢻⢹⢸⢰⢠⢀"
    __COUNTER_LEN = len(__COUNTER)

    class _Operation:
        def __init__(
            self,
            message: Optional[str] = None,
            result: Optional[TaskResult] = None,
            description: Optional[str] = None,
        ) -> None:
            self.message: Optional[str] = message
            self.result: Optional[TaskResult] = result
            self.description: Optional[str] = description

    def __init__(self) -> None:
        self.__thread = Thread(target=TaskPrinter.__run, args=[self])
        self._operations: Queue[TaskPrinter._Operation] = Queue()
        self.__stop_mutex = Lock()
        self.__stop = False
        self._current_task: str = ""

    def start(self):
        self.__thread.start()

    def stop(self):
        self.__stop_mutex.acquire()
        self.__stop = True
        self.__stop_mutex.release()
        self.__thread.join()

    def set_result(self, result: TaskResult):
        self._operations.put(TaskPrinter._Operation(result=result))

    def set_task_description(self, description: str):
        self._operations.put(TaskPrinter._Operation(description=description))

    def write(self, message: str):
        self._operations.put(TaskPrinter._Operation(message=message))

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
                TaskPrinter.__print_description(self._current_task)
                sleep(0.008)

    def __handle_operation(self, operation: _Operation):
        if not operation.result is None:
            self.__handle_operation_result(operation.result)
        elif not operation.description is None:
            self.__handle_operation_description(operation.description)
        elif not operation.message is None:
            self.__handle_operation_message(operation.message)

    def __handle_operation_result(self, result: TaskResult):
        has_task_name = len(self._current_task) > 0
        if not result.success:
            if has_task_name:
                TaskPrinter.__print_description(self._current_task, failure=True)
            if not result.error is None:
                print(
                    SB()
                    .append("\n")
                    .append(
                        Session.format_exception(result.error),
                        SB.Color.RED,
                    )
                    .str()
                )
            elif has_task_name:
                print("")
        else:
            has_warning = not result.error is None or isinstance(
                result.error, SilentWarning
            )
            if has_task_name:
                TaskPrinter.__print_description(
                    self._current_task, success=not has_warning, warning=has_warning
                )
                if not has_warning:
                    print("")
            if has_warning:
                assert not result.error is None
                print(
                    SB()
                    .append("\n")
                    .append(
                        Session.format_exception(result.error),
                        SB.Color.YELLOW,
                    )
                    .str()
                )
        self._current_task = ""
        if not result.message is None:
            print(result.message)

    def __handle_operation_description(self, description: str):
        self._current_task = description
        TaskPrinter.__print_description(self._current_task)

    def __handle_operation_message(self, message: str):
        TaskPrinter.__clear_line(self._current_task)
        print(message)
        TaskPrinter.__print_description(self._current_task)

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
