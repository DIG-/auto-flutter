from json import dump as json_dump
from json import load as json_load
from pathlib import Path, PurePath, PurePosixPath
from typing import Dict, NoReturn, Optional, Union

from appdirs import user_config_dir  # type: ignore[import]

from ..core.os import OS

__all__ = ["Config"]


class __Config:
    def __init__(self) -> None:
        self.__is_loaded: bool = False
        self.__content: Dict[str, Union[str, bool, int]] = {}

    def __value_error(self, key: str, expect: type, received: type) -> NoReturn:
        raise ValueError(
            'Unexpected value for key "{}". Expected `{}` but received `{}`'.format(
                key, expect.__name__, received.__name__
            )
        )

    @staticmethod
    def __config_file_path() -> Path:
        return Path(user_config_dir("auto-flutter", "DIG")).joinpath("config.json")

    def _get_value(self, key: str) -> Union[str, bool, int, None]:
        if not key in self.__content:
            return None
        return self.__content[key]

    def _put_value(self, key: str, value: Union[str, bool, int, None]) -> None:
        if value is None:
            if key in self.__content:
                self.__content.pop(key)
            return
        if not isinstance(value, (str, bool, int)):
            raise ValueError(
                "Value must be instance of `str`, `bool` or `int`, but `{}` was used".format(
                    type(value).__name__
                )
            )
        self.__content[key] = value

    ## General Methods

    def load(self) -> bool:
        self.__is_loaded = True  # Load was called
        filepath = self.__config_file_path()
        if not filepath.exists():
            return False
        file = open(filepath, mode="r", encoding="utf-8")
        parsed = json_load(file)
        file.close()
        if not isinstance(parsed, Dict):
            raise SyntaxError(
                "Config file is in incorrect format.\n{}".format(str(filepath))
            )
        self.__content = parsed
        return True

    @property
    def is_loaded(self) -> bool:
        return self.__is_loaded

    def save(self) -> None:
        filepath = self.__config_file_path()
        if not filepath.exists():
            filepath.parent.mkdir(parents=True, exist_ok=True)

        file = open(filepath, mode="wt", encoding="utf-8")
        json_dump(self.__content, file, indent=2)
        file.close()

    def contains(self, key: str) -> bool:
        return key in self.__content

    def remove(self, key: str) -> None:
        self._put_value(key, None)

    ## Boolean methods

    def get_bool(self, key: str, default: bool = False) -> bool:
        value = self._get_value(key)
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return not value.lower() in ("f", "n", "no", "false")
        if isinstance(value, int):
            return value != 0
        return self.__value_error(key, bool, type(value))

    def put_bool(self, key: str, value: bool) -> None:
        self._put_value(key, value)

    ## String methods

    def get_str(self, key: str, default: str = "") -> str:
        value = self._get_value(key)
        if value is None:
            return default
        if isinstance(value, bool):
            return str(value)
        if isinstance(value, str):
            return value
        if isinstance(value, int):
            return str(value)
        return self.__value_error(key, str, type(value))

    def put_str(self, key: str, value: str) -> None:
        self._put_value(key, value)

    ## Integer methods

    def get_int(self, key: str, default: int = 0) -> int:
        value = self._get_value(key)
        if value is None:
            return default
        if isinstance(value, bool):
            return 1 if value else 0
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return default
        if isinstance(value, int):
            return value
        return self.__value_error(key, int, type(value))

    def put_int(self, key: str, value: int) -> None:
        self._put_value(key, value)

    ## PurePath methods

    def get_path(self, key: str, default: Optional[PurePath] = None) -> PurePosixPath:
        value = self._get_value(key)
        if value is None:
            if default is None:
                raise ValueError(
                    'Key "{}" not found and no default value informed'.format(key)
                )
            return OS.machine_to_posix_path(default)
        if isinstance(value, str):
            return PurePosixPath(value)
        return self.__value_error(key, int, type(value))

    def put_path(self, key: str, value: PurePath) -> None:
        self._put_value(key, str(OS.machine_to_posix_path(value)))


Config = __Config()
