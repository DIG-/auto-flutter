from pathlib import Path
from typing import Final, Optional
from xml.etree.ElementTree import parse as xml_parse

from ....core.string_builder import SB
from ....model.platform import PlatformConfig, PlatformConfigFlavored
from ....model.project import Project
from ....model.task import Task


class FindFlavor(Task):
    option_skip_idea: Final = Task.Option(
        None,
        "skip-flavor-idea",
        "Skip algorithm to detect flavor from Idea Run config",
        False,
    )
    option_skip_android: Final = Task.Option(
        None,
        "skip-flavor-android",
        "Skip algorithm to detect flavor using android data",
        False,
    )
    option_skip_ios: Final = Task.Option(
        None,
        "skip-flavor-android",
        "Skip algorithm to detect flavor using ios data",
        False,
    )

    def describe(self, args: Task.Args) -> str:
        return "Detecting project flavors"

    def execute(self, args: Task.Args) -> Task.Result:
        project: Final = Project.current
        if not args.contains(FindFlavor.option_skip_idea):
            idea_run: Final = Path(".run")
            if not idea_run.exists():
                self.print("    Idea run config not found")
            else:
                self.print("    Trying to detect from Idea run config")
                for filename in idea_run.glob("*.run.xml"):
                    try:
                        self._extract_from_idea(project, filename)
                    except BaseException as error:
                        self.print_error(
                            'Failed to process "{}": '.format(str(filename)), error
                        )
                if self._check_flavor_success(project):
                    return Task.Result(args)

        return Task.Result(args, success=False)

    def print_error(self, message: str, error: BaseException):
        self.print(
            SB()
            .append("  ")
            .append(message, SB.Color.RED)
            .append(str(error), SB.Color.RED)
            .str()
        )

    def _check_flavor_success(self, project: Project) -> bool:
        if not project.flavors is None and len(project.flavors) > 0:
            self.print(
                SB()
                .append("    Flavors were found: ", SB.Color.GREEN)
                .append(" ".join(project.flavors), SB.Color.GREEN, True)
            )
            return True
        return False

    def _append_flavor(
        self,
        project: Project,
        platform: Project.Platform,
        flavor: str,
        build_param: Optional[str],
    ):
        if project.flavors is None:
            project.flavors = []
        project.flavors.append(flavor)

        if not build_param is None and len(build_param) > 0:
            if not platform in project.build_config:
                project.build_config[platform] = PlatformConfigFlavored(
                    build_param=None,
                    run_before=None,
                    output=None,
                    outputs=None,
                    extras=None,
                    flavored={},
                )
            if project.build_config[platform].flavored is None:
                project.build_config[platform].flavored = {}
            project.build_config[platform].flavored[flavor] = PlatformConfig(
                build_param=build_param,
                run_before=None,
                output=None,
                outputs=None,
                extras=None,
            )

    def _extract_from_idea(self, project: Project, filename: Path):
        file = open(filename, "r")
        try:
            content = xml_parse(file)
        except BaseException as error:
            file.close()
            raise error
        file.close()
        root: Final = content.getroot()
        if (
            root.tag != "component"
            or not "name" in root.attrib
            or root.attrib["name"] != "ProjectRunConfigurationManager"
        ):
            return

        configuration: Final = root.find("configuration")
        if (
            configuration is None
            or not "type" in configuration.attrib
            or configuration.attrib["type"] != "FlutterRunConfigurationType"
        ):
            return
        options: Final = configuration.findall("option")
        if options is None:
            return

        flavor: Optional[str] = None
        build_param: Optional[str] = None
        for option in options:
            if not "name" in option.attrib or not "value" in option.attrib:
                continue
            name = option.attrib["name"]
            value = option.attrib["value"]
            if name == "buildFlavor":
                flavor = value
            elif name == "additionalArgs":
                build_param = value

        if not flavor is None:
            self._append_flavor(project, Project.Platform.DEFAULT, flavor, build_param)
