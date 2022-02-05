from __future__ import annotations

from operator import itemgetter
from queue import Queue
from sys import stdout as sys_stdout
from threading import Lock, Thread
from time import sleep, time
from traceback import TracebackException
from typing import Optional, Tuple

from ...model.task import Task
from ..session import Session
from ..string_builder import SB


class TaskPrinterOperation(Tuple[Optional[str], Optional[Task.Result], Optional[str]]):
    def __new__(
        cls: type[TaskPrinterOperation],
        message: Optional[str] = None,
        result: Optional[Task.Result] = None,
        description: Optional[str] = None,
    ) -> TaskPrinterOperation:
        return super().__new__(TaskPrinterOperation, (message, result, description))

    message: Optional[str] = property(itemgetter(0))
    result: Optional[Task.Result] = property(itemgetter(1))
    description: Optional[str] = property(itemgetter(2))


class TaskPrinter:
    __COUNTER = "⡀⡄⡆⡇⡏⡟⡿⣿⢿⢻⢹⢸⢰⢠⢀"
    __COUNTER_LEN = len(__COUNTER)

    def __init__(self) -> None:
        self.__thread = Thread(target=TaskPrinter.__run, args=[self])
        self.messages: Queue[TaskPrinterOperation] = Queue()
        self.__stop_mutex = Lock()
        self.__stop = False

    def start(self):
        self.__thread.start()

    def stop(self):
        self.__stop_mutex.acquire()
        self.__stop = True
        self.__stop_mutex.release()
        self.__thread.join()

    def set_result(self, result: Task.Result):
        self.messages.put(TaskPrinterOperation(result=result))

    def set_task_description(self, description: str):
        self.messages.put(TaskPrinterOperation(description=description))

    def write(self, message: str):
        self.messages.put(TaskPrinterOperation(message=message))

    def __run(self):
        current_task: str = ""
        while True:
            self.__stop_mutex.acquire()
            if self.__stop:
                self.__stop_mutex.release()
                if self.messages.empty():
                    break
            else:
                self.__stop_mutex.release()

            if not self.messages.empty():
                while not self.messages.empty():
                    message = self.messages.get()
                    if not message.result is None:
                        if current_task != "":
                            if message.result.success:
                                if message.result.error is None:
                                    TaskPrinter.__print_description(
                                        current_task, success=True
                                    )
                                    current_task = ""
                                    print("")
                                else:
                                    TaskPrinter.__print_description(
                                        current_task, warning=True
                                    )
                                    current_task = ""
                                    print(
                                        SB()
                                        .append("\n")
                                        .append(
                                            self.__format_error(message.result.error),
                                            SB.Color.YELLOW,
                                        )
                                        .str()
                                    )
                            else:
                                TaskPrinter.__print_description(
                                    current_task, failure=True
                                )
                                if message.result.error is None:
                                    print("")
                                else:
                                    print(
                                        SB()
                                        .append("\n")
                                        .append(
                                            self.__format_error(message.result.error),
                                            SB.Color.RED,
                                        )
                                        .str()
                                    )
                        if not message.result.message is None:
                            print(message.result.message, end="")

                    elif not message.description is None:
                        current_task = message.description
                        TaskPrinter.__print_description(current_task)

                    elif not message.message is None:
                        TaskPrinter.__clear_line(current_task)
                        print(message.message)
                        TaskPrinter.__print_description(current_task)
            else:
                TaskPrinter.__print_description(current_task)
                sleep(0.008)

    def __clear_line(description: str):
        print("\r" + (" " * (len(description) + 8)), end="\r")

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

    def __format_error(self, error: BaseException) -> str:
        if not Session.show_stacktrace:
            return str(error)
        return "".join(TracebackException.from_exception(error).format())