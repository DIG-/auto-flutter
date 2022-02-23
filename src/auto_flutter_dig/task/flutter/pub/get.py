from ....task.flutter.command import FlutterCommand
from ....task.identity import FlutterTaskIdentity

__all__ = ["FlutterPubGet"]

FlutterPubGet = FlutterTaskIdentity(
    "pub-get",
    "Runs flutter pub get",
    [],
    lambda: FlutterCommand(
        command=["pub", "get"], describe="Running pub get", require_project=True
    ),
)
