from PyAsoka.src.Debug.Logs import Logs

from enum import IntEnum, auto
from selenium import webdriver


class Browser:

    class Name(IntEnum):
        EDGE = 1
        CHROME = 2
        OPERA = 3

    class Tab:
        def __init__(self, browser, handle, name):
            self.browser = browser
            self.handle = handle
            self.name = name
            self.url = None

        def open(self):
            self.browser.openTab(self)

    @staticmethod
    def getDriver(name):
        drivers = {
            Browser.Name.EDGE: Browser.edgeDriver,
            Browser.Name.CHROME: Browser.chromeDriver,
            Browser.Name.OPERA: Browser.operaDriver
        }
        return drivers.get(name)()

    @staticmethod
    def edgeDriver():
        Logs.message('Initialized Edge driver')
        return webdriver.Edge()

    @staticmethod
    def chromeDriver():
        Logs.message('Initialized Chrome driver')
        return webdriver.Chrome()

    @staticmethod
    def operaDriver():
        Logs.message('Initialized Opera driver')
        options = webdriver.ChromeOptions()
        options.binary_location = 'C:\\Users\\Демьян\\AppData\\Local\\Programs\\Opera GX'
        options.add_argument('allow-elevated-browser')
        return webdriver.Opera(options=options)

    def __init__(self, browser_name: Name):
        self._driver_ = self.getDriver(browser_name)
        self._tabs_ = []
        self._current_tab_ = None

    @property
    def driver(self):
        return self._driver_

    @property
    def currentTab(self):
        return self._current_tab_

    def getTab(self, arg):
        if isinstance(arg, int):
            if arg < len(self._tabs_):
                return self._tabs_[arg]
            else:
                return None
        elif isinstance(arg, str):
            for tab in self._tabs_:
                if tab.name == arg:
                    return tab
            return None

    def openTab(self, tab):
        self.driver.switch_to.window(tab.handle)

    def openTabByNumber(self, number):
        if number < len(self._tabs_):
            self.openTab(self._tabs_[number])

    def openSite(self, url):
        self.driver.get(url)
        self.checkTab(url)

    def checkTab(self, current_url):
        handle, checked, current_tab = self.driver.current_window_handle, False, None
        for tab in self._tabs_:
            if tab.handle == handle:
                checked = True
                current_tab = tab

        if not checked:
            current_tab = Browser.Tab(self, handle, current_url)
            self._tabs_.append(current_tab)

        current_tab.url = current_url
        self._current_tab_ = current_tab

    def newTab(self):
        self.driver.switch_to.new_window('tab')

    def close(self):
        self.driver.close()
