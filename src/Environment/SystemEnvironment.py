import subprocess

from PyAsoka.src.Environment.Builder import Builder
from PyAsoka.src.Environment.Package import Package


class SystemEnvironment:
    @staticmethod
    def check(package: Package):
        if package.params.architecture == Builder.Architecture.LINUX \
                and package.params.system == Builder.System.MANJARO:
            script = f'pacman -Q {package.name}'
            if package.version is not None:
                script += f'={package.version}'
            result = subprocess.getoutput(script)
            return result.find(package.name) != -1

    @staticmethod
    def install_script(package: Package):
        script = ''
        arch, sys = package.params.architecture, package.params.system
        Arch, Sys = Builder.Architecture, Builder.System

        if arch == Arch.LINUX and sys == Sys.MANJARO:
            if package.version is not None:
                script = f'''
NAME="{package.name}"
VERSION="{package.version}"
PACKAGE="$NAME=$VERSION"
RESULT=`pacman -Q $PACKAGE`
if [ "$RESULT" = "$NAME $VERSION" ]; 
then
echo "$NAME already installed"
else
echo "Installing: $NAME $VERSION"
sudo pacman -Sy $PACKAGE --noconfirm
fi
'''
            else:
                script += f'''
PACKAGE="{package.name}"
RESULT=`pacman -Q $PACKAGE`
if [[ $RESULT =~ $PACKAGE ]]; 
then
echo "$PACKAGE already installed"
else
echo "Installing: $PACKAGE"
sudo pacman -Sy $PACKAGE --noconfirm
fi
'''

        return script
