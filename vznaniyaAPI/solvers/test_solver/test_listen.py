from itertools import count
from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from vznaniyaAPI.solvers.base import ExerciseUnsolvableError


def TestListen(self, locate: WebElement):
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

    for task_num, task in enumerate(tasks):
        self.go_to_tab(0)
        self.wait_to_loading_elem_local(task, self.config.get("FINAL_TEST_XPATHS", "local_voice_button"))
        task.find_element(By.XPATH, self.config.get("FINAL_TEST_XPATHS", "local_voice_button")).click()
        sleep(1)
        while len(self.get_requests_list()) <= task_num:
            self.go_to_tab(0)
            self.wait_to_loading_elem_local(task, self.config.get("FINAL_TEST_XPATHS", "local_voice_button"))
            task.find_element(By.XPATH, self.config.get("FINAL_TEST_XPATHS", "local_voice_button")).click()
            sleep(.3)

        audio = self.get_requests_list()[task_num]
        label = None
        for i in self.words:
            if i.audio == audio:
                label = i.translate
        if label is None:
            raise ExerciseUnsolvableError(f"Aurio {audio} doesn't exits!")

        labels = {}
        self.go_to_tab(0)
        for i in range(1, 5):
            self.wait_to_loading_elem_local(task, self.config.get("FINAL_TEST_XPATHS", f"local_label{i}"))
            button: WebElement = task.find_element(By.XPATH, self.config.get("FINAL_TEST_XPATHS", f"local_label{i}"))
            while not button.text:
                pass
            labels[button.text] = button

        if label not in labels:
            raise ExerciseUnsolvableError(f"Word {label} doesn't show in [{', '.join(labels)}]")

        while True:
            try:
                labels[label].click()
                break
            except (BaseException, Exception):
                pass
