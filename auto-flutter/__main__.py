import sys
from platform import system as platform_system
from termcolor import colored
from .core.logger import log
from .model.config import Config
from .task._list import task_list
from .core.task_manager import TaskManager

# Enable color support on windows
if platform_system() == "Windows":
    from colorama import init

    init()

manager = TaskManager.instance()

if len(sys.argv) <= 1:
    print(colored("Auto-Flutter requires at least one task\n", "red"))
    manager.add_id("help")
    manager.execute()
    exit(1)

log.debug("Loading config")
if not Config.instance().load():
    print(colored("Failed to read config. Assume default", "yellow"))
    print("Use task " + colored("setup", "magenta") + " to configure you environment\n")

taskname = sys.argv[1]
if taskname.startswith("-"):
    print(colored("Unknown task ", "red") + colored(taskname, "magenta") + "\n")
    manager.add_id("help")
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
