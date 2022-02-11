from pprint import pprint
from subprocess import run


def command(*args):
    arg = " ".join(*args)
    print(arg)
    run(arg, shell=True, check=True)


__all__ = ["command"]
