## Version 0.6.1
- Capture and handle SIGTERM, SIGINT and SIGKILL

## Version 0.6.0
- Multiple adjusts with pylint
- Created BaseTask to be used with TaskManager, to reduce chance of cyclic-import
- Refactor in PlatformConfig
- Removed code from __init__.py to avoid cyclic-import
- Refactor class E to function Err
- Prohibited wildcard import. Except `model.task.task` and rare cases
- All imports are from root, to make easier to see where something is being imported

## Version 0.5.0
- Refactor Task structure with TaskGroup concept
- Mostly of tasks were refactored to new structure of sub-tasks
- Basically, one TaskIdentity can be TaskGroup, is that way, allow to use subtask

## Version 0.4.0
- Refactor TaskPrinter and created new Result class (without Args used in TaskResult)
- Changed entire `Option` structure to allow new style of parsing commands
- Added **group** to task, that allow to pass option to only one group
- Updated `Args` structure to support new format of grouped options
- Updated `StringFormater` to support new format of grouped options
- Refactor `ParseOptions` to support grouped options
- Made **read config** and **task resolver** as task to future modularization

## Version 0.3.1
- Fix error where child processes are executed without arguments in Linux and MacOS
- New method to find and check executable. Relative, absolute or in system path
- Minnor change to convert paths between machine and posix (default)

## Version 0.3.0