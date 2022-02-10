from __future__ import annotations

from distutils.errors import UnknownFileError
from enum import Enum
from pathlib import PurePath, PurePosixPath, PureWindowsPath
from sys import platform


class OS(Enum):
    UNKNOWN = 0
    WINDOWS = 1
    LINUX = 2
    MAC = 3

    @staticmethod
    def current() -> OS:
        if platform.startswith("win32") or platform.startswith("cygwin"):
            return OS.WINDOWS
        if platform.startswith("linux"):
            return OS.LINUX
        if platform.startswith("darwin"):
            return OS.MAC
        return OS.UNKNOWN

    @staticmethod
    def posix_to_machine_path(path: PurePath) -> PurePath:
        if OS.current() != OS.WINDOWS:
            return path

        if not path.is_absolute():
            if path is PureWindowsPath:
                return path
            if len(path.parts) == 1:
                return PureWindowsPath(path)

            first = path.parts[0]
            if not (len(first) == 2 and first[1] == ":"):
                return PureWindowsPath(path)

        output = PureWindowsPath()
        for segment in path.parts:
            if len(output.drive) == 0:
                if segment == "/":
                    pass
                if len(segment) > 2:
                    raise UnknownFileError(
                        'Can not find drive letter from path "{}"'.format(path)
                    )
                if len(segment) == 1:
                    output = PureWindowsPath(segment + ":")
                elif segment[1] != ":":
                    raise UnknownFileError(
                        'Unrecognized drive letter from path "{}"'.format(path)
                    )
                else:
                    output = PureWindowsPath(segment)
                continue
            if len(output.parts) == 1:
                output = output.joinpath("/" + segment)
            else:
                output = output.joinpath(segment)
        return output

    @staticmethod
    def machine_to_posix_path(path: PurePath) -> PurePosixPath:
        if isinstance(path, PurePosixPath):
            return path

        if not path.is_absolute():
            return PurePosixPath(path.as_posix())

        output = PurePosixPath("/" + path.drive[:1])
        for i, segment in enumerate(path.parts):
            if i == 0:
                continue
            output = output.joinpath(segment)
        return output
