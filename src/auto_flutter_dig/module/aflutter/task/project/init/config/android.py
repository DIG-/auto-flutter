from .......model.build import BuildType
from .......model.error import SilentWarning
from .......model.platform import Platform
from .......model.project import Project
from .......model.task import *
from .....identity import AflutterTaskIdentity


class ProjectInitConfigAndroidTask(Task):
    identity = AflutterTaskIdentity(
        "-project-init-config-android",
        "",
        [],
        lambda: ProjectInitConfigAndroidTask(),  # pylint: disable=unnecessary-lambda
    )

    def describe(self, args: Args) -> str:
        return "Apply android base config"

    def execute(self, args: Args) -> TaskResult:
        project = Project.current
        if not Platform.ANDROID in project.platforms:
            self._uptade_description("")
            return TaskResult(args, E(SilentWarning("Project does not support android platform")).error, success=True)

        config = project.obtain_platform_cofig(Platform.ANDROID)
        config.append_build_param(None, "--no-android-gradle-daemon")
        if project.flavors is None or len(project.flavors) <= 0:
            config.outputs = {
                BuildType.APK: "build/app/outputs/flutter-apk/app-${arg:build-mode}.apk",
                BuildType.BUNDLE: "build/app/outputs/bundle/${arg:build-mode}/app-${arg:build-mode}.aab",
            }
        else:
            config.outputs = {
                BuildType.APK: "build/app/outputs/flutter-apk/app-${arg:flavor}-${arg:build-mode}.apk",
                BuildType.BUNDLE: "build/app/outputs/bundle/${arg:flavor}${arg:build-mode|capitalize}/app-${arg:flavor}-${arg:build-mode}.aab",
            }
        return TaskResult(args)
