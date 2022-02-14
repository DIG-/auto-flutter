from ...model.project.custom_task import CustomTask
from ...model.task import *
from ..flutter._const import FLUTTER_DISABLE_VERSION_CHECK
from ..flutter.exec import Flutter


class CustomTaskExec(Flutter):
    def __init__(self, identity: TaskIdentity, custom: CustomTask) -> None:
        if custom.type != CustomTask.Type.EXEC:
            raise TypeError("Require CustomTask EXEC, but found " + str(custom.type))
        if custom.content is None:
            raise ValueError("CustomTask EXEC require content")
        self._custom: CustomTask = custom
        command = [custom.content.command]
        if not custom.content.args is None:
            command.extend(custom.content.args)
        command.append(FLUTTER_DISABLE_VERSION_CHECK)
        super().__init__(True, command, False, custom.content.output, False, False)
        self.identity = identity

    def require(self) -> List[TaskId]:
        if not self._custom.require is None:
            return super().require().extend(self._custom.require)
        return super().require()

    def execute(self, args: Args) -> TaskResult:
        result = super().execute(args)
        if self._custom.content.skip_failure:
            result.success = True
        return result
