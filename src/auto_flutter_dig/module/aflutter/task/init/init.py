from .....model.task import *

class AflutterInitTask(Task):
    def describe(self, args: Args) -> str:
        return "Initialize Aflutter"

    def execute(self, args: Args) -> TaskResult:
        return super().execute(args)