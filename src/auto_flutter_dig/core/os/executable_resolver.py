import os
from abc import ABC, abstractmethod
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath
from typing import Iterable, Optional

from ...core.utils import _Iterable
from .os import OS

__all__ = ["ExecutableResolver"]


class ExecutableResolver(ABC):
    @abstractmethod
    def __none(self) -> None:
        pass

    @staticmethod
    def is_executable(path: PurePath) -> bool:
        if OS.current() == OS.WINDOWS:
            return path.suffix.lower() in (".exe", ".bat", ".cmd")
        return os.access(path, os.X_OK)

    @staticmethod
    def get_executable(path: PurePath) -> Optional[Path]:
        try:
            _path = Path(path)
        except:
            return None
        ## Fast mode
        if ExecutableResolver.is_executable(_path):
            if _path.exists():
                return _path
            return None

        ## Test others variants for windows
        if OS.current() == OS.WINDOWS:
            for suffix in (".exe", ".bat", ".cmd"):
                _path = _path.with_suffix(suffix)
                if _path.exists():
                    return _path
            return None

        ## Test others variants
        for suffix in ("", ".sh"):
            _path = _path.with_suffix(suffix)
            if _path.exists() and ExecutableResolver.is_executable(_path):
                return _path
        return None

    @staticmethod
    def resolve_executable(path: PurePath) -> Optional[PurePath]:
        if path.is_absolute():
            # Already absolute
            return ExecutableResolver.get_executable(path)

        if (isinstance(path, PurePosixPath) and path.parent != PurePosixPath(".")) or (
            isinstance(path, PureWindowsPath) and path.parent != PureWindowsPath(".")
        ):
            # Is relative
            _path = ExecutableResolver.get_executable(path)
            if not _path is None:
                return _path.resolve()
            return None

        # Then can be at current local or in sys path
        # First try sys path
        for root in ExecutableResolver.get_sys_path():
            _path = ExecutableResolver.get_executable(root / path)
            if not _path is None:
                # Executable is in path
                return PurePath(_path.name)
            pass
        # Not in path, try at current local
        _path = ExecutableResolver.get_executable(path)
        if not _path is None:
            return _path.absolute()
        return None

    @staticmethod
    def get_sys_path() -> Iterable[Path]:
        splitted = ExecutableResolver.__get_sys_path().split(os.pathsep)
        mapped = map(ExecutableResolver.__try_create_path, splitted)
        not_none = _Iterable.not_none(mapped)
        return filter(lambda x: x.exists(), not_none)

    @staticmethod
    def __try_create_path(path: str) -> Optional[Path]:
        try:
            return Path(path)
        except:
            return None

    @staticmethod
    def __get_sys_path() -> str:
        if "PATH" in os.environ:
            return os.environ["PATH"]
        if "path" in os.environ:
            return os.environ["path"]
        if "Path" in os.environ:
            return os.environ["Path"]
        for k, v in os.environ.items():
            if k.lower() == "path":
                return v
        return ""
