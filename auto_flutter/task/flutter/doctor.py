from ...model.argument import OptionAll
from ...model.task import *
from .exec import Flutter

FlutterDoctor = TaskIdentity(
    "doctor",
    "Run flutter doctor",
    [OptionAll()],
    lambda: Flutter(project=False, command=["doctor"], command_append_args=True),
)
