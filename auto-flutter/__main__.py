from pprint import pprint
import sys
from .core.logger import log
from .model.config import Config
from .task._list import task_list
from .core.task_manager import TaskManager
from .task.help import Help

if len(sys.argv) <= 1:
    log.error("Auto-Flutter requires at least one task")
    exit(1)

log.debug("Loading config")
if not Config.instance().load():
    log.error("Failed to read config file")
    exit(2)

taskname = sys.argv[1]
manager = TaskManager()
if taskname.startswith("-"):
    log.error('Unknown task "{}"'.format(taskname))
    manager.add(Help())
    manager.execute()
    exit(3)

if taskname in task_list:
    manager.add(task_list[taskname].creator())
    if manager.execute():
        exit(0)
    else:
        exit(1)

# TODO: Call read project task
# TODO: Check if project constains that task
# TODO: Call task
