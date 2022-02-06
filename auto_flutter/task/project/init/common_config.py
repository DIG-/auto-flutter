from typing import Final

from ....core.string_builder import SB
from ....model.build_type import BuildType
from ....model.platform import PlatformConfigFlavored
from ....model.project import Project
from ....model.task import Task


class CommonConfig(Task):
    def describe(self, args: Task.Args) -> str:
        return "Applying common config"

    def execute(self, args: Task.Args) -> Task.Result:
        project: Final = Project.current
        if Project.Platform.ANDROID in project.platforms:
            self.print("    Apply common config for android")
            self.print("    Disabling gradle daemon in build")
            if not Project.Platform.ANDROID in project.build_config:
                project.build_config[
                    Project.Platform.ANDROID
                ] = PlatformConfigFlavored()
            config = project.build_config[Project.Platform.ANDROID]
            if config.build_param is None:
                config.build_param = ""
            config.build_param += " --no-android-gradle-daemon"
            config.build_param = config.build_param.strip()

            if len(project.flavors) > 0:
                self.print("    Applying default output for android flavored build")
                config.outputs = {
                    BuildType.APK: "build/app/outputs/flutter-apk/app-${{arg:flavor}}-${{arg:build_type}}.apk",
                    BuildType.BUNDLE: "build/app/outputs/bundle/${{arg:flavor}}${{arg:build|capitalize}}/app-${{arg:flavor}}-${{arg:build}}.aab",
                }
            else:
                self.print("    Applying default output for android build")
                config.outputs = {
                    BuildType.APK: "build/app/outputs/flutter-apk/app-${{arg:build_type}}.apk",
                    BuildType.BUNDLE: "build/app/outputs/bundle/${{arg:build}}/app-${{arg:build}}.aab",
                }

        if Project.Platform.IOS in project.platforms:
            self.print("    Apply common config for ios")
            self.print(
                SB()
                .append(
                    "  Sorry. I don't known how to configure this little thing",
                    SB.Color.YELLOW,
                )
                .str()
            )

        if Project.Platform.IOS in project.platforms:
            self.print("    Apply common config for web")
            self.print(
                SB()
                .append(
                    "  Sorry. I don't known how to configure this little thing",
                    SB.Color.YELLOW,
                )
                .str()
            )

        return Task.Result(args)
