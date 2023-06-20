from selenium.webdriver.common.by import By

from vznaniyaAPI.solvers.base import SolverBase, ExerciseUnsolvableError


class TypeInSolver(SolverBase):
    """
    Солвер для задания "введи слова"
    """
    solver_name = "type_in"
    solver_name_in_config = "TYPE_IN_XPATHS"

    def solve_word(self):
        # Банально читаем слово
        self.wait_to_loading_elem(self.config.get("TYPE_IN_XPATHS", "word"))
        question = self.stamp.find_element(By.XPATH, self.config.get("TYPE_IN_XPATHS", "word")).text
        word = None

        # Банально ищем перевод
        for w in self.words:
            if w.translate == question:
                word = w.text

        # Банально посылае за хлебом, если его нет
        if word is None:
            raise ExerciseUnsolvableError(f"Word {question} doesn't exist!")

        # Тупо вводим его в поле внизу
        self.wait_to_loading_elem(self.config.get("TYPE_IN_XPATHS", "input"))
        self.stamp.find_element(By.XPATH, self.config.get("TYPE_IN_XPATHS", "input")).send_keys(word)
