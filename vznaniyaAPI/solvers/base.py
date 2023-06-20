import os
from time import sleep
from typing import Callable

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from vznaniyaAPI import User
from vznaniyaAPI.atom_with_stamp import AtomWithStamp


class SolverBase(AtomWithStamp):
    def __init__(
            self,
            config_file: str = os.path.join(
                *os.path.split(__file__)[:-1],
                "constants.ini"
            ),
            host: str = None,
            proxy: str = None,
            dump_address: str = None,
            reuse_stamp = None,
            on_new_word: Callable = None
    ):
        """
        Класс, на котором базируются все солверы.

        :param config_file: Файл с константами - или открытый ConfigParser, или путь к файлу.
        :param host: Хост, с которого совершает запросы RequestExecuter
        :param proxy: Адрес прокси
        :param dump_address: Адрес монитора прокси
        :param reuse_stamp: Либо None, либо Crome. Если передан Crome, не моздаёт новое окно.
        :param on_new_word: Процедура, которая выполняется при каждом появлении нового слова.
        """
        super().__init__(config_file, host, proxy, dump_address, reuse_stamp)
        self.module_data = None
        self.words = None
        self.group_id = None
        self.id = None
        if on_new_word is None:
            on_new_word = lambda n, a: None
        self.compare = on_new_word

    solver_name = NotImplemented
    solver_name_in_config = NotImplemented

    def get_progress(self) -> (int, int):
        """
        Получение двнных о прогрессе по заданию.

        :return: (сколько слов сделано, сколько слов всего)
        """
        self.wait_to_loading_elem(self.config.get(self.solver_name_in_config, "process_bar"))
        data = self.stamp.find_element(By.XPATH, self.config.get(self.solver_name_in_config, "process_bar")).text
        a, *_, b = data.split()
        return int(a), int(b)

    def default_init_page(self):
        """
        Базовая инициализация страницы задания по умолчанию.
        """
        # Открывает страницу задания и ждёт её загрузки.
        self.stamp.get(self.config.get("APP_URLS", self.solver_name).format(id=self.id, group_id=self.group_id))
        while self.get_progress()[1] == 0:
            pass

    def init_solver(self, user: User):
        """
        Инициализация пользователя на сайте.

        :param user: Пользователь, от имени которого будет решаться модуль.
        """
        self.stamp.get(self.config.get("APP_URLS", "login"))
        self.wait_to_loading_elem(self.config.get("XPATHS", "login"))
        self.stamp.find_element(By.XPATH, self.config.get("XPATHS", "login")).send_keys(user.data["email"])
        self.stamp.find_element(By.XPATH, self.config.get("XPATHS", "password")).send_keys(user.data["password"] + Keys.ENTER)
        sleep(2)

    # noinspection PyShadowingBuiltins
    def run_default_cycle(self, gen_args: Callable = lambda now, all: ()):
        """
        Базовый цикл решения модуля.

        :param gen_args: Функция, которая из текущего прогресса формирует данные, передаваемые в solve_word
        """
        now, all = self.get_progress()
        self.compare(now, all)
        while now != all:
            self.solve_word(*gen_args(now, all))
            while self.get_progress()[0] == now:
                pass
            now, all = self.get_progress()
            self.compare(now, all)

    def default_press_submit_button(self):
        """
        Базовое нажатие на кнопку "ОК" после прохождения задания.
        """
        self.wait_to_loading_elem(self.config.get("TYPE_IN_XPATHS", "submit_button"))
        self.stamp.find_element(By.XPATH, self.config.get("TYPE_IN_XPATHS", "submit_button")).click()

    def solve_word(self, *args, **kwargs):
        """
        Решение одного слова. Определяется конкретным солвером.
        """
        raise NotImplemented

    def solve(self):
        """
        Решить всё задание
        """
        self.default_init_page()
        self.run_default_cycle()
        self.default_press_submit_button()

    def init_module(self, module):
        """
        Инициализировать модуль, который будем решать.

        :param module: Модуль, который нужно решать.
        """
        self.id = module.id
        self.group_id = module.group_id
        self.words = module.words
        self.module_data = module.data


# Мне лень перетаскивать это в errors, так что пусть будет здесь
class ProxyNotFoundError(Exception): pass
class ExerciseUnsolvableError(Exception): pass

# Фигня, которая ничего не делает
class NullSolver(SolverBase):
    def solve(self):
        pass
