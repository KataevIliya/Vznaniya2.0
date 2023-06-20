from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from vznaniyaAPI.solvers.base import SolverBase, ExerciseUnsolvableError


class MatchesSolver(SolverBase):
    """
    Солвер для задания "найди пару"
    """
    solver_name = "match"
    solver_name_in_config = "MATCHES_XPATHS"

    def solve(self):
        # Дефолт
        self.default_init_page()
        # ПОлучаем число карточек (оно не всегда равно числу слов, ибо разрабы взнаний - не самые адекватные люди. Н-да)
        card_nums = len(
            self.stamp.find_element(
                By.XPATH,
                self.config.get("MATCHES_XPATHS", "locate_pairs")
            ).find_elements(
                By.CLASS_NAME,
                self.config.get("BASE", "card_class")
            )
        )
        # Дефолт, но передаём количество карточек
        self.run_default_cycle(lambda n, a: (card_nums,))
        self.default_press_submit_button()

    def solve_word(self, card_nums):
        # Ищем выбранную карточку
        selected = None
        row = None
        for r in range(1, 3):
            for i in range(1, card_nums + 1):
                card = self.stamp.find_element(By.XPATH, self.config.get("MATCHES_XPATHS", f"row{r}").format(num=i))
                if self.config.get("BASE", "selected_card_class") in card.get_attribute("class"):
                    selected = card.find_element(By.XPATH, self.config.get("MATCHES_XPATHS", "local_text")).text
                    row = r

        if selected is None:
            # Если её нет, иди-ка ты лесом.
            raise ExerciseUnsolvableError("Any card doesn't selected!")

        # Ищем перевод
        translated = None
        for word in self.words:
            if row == 1:
                if word.translate == selected:
                    translated = word.text
            else:
                if word.text == selected:
                    translated = word.translate

        if translated is None:
            # Если его нет, иди-ка ты более далёким лесом.
            raise ExerciseUnsolvableError(f"Word {selected} doesn't exist!")

        # Ижем карточку с нужным переводом в противоположном столбце
        for i in range(1, card_nums + 1):
            card = self.stamp.find_element(By.XPATH, self.config.get("MATCHES_XPATHS", f"row{3 - row}").format(num=i))
            card_word = card.find_element(By.XPATH, self.config.get("MATCHES_XPATHS", "local_text"))
            if card_word.text == translated:
                while True:
                    if EC.element_to_be_clickable(card_word):
                        # Кликаем на неё (да, стандартное .click() не всегда работает, ибо читай первый коммент)
                        self.stamp.execute_script("arguments[0].click();", card_word)
                        return

        # Если дошли до сюда, значит перебрали все варианты и перевода не нашли
        # Да пусть идут юзеры азербайджанским лесом!
        raise ExerciseUnsolvableError(f"Word {translated} doesn't been on screen!")
