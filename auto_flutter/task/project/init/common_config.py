from ....core.string import SB
from ....model.build import BuildType
from ....model.platform import PlatformConfigFlavored
from ....model.project import Project
from ....model.task import *


class CommonConfig(Task):
    def describe(self, args: Args) -> str:
        return "Applying common config"

    def execute(self, args: Args) -> TaskResult:
        project = Project.current
        if Project.Platform.ANDROID in project.platforms:
            self._print("    Apply common config for android")
            self._print("    Disabling gradle daemon in build")
            if not Project.Platform.ANDROID in project.platform_config:
                project.platform_config[
                    Project.Platform.ANDROID
                ] = PlatformConfigFlavored()
            config = project.platform_config[Project.Platform.ANDROID]
            config._append_build_param("--no-android-gradle-daemon")

            if len(project.flavors) > 0:
                self._print("    Applying default output for android flavored build")
                config.outputs = {
                    BuildType.APK: "build/app/outputs/flutter-apk/app-${arg:flavor}-${arg:build_type}.apk",
                    BuildType.BUNDLE: "build/app/outputs/bundle/${arg:flavor}${arg:build_type|capitalize}/app-${arg:flavor}-${arg:build_type}.aab",
                }
            else:
                self._print("    Applying default output for android build")
                config.outputs = {
                    BuildType.APK: "build/app/outputs/flutter-apk/app-${arg:build_type}.apk",
                    BuildType.BUNDLE: "build/app/outputs/bundle/${arg:build_type}/app-${arg:build_type}.aab",
                }

        if Project.Platform.IOS in project.platforms:
            self._print("    Apply common config for ios")
            self._print(
                SB()
                .append(
                    "  Sorry. I don't known how to configure this little thing",
                    SB.Color.YELLOW,
                )
                .str()
            )

        if Project.Platform.IOS in project.platforms:
            self._print("    Apply common config for web")
            self._print(
                SB()
                .append(
                    "  Sorry. I don't known how to configure this little thing",
                    SB.Color.YELLOW,
                )
                .str()
            )

        return TaskResult(args)
