from pathlib import Path, PurePosixPath
from typing import List, Optional

from auto_flutter.model.error import SilentWarning

from ....core.os import OS
from ....core.string import SB, SF
from ....core.utils import _Dict
from ....model.build import BuildType
from ....model.platform import Platform, PlatformConfigFlavored
from ....model.project import Flavor, Project
from ....model.task import Task
from .. import Flutter
from .._const import FLUTTER_DISABLE_VERSION_CHECK


class FlutterBuild(Flutter):
    def __init__(
        self,
        project: Project,
        platform: Platform,
        type: BuildType,
        flavor: Optional[Flavor],
        config: PlatformConfigFlavored,
        debug: bool = False,
        android_rebuild_fix_other: bool = False,
        android_rebuild_fix_desired: bool = False,
    ) -> None:
        super().__init__(
            project=False,
            command=None,
            command_append_args=False,
            output_running=True,
            output_end=False,
            output_arg=True,
        )
        self.project = project
        self.platform = platform
        self.type = type
        self.flavor = flavor
        self.config = config
        self.debug = debug
        self.android_rebuild_fix_other = android_rebuild_fix_other
        self.android_rebuild_fix_desired = android_rebuild_fix_desired
        if (
            android_rebuild_fix_other or android_rebuild_fix_desired
        ) and android_rebuild_fix_other == android_rebuild_fix_desired:
            raise AssertionError(
                "Trying rebuild android fix for other and desired at same time"
            )

    def require(self) -> List[Task.ID]:
        required = _Dict.get_or_none(
            self.config.get_run_before(self.flavor), RunType.BUILD
        )
        return [] if required is None else required

    def describe(self, args: Task.Args) -> str:
        if self.android_rebuild_fix_desired:
            return "Rebuild flutter {}, flavor {}".format(
                self.platform.value, self.flavor
            )
        if self.flavor is None:
            return "Building flutter {}".format(self.platform.value)
        else:
            return "Building flutter {}, flavor {}".format(
                self.platform.value, self.flavor
            )

    def execute(self, args: Task.Args) -> Task.Result:
        command: List[str] = [FLUTTER_DISABLE_VERSION_CHECK, "build", self.type.flutter]

        if not self.flavor is None:
            command.append("--flavor")
            command.append(self.flavor)

        if self.debug:
            command.append("--debug")
        else:
            command.append("--release")

        command.extend(self.config.get_build_param(self.flavor))
        self._command = command

        process = super().execute(args)
        if not process.error is None:
            process.args.pop("output")
            return process

        if not process.success and self.platform == Platform.ANDROID:
            if self.android_rebuild_fix_other or self.android_rebuild_fix_desired:
                pass  # Skip, since it is a fix build
            else:
                output = args.get_value("output")
                if (
                    output.find(
                        "This issue appears to be https://github.com/flutter/flutter/issues/58247"
                    )
                    < 0
                ):
                    pass  # Error can be from others reasons
                elif self.project.flavors is None or len(self.project.flavors) <= 1:
                    pass  # There is no other flavor to raise this error
                else:
                    process.args.pop("output")
                    others_flavors = filter(
                        lambda x: x != self.flavor, self.project.flavors
                    )
                    from ....core.task import TaskManager

                    manager = TaskManager
                    ## Add to rebuild self task
                    manager.add(
                        FlutterBuild(
                            project=self.project,
                            platform=self.platform,
                            type=self.type,
                            flavor=self.flavor,
                            config=self.config,
                            debug=self.debug,
                            android_rebuild_fix_other=False,
                            android_rebuild_fix_desired=True,
                        )
                    )
                    for flavor in others_flavors:
                        manager.add(
                            FlutterBuild(
                                project=self.project,
                                platform=self.platform,
                                type=self.type,
                                flavor=flavor,
                                config=self.config,
                                debug=self.debug,
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
                    return Task.Result(
                        args,
                        error=SilentWarning(
                            "Build others flavor, than rebuild current flavor"
                        ),
                        success=True,
                    )

        process.args.pop("output")
        if not process.success:
            if (
                self.android_rebuild_fix_other
            ):  # Other build failed, maybe there is more to build
                return Task.Result(
                    process.args,
                    error=SilentWarning(
                        "Build failed. Maybe there is more flavors to build"
                    ),
                    success=True,
                )
            return process

        output_file = self.config.get_output(self.flavor, self.type)
        if output_file is None:
            return Task.Result(
                args,
                error=Warning("Build success, but file output not defined"),
                success=True,
            )
        output_file = SF.format(
            output_file,
            args,
            {
                "flavor": self.flavor,
                "build_type": "debug" if self.debug else "release",
                "platform": self.platform.value,
            },
        )

        if Path(OS.posix_to_machine_path(PurePosixPath(output_file))).exists():
            self._print(
                SB().append("Build output found successfully", SB.Color.GREEN).str()
            )
        else:
            return Task.Result(
                args,
                FileNotFoundError('Output "{}" not found'.format(output_file)),
                success=False,
            )

        args.add_arg("output", output_file)
        return Task.Result(args, success=True)
