from PyAsoka.src.Debug.Logs import Logs

import inspect
import traceback


class Tester:
    unites = []

    @classmethod
    def run(cls):
        for unite in cls.unites:
            unite.run()

    @classmethod
    def results(cls):
        all, successful, failed = 0, 0, 0
        for unite in cls.unites:
            all += unite.all
            successful += unite.successful
            failed += unite.failed
            unite.results()

        Logs.warning(f'Всего:', True)
        Logs.warning(f'Выполнено {all} тестов')
        Logs.warning(f'Успешно: {successful}')
        Logs.warning(f'Провалено: {failed}')


class UnitTester:

    class Test:
        def __init__(self, name, func):
            self.name = name
            self.method = func

    def __init__(self):
        self.all = 0
        self.successful = 0
        self.failed = 0
        self.exception = False
        self.tests = []
        self.current = None

        methods = inspect.getmembers(self, predicate=inspect.ismethod)
        for method in methods:
            name, func = method
            if 'test' in name or 'Test' in name:
                self.tests.append(UnitTester.Test(name, func))

        Tester.unites.append(self)

    def run(self):
        for test in self.tests:
            self.current = test
            test.method()
        self.current = None

    def exceptWithFailure(self, state: bool):
        self.exception = state

    def breakPoint(self, condition):
        self.all += 1
        if condition:
            self.successful += 1
        else:
            self.failed += 1
            if self.exception:
                raise Exception('Test failed')
            else:
                Logs.error(f'Test point failed in {self.__class__.__name__}:'
                           f'{self.current.name} at line {traceback.extract_stack()[-2].lineno}')

    def results(self):
        Logs.warning(f'Модуль {self.__class__.__name__}:', True)
        Logs.warning(f'Выполнено {self.all} тестов')
        Logs.warning(f'Успешно: {self.successful}')
        Logs.warning(f'Провалено: {self.failed}')
