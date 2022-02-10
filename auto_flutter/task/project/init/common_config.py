from ....core.string import SB
from ....model.platform import PlatformConfigFlavored
from ....model.platform.build_type import BuildType
from ....model.project import Project
from ....model.task import Task


class CommonConfig(Task):
    def describe(self, args: Task.Args) -> str:
        return "Applying common config"

    def execute(self, args: Task.Args) -> Task.Result:
        project = Project.current
        if Project.Platform.ANDROID in project.platforms:
            self.print("    Apply common config for android")
            self.print("    Disabling gradle daemon in build")
            if not Project.Platform.ANDROID in project.platform_config:
                project.platform_config[
                    Project.Platform.ANDROID
                ] = PlatformConfigFlavored()
            config = project.platform_config[Project.Platform.ANDROID]
            config.append_build_param("--no-android-gradle-daemon")

            if len(project.flavors) > 0:
                self.print("    Applying default output for android flavored build")
                config.outputs = {
                    BuildType.APK: "build/app/outputs/flutter-apk/app-${arg:flavor}-${arg:build_type}.apk",
                    BuildType.BUNDLE: "build/app/outputs/bundle/${arg:flavor}${arg:build_type|capitalize}/app-${arg:flavor}-${arg:build_type}.aab",
                }
            else:
                self.print("    Applying default output for android build")
                config.outputs = {
                    BuildType.APK: "build/app/outputs/flutter-apk/app-${arg:build_type}.apk",
                    BuildType.BUNDLE: "build/app/outputs/bundle/${arg:build_type}/app-${arg:build_type}.aab",
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
