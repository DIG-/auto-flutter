from __future__ import annotations
import json
from pathlib import Path, PurePosixPath
from typing import Dict
from appdirs import user_config_dir
from core.os import OS


class Config:
    _instance: Config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.flutter: PurePosixPath = PurePosixPath("flutter")
        self.firebase: PurePosixPath = PurePosixPath("firebase")
        self.firebase_standalone: bool = False

    def load(self) -> bool:
        filepath = Config.get_config_file_path()
        if not filepath.exists():
            return False
        file = open(filepath, mode="r", encoding="utf-8")
        parsed = json.load(file)
        file.close()
        if not parsed is Dict:
            raise TypeError("Parsed config is invalid")
        if "flutter" in parsed and len(parsed["flutter"]) != 0:
            self.flutter = OS.machine_to_posix_path(parsed["flutter"])

        if "firebase" in parsed and len(parsed["firebase"]) != 0:
            self.firebase = OS.machine_to_posix_path(parsed["firebase"])

        if "firebase-standalone" in parsed and parsed["firebase-standalone"] is bool:
            self.firebase_standalone = bool(parsed["firebase-standalone"])
        return True

    @staticmethod
    def get_config_file_path() -> Path:
        return Path(user_config_dir("auto-flutter", "DIG")).joinpath("config.json")
