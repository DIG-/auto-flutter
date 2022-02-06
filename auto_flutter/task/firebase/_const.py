from typing import Final

from ...model.config import Config

FIREBASE_DISABLE_INTERACTIVE_MODE: Final = "--non-interactive"
FIREBASE_ENV: Final = (
    {"FIREPIT_VERSION": "1"} if Config.instance().firebase_standalone else {}
)
