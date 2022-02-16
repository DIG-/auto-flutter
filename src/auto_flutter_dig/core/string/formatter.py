from os import environ
from re import Match as re_Match
from re import compile as re_compile
from typing import Dict, Optional, Tuple

from ...model.argument import Args
from ..utils import _Dict


class StringFormatter:
    REGEX = re_compile("\$\{(\w+):(\w+)(\|\w+)?}")
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
        option: str = match.group(2)
        operation: Optional[str] = match.group(3)

        if source in ("arg", "ARG", "Arg"):
            arg: str = option
            if arg.isnumeric():
                arg = "-" + arg
            parsed = _Dict.get_or_none(args_extras, arg)
            if parsed is None:
                parsed = args.get_value(arg)
        elif source in ("env", "ENV", "Env"):
            parsed = _Dict.get_or_none(environ, option)
        else:
            raise ValueError('Unknown source "{}"'.format(source))

        if parsed is None:
            raise ValueError('Value not found for "{}"'.format(option))

        if operation is None or len(operation) <= 0:
            pass
        elif operation in ("|capitalize"):
            parsed = parsed.capitalize()
        elif operation in ("|upper", "|uppercase"):
            parsed = parsed.upper()
        elif operation in ("|lower", "|lowercase"):
            parsed = parsed.lower()
        else:
            raise ValueError('Unknown operation "{}"'.format(operation))

        return (match.group(0), parsed)


SF = StringFormatter()
