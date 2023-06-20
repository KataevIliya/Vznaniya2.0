from time import sleep
from typing import List

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from vznaniyaAPI.solvers.base import SolverBase, ProxyNotFoundError, ExerciseUnsolvableError


class ListenSolver(SolverBase):
    """
    Солвер для задания "послушай"
    """
    solver_name = "listen"
    solver_name_in_config = "LISTEN_XPATHS"

    def solve(self):
        # Нам нужно прокси, мы без него никуда
        if self.proxy is None:
            raise ProxyNotFoundError
        # Создаём вторую вкладку с монитором запросов и настраиваем её.
        self.create_tab(self.dump_address)
        self.go_to_tab(1)
        self.wait_to_loading_elem(self.config.get("SERVICE_XPATHS", "mitmproxy_search"))
        self.stamp.find_element(By.XPATH, self.config.get("SERVICE_XPATHS", "mitmproxy_search")).send_keys(".mp3")
        # Переходим на первую и стандартно её запускаем.
        self.go_to_tab(0)
        self.stamp.get(self.config.get("APP_URLS", self.solver_name).format(id=self.id, group_id=self.group_id))
        self.wait_to_loading_elem(self.config.get("LISTEN_XPATHS", "voice_button"))
        while self.get_progress()[1] == 0:
            pass
        # Всё по деволту
        self.run_default_cycle(lambda n, a: (n,))
        self.default_press_submit_button()

    def solve_word(self, progress):
        # Переходим на вкладку с заданием и нажимаем на кнопку до тех пор, пока не появится аудио в списке запросов
        self.go_to_tab(0)
        self.wait_to_loading_elem(self.config.get("LISTEN_XPATHS", "voice_button"))
        self.stamp.find_element(By.XPATH, self.config.get("LISTEN_XPATHS", "voice_button")).click()
        # Этот слип очень нужен, просьба не убирать.
        sleep(1)
        while len(self.get_requests_list()) <= progress:
            self.go_to_tab(0)
            self.wait_to_loading_elem(self.config.get("LISTEN_XPATHS", "voice_button"))
            self.stamp.find_element(By.XPATH, self.config.get("LISTEN_XPATHS", "voice_button")).click()
            # А этот - не очень
            # Как оказалось - очень
            # Или нет,
            # Или да
            # После небольшого исследования, мы пришли к выводу, что он него сильно хуже не станет, так что оставляем.
            sleep(.3)
        # Получаем текущее аудио
        audio = self.get_requests_list()[progress]
        # Ищем слово, которое ему соответствует.
        label = None
        for i in self.words:
            if i.audio == audio:
                label = i.translate
        # Если такого нет - орём матом
        if label is None:
            raise ExerciseUnsolvableError(f"Aurio {audio} doesn't exits!")
        # Получаем варианты выбора ответов
        labels = {}
        self.go_to_tab(0)
        for i in range(1, 5):
            self.wait_to_loading_elem(self.config.get("LISTEN_XPATHS", f"label{i}"))
            button: WebElement = self.stamp.find_element(By.XPATH, self.config.get("LISTEN_XPATHS", f"label{i}"))
            while not button.text:
                pass
            labels[button.text] = button
        # Если нашего слова нет среди них - орём матом ещё гормче.
        if label not in labels:
            raise ExerciseUnsolvableError(f"Word {label} doesn't show in [{', '.join(labels)}]")
        # Пытаемся нажать на нужное слово, пока не нажмётся (не всегда нажимается с первого раза).
        while True:
            try:
                labels[label].click()
                break
            except (BaseException, Exception):
                pass

    def get_requests_list(self) -> List[str]:
        """
        Получение списка запросов

        :return: Список ссылок запросов.
        """
        # Переходим на вкладку мониторинга.
        self.go_to_tab(1)
        # Надо, Федя, НАДО
        sleep(.1)
        # И просто считываем все запросы
        requests = []
        for request in self.stamp.find_elements(By.CLASS_NAME, self.config.get("BASE", "mitmproxy_requests_class")):
            if request.text not in ["Path", "", None]:
                requests.append(request.text)
        return requests
