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
        from .path_converter import PathConverter

        return PathConverter.from_path(path).to_machine()

    @staticmethod
    def machine_to_posix_path(path: PurePath) -> PurePosixPath:
        from .path_converter import PathConverter

        return PathConverter.from_machine(path).to_posix()
