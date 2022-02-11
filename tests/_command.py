from subprocess import run


def command(*args):
    exit(run(*args,shell=True).returncode)


__all__ = ["command"]
