from ...model.argument import OptionAll
from ...model.task import Task
from . import Flutter

FlutterDoctor = Task.Identity(
    "doctor",
    "Run flutter doctor",
    [OptionAll()],
    lambda: Flutter(project=False, command=["doctor"], command_append_args=True),
)
