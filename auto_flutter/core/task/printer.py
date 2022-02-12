from __future__ import annotations

from operator import itemgetter
from queue import Queue
from sys import stdout as sys_stdout
from threading import Lock, Thread
from time import sleep, time
from typing import Optional, Tuple

from ...model.error import SilentWarning
from ...model.task import Task
from ..session import Session
from ..string import SB


class TaskPrinter:
    __COUNTER = "⡀⡄⡆⡇⡏⡟⡿⣿⢿⢻⢹⢸⢰⢠⢀"
    __COUNTER_LEN = len(__COUNTER)

    class _Operation(Tuple[Optional[str], Optional[Task.Result], Optional[str]]):
        def __new__(
            cls: type[TaskPrinter._Operation],
            message: Optional[str] = None,
            result: Optional[Task.Result] = None,
            description: Optional[str] = None,
        ) -> TaskPrinter._Operation:
            return super().__new__(
                TaskPrinter._Operation, (message, result, description)
            )

        message: Optional[str] = property(itemgetter(0))
        result: Optional[Task.Result] = property(itemgetter(1))
        description: Optional[str] = property(itemgetter(2))

    def __init__(self) -> None:
        self.__thread = Thread(target=TaskPrinter.__run, args=[self])
        self.messages: Queue[TaskPrinter._Operation] = Queue()
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
        self.messages.put(TaskPrinter._Operation(result=result))

    def set_task_description(self, description: str):
        self.messages.put(TaskPrinter._Operation(description=description))

    def write(self, message: str):
        self.messages.put(TaskPrinter._Operation(message=message))

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

                                elif isinstance(message.result.error, SilentWarning):
                                    TaskPrinter.__print_description(
                                        current_task, warning=True
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
                                            Session.format_exception(
                                                message.result.error
                                            ),
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
                                            Session.format_exception(
                                                message.result.error
                                            ),
                                            SB.Color.RED,
                                        )
                                        .str()
                                    )
                        if not message.result.message is None:
                            print(message.result.message)

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
