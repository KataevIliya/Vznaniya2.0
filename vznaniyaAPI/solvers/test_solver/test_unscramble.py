from itertools import count
from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from vznaniyaAPI.solvers.base import ExerciseUnsolvableError


def TestUnscramble(self, locate: WebElement):
    tasks = []
    for task_num in count(1):
        try:
            tasks.append(
                locate.find_element(
                    By.XPATH,
                    self.config.get(
                        "FINAL_TEST_XPATHS",
                        "local_unscramble_tasks"
                    ).format(
                        num=task_num
                    )
                )
            )
        except NoSuchElementException:
            break

    for task in tasks:
        self.wait_to_loading_elem_local(task, self.config.get("FINAL_TEST_XPATHS", "local_scrambled_word"))
        question = task.find_element(By.XPATH, self.config.get("FINAL_TEST_XPATHS", "local_scrambled_word")).text
        word = None
        for w in self.words:
            if w.translate == question:
                word = w.text

        if word is None:
            raise ExerciseUnsolvableError(f"Word {question} doesn't exist!")

        for let in word:
            n = 1
            while True:
                self.wait_to_loading_elem_local(task, self.config.get("FINAL_TEST_XPATHS", "local_letter").format(num=n))
                now_let = task.find_element(By.XPATH, self.config.get("FINAL_TEST_XPATHS", "local_letter").format(num=n))
                if (let, now_let.text) == (" ", "") or let == now_let.text:
                    now_let.click()
                    sleep(.2)
                    break
                n += 1
