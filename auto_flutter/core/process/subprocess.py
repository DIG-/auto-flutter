from pathlib import Path
from typing import Any, List, Optional, Tuple
from .process import Process
from subprocess import Popen, PIPE, STDOUT
from ..string import SB
from codecs import IncrementalDecoder, getincrementaldecoder
from ..logger import log
from ..os import OS


class _SubProcess(Process):
    __DEFAULT_DECODER: Optional[IncrementalDecoder] = None

    def run(self):
        if self._executable.is_absolute():
            if not Path(self._executable).exists():
                raise FileNotFoundError(
                    0, "Executable `{}` not found".format(self._executable)
                )
        output = SB()
        with Popen(
            [self._executable] + self._arguments,
            shell=True,
            stdout=PIPE,
            stderr=STDOUT,
            env=self._environment,
        ) as p:
            decoder: IncrementalDecoder = _SubProcess.__get_default_decoder()
            while True:
                buffer = decoder.decode(p.stdout.read(1))
                if len(buffer) > 0:
                    output.append(buffer)
                    self._write_output(buffer)
                code = p.poll()
                if not code is None:
                    self.exit_code = code
                    break
            self._write_output("\n")
            self.output = output.str()
            if self.exit_code == 127:
                raise FileNotFoundError(
                    0, "Command `{}` not found".format(self._executable)
                )

    def __get_default_decoder() -> IncrementalDecoder:
        if _SubProcess.__DEFAULT_DECODER is None:
            _SubProcess.__DEFAULT_DECODER = _SubProcess.__generate_decoder()
        return _SubProcess.__DEFAULT_DECODER

    def __generate_decoder() -> IncrementalDecoder:
        if OS.current() != OS.WINDOWS:
            return getincrementaldecoder("utf-8")()
        multiple = _IncrementalDecoderMultiple()
        multiple.add(getincrementaldecoder("utf-8")())
        from winreg import QueryValueEx, OpenKey, CloseKey, HKEY_LOCAL_MACHINE, REG_SZ

        try:  # Get windows default charset for console
            key = OpenKey(
                HKEY_LOCAL_MACHINE, "SYSTEM\\CurrentControlSet\\Control\\Nls\\CodePage"
            )
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
