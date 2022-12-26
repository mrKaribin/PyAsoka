from PyAsoka.Environment.Package import Package
from PyAsoka.Environment.Builder import Builder
from PyAsoka import Asoka


class Fit:
    def __init__(self):
        self._packages_ = []

    def addPackage(self, package: Package):
        self._packages_.append(package)
        return self

    def compatibleWith(self, os_type):
        incompatible = []
        for package in self._packages_:
            if package._supported_ is not None:
                ok = False
                for os in package._supported_:
                    if os == os_type:
                        ok = True
                if not ok:
                    incompatible.append(package.name)
        if len(incompatible) == 0:
            return Asoka.Results(True)
        else:
            return Asoka.Results(False, data={'incompatible': incompatible})

    def install(self):
        for package in self._packages_:
            package.install()

    def create_install_script(self):
        script = '#!/bin/bash\n'
        for package in self._packages_:
            script += '\n' + package.create_install_script() + '\n'
        return script
