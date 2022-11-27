from PyAsoka.Environment.BuildParameters import BuildParameters
from PyAsoka.Environment.Module import Package


class PythonEnvironment:
    @staticmethod
    def check(package: Package):
        if package.params.architecture == BuildParameters.Architecture.LINUX \
                and package.params.system == BuildParameters.System.MANJARO:
            pass  # TODO

    @staticmethod
    def install_script(package: Package):
        script = ''
        arch, sys = package.params.architecture, package.params.system
        Arch, Sys = BuildParameters.Architecture, BuildParameters.System

        if arch == Arch.LINUX and sys == Sys.MANJARO:
            script = f'\nsudo pip3 install {package.name}'
            if package.version is not None:
                script += f'=={package.version}'

        return script + '\n'
