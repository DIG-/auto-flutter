from pathlib import Path, PurePosixPath
from typing import Optional

from ....core.os import OS
from ....core.string import SB, SF
from ....model.build import *
from ....model.error import SilentWarning
from ....model.platform import *
from ....model.project import *
from ....model.task import *
from ....task.flutter.command import FlutterCommand


class FlutterBuildTask(FlutterCommand):
    identity = TaskIdentity("--flutter-build-task--", "", [], lambda: None, True)

    def __init__(
        self,
        project: Project,
        type: BuildType,
        flavor: Optional[Flavor],
        config: PlatformConfigFlavored,
        debug: bool = False,
        android_rebuild_fix_other: bool = False,
        android_rebuild_fix_desired: bool = False,
    ) -> None:
        super().__init__(
            ignore_failure=False,
            show_output_at_end=False,
            command=None,
            show_output_running=True,
            put_output_args=True,
        )
        self._project: Project = project
        self._type: BuildType = type
        self._flavor: Optional[Flavor] = flavor
        self._config: PlatformConfigFlavored = config
        self._debug: bool = debug
        self._android_rebuild_fix_other: bool = android_rebuild_fix_other
        self._android_rebuild_fix_desired: bool = android_rebuild_fix_desired
        if (
            android_rebuild_fix_other or android_rebuild_fix_desired
        ) and android_rebuild_fix_other == android_rebuild_fix_desired:
            raise AssertionError(
                "Trying rebuild android fix for other and desired at same time"
            )

    def require(self) -> List[TaskId]:
        return self._config.get_run_before(RunType.BUILD, self._flavor)

    def describe(self, args: Args) -> str:
        if self._android_rebuild_fix_desired:
            return "Rebuild flutter {}, flavor {}".format(
                self._type.platform.value, self._flavor
            )
        if self._flavor is None:
            return "Building flutter {}".format(self._type.platform.value)
        else:
            return "Building flutter {}, flavor {}".format(
                self._type.platform.value, self._flavor
            )

    def execute(self, args: Args) -> TaskResult:
        self._command = ["build", self._type.flutter]

        if not self._flavor is None:
            self._command.extend(("--flavor", self._flavor))

        if self._debug:
            self._command.append("--debug")
        else:
            self._command.append("--release")

        self._command.extend(self._config.get_build_param(self._flavor))

        result = super().execute(args)

        if result.success:
            self._clear_output(args)
            return self._check_output_file(args)

        if self._type.platform == Platform.ANDROID:
            return self._handle_android_error(args, result)

        self._clear_output(args)
        return result

    def _check_output_file(self, args: Args) -> TaskResult:
        output_file = self._config.get_output(self._flavor, self._type)
        if output_file is None:
            return TaskResult(
                args,
                error=Warning("Build success, but file output not defined"),
                success=True,
            )
        output_file = SF.format(
            output_file,
            args,
            {
                "flavor": "" if self._flavor is None else self._flavor,
                "build_type": "debug" if self._debug else "release",
                "platform": self._type.platform.value,
            },
        )

        if Path(OS.posix_to_machine_path(PurePosixPath(output_file))).exists():
            self._print(
                SB().append("Build output found successfully", SB.Color.GREEN).str()
            )
        else:
            return TaskResult(
                args,
                FileNotFoundError('Output "{}" not found'.format(output_file)),
                success=False,
            )

        args.add_arg("output", output_file)
        return TaskResult(args, success=True)

    def _handle_android_error(self, args: Args, result: TaskResult) -> TaskResult:
        if self._android_rebuild_fix_other:
            # Skip, since it is a fix build
            self._clear_output(args)
            return TaskResult(
                args,
                error=SilentWarning(
                    "Build failed. Maybe there is more flavors to build"
                ),
                success=True,
            )

        if self._android_rebuild_fix_desired:
            # Failed our desired build
            self._clear_output(args)
            return result

        output = args.get_value("output")
        self._clear_output(args)
        if (
            output is None
            or output.find(
                "This issue appears to be https://github.com/flutter/flutter/issues/58247"
            )
            < 0
        ):
            # This error is not the issue we handle
            return result

        flavors = self._project.flavors
        if flavors is None or len(flavors) <= 1:
            # There is no other flavor to be the reason of this issue
            return result

        self._append_task(
            FlutterBuildTask(
                self._project,
                self._type,
                self._flavor,
                self._config,
                self._debug,
                android_rebuild_fix_other=False,
                android_rebuild_fix_desired=True,
            )
        )
        for flavor in filter(lambda x: x != self._flavor, flavors):
            self._append_task(
                FlutterBuildTask(
                    self._project,
                    self._type,
                    flavor,
                    self._config,
                    self._debug,
                    android_rebuild_fix_other=True,
                    android_rebuild_fix_desired=False,
                )
            )

        self._print(
            SB()
            .append(
                "Flutter issue #58247 detected, building others flavors to fix",
                SB.Color.BLUE,
                True,
            )
            .str()
        )
        return TaskResult(
            args,
            error=SilentWarning("Build others flavor, than rebuild current flavor"),
            success=True,
        )

    def _clear_output(self, args: Args) -> None:
        if args.contains("output"):
            args.pop("output")
