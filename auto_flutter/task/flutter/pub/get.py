from ....model.task import TaskIdentity
from ....task.flutter.command import FlutterCommand

__all__ = ["FlutterPubGet"]

FlutterPubGet = TaskIdentity(
    "pub-get",
    "Runs flutter pub get",
    [],
    lambda: FlutterCommand(
        command=["pub", "get"], describe="Running pub get", require_project=True
    ),
)
