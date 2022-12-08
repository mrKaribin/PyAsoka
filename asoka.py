from PyAsoka.Core.Application import Application


defaultPassword = 'topsecretpassword'


def app() -> Application:
    return Application.current()


