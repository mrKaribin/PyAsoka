from PyAsoka.src.Services.YandexMusic.Track import Track
from PyAsoka.src.Services.YandexMusic.Playlist import Playlist
from PyAsoka.src.Services.YandexMusic.Tracklist import Tracklist
from PyAsoka.Asoka import Asoka

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.remote.command import Command
from yandex_music import Client
from yandex_music.account.user_settings import UserSettings

import json
import os
from time import sleep


class Account:
    VariableName = 'AsokaMusic'
    _account_ = None

    def __init__(self):
        self._settings_ = Account.checkSettings()
        self._token_ = self.checkToken()
        self._client_ = None
        self._account_settings_ = None
        if self._token_ is not None:
            self.init()

    @property
    def ok(self):
        return self._token_ is not None

    @property
    def token(self):
        return self._token_

    @property
    def settings(self):
        return self._settings_

    @property
    def client(self) -> Client:
        return self._client_

    @property
    def accountSettings(self) -> UserSettings:
        return self._account_settings_

    def init(self):
        self._client_ = Client(self.token).init()
        self._account_settings_ = self._client_.account_settings()
        Account._account_ = self

    def getLikesPlaylist(self):
        return Tracklist(self._client_.users_likes_tracks())

    def playlists(self):
        return [Playlist(playlist) for playlist in self.client.users_playlists_list(user_id=self.accountSettings.uid)]

    def searchTracks(self, text):
        search = self._client_.search(text, type_='track', playlist_in_best=False)
        results = search.tracks.results
        tracks = []
        for result in results:
            tracks.append(Track(result))
        return tracks

    def saveSettings(self):
        Asoka.Variables.set(Account.VariableName, self._settings_)

    def checkToken(self):
        if self._settings_ is None or self._settings_['token'] is None:
            # try:
            token = Account.getToken()
            if self._settings_ is None:
                self._settings_ = {'token': token}
            self.saveSettings()
            return token
            # except Exception as e:
            #     print('Не удалось авторизоваться через Яндекс:', e)
            #     return None
        else:
            return self._settings_['token']

    @staticmethod
    def checkSettings():
        return Asoka.Variables.get(Account.VariableName)

    @staticmethod
    def isDriverActive(driver):
        try:
            driver.execute(Command.GET_ALL_COOKIES)
            return True
        except Exception:
            return False

    @staticmethod
    def getToken():
        # make chrome log requests
        capabilities = DesiredCapabilities.CHROME
        capabilities["goog:loggingPrefs"] = {"performance": "ALL"}

        home = os.getcwd()
        os.chdir(Asoka.Project.Path.Asoka.Drivers())
        driver = webdriver.Chrome(desired_capabilities=capabilities)
        os.chdir(home)
        driver.get("https://oauth.yandex.ru/authorize?response_type=token&client_id=23cabbbdc6cd418abb4b39c32c41195d")

        token = None

        logs_raw = []
        while token is None and Account.isDriverActive(driver):
            sleep(1)
            try:
                logs_raw = driver.get_log("performance")
            except Exception as e:
                pass

            for lr in logs_raw:
                log = json.loads(lr["message"])["message"]
                url_fragment = log.get('params', {}).get('frame', {}).get('urlFragment')

                if url_fragment:
                    token = url_fragment.split('&')[0].split('=')[1]

        try:
            driver.close()
        except:
            pass

        return token


def account() -> Account:
    if Account._account_ is not None:
        return Account._account_
    else:
        raise Exception('Еще не создан объект Account')

