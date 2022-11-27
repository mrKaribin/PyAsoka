from PyAsoka.Environment.Module import Package
from PyAsoka.Environment.BuildParameters import BuildParameters


class Fitting:
    def __init__(self, params: BuildParameters):
        self.params = params
        self.packages = []

    def addPackage(self, package: Package):
        if package.params == self.params:
            self.packages.append(package)
            return self
        else:
            raise Exception('Параметры установки пакета не соответствуют параметрам установки сборки')

    def create_install_script(self):
        script = '#!/bin/bash\n'
        for package in self.packages:
            script += package.create_install_script()
        return script
