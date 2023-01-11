from PyAsoka.Debug import Logs

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
        try:
            self._process_ = subprocess.Popen(script, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.output = ShellOutput(self._process_.stdout)
            self.errors = ShellErrors(self._process_.stderr)
            self._ok_ = True
        except FileNotFoundError as e:
            self._ok_ = False
            Logs.error(f'Script error: <{script}> : {e}')
            self._process_ = None
            self.output = None
            self.errors = None

    def wait(self):
        if self._ok_:
            self._process_.wait()
        return self

    def ok(self):
        return self._ok_
