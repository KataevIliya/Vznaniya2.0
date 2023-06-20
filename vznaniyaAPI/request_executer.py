import calendar
import time
from configparser import ConfigParser

import requests

from vznaniyaAPI.errors import *


class RequestExecuter:
    def __init__(self, parser: ConfigParser, host: str = None):
        """
        Красиво обращается к API.
        :param parser: Файл с константами - или открытый ConfigParser, или путь к файлу.
        :param host: Хост, с которого совершаются запросы
        """
        self.config = parser
        self.host = host if host is not None else self.config.get("BASE", "host")
        self.headers = {}

    def execute_request(self, request_name: str, data: dict = None, headers: dict = None, section: str = "URL", **kwargs) -> requests.Response:
        """
        Я этот кусок со StackOwerdflow стыбрил, как работает примерно понятно, но только примерно.

        :param request_name: Имя запроса в файле.
        :param data: Даннве запроса.
        :param headers: Заголовки запроса.
        :param section: Секция в файле, где лежат запросы.
        :param kwargs: Всякая прочая хрень для request.get или request.post
        :return: Возвращает типа результат.
        """
        if data is None:
            data = {}
        if headers is None:
            headers = self.headers
        url, method = self.config.get(section, request_name).split(",")
        if method == "get":
            return requests.get(f"{self.host}{url}", params=data, headers=headers, **kwargs)
        elif method == "post":
            return requests.post(f"{self.host}{url}", data=data, headers=headers, **kwargs)
        else:
            raise UnknownMethodError

    def get(self, url, data: dict = None, headers: dict = None, hosted: bool = True, **kwargs):
        if data is None:
            data = {}
        if headers is None:
            headers = self.headers
        return requests.get(f"{self.host if not hosted else ''}{url}", params=data, headers=headers, **kwargs)


class Atom:
    def __init__(self, config_file, host):
        if type(config_file) == ConfigParser:
            self.config = config_file
        else:
            self.config: ConfigParser = ConfigParser()
            self.config.read(config_file)
        self.executer: RequestExecuter = RequestExecuter(self.config, host=host)
        self.config_file: str = config_file

    @property
    def timestamp(self):
        return calendar.timegm(time.gmtime())
