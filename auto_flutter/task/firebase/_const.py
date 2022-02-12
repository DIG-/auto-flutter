from ...core.utils import _Lazy, _NotLazy
from ...model.config import Config

FIREBASE_PROJECT_APP_ID_KEY = _NotLazy("google-app-id")
FIREBASE_DISABLE_INTERACTIVE_MODE = _NotLazy("--non-interactive")
FIREBASE_ENV = _Lazy(
    lambda: {"FIREPIT_VERSION": "1"} if Config.firebase_standalone else {}
)
