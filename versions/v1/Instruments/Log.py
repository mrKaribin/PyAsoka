import datetime
import PyAsoka.Asoka as a


def write(text, newline: bool = False):
    global mode
    text = f'{getTimeMark()} :: {text}'
    if newline:
        text = '\n' + text
    if mode == 1:
        with getLogFile() as file:
            file.write(text)
    elif mode == 2:
        print(text)


def getLogFile():
    file = open(a.dir.log(), 'a')
    file.write('\n')
    return file


def getTimeMark():
    now = datetime.datetime.now()
    return now.strftime("%d-%m-%Y %H:%M:%S")  # ToDo


def comment(text, newline=False):
    global level
    if level > 1:
        return
    write(text, newline)


def warning(text):
    if level > 2:
        return
    write(f"WARNING !!! {text}")


def error(text):
    if level > 3:
        return
    write(f"ERROR !!! {text}")


def exception_unsupportable_type(*values):
    text = f'Получен некорректный тип данных: '
    for value in values:
        text += f' {value}'
    error(text)
    raise Exception(text)


a.comment = comment
a.warning = warning
a.error = error

a.exception_unsupportable_type = exception_unsupportable_type


mode = 2
level = 1
