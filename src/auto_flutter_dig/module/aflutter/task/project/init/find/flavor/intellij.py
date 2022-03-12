from pathlib import Path
from typing import Optional
from xml.etree.ElementTree import parse as xml_parse

from ........model.platform import Platform
from ........model.project import Project
from ........model.result import Result
from ........model.task import *
from .base import BaseProjectInitFindFlavorIdentity, BaseProjectInitFindFlavorTask


class ProjectInitFindFlavorIntellijTask(BaseProjectInitFindFlavorTask):
    identity = BaseProjectInitFindFlavorIdentity(
        "-project-init-find-flavor-0-intellij",
        "",
        [],
        lambda: ProjectInitFindFlavorIntellijTask(),  # pylint: disable=unnecessary-lambda
    )

    def describe(self, args: Args) -> str:
        return "Detect flavor config via Intellij"

    def execute(self, args: Args) -> TaskResult:
        project = Project.current
        root = Path(".run")
        if not root.exists():
            return TaskResult(args, error=E(FileNotFoundError("Intellij .run folder not found")).error, success=True)

        found = False
        for filename in root.glob("*.run.xml"):
            self._uptade_description(f'Detect flavor config in "{filename.name}"')
            success = False
            try:
                file = open(filename, "r", encoding="utf-8")
                content = xml_parse(file)
                file.close()
                xml_root = content.getroot()
                if (
                    xml_root.tag != "component"
                    or not "name" in xml_root.attrib
                    or xml_root.attrib["name"] != "ProjectRunConfigurationManager"
                ):
                    raise ValueError("Can not find tag component")

                configuration = xml_root.find("configuration")
                if (
                    configuration is None
                    or not "type" in configuration.attrib
                    or configuration.attrib["type"] != "FlutterRunConfigurationType"
                ):
                    raise ValueError("Can not find tag configuration for FlutterRun")

                options = configuration.findall("option")
                if options is None:
                    raise ValueError("Configuration has no options")

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

                if flavor is None:
                    raise ValueError("Flavor not found in options")

                self._append_flavor(project, Platform.DEFAULT, flavor, build_param)
                success = True
                found = True

            except BaseException as error:
                self._reset_description(args, Result(E(LookupError("Failed to find flavor")).caused_by(error)))
                continue

            if success:
                self._reset_description(args, Result(success=True))
            else:
                self._reset_description(args, Result(E(LookupError("Failed to find flavor")).error))

        if not found:
            return TaskResult(args, error=E(LookupError("No flavor was found")).error, success=True)
        return TaskResult(args)
