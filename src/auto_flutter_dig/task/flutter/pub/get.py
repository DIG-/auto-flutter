from ....module.flutter.task.command import FlutterCommandTask
from ....task.identity import FlutterTaskIdentity

__all__ = ["FlutterPubGet"]

FlutterPubGet = FlutterTaskIdentity(
    "pub-get",
    "Runs flutter pub get",
    [],
    lambda: FlutterCommandTask(command=["pub", "get"], describe="Running pub get", require_project=True),
)
