from PyAsoka.Environment.Fit import Fit
from PyAsoka.Environment.Package import Package
from PyAsoka.Environment.Builder import Builder as Params


params = Params(Params.Architecture.LINUX, Params.System.MANJARO)
fit = Fit(params)\
    .addPackage(Package(params, Package.Type.SYSTEM, 'python', '3.10.5-1'))\
    .addPackage(Package(params, Package.Type.SYSTEM, 'rhvoice', '1.8.0-1'))\
    .addPackage(Package(params, Package.Type.SYSTEM, 'scons', '4.3.0-3'))\
    .addPackage(Package(params, Package.Type.SYSTEM, 'gcc', '12.1.0-2'))\
    .addPackage(Package(params, Package.Type.SYSTEM, 'flite', '2.2-1'))\
    .addPackage(Package(params, Package.Type.SYSTEM, 'expat', '2.4.8-1'))\
    .addPackage(Package(params, Package.Type.SYSTEM, 'pkgconf', '1.8.0-1'))\
    .addPackage(Package(params, Package.Type.SYSTEM, 'speech-dispatcher', '0.11.1-3'))\
    .addPackage(Package(params, Package.Type.SYSTEM, 'boost', '1.79.0-1'))\
    .addPackage(Package(params, Package.Type.PYTHON, 'vosk', '0.3.42'))\
    .addPackage(Package(params, Package.Type.PYTHON, 'pyaudio', '0.2.11'))\
    .addPackage(Package(params, Package.Type.PYTHON, 'pymorphy2', '0.9.1'))\
    .addPackage(Package(params, Package.Type.PYTHON, 'pyautogui', '0.9.53'))\
    .addPackage(Package(params, Package.Type.PYTHON, 'pynput', '1.7.6'))

script = fit.create_install_script()
file = open('installer.sh', 'w')
file.write(script)
file.close()
