from time import sleep

from selenium.webdriver.common.by import By

from vznaniyaAPI.solvers.base import SolverBase, ExerciseUnsolvableError


class UnscrambleSolver(SolverBase):
    """
    Солвер для задания "скрэмбл"
    """
    solver_name = "unscramble"
    solver_name_in_config = "UNSCRAMBLE_XPATHS"

    def solve_word(self):
        # Банально читаем слово
        self.wait_to_loading_elem(self.config.get("UNSCRAMBLE_XPATHS", "word"))
        question = self.stamp.find_element(By.XPATH, self.config.get("UNSCRAMBLE_XPATHS", "word")).text
        # Деволтный поиск перевода...
        word = None
        for w in self.words:
            if w.translate == question:
                word = w.text

        # ...и отправление пользователя к синему коню, если его нет.
        if word is None:
            raise ExerciseUnsolvableError(f"Word {question} doesn't exist!")

        # Перебираем перевод по буковкам
        for let in word:
            # Перебираем буковки внизу
            n = 1
            while True:
                # Берём конкретную буковку
                self.wait_to_loading_elem(self.config.get("UNSCRAMBLE_XPATHS", "letter").format(num=n))
                now_let = self.stamp.find_element(By.XPATH, self.config.get("UNSCRAMBLE_XPATHS", "letter").format(num=n))
                # Бам! Они совпали, что же делать?
                if (let, now_let.text) == (" ", "") or let == now_let.text:
                    # Наверное, ткнуть на неё и идти нафиг
                    now_let.click()
                    # Слип НУЖЕН, сервер не выносит слишком быстрого решения скрэмбла. Проблема не моя - руки на столе.
                    sleep(.2)
                    break
                n += 1
