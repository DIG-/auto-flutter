class SilentWarning(Warning):
    ...


class TaskNotFound(LookupError):
    def __init__(self, task_id: str, *args: object) -> None:
        super().__init__(*args)
        self.task_id: str = task_id
