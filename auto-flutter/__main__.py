from pprint import pprint
import sys
from .core.logger import log
from .model.config import Config
from .task._list import task_list

if len(sys.argv) <= 1:
    log.error("Auto-Flutter requires at least one task")
    exit(1)

log.debug("Loading config")
if not Config.instance().load():
    log.error("Failed to read config file")
    exit(2)

taskname = sys.argv[1]
if taskname.startswith("-"):
    log.error('Unknown task "{}"'.format(taskname))
    # TODO: Show help with available tasks
    exit(3)

if taskname in task_list:
    # Use this task
    exit(0)

# TODO: Call read project task
# TODO: Check if project constains that task
# TODO: Call task
