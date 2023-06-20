import datetime
import os
from typing import List

from .request_executer import Atom
from .word import Word

# Просто контейнер, содержащий статус по модулю
class Status:
    SOLVED = 2
    PASSED = 1
    ACTIVE = 0

    @staticmethod
    def toStr(status):
        if status == Status.SOLVED:
            return "SOLVED"
        elif status == Status.PASSED:
            return "PASSED"
        elif status == Status.ACTIVE:
            return "ACTIVE"
        return "UNKNOWN"


class Module(Atom):
    def __init__(
            self,
            id: int,
            group_id: int,
            data: dict,
            config_file = os.path.join(
                *os.path.split(__file__)[:-1],
                "constants.ini"
            ),
            host: str = None
    ):
        """


        :param id: ID урока
        :param group_id: ID группы
        :param data: Необработанные данные модуля
        :param config_file: Файл с константами - или открытый ConfigParser, или путь к файлу.
        :param host: Хост, с которого совершает запросы RequestExecuter
        """
        super().__init__(config_file, host)
        self.id: int = id
        self.group_id: int = group_id
        self.data: dict = data
        self.name: str = data["name"]
        try:
            dt = datetime.datetime.strptime(data["expires_at"], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            dt = datetime.datetime.strptime(data["expires_at"], "%Y-%m-%d")
        # Получаем статус
        if data["pass_once_current"]:
            self.status: int = Status.SOLVED
        elif dt < datetime.datetime.now():
            self.status: int = Status.PASSED
        else:
            self.status: int = Status.ACTIVE
        # Это костыль... когда-то было TO-DO на его исправление, но потом я забил
        self.cashed_words = None

    @property
    def words(self) -> List[Word]:
        """
        Слова из этого модуля (решение с костылём, но быстрее).
        :return: Список объектов Word.
        """
        if self.cashed_words is None:
            self.cashed_words = self.get_words
        return self.cashed_words

    @property
    def get_words(self) -> List[Word]:
        """
        Слова из этого модуля.
        :return: Список объектов Word.
        """
        ans = self.executer.execute_request("getWords", data={"lesson_id": self.id, "timestamp": self.timestamp}).json()
        return list(map(Word, ans["data"]))

    def __repr__(self):
        return f"Module({self.name}, id={self.id}, group_id={self.group_id}, status={Status.toStr(self.status)})"


