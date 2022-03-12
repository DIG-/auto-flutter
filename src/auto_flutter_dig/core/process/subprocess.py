from codecs import IncrementalDecoder, getincrementaldecoder
from pathlib import Path, PurePath
from subprocess import PIPE, STDOUT, Popen, run
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from ...module.aflutter.config.const import AFLUTTER_CONFIG_PRINT_PROCESS_COMMAND
from ..config import Config
from ..logger import log
from ..os import OS
from ..string import SB
from .process import Process


class _SubProcess(Process):
    __DEFAULT_DECODER: Optional[IncrementalDecoder] = None

    def __init__(
        self,
        executable: Union[str, PurePath],
        arguments: Optional[List[str]] = None,
        environment: Optional[Dict[str, str]] = None,
        writer: Optional[Callable[[str], None]] = None,
        inherit_environment: bool = True,
    ) -> None:
        super().__init__(executable, arguments, environment, writer, inherit_environment)
        self.__process: Optional[Popen] = None
        self.__stopped: bool = False
        self.__killed: bool = False

    def run(self):
        if self._executable.is_absolute():
            if not Path(self._executable).exists():
                raise FileNotFoundError(0, "Executable `{}` not found".format(self._executable))
        output = SB()
        command = " ".join(map(self.__escape_arg, [str(self._executable)] + self._arguments))
        if Config.get_bool(AFLUTTER_CONFIG_PRINT_PROCESS_COMMAND):
            self._write_output(command)
            self._write_output("\n")
        self.__process = Popen(
            command,
            shell=True,
            stdout=PIPE,
            stderr=STDOUT,
            env=self._environment,
        )
        with self.__process as p:
            decoder: IncrementalDecoder = _SubProcess.__get_default_decoder()
            while True:
                self.__read_output(decoder, output, p.stdout.read(1))
                code = p.poll()
                if not code is None:
                    self.exit_code = code
                    while True:
                        remain = p.stdout.read(1)
                        if remain == b"":
                            break
                        self.__read_output(decoder, output, remain)
                    break
            self.__process = None
            self._write_output("\n")
            self.output = output.str()
            if self.exit_code == 127:
                raise FileNotFoundError(0, "Command `{}` not found".format(self._executable))
            if self.__killed:
                raise Process.ChildProcessKilled("Command `{}` was killed".format(self._executable))
            if self.__stopped:
                raise Process.ChildProcessStopped("Command `{}` was stopped".format(self._executable))

    def stop(self):
        process = self.__process
        if not process is None:
            self.__stopped = True
            process.terminate()

    def kill(self):
        process = self.__process
        if not process is None:
            self.__killed = True
            process.kill()
            if OS.current() == OS.WINDOWS:
                try:
                    result = run(
                        ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                        shell=True,
                        stdout=PIPE,
                        stderr=PIPE,
                    )
                    if result.returncode != 0:
                        result = run(
                            ["taskkill", "/F", "/T", "/IM", self._executable.name],
                            shell=True,
                            stdout=PIPE,
                            stderr=PIPE,
                        )
                except BaseException as error:
                    raise SystemError(
                        'Failed to kill process "{}"'.format(self._executable.name),
                        error,
                    )
                if result.returncode != 0:
                    raise SystemError('Failed to kill process "{}"'.format(self._executable.name))

    def __read_output(self, decoder: IncrementalDecoder, output: SB, value: bytes):
        decoded = decoder.decode(value)
        if len(decoded) > 0:
            output.append(decoded)
            self._write_output(decoded)

    @staticmethod
    def __escape_arg(arg: str) -> str:
        arg = arg.strip()
        if arg.find(" ") < 0:
            return arg
        st_double = arg.startswith('"')
        st_single = arg.startswith("'")
        if st_double and arg.endswith('"'):
            return arg  # Already escaped
        if st_single and arg.endswith("'"):
            return arg  # Already escaped
        if st_double:
            return "'{}'".format(arg)
        return '"{}"'.format(arg)

    @staticmethod
    def __get_default_decoder() -> IncrementalDecoder:
        if _SubProcess.__DEFAULT_DECODER is None:
            _SubProcess.__DEFAULT_DECODER = _SubProcess.__generate_decoder()
        return _SubProcess.__DEFAULT_DECODER

    @staticmethod
    def __generate_decoder() -> IncrementalDecoder:
        if OS.current() != OS.WINDOWS:
            return getincrementaldecoder("utf-8")()
        multiple = _IncrementalDecoderMultiple()
        multiple.add(getincrementaldecoder("utf-8")())
        from winreg import HKEY_LOCAL_MACHINE, REG_SZ, CloseKey, OpenKey, QueryValueEx

        try:  # Get windows default charset for console
            key = OpenKey(HKEY_LOCAL_MACHINE, "SYSTEM\\CurrentControlSet\\Control\\Nls\\CodePage")
            read: Tuple[Any, int] = QueryValueEx(key, "OEMCP")
            CloseKey(key)
            if read[1] == REG_SZ and isinstance(read[0], str):
                multiple.add(getincrementaldecoder("cp" + read[0])())
        except:
            try:
                multiple.add(getincrementaldecoder("cp850")())
            except:
                pass
        return multiple


class _IncrementalDecoderMultiple(IncrementalDecoder):
    def __init__(self) -> None:
        super().__init__("multiple")
        self._decoders: List[_IncrementalDecoderStopOnFailure] = []

    def add(self, decoder: IncrementalDecoder):
        self._decoders.append(_IncrementalDecoderStopOnFailure(decoder))

    def decode(self, input: bytes, final: bool = False) -> str:
        has_error: bool = True  # Check if all decoders has error
        hold: bool = False  # Hold if firsts decoders are still decoding
        for decoder in self._decoders:
            out = decoder.decode(input, final)
            has_error &= decoder._has_error
            if hold or (len(out) == 0 and not decoder._has_error):
                hold = True
            elif len(out) > 0:
                out = decoder._out_buffer
                self.reset()
                return out

        if has_error:  ## All decoders failed
            length = 1
            for decoder in self._decoders:
                length = max(length, len(decoder.getstate()[0]))
            self.reset()
            log.error("Some crazy byte stream appear")
            return "�" * length
        return ""

    def reset(self) -> None:
        for decoder in self._decoders:
            decoder.reset()

    def getstate(self) -> Tuple[bytes, int]:
        return self._decoders[0].getstate()  # Why not?.......

    def setstate(self, state: Tuple[bytes, int]) -> None:
        for decoder in self._decoders:
            decoder.setstate(state)


class _IncrementalDecoderStopOnFailure(IncrementalDecoder):
    def __init__(self, other: IncrementalDecoder) -> None:
        super().__init__("stop")
        self._decoder: IncrementalDecoder = other
        self._has_error = False
        self._out_buffer: str = ""

    def decode(self, input: bytes, final: bool = False) -> str:
        if self._has_error:
            return ""  # Does not decode until reset
        try:
            output = self._decoder.decode(input, final)
        except UnicodeDecodeError:
            output = ""
            self._has_error = True
        except BaseException as error:
            log.error(error)
            output = ""
            self._has_error = True
        self._out_buffer += output
        return output

    def reset(self) -> None:
        self._has_error = False
        self._out_buffer = ""
        self._decoder.reset()

    def getstate(self) -> Tuple[bytes, int]:
        return self._decoder.getstate()

    def setstate(self, state: Tuple[bytes, int]) -> None:
        return self._decoder.setstate(state)
