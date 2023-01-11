from PyAsoka.src.Environment.Package import Package
from PyAsoka.src.Environment.Builder import Builder


class Fitting:
    def __init__(self, params: Builder):
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
