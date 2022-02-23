from os import environ
from re import Match as re_Match
from re import compile as re_compile
from typing import Dict, Optional, Tuple

from ...model.argument import Args
from ..utils import _Dict


class StringFormatter:
    REGEX = re_compile("\$\{(\w+):(\w+\.)?(\w+)(\|\w+)?}")
    EXTRAS = Dict[str, str]

    def format(
        self, input: str, args: Args, args_extra: Optional[EXTRAS] = None
    ) -> str:
        if args_extra is None:
            args_extra = {}
        replaces: Dict[str, str] = {}
        for match in StringFormatter.REGEX.finditer(input):
            try:
                processed = self.__sub(match, args, args_extra)
                replaces[processed[0]] = processed[1]
            except ValueError as error:
                raise ValueError('Error in "{}": {}'.format(match.group(0), str(error)))

        output: str = input
        for key, value in replaces.items():
            output = output.replace(key, value)
        return output

    def __sub(
        self, match: re_Match, args: Args, args_extras: EXTRAS
    ) -> Tuple[str, str]:
        parsed: Optional[str] = None

        source: str = match.group(1)
        group: Optional[str] = match.group(2)
        argument: str = match.group(3)
        operation: Optional[str] = match.group(4)

        source = source.lower()
        argument = argument.lower()
        if not group is None:
            group = group.lower()[:1]
        if not operation is None:
            operation = operation.lower()[1:]

        if source == "arg":
            if group is None:
                parsed = args.get(argument)
            else:
                parsed = args.group_get(group, argument)
            if parsed is None:
                parsed = _Dict.get_or_none(args_extras, argument)
        elif source == "env":
            if not group is None:
                raise ValueError("Substitution from environment does not accept group")
            for key, value in environ.items():
                if key.lower() == argument:
                    parsed = value
                    break
        else:
            raise ValueError('Unknown source "{}"'.format(source))

        if parsed is None:
            raise ValueError('Value not found for "{}"'.format(argument))

        if operation is None or len(operation) <= 0:
            pass
        elif operation in ("capitalize"):
            parsed = parsed.capitalize()
        elif operation in ("upper", "uppercase"):
            parsed = parsed.upper()
        elif operation in ("lower", "lowercase"):
            parsed = parsed.lower()
        else:
            raise ValueError('Unknown operation "{}"'.format(operation))

        return (match.group(0), parsed)


SF = StringFormatter()
