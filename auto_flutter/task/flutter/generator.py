from ...core.string import SB
from ...core.utils import _Dict
from ...model.task import *
from ...task.flutter.command import FlutterCommand
from ...task.options import ParseOptions
from ...task.project import ProjectRead


class FlutterGeneratorTask(Task):
    __options = {
        "code": Option(None, "code", "Generate code with `pub run build_runner build`"),
        "force1": Option(
            None,
            "delete-conflicting-outputs",
            "Delete conflicting output for code generation",
        ),
        "force2": Option(None, "force", "Same as --delete-conflicting-outputs"),
        "appicon": Option(
            None, "appicon", "Generate app icon with package `flutter_launcher_icons`"
        ),
        "splash": Option(
            None,
            "splash",
            "Generate splash screen with package `flutter_native_splash`",
        ),
    }

    identity = TaskIdentity(
        "generate",
        "Generate code, appicon and/or splash screen. Default is code",
        _Dict.flatten(__options),
        lambda: FlutterGeneratorTask(False),
    )

    identity_code = TaskIdentity(
        "generate-code",
        "Generate code with --force",
        [],
        lambda: FlutterGeneratorTask(True),
    )

    def __init__(self, force: bool = False) -> None:
        super().__init__()
        self.force = force

    def require(self) -> List[TaskId]:
        return [ParseOptions.identity.id, ProjectRead.identity.id]

    def describe(self, args: Args) -> str:
        return ""

    def execute(self, args: Args) -> TaskResult:
        code = self.force or args.contains(self.__options["code"])
        force = (
            self.force
            or args.contains(self.__options["force1"])
            or args.contains(self.__options["force2"])
        )
        appicon = args.contains(self.__options["appicon"])
        splash = args.contains(self.__options["splash"])
        if not code and not appicon and not splash:
            self._print(
                SB()
                .append(
                    "  No type for generation was chosen. Auto-enabling code generation",
                    SB.Color.YELLOW,
                )
                .str()
            )
            code = True

        if splash:
            self._append_task(
                FlutterCommand(
                    command=["pub", "run", "flutter_native_splash:create"],
                    describe="Generate splash screen",
                )
            )

        if appicon:
            self._append_task(
                FlutterCommand(
                    command=["pub", "run", "flutter_launcher_icons:main"],
                    describe="Generate app icon",
                )
            )

        if code:
            command = ["pub", "run", "build_runner", "build"]
            if force:
                command.append("--delete-conflicting-outputs")
            self._append_task(FlutterCommand(command=command, describe="Generate code"))
        return TaskResult(args)
