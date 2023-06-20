import os
import sys

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from .request_executer import Atom


class AtomWithStamp(Atom):
    def __init__(
            self,
            config_file = os.path.join(
                *os.path.split(__file__)[:-1],
                "constants.ini"
            ),
            host: str = None,
            proxy: str = None,
            dump_address: str = None,
            reuse_stamp = None
    ):
        """
        Базовый элемент со встроенным драйвером

        :param config_file: Файл с константами - или открытый ConfigParser, или путь к файлу.
        :param host: Хост, с которого совершает запросы RequestExecuter
        :param proxy: Адрес прокси
        :param dump_address: Адрес монитора прокси
        :param reuse_stamp: Либо None, либо Crome. Если передан Crome, не моздаёт новое окно.
        """
        super().__init__(config_file, host)
        self.proxy: str = proxy
        self.dump_address: str = dump_address
        self.stamp: webdriver.Chrome = NotImplemented
        if reuse_stamp is None:
            self.create_stamp()
        else:
            self.stamp: webdriver.Chrome = reuse_stamp

    @property
    def actions(self) -> ActionChains:
        """
        :return: Этот объект нужен для эмуляции нажатия клавиш
        """
        return ActionChains(self.stamp)

    def wait_to_loading_elem(self, elem, by=By.XPATH):
        """
        Ожидание загрузки элемента.

        :param elem: Элемент (его XPATH, CLASS_NAME, и т. п.)
        :param by: Классификатор, по которому определяется элемент (XPATH, CLASS_NAME и т. п.)
        """
        while True:
            try:
                self.stamp.find_element(by, elem)
                return
            except NoSuchElementException:
                pass

    @staticmethod
    def wait_to_loading_elem_local(locate: WebElement, elem: WebElement, by=By.XPATH):
        """
        Ожидает загрузки по локальному пути

        :param locate: Главный обхект (откуда счтается путь)
        :param elem: Элемент (его XPATH, CLASS_NAME, и т. п.)
        :param by: Классификатор, по которому определяется элемент (XPATH, CLASS_NAME и т. п.)
        """
        while True:
            try:
                locate.find_element(by, elem)
                return
            except NoSuchElementException:
                pass

    def create_stamp(self):
        """
        Создаёёт новый экземпляр Chrome
        """
        try:
            # Закрываем старый, если он есть вообще
            self.stamp.close()
        except AttributeError:
            pass
        options = webdriver.ChromeOptions()
        # Звук вырубать НЕ НАДО, ХУЖЕ БУДЕТ, УЖ ПОВЕРЬ
        # А нет, будет только лучше...
        options.add_argument("--mute-audio")
        options.add_argument("--incognito")
        # Проверяем, надо ли убирать окно
        if "IS_CHROME_BROWSER_HEADLESS" in os.environ:
            options.add_argument("--headless")
        # Подключаем прокси
        if self.proxy is not None:
            options.add_argument(f"--proxy-server={self.proxy}")
            options.add_argument("--proxy-type=http")
        self.stamp: webdriver.Chrome = webdriver.Chrome(chrome_options=options, executable_path=(
            self.config.get("BASE", "linux_driver") if sys.platform in ["linux", "linux2"]
            else self.config.get("BASE", "windows_driver")
        ))

    def close_proxy_window(self):
        """
        УСТАР. УЖЕ НЕ НУЖНО.
        Закрывает окно "Небесопасное подключение".
        """
        self.wait_to_loading_elem(self.config.get("SERVICE_XPATHS", "details"))
        self.stamp.find_element(By.XPATH, self.config.get("SERVICE_XPATHS", "details")).click()
        self.wait_to_loading_elem(self.config.get("SERVICE_XPATHS", "proceed_link"))
        self.stamp.find_element(By.XPATH, self.config.get("SERVICE_XPATHS", "proceed_link")).click()

    def create_tab(self, url: str):
        """
        Создвёт новую вкладку справа.
        :param url: URL, который загружается во вкладке.
        """
        self.stamp.execute_script(f"window.open('{url}');")

    def go_to_tab(self, num: int):
        """
        Перейти на другую вкладку

        :param num: Номрер вкладки
        """
        # noinspection PyDeprecation
        self.stamp.switch_to_window(self.stamp.window_handles[num])

    def close_tab(self, num: int):
        """
        Закрыть вкладку.

        :param num: Номер вкладки, которую надо закрыть.
        """
        self.stamp.window_handles[num].close()

    def close(self):
        """
        Закрытие окна браузера. Завершение процесса браузера.
        """
        self.stamp.delete_all_cookies()
        self.stamp.execute_script("window.localStorage.clear();")
        self.stamp.close()
        self.stamp.quit()
        self.stamp = NotImplemented
