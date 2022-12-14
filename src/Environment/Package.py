from enum import Enum
from PyAsoka.src.Environment.Builder import Builder
from PyAsoka.src.Debug.Logs import Logs
from PyAsoka.src.Instruments.ShellProcess import ShellProcess


class Package:

    class Type(Enum):
        SYSTEM = 'SYSTEM'
        PYTHON = 'PYTHON'
        CUSTOM = 'SCRIPT'

    def __init__(self, _type, name, version: str = None, parameters=None, supported=None):
        self.type = _type
        self.name = name
        self.version = version
        self.parameters = parameters
        self._script_ = None
        self._supported_ = supported
        self._builder_ = None

    @property
    def builder(self):
        return self._builder_

    @builder.getter
    def builder(self):
        if self._builder_ is None:
            self._builder_ = Builder.fromSystem()
        return self._builder_

    @builder.setter
    def builder(self, builder: Builder):
        self._builder_ = builder

    def isInstalled(self):
        pass

    def install(self):
        pass

    def uninstall(self):
        pass

    def createInstallScript(self):
        pass

    def createUninstallScript(self):
        pass


class PythonPackage(Package):
    def __init__(self, name, version=None, parameters=None, supported=None):
        super().__init__(Package.Type.PYTHON, name, version, parameters, supported)

    def isInstalled(self):
        script = f'pip show {self.name}'
        process = ShellProcess(script).wait()
        output = process.output.read()
        if f'Package(s) not found: {self.name}' in output:
            return False
        else:
            if self.version is not None:
                if f'Version: {self.version}' in output:
                    return True
                else:
                    return False
            else:
                return True

    def install(self):
        def parse(message):
            errors, warnings = [], []
            lines = message.split('\n')
            for line in lines:
                # print(line)
                ind = line.find(':')
                header, text = line[:ind], line[ind + 2:]
                if header == 'ERROR':
                    errors.append(text)
                elif header == 'WARNING':
                    warnings.append(text)
            return errors, warnings

        if not self.isInstalled():
            script = self.createInstallScript()
            process = ShellProcess(script).wait()
            errors, warnings = parse(process.errors.read())
            if not len(errors):
                Logs.success(f'?????????? {self.name} ????????????????????')
            else:
                mess = f'???? ?????????????? ???????????????????? ?????????? {self.name}:'
                for error in errors:
                    mess += '\n                   ' + error
                Logs.error(mess)
        else:
            Logs.warning(f'?????????? {self.name} ?????? ????????????????????')

    def uninstall(self):
        if self.isInstalled():
            script = self.createUninstallScript()
            process = ShellProcess(script).wait()
            Logs.success(f'?????????? {self.name} ????????????')
        else:
            Logs.warning(f'?????????? {self.name} ???? ????????????????????')

    def createInstallScript(self):
        builder = self.builder
        if builder.os.name == Builder.OSType.LINUX.name:
            script = f'sudo pip3 install {self.name}'
        elif builder.os.name == Builder.OSType.WINDOWS.name:
            script = f'pip3 install {self.name}'
        else:
            script = f'pip3 install {self.name}'

        if self.version is not None:
            script += f'=={self.version}'
        if self.parameters is not None:
            script += ' ' + self.parameters
        return script

    def createUninstallScript(self):
        builder = self.builder
        if builder.os.name == Builder.OSType.LINUX.name:
            script = f'sudo pip3 uninstall -y {self.name}'
        elif builder.os.name == Builder.OSType.WINDOWS.name:
            script = f'pip3 uninstall -y {self.name}'
        else:
            script = f'pip3 uninstall -y {self.name}'

        if self.version is not None:
            script += f'=={self.version}'
        return script


class SystemPackage(Package):
    def __init__(self, _type, name, version=None, parameters=None, supported=None):
        super().__init__(Package.Type.SYSTEM, name, version, parameters, supported)

    def createInstallScript(self):
        builder = self.builder
        if builder.os.name == Builder.OSType.LINUX.name:
            script = ''  # ToDo
        elif builder.os.name == Builder.OSType.WINDOWS.name:
            script = f'choco install -force --confirm {self.name}'
        else:
            raise Exception(f'?????????????????????? ?????????????? ????: {builder.os.name}')

