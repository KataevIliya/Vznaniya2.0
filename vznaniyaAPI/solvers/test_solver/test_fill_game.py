from itertools import count

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from vznaniyaAPI.solvers.base import ExerciseUnsolvableError


def TestFillGame(self, locate: WebElement):
    tasks = []
    for task_num in count(1):
        try:
            tasks.append(
                locate.find_element(
                    By.XPATH,
                    self.config.get(
                        "FINAL_TEST_XPATHS",
                        "local_listen_tasks"
                    ).format(
                        num=task_num
                    )
                )
            )
        except NoSuchElementException:
            break

    for task in tasks:
        self.wait_to_loading_elem_local(task, self.config.get("FINAL_TEST_XPATHS", "local_fill_game_word"))
        question = task.find_element(By.XPATH, self.config.get("FINAL_TEST_XPATHS", "local_fill_game_word")).text

        word = None
        for w in self.words:
            if w.translate == question:
                word = w.text

        if word is None:
            raise ExerciseUnsolvableError(f"Word {question} doesn't exist!")

        item_paths = []

        blocks = task.find_element(
            By.XPATH,
            self.config.get("FINAL_TEST_XPATHS", "local_blocks_locate")
        ).find_elements(
            By.TAG_NAME,
            self.config.get("FINAL_TEST_XPATHS", "local_block")
        )
        for block in blocks:
            items = block.find_elements(
                By.TAG_NAME,
                self.config.get("FINAL_TEST_XPATHS", "local_item")
            )
            for item in items:
                item_paths.append(item.find_element(By.XPATH, self.config.get("FINAL_TEST_XPATHS", "local_input")))

        for let, item in zip(word, item_paths):
            if item.get_attribute(self.config.get("BASE", "input_items_attribute")) is None:
                item.send_keys(let)
