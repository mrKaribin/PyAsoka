from PyAsoka import Asoka

import io
import subprocess


class ShellErrors:
    def __init__(self, errors: io.BufferedReader):
        self._errors_ = errors

    def read(self):
        return str(self._errors_.read(), 'utf-8')

    def empty(self):
        return not self._errors_.readable()


class ShellOutput:
    def __init__(self, output: io.BufferedReader):
        self._output_ = output

    def read(self):
        return str(self._output_.read(), 'utf-8')


class ShellProcess:
    def __init__(self, script: str):
        self._process_ = subprocess.Popen(script, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.output = ShellOutput(self._process_.stdout)
        self.errors = ShellErrors(self._process_.stderr)

    def wait(self):
        self._process_.wait()
        return self
