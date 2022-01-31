from __future__ import annotations
from json import load as json_load, dump as json_dump
from pathlib import Path, PurePath, PurePosixPath
from typing import Optional
from appdirs import user_config_dir
from ..core.os import OS


class Config:
    _instance: Optional[Config] = None

    @staticmethod
    def instance() -> Config:
        if Config._instance is None:
            Config._instance = Config()
        return Config._instance

    def __init__(self):
        self.flutter: PurePosixPath = PurePosixPath("flutter")
        self.firebase: PurePosixPath = PurePosixPath("firebase")
        self.firebase_standalone: bool = False

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return (
            "Config("
            + "flutter="
            + str(self.flutter)
            + ", "
            + "firebase="
            + str(self.firebase)
            + ", "
            + "firebase-standalone="
            + str(self.firebase_standalone)
            + ")"
        )

    def load(self) -> bool:
        filepath = Config.get_config_file_path()
        if not filepath.exists():
            return False
        file = open(filepath, mode="r", encoding="utf-8")
        parsed = json_load(file)
        file.close()

        if "flutter" in parsed and len(parsed["flutter"]) != 0:
            self.flutter = OS.machine_to_posix_path(PurePath(parsed["flutter"]))

        if "firebase" in parsed and len(parsed["firebase"]) != 0:
            self.firebase = OS.machine_to_posix_path(PurePath(parsed["firebase"]))

        if (
            "firebase-standalone" in parsed
            and type(parsed["firebase-standalone"]) is bool
        ):
            self.firebase_standalone = bool(parsed["firebase-standalone"])
        return True

    def save(self):
        filepath = Config.get_config_file_path()
        if not filepath.exists():
            filepath.parent.mkdir(parents=True, exist_ok=True)
        output = {
            "flutter": str(self.flutter),
            "firebase": str(self.firebase),
            "firebase-standalone": self.firebase_standalone,
        }
        file = open(filepath, mode="wt", encoding="utf-8")
        json_dump(output, file, indent=2)
        file.close()

    @staticmethod
    def get_config_file_path() -> Path:
        return Path(user_config_dir("auto-flutter", "DIG")).joinpath("config.json")
