from ...core.utils import _Lazy, _Static
from ...model.config import Config

FIREBASE_PROJECT_APP_ID_KEY = _Static("google-app-id")
FIREBASE_DISABLE_INTERACTIVE_MODE = _Static("--non-interactive")
FIREBASE_ENV = _Lazy(
    lambda: {"FIREPIT_VERSION": "1"} if Config.firebase_standalone else {}
)
