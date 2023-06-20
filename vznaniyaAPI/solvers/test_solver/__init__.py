from time import sleep

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By

from vznaniyaAPI.solvers.base import SolverBase, ProxyNotFoundError
from .test_fill_game import TestFillGame
from .test_listen import TestListen
from .test_type_in import TestTypeIn
from .test_unscramble import TestUnscramble


class TestSolver(SolverBase):
    """
    Солвер для теста
    """
    solver_name = "final_test"
    solver_name_in_config = "FINAL_TEST_XPATHS"

    def solve(self):
        # Нам проси не нужён... шутка, нужен.
        if self.proxy is None:
            raise ProxyNotFoundError
        # Тут как в ListenSolver
        self.create_tab(self.dump_address)
        self.go_to_tab(1)
        self.wait_to_loading_elem(self.config.get("SERVICE_XPATHS", "mitmproxy_search"))
        self.stamp.find_element(By.XPATH, self.config.get("SERVICE_XPATHS", "mitmproxy_search")).send_keys(".mp3")
        self.go_to_tab(0)
        # Дефолтное открытие страницы (но тут костыль, разбирайся сам)
        self.stamp.get(self.config.get("APP_URLS", self.solver_name).format(id=self.id, group_id=self.group_id))
        self.wait_to_loading_elem(self.config.get("LISTEN_XPATHS", "process_bar"))
        self.wait_to_loading_elem(self.config.get("FINAL_TEST_XPATHS", "test_tab_button"))
        self.stamp.find_element(By.XPATH, self.config.get("FINAL_TEST_XPATHS", "test_tab_button")).click()
        self.wait_to_loading_elem(self.config.get("FINAL_TEST_XPATHS", "waited_elem"))
        # Слип нужен. 5 поставил для перестраховки, но лучше не убирай, на всякий. 5 сек, не так уж и долго, правда?
        sleep(5)
        # Перебираем части теста
        parts = self.stamp.find_elements(By.XPATH, self.config.get("FINAL_TEST_XPATHS", "parts_locate"))
        for n, part in enumerate(parts):
            self.compare(n, len(parts))
            # Поиск соответствия каждой части конкретному заданию, и решение этого задания
            try:
                part.find_element(By.CLASS_NAME, self.config.get("FINAL_TEST_CHECK_CLASSES", "listen"))
                TestListen(self, part)
                continue
            except NoSuchElementException:
                pass
            try:
                part.find_element(By.CLASS_NAME, self.config.get("FINAL_TEST_CHECK_CLASSES", "unscramble"))
                TestUnscramble(self, part)
                continue
            except NoSuchElementException:
                pass
            try:
                part.find_element(By.CLASS_NAME, self.config.get("FINAL_TEST_CHECK_CLASSES", "fill_game"))
                TestFillGame(self, part)
                continue
            except NoSuchElementException:
                pass
            try:
                part.find_element(By.CLASS_NAME, self.config.get("FINAL_TEST_CHECK_CLASSES", "type_in"))
                TestTypeIn(self, part)
                continue
            except NoSuchElementException:
                pass
        self.compare(len(parts), len(parts))
        # Этот слип тоже нужен. Перед тем, как его убрать, вспомни: "Лучше посрать и опоздать, чем успеть и обостраться".
        sleep(5)

        # Хитро-мудрое завершение теста. Разобраться можно, но мне лень объяснять.
        self.wait_to_loading_elem(self.config.get("FINAL_TEST_XPATHS", "submit1"))
        self.stamp.find_element(By.XPATH, self.config.get("FINAL_TEST_XPATHS", "submit1")).click()

        while True:
            try:
                self.stamp.find_element(By.XPATH, self.config.get("FINAL_TEST_XPATHS", "submit2")).click()
            except (NoSuchElementException, StaleElementReferenceException):
                try:
                    self.stamp.find_element(By.XPATH, self.config.get("FINAL_TEST_XPATHS", "submit3")).click()
                    break
                except (NoSuchElementException, StaleElementReferenceException):
                    pass


    def get_requests_list(self):
        """
        Получение списка запросов

        :return: Список ссылок запросов.
        """
        # Переходим на вкладку мониторинга.
        self.go_to_tab(1)
        # Надо, Вася, НАДО
        sleep(.1)
        # И просто считываем все запросы
        requests = []
        for request in self.stamp.find_elements(By.CLASS_NAME, self.config.get("BASE", "mitmproxy_requests_class")):
            if request.text not in ["Path", "", None]:
                requests.append(request.text)
        return requests
