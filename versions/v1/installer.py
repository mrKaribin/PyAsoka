import os


def install_pylibs():
    os.system('pip3 install vosk')
    # os.system('pip install pyttsx3 ')
    os.system('pip3 install pyaudio')
    os.system('pip3 install pymorphy2 ')
    os.system('sudo pacman -S rhvoice')
    os.system('sudo pacman -S scons gcc flite expat pkg-config speech-dispatcher boost')
    os.system('git clone https://github.com/Olga-Yakovleva/RHVoice')
    current_dir = os.getcwd()
    os.chdir('RHVoice')
    os.system('git submodule update --init')
    os.system('scons')
    os.system('sudo scons install')
    os.system('sudo ldconfig')
    os.system('sudo ln -sv /usr/local/lib/libRHVoice_core.so.7 /usr/lib/libRHVoice_core.so.7')
    os.system('sudo ln -sv /usr/local/lib/libRHVoice_core.so.6 /usr/lib/libRHVoice_core.so.6')
    os.chdir(current_dir)

    os.system('pip3 install pyautogui')
    os.system('pip3 install pynput')


install_pylibs()