from queue import Queue
from time import sleep
from typing import NewType, Any

from vznaniyaAPI import User, Module
from vznaniyaAPI.proxy import Proxy
from vznaniyaAPI.solvers import *
from vznaniyaAPI.solvers.base import NullSolver

Solver = NewType("Solver", Any)


class SolveManager:
    need_to_restart = [ListenSolver, TestSolver]
    solvers_dict = {
        'find_word': MatchesSolver,
        'insert_missed': FillGameSolver,
        'learn_word': FlashcardSolver,
        'listen': ListenSolver,
        'scrabble': UnscrambleSolver,
        'write_word': TypeInSolver
    }
    tasks = ["listen", "find_word", "learn_word", "scrabble", "insert_missed", "write_word"]

    def __init__(self, user: User, module: Module, proxy: Proxy, debug: bool = False):
        """
        Короче, самая главная штука. Она управляет солверами и решает твои задания.

        :param user: От имени какого пользователя будет осуществляться решение.
        :param module: Модуль, который будет решаться.
        :param proxy: Прокси для перехвата запросов.
        :param debug: Надо ли выводить красиво в консольку тебе всё.
        """
        self.actions = Queue()
        self.user = user
        self.module = module
        self.proxy = proxy
        self.stamp = None
        if not debug:
            self.debug = lambda *a, **b: None
        else:
            self.debug = print

    def add_all(self):
        """
        Добавить в очередь солверы для всех заданий, которые есть в модуле.
        """
        self.debug("========ADDING ALL SOLVERS=======")
        try:
            tasks = self.module.data["additional_info"]["tasks"]
        except KeyError:
            raise ValueError("Incorrect module data!")
        for task in self.tasks:
            if task not in tasks:
                continue
            self.debug(f"Find {tasks[task]} exersice \"{task}\":")
            for _ in range(int(tasks[task])):
                # noinspection PyTypeChecker
                solver = self.solvers_dict.setdefault(task, NullSolver)
                self.debug(f"    Adding solver \"{solver.__name__}\"")
                self.add_solver(solver)
        self.debug(f"Find 1 exersice \"test\":")
        self.debug(f"    Adding solver \"{TestSolver.__name__}\"")
        self.add_solver(TestSolver)

    def add_solver(self, solver: Solver):
        """
        Добавить солвер в очередь.

        :param solver: Солвер, который нужно добавить.
        """
        self.actions.put(solver)

    def __bool__(self):
        return not self.actions.empty()

    def close(self):
        """
        Взорвать нафиг этот штамп браузера!
        За МОНОЛИИИТ!
        """
        if self.stamp is None:
            return
        self.debug("========CLOSING STAMP============")
        self.debug("Clear session...   ", end="")
        self.stamp.delete_all_cookies()
        self.stamp.execute_script("window.localStorage.clear();")
        self.debug("complete!")
        self.debug("Closing stamp...   ", end="")
        self.stamp.close()
        self.stamp.quit()
        self.debug("complete!")
        self.debug("Restart proxy...   ", end="")
        sleep(2)
        self.proxy.restart()
        sleep(3)
        self.debug("complete!")

    def __debug_progress(self, n, a):
        if n != a:
            self.debug(f"\rSolve progres...  {n}/{a}\t-\t[{round(100 * n / a)}%]", end="")
        else:
            self.debug(f"\rSolve progres...  all!")

    def next(self) -> True:
        """
        Запускает следующий солвер из очереди.

        :return: True если чего-то решил. False если нечего решать.
        """
        # Берем следующий солвер
        solver = self.actions.get()
        # Если его нету, сдыхаем.
        if solver is None:
            self.close()
            return False
        # Если перед ним надо перезапустить штамп, так и делаем
        if solver in self.need_to_restart:
            self.close()
            self.stamp = None
        self.debug("===========RUN SOLVER============")
        self.debug(f"Running solver {solver.__name__}")
        # Ну, типа собираем
        sr = solver(
            proxy=self.proxy.proxy,
            dump_address=self.proxy.address,
            config_file=self.user.config,
            reuse_stamp=self.stamp,
            on_new_word=self.__debug_progress
        )
        # Иницим юзера только если до этого у нас не был открыт штамп. Иначе он там уже зареган и грохгется всё к чертовой бабушке.
        if self.stamp is None:
            self.debug("Init user...      ", end="")
            sr.init_solver(self.user)
            self.debug("complete!")
        else:
            self.debug("User already inited!")
        # Иницим модуль, который будем решать
        self.debug("Init module...    ", end="")
        sr.init_module(self.module)
        self.debug("complete!")
        # Вы не поверите..... решаем его!
        # if solver == TestSolver:
        #     self.debug("Solving test...   ", end="")
        sr.solve()
        # if solver == TestSolver:
        #     self.debug("complete!")
        # Обновляем штамп
        self.stamp = sr.stamp
        # Говорим оки-доки мы негры, мы всё решили.
        return True
