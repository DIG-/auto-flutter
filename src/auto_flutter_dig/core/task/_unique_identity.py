from ...model.task import Task, TaskIdentity

__all__ = ["_TaskUniqueIdentity"]


class _TaskUniqueIdentity(TaskIdentity):
    def __init__(self, task: Task) -> None:
        super().__init__("-#-#-", "-#-#-", "", [], lambda: task, True)
        self.__task = task

    def __repr__(self) -> str:
        return "{cls}(group={group}, id={id}, name={name}, options={options}, creator={creator}, allow_more={allow_more})".format(
            cls=type(self).__name__,
            group=self.group,
            id=self.id,
            name=self.name,
            options=self.options,
            creator=self.__task,
            allow_more=self.allow_more,
        )
