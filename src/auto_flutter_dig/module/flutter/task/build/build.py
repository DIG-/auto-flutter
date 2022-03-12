from pathlib import Path, PurePosixPath
from typing import Optional

from .....core.os import OS
from .....core.string import SB, SF
from .....model.build import *
from .....model.error import SilentWarning
from .....model.platform import Platform
from .....model.platform.flavored_config import PlatformConfigFlavored
from .....model.platform.run_type import RunType
from .....model.project import *
from .....model.task import *
from ...identity import FlutterTaskIdentity
from ..command import FlutterCommandTask


class FlutterBuildTaskIdentity(FlutterTaskIdentity):
    def __init__(
        self,
        project: Project,
        build_type: BuildType,
        flavor: Optional[Flavor],
        config: PlatformConfigFlavored,
        build_mode: BuildMode = BuildMode.RELEASE,
        android_rebuild_fix_other: bool = False,
        android_rebuild_fix_desired: bool = False,
    ) -> None:
        super().__init__(
            "--flutter-build-task--",
            "",
            [],
            lambda: FlutterBuildTask(
                project=project,
                build_type=build_type,
                flavor=flavor,
                config=config,
                build_mode=build_mode,
                android_rebuild_fix_other=android_rebuild_fix_other,
                android_rebuild_fix_desired=android_rebuild_fix_desired,
            ),
        )


class FlutterBuildTask(FlutterCommandTask):
    identity = FlutterTaskIdentity("--flutter-build-task--", "", [], lambda: None, True)

    def __init__(
        self,
        project: Project,
        build_type: BuildType,
        flavor: Optional[Flavor],
        config: PlatformConfigFlavored,
        build_mode: BuildMode = BuildMode.RELEASE,
        android_rebuild_fix_other: bool = False,
        android_rebuild_fix_desired: bool = False,
    ) -> None:
        super().__init__(
            command=[],
            ignore_failure=False,
            show_output_at_end=False,
            put_output_args=True,
        )
        self._project: Project = project
        self._build_type: BuildType = build_type
        self._flavor: Optional[Flavor] = flavor
        self._config: PlatformConfigFlavored = config
        self._build_mode: BuildMode = build_mode
        self._android_rebuild_fix_other: bool = android_rebuild_fix_other
        self._android_rebuild_fix_desired: bool = android_rebuild_fix_desired
        if (
            android_rebuild_fix_other or android_rebuild_fix_desired
        ) and android_rebuild_fix_other == android_rebuild_fix_desired:
            raise AssertionError("Trying rebuild android fix for other and desired at same time")

    def require(self) -> List[TaskId]:
        return self._config.get_run_before(RunType.BUILD, self._flavor)

    def describe(self, args: Args) -> str:
        if self._android_rebuild_fix_desired:
            return f"Rebuild flutter {self._build_type.platform.value}, flavor {self._flavor}"
        if self._flavor is None:
            return f"Building flutter {self._build_type.platform.value}"
        else:
            return f"Building flutter {self._build_type.platform.value}, flavor {self._flavor}"

    def execute(self, args: Args) -> TaskResult:
        self._command = ["build", self._build_type.flutter]

        if not self._flavor is None:
            self._command.extend(("--flavor", self._flavor))

        self._command.append("--" + self._build_mode.value)

        self._command.extend(self._config.get_build_param(self._flavor))

        result = super().execute(args)

        if result.success:
            self._clear_output(args)
            return self._check_output_file(args)

        if self._build_type.platform == Platform.ANDROID:
            return self._handle_android_error(args, result)

        self._clear_output(args)
        return result

    def _check_output_file(self, args: Args) -> TaskResult:
        output_file = self._config.get_output(self._flavor, self._build_type)
        if output_file is None:
            return TaskResult(
                args,
                error=E(Warning("Build success, but file output not defined")).error,
                success=True,
            )
        output_file = SF.format(
            output_file,
            args,
            {
                "platform": self._build_type.platform.value,
            },
        )

        if Path(OS.posix_to_machine_path(PurePosixPath(output_file))).exists():
            self._print_content(SB().append("Build output found successfully", SB.Color.GREEN).str())
        else:
            return TaskResult(
                args,
                E(FileNotFoundError(f'Output "{output_file}" not found')).error,
                success=False,
            )

        args.global_add("output", output_file)
        return TaskResult(args, success=True)

    def _handle_android_error(self, args: Args, result: TaskResult) -> TaskResult:
        if self._android_rebuild_fix_other:
            # Skip, since it is a fix build
            self._clear_output(args)
            return TaskResult(
                args,
                error=E(SilentWarning("Build failed. Maybe there is more flavors to build")).error,
                success=True,
            )

        if self._android_rebuild_fix_desired:
            # Failed our desired build
            self._clear_output(args)
            return result

        output = args.global_get("output")
        self._clear_output(args)
        if (
            output is None
            or output.find("This issue appears to be https://github.com/flutter/flutter/issues/58247") < 0
        ):
            # This error is not the issue we handle
            return result

        flavors = self._project.flavors
        if flavors is None or len(flavors) <= 1:
            # There is no other flavor to be the reason of this issue
            return result

        self._append_task(
            FlutterBuildTaskIdentity(
                self._project,
                self._build_type,
                self._flavor,
                self._config,
                self._build_mode,
                android_rebuild_fix_other=False,
                android_rebuild_fix_desired=True,
            )
        )
        for flavor in filter(lambda x: x != self._flavor, flavors):
            self._append_task(
                FlutterBuildTaskIdentity(
                    self._project,
                    self._build_type,
                    flavor,
                    self._config,
                    self._build_mode,
                    android_rebuild_fix_other=True,
                    android_rebuild_fix_desired=False,
                )
            )

        return TaskResult(
            args,
            error=E(Warning("Flutter issue #58247 detected, building others flavors to fix...")).error,
            success=True,
        )

    def _clear_output(self, args: Args) -> None:
        args.global_remove("output")
