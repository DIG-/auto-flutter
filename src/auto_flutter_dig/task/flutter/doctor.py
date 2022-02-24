from ...model.argument.option import OptionAll
from ...model.task import *
from ...task.identity import FlutterTaskIdentity
from .exec import Flutter

FlutterDoctor = FlutterTaskIdentity(
    "doctor",
    "Run flutter doctor",
    [OptionAll()],
    lambda: Flutter(project=False, command=["doctor"], command_append_args=True),
)
