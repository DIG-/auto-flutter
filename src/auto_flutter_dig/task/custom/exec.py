from ...model.project.custom_task import CustomTask, CustomTaskType
from ...model.task import *
from ..flutter._const import FLUTTER_DISABLE_VERSION_CHECK
from ..flutter.exec import Flutter


class CustomTaskExec(Flutter):
    def __init__(self, identity: TaskIdentity, custom: CustomTask) -> None:
        if custom.type != CustomTaskType.EXEC:
            raise TypeError("Require CustomTask EXEC, but found " + str(custom.type))
        if custom.content is None:
            raise ValueError("CustomTask EXEC require content")
        self._custom: CustomTask = custom
        self._content = custom.content
        command = [custom.content.command]
        if not custom.content.args is None:
            command.extend(custom.content.args)
        command.append(FLUTTER_DISABLE_VERSION_CHECK)
        super().__init__(True, command, False, custom.content.output, False, False)
        self.identity = identity

    def require(self) -> List[TaskId]:
        parent = super().require()
        if not self._custom.require is None:
            parent.extend(self._custom.require)
        return parent

    def execute(self, args: Args) -> TaskResult:
        result = super().execute(args)
        if self._content.skip_failure:
            result.success = True
        return result
