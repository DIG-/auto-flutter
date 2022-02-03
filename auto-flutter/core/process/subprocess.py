from .process import Process
from subprocess import Popen, PIPE, STDOUT
from encodings import utf_8
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
            encoding=utf_8.getregentry().name,
        ) as p:
            while True:
                buffer = p.stdout.read(1)
                output.append(buffer)
                self._write_output(buffer)
                code = p.poll()
                if not code is None:
                    self.exit_code = code
                    break
            self._write_output("\n")
            self.output = output.str()
