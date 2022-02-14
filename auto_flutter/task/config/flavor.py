from ._base import *


class ConfigFlavor(_BaseConfigTask):
    option_add = Option(None, "add", "Add flavor to project", True)
    option_remove = Option(None, "remove", "Remove flavor from project", True)
    option_rename = Option(
        None, "rename", "Rename flavor from project. Use with --to-name", True
    )
    option_toname = Option(None, "to-name", "New flavor name from --rename", True)
    identity = TaskIdentity(
        "flavor",
        "Handle project flavors in general",
        [option_add, option_remove, option_rename, option_toname],
        lambda: ConfigFlavor(),
    )

    def describe(self, args: Args) -> str:
        return "Updating project flavor"

    def execute(self, args: Args) -> TaskResult:
        project = Project.current
        if project.flavors is None:
            project.flavors = []

        has_change: bool = False

        add_flavor = args.get_value(self.option_add)
        if not add_flavor is None and len(add_flavor) > 0:
            self._print("    Adding flavor " + add_flavor)
            if add_flavor in project.flavors:
                return TaskResult(
                    args,
                    error=AssertionError(
                        "Flavor `{}` already exist in project".format(add_flavor)
                    ),
                )
            project.flavors.append(add_flavor)
            has_change = True

        rem_flavor = args.get_value(self.option_remove)
        if not rem_flavor is None and len(rem_flavor) > 0:
            self._print("    Removing flavor " + rem_flavor)
            if not rem_flavor in project.flavors:
                return TaskResult(
                    args,
                    error=AssertionError(
                        "Flavor `{}` do not exist in project".format(rem_flavor)
                    ),
                )
            project.flavors.remove(rem_flavor)
            has_change = True
            if not project.platform_config is None:
                for platform, config in project.platform_config.items():
                    if not config.flavored is None and rem_flavor in config.flavored:
                        config.flavored.pop(rem_flavor)

        ren_flavor = args.get_value(self.option_rename)
        to_flavor = args.get_value(self.option_toname)
        has_ren = not ren_flavor is None and len(ren_flavor) > 0
        has_to = not to_flavor is None and len(to_flavor) > 0
        if has_ren or has_to:
            if has_ren != has_to:
                if has_ren:
                    return TaskResult(
                        args,
                        error=ValueError("Trying to rename without destination name"),
                    )
                return TaskResult(
                    args, error=ValueError("Trying to rename without origin name")
                )
            assert not ren_flavor is None
            assert not to_flavor is None
            self._print("    Renaming flavor " + ren_flavor + " to " + to_flavor)
            if ren_flavor == to_flavor:
                return TaskResult(
                    args, error=ValueError("Trying to rename flavor to same name")
                )
            if to_flavor in project.flavors:
                return TaskResult(
                    args, error=AssertionError("Destination flavor name already exist")
                )
            if not ren_flavor in project.flavors:
                return TaskResult(
                    args, error=AssertionError("Origin flavor name does not exist")
                )
            project.flavors.remove(ren_flavor)
            project.flavors.append(to_flavor)
            has_change = True
            if not project.platform_config is None:
                for platform, config in project.platform_config.items():
                    if (not config.flavored is None) and ren_flavor in config.flavored:
                        config.flavored[to_flavor] = config.flavored.pop(ren_flavor)

        if not has_change:
            return TaskResult(
                args, error=AssertionError("No change was made"), success=True
            )
        if len(project.flavors) <= 0:
            project.flavors = None

        self._add_save_project()
        return TaskResult(args)
