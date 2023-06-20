from selenium.webdriver.common.by import By

from vznaniyaAPI.solvers.base import SolverBase


class FlashcardSolver(SolverBase):
    """
    Солвер для задания "проверь"
    """
    solver_name = "flashcard"
    solver_name_in_config = "FLASHCARD_XPATHS"

    def solve_word(self):
        # Ждем кнопку - тыкаем на кнопку
        self.wait_to_loading_elem(self.config.get("FLASHCARD_XPATHS", "next_button"))
        self.stamp.find_element(By.XPATH, self.config.get("FLASHCARD_XPATHS", "next_button")).click()