# Auto Flutter
[![Build status](https://ci.appveyor.com/api/projects/status/4mqob9dpr98a8dlm/branch/main?svg=true)](https://ci.appveyor.com/project/DIG-/auto-flutter/branch/main)

Automatic build tools for flutter build tools

### Reason
Flutter build tools does not allow to create or bind tasks, making some process tedious.
Auto Flutter came with that in mind. Tasks that can be bind with other, and some integrations, like Firebase AppDist out of box.

## License
[CC BY-ND 4.0](https://creativecommons.org/licenses/by-nd/4.0/)

- You can use and redist freely.
- You can also modify, but only for yourself.
- You can use it as a part of your project, but without modifications in this project.

## Installation
### From github release:
``` sh
python -m pip install "https://github.com/DIG-/auto-flutter/releases/download/0.3.0/auto_flutter_dig.whl"
```
or
``` sh
python -m pip install "https://github.com/DIG-/auto-flutter/releases/download/0.3.0/auto_flutter_dig.tar.gz"
```

### From github main branch:
``` sh
python -m pip install "git+https://github.com/DIG-/auto-flutter.git@main#egg=auto_flutter_dig"
```

## Usage
``` sh
python -m auto_flutter_dig
```
or
``` sh
aflutter
```

### First steps
``` sh
# To show help
aflutter help
# To show how to configure environment
aflutter setup -h
# Check if everything is ok
aflutter setup --check
```

Go to your flutter project root. Aka. Where is `pubspec.yaml` and:
``` sh
aflutter init --name "Name to your project"
# And let the magic happen
```