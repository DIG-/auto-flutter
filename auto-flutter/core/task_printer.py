from __future__ import annotations
from operator import itemgetter
from queue import Queue
from threading import Thread, Lock
from time import sleep, time
from typing import Optional, Tuple
from termcolor import colored
from ..core.task import Task


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

            while not self.messages.empty():
                message = self.messages.get()
                if not message.result is None:
                    if message.result.success:
                        if message.result.error is None:
                            TaskPrinter.__print_description(current_task, success=True)
                            current_task = ""
                            print("")
                            continue
                        else:
                            TaskPrinter.__print_description(current_task, warning=True)
                            current_task = ""
                            print("\n" + colored(str(message.result.error), "yellow"))
                            continue
                    else:
                        TaskPrinter.__print_description(current_task, failure=True)
                        if message.result.error is None:
                            print("")
                        else:
                            print("\n" + colored(str(message.result.error), "red"))

                elif not message.description is None:
                    current_task = message.description
                    TaskPrinter.__print_description(current_task)
                    continue

                elif not message.message is None:
                    TaskPrinter.__clear_line(current_task)
                    print(message.message)
                    TaskPrinter.__print_description(current_task)
                    continue

            TaskPrinter.__print_description(current_task)
            sleep(0.1)

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
        icon: str
        if success:
            icon = "✔️"
        elif failure:
            icon = "❌"
        elif warning:
            icon = "⚠️"
        else:
            icon = TaskPrinter.__COUNTER[int(time() * 10) % TaskPrinter.__COUNTER_LEN]
        print("\r[" + icon + "] " + description, end="")
