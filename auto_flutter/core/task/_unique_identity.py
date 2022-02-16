from ...model.task import Task, TaskIdentity

__all__ = ["_TaskUniqueIdentity"]


class _TaskUniqueIdentity(TaskIdentity):
    def __init__(self, task: Task) -> None:
        super().__init__("-#-#-", "", [], lambda: task, True)
