from PyAsoka.Environment.Builder import Builder
from PyAsoka.Environment.Package import Package


class PythonEnvironment:
    @staticmethod
    def check(package: Package):
        if package.params.architecture == Builder.Architecture.LINUX \
                and package.params.system == Builder.System.MANJARO:
            pass  # TODO

    @staticmethod
    def install_script(package: Package):
        script = ''
        arch, sys = package.params.architecture, package.params.system
        Arch, Sys = Builder.Architecture, Builder.System

        if arch == Arch.LINUX and sys == Sys.MANJARO:
            script = f'\nsudo pip3 install {package.name}'
            if package.version is not None:
                script += f'=={package.version}'

        return script + '\n'
