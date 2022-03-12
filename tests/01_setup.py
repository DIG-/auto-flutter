import _command

_command.command(
    [
        "aflutter",
        "setup",
        "stack-trace",
        "--on",
    ]
)
_command.command(
    [
        "aflutter",
        "setup",
        "flutter",
        "tests/dummy/flutter",
    ]
)
_command.command(
    [
        "aflutter",
        "setup",
        "firebase",
        "tests/dummy/firebase",
    ]
)
