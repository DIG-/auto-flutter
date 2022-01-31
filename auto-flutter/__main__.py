from .core.logger import log
from .model.config import Config

log.debug("Loading config")
if not Config.instance().load():
    log.error("Failed to read config file")
    exit(1)
