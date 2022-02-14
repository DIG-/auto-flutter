from pathlib import Path, PurePosixPath
from re import compile as re_compile
from typing import List, Optional
from xml.etree.ElementTree import parse as xml_parse

from ....core.os import OS
from ....core.session import Session
from ....core.string import SB
from ....model.platform import Platform
from ....model.project import Project
from ....model.task import *


class FindFlavor(Task):
    option_skip_idea = Option(
        None,
        "skip-flavor-idea",
        "Skip algorithm to detect flavor from Idea Run config",
        False,
    )
    option_skip_android = Option(
        None,
        "skip-flavor-android",
        "Skip algorithm to detect flavor using android data",
        False,
    )
    option_skip_ios = Option(
        None,
        "skip-flavor-ios",
        "Skip algorithm to detect flavor using ios data",
        False,
    )

    def describe(self, args: Args) -> str:
        return "Detecting project flavors"

    def execute(self, args: Args) -> TaskResult:
        project = Project.current
        if not args.contains(FindFlavor.option_skip_idea):
            idea_run = Path(".run")
            if not idea_run.exists():
                self._print("    Idea run config not found")
            else:
                self._print("    Trying to detect flavor from Idea run config")
                for filename in idea_run.glob("*.run.xml"):
                    try:
                        self._extract_from_idea(project, filename)
                    except BaseException as error:
                        self.print_error(
                            'Failed to process "{}": '.format(str(filename)), error
                        )
                if self._check_flavor_success(project):
                    return TaskResult(args)

        if not args.contains(FindFlavor.option_skip_android):
            gradle = Path(
                OS.posix_to_machine_path(PurePosixPath("android/app/build.gradle"))
            )
            if not Platform.ANDROID in project.platforms:
                self._print(
                    "    Skip android analysis, since project does not support android"
                )
            elif not gradle.exists():
                self._print("    Android build.gradle not found")
            else:
                self._print("    Trying to detect flavor from android project")
                try:
                    self._extract_from_gradle(project, gradle)
                except BaseException as error:
                    self.print_error("Failed to extract flavor from android. ", error)
                if self._check_flavor_success(project):
                    return TaskResult(args)

        if not args.contains(FindFlavor.option_skip_ios):
            if not Platform.IOS in project.platforms:
                self._print("    Skip ios analysis, since project does not support ios")
            else:
                self._print("    Trying to detect flavor from ios project")
                self._print(
                    SB()
                    .append(
                        "  ios flavor extraction was not implemented yet",
                        SB.Color.YELLOW,
                    )
                    .str()
                )

        if project.flavors is None or len(project.flavors) == 0:
            project.flavors = None
            self._print(
                "  No flavors were found. Maybe this project does not have flavor 🙂"
            )
        return TaskResult(args, success=True)

    def print_error(self, message: str, error: BaseException):
        self._print(
            SB()
            .append("  ")
            .append(message, SB.Color.RED)
            .append(Session.format_exception(error), SB.Color.RED)
            .str()
        )

    def _check_flavor_success(self, project: Project) -> bool:
        if not project.flavors is None and len(project.flavors) > 0:
            self._print(
                SB()
                .append("    Flavors were found: ", SB.Color.GREEN)
                .append(" ".join(project.flavors), SB.Color.GREEN, True)
                .str()
            )
            return True
        return False

    def _append_flavor(
        self,
        project: Project,
        platform: Platform,
        flavor: str,
        build_param: Optional[List[str]],
    ):
        if project.flavors is None:
            project.flavors = []
        project.flavors.append(flavor)

        if not build_param is None and len(build_param) > 0:
            project.obtain_platform_cofig(platform).obtain_config_by_flavor(
                flavor
            ).build_param = build_param

    def _extract_from_idea(self, project: Project, filename: Path):
        file = open(filename, "r")
        try:
            content = xml_parse(file)
        except BaseException as error:
            file.close()
            raise error
        file.close()
        root = content.getroot()
        if (
            root.tag != "component"
            or not "name" in root.attrib
            or root.attrib["name"] != "ProjectRunConfigurationManager"
        ):
            return

        configuration = root.find("configuration")
        if (
            configuration is None
            or not "type" in configuration.attrib
            or configuration.attrib["type"] != "FlutterRunConfigurationType"
        ):
            return
        options = configuration.findall("option")
        if options is None:
            return

        flavor: Optional[str] = None
        build_param: Optional[List[str]] = None
        for option in options:
            if not "name" in option.attrib or not "value" in option.attrib:
                continue
            name = option.attrib["name"]
            value = option.attrib["value"]
            if name == "buildFlavor":
                flavor = value
            elif name == "additionalArgs":
                build_param = value.split()

        if not flavor is None:
            self._append_flavor(project, Platform.DEFAULT, flavor, build_param)

    def _extract_from_gradle(self, project: Project, filename: Path):
        file = open(filename, "r")
        content = "".join(file.readlines())
        file.close()
        try:
            start = content.index("productFlavors")
            start = content.index("{", start)
        except BaseException as error:
            self.print_error("Failed to find flavor section in build.gradle. ", error)
        end = 0
        count = 0
        for i in range(start, len(content)):
            if content[i] == "{":
                count += 1
            elif content[i] == "}":
                count -= 1
                if count <= 0:
                    end = i
                    break
        if end < start:
            self.print_error(
                "Failed to find flavor section in build.gradle. ",
                IndexError("End of string is before start"),
            )
        flavors = content[start + 1 : end]
        count = 0
        buffer = ""
        space = re_compile("\s")
        for i, c in enumerate(flavors):
            if not space.match(c) is None:
                continue
            elif c == "{":
                count += 1
                if count == 1:
                    self._append_flavor(project, Platform.ANDROID, buffer, None)
                    buffer = ""
                continue
            elif c == "}":
                count -= 1
            elif count == 0:
                buffer += c
