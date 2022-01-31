from ..core.arguments import Option, Args
from ..core.task import Task, TaskIdentity
from ..task._list import task_list
from typing import Dict, List, Optional


class Help(Task):
    identity = TaskIdentity(
        "help",
        "Show help",
        [Option("t", "task", "Show help details about given task", True)],
        lambda: Help(),
    )

    def describe(self, args: Args) -> str:
        return "Showing help page"

    def execute(self, args: Args) -> Optional[Args]:
        self.show_header()
        if "task" in args:
            task_name = args["task"].value
            if not task_name is None:
                if task_name in task_list:
                    self.show_task_options(task_list[task_name])
                    exit(0)
                else:
                    print('Task "{}" not found\n'.format(task_name))
        print("Default tasks:")
        for task in Help.get_default_task_list():
            self.show_task_name(task)
        exit(0)

    def show_header(self):
        print("Usage:\t{} TASK [options]\n")

    def show_task_options(task: TaskIdentity):
        pass

    def show_task_name(task: TaskIdentity):
        print("  {}\t{}".format(task.id, task.name))
        pass

    def get_default_task_list() -> List[TaskIdentity]:
        return Help.reduce_indexed_task_into_list(task_list)

    def reduce_indexed_task_into_list(
        tasks: Dict[str, TaskIdentity]
    ) -> List[TaskIdentity]:
        filtered = filter(lambda it: not it[0].startswith("-"), task_list.items())
        reduced = map(lambda it: it[1], filtered)
        return list(reduced)
