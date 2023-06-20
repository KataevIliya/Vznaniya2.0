from selenium.webdriver.common.by import By

from vznaniyaAPI.solvers.base import SolverBase, ExerciseUnsolvableError


class FillGameSolver(SolverBase):
    """
    Солвер для задания "заполни пропуски"
    """
    solver_name = "fill_game"
    solver_name_in_config = "FILL_GAME_XPATHS"

    def solve_word(self):
        # Ждём, пока не отобразится слово
        self.wait_to_loading_elem(self.config.get("FILL_GAME_XPATHS", "word"))
        # Получаем слово
        question = self.stamp.find_element(By.XPATH, self.config.get("FILL_GAME_XPATHS", "word")).text
        # Ищем его перевод
        word = None
        for w in self.words:
            if w.translate == question:
                word = w.text
        if word is None:
            # Если его нет - летим к ежам зелёным.
            raise ExerciseUnsolvableError(f"Word {question} doesn't exist!")

        # Список всех буковок (и пропущенных и нет)
        item_paths = []
        # Сколько слов в ответе
        blocks_count = len(
            self.stamp.find_element(
                By.XPATH,
                self.config.get("FILL_GAME_XPATHS", "locate_blocks")
            ).find_elements(
                By.CLASS_NAME,
                self.config.get("BASE", "block_class")
            )
        )
        # Перебираем слова
        for block in range(1, blocks_count + 1):
            # Сколько букв в конкретном слове
            items_count = len(
                self.stamp.find_element(
                    By.XPATH,
                    self.config.get("FILL_GAME_XPATHS", "locate_items").format(block=block)
                ).find_elements(
                    By.TAG_NAME,
                    self.config.get("BASE", "item_class")
                )
            )
            # Перебираем буквы
            for item in range(1, items_count + 1):
                self.wait_to_loading_elem(self.config.get("FILL_GAME_XPATHS", "item").format(block=block, num=item))
                item_paths.append(self.stamp.find_element(By.XPATH, self.config.get("FILL_GAME_XPATHS", "item").format(block=block, num=item)))

        # Ну, тут всё понятно
        for let, item in zip(word, item_paths):
            # Проверяем, пустая ли буква
            if item.get_attribute(self.config.get("BASE", "input_items_attribute")) is None:
                # Если да - заполняем
                item.send_keys(let)
