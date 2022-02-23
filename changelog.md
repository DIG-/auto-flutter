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