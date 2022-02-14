from ...project.custom_task.custom_task import CustomTask
from ..task import TaskIdentity


class CustomExecIdentity(TaskIdentity):
    def __init__(self, custom: CustomTask) -> None:
        if custom.type != CustomTask.Type.EXEC:
            raise TypeError("Require CustomTask EXEC, but found " + str(custom.type))
        from ....task.custom.exec import CustomTaskExec

        super().__init__(
            custom.id, custom.name, [], lambda: CustomTaskExec(self, custom)
        )