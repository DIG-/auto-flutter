from typing import Final

from ...core.utils import _Lazy, _NotLazy
from ...model.config import Config

FIREBASE_PROJECT_APP_ID_KEY: Final = _NotLazy("google-app-id")
FIREBASE_DISABLE_INTERACTIVE_MODE: Final = _NotLazy("--non-interactive")
FIREBASE_ENV: Final = _Lazy(
    lambda: {"FIREPIT_VERSION": "1"} if Config.instance().firebase_standalone else {}
)
