from ..core.arguments import Option, Args
from ..core.task import Task, TaskIdentity
from sys import argv as sys_argv
from typing import Dict, List, Optional


class Help(Task):
    identity = TaskIdentity(
        "help",
        "Show help",
        [Option("t", "task", "Show help details about given task", True)],
        lambda: Help(None),
    )

    def __init__(self, default: Dict[str, TaskIdentity]) -> None:
        super().__init__()
        self._default = default

    def describe(self, args: Args) -> str:
        return "Showing help page"

    def execute(self, args: Args) -> Optional[Args]:
        self.show_header()
        if "task" in args:
            task_name = args["task"].value
            if not task_name is None:
                if task_name in self._default:
                    self.show_task_options(self._default[task_name])
                    exit(0)
                else:
                    print('Task "{}" not found\n'.format(task_name))
        print("Default tasks:")
        for task in Help.reduce_indexed_task_into_list(self._default):
            self.show_task_name(task)
        exit(0)

    def show_header(self):
        print("Usage:\t{} TASK [options]\n".format(sys_argv[0]))

    def show_task_options(self, task: TaskIdentity):
        pass

    def show_task_name(self, task: TaskIdentity):
        print("  {}\t{}".format(task.id, task.name))

    def reduce_indexed_task_into_list(
        tasks: Dict[str, TaskIdentity]
    ) -> List[TaskIdentity]:
        filtered = filter(lambda it: not it[0].startswith("-"), tasks.items())
        reduced = map(lambda it: it[1], filtered)
        return list(reduced)
