from ...model.task.identity import *

GROUP_FLUTTER = "flutter"


class FlutterTaskIdentity(TaskIdentity):
    def __init__(
        self,
        id: TaskId,
        name: str,
        options: List[Option],
        creator: Callable[[], "Task"],  # type: ignore[name-defined]
        allow_more: bool = False,
    ) -> None:
        super().__init__(GROUP_FLUTTER, id, name, options, creator, allow_more)
