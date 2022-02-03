from typing import List, Optional
from .process import Process
from subprocess import run, Popen, PIPE, STDOUT
from ..string_builder import SB


class _SubProcess(Process):
    def run(self):
        output = SB()
        with Popen(
            [self._executable] + self._arguments,
            shell=True,
            text=True,
            stdout=PIPE,
            stderr=STDOUT,
        ) as p:
            while True:
                buffer = p.stdout.read(1024)
                output.append(buffer)
                self.__write_output(buffer)
                code = p.poll()
                if not code is None:
                    self.exit_code = code
                    break
            self.__write_output("\n")
            self.output = output.str()
