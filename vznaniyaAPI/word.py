import os

from .request_executer import Atom


class Word(Atom):
    def __init__(
            self,
            data: dict,
            config_file = os.path.join(
                *os.path.split(__file__)[:-1],
                "constants.ini"
            ),
            host: str = None
    ):
        """
        Контейнер, содержащий данные конкретного слова.

        :param data: Необработанные данные.
        :param config_file: Файл с константами - или открытый ConfigParser, или путь к файлу.
        :param host:Хост, с которого совершает запросы RequestExecuter.
        """
        super().__init__(config_file, host)
        self.id = data["id"]
        self.text = data["text"]
        self.translate = data["translate"]
        self.audio = data["audio"]
        self.data = data

    def __repr__(self):
        return f"Word({self.text} -> {self.translate}, id={self.id}, audio={self.audio})"

