from typing import Final


def __get_version() -> str:
    PACKAGE_NAME: Final = "auto_flutter"
    try:
        from importlib.metadata import version

        return version(PACKAGE_NAME)
    except ImportError:
        pass
    try:
        from pkg_resources import get_distribution

        return get_distribution(PACKAGE_NAME).version
    except ImportError:
        pass
    return "unknown"


VERSION: Final = __get_version()
