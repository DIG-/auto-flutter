from ...model.task.identity import *

GROUP_AFLUTTER = "aflutter"


class AflutterTaskIdentity(TaskIdentity):
    def __init__(
        self,
        id: TaskId,
        name: str,
        options: List[Option],
        creator: Callable[[], "Task"],  # type: ignore[name-defined]
        allow_more: bool = False,
    ) -> None:
        super().__init__(GROUP_AFLUTTER, id, name, options, creator, allow_more)
