from pprint import pprint
from subprocess import run


def command(*args):
    pprint(*args)
    exit(run(*args,shell=True).returncode)


__all__ = ["command"]
