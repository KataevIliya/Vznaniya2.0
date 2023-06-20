import os.path

from .errors import *
from .module import Module, Status
from .request_executer import Atom


# ИДИ НАФИГ С ЭТИМ КОДОМ. ДА НИ ОДИН ТРЕЗВЫЙ ЧЕЛОВЕК В НЁМ НЕ РАЗБЕРЁТСЯ.
# Удачи
class User(Atom):
    def __init__(
            self,
            email: str,
            password: str,
            config_file = os.path.join(
                *os.path.split(__file__)[:-1],
                "constants.ini"
            ),
            host: str = None
    ):
        """
        Контейнер, содержащий данные пользователя

        :param email: Почта пользователя
        :param password: Пароль пользователя
        :param config_file: Файл с константами - или открытый ConfigParser, или путь к файлу.
        :param host: Хост, с которого совершает запросы RequestExecuter
        """
        super().__init__(config_file, host)
        self.data = {"email": email, "password": password}

        aut_req = self.executer.execute_request("loginTo", data=self.data)
        if aut_req.status_code == 500:
            raise IncorrectLoginOrPassword
        elif aut_req.status_code != 200:
            raise UnknownError(aut_req.status_code)
        self.data.update(aut_req.json()["data"])
        self.executer.headers["Authorization"] = f"Bearer {self.data['access_token']}"

    def __get_modules(self):
        data = self.executer.execute_request("getModules", data={"timestamp": self.timestamp}).json()
        links = data["links"]
        for mod in data["data"]:
            yield Module(mod["id"], mod["group_id"], mod)
        for mod in self.__pages_iter(links["first"], links["next"], links["last"]):
            yield mod

    def get_modules(self, generator: bool = False):
        if generator:
            return self.__get_modules()
        return list(set(self.__get_modules()))

    def __get_active_modules(self):
        for mod in self.get_modules(True):
            if mod.status != Status.ACTIVE:
                break
            yield mod

    def get_active_modules(self, generator: bool = False):
        if generator:
            return self.__get_active_modules()
        return list(set(self.get_active_modules(True)))

    def __pages_iter(self, t, n, l):
        while t != l:
            new = self.executer.get(n).json()
            for m in new["data"]:
                yield Module(m["id"], m["group_id"], m)
            t = n
            n = new["links"]["next"]

