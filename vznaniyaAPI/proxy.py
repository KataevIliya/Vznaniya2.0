from subprocess import Popen, PIPE

import psutil as psutil


# TODO - поставить своё значение, оно должно иметь такой вид:
# TODO - путь/до/python.exe путь/до/mitmweb.py
# TODO - после установки всех библиотек mitmweb.py должно лежать в той же директории, что и python
MITMWEB_COMMAND = "mitmweb"


def kill_proc_with_childs(pid: int):
    """
    Убить процесс и все его подпроцессы.
    :param pid: PID процесса
    """
    pr = psutil.Process(pid)
    for i in pr.children(True):
        i.terminate()
    pr.terminate()


# Короче, это не класс, а большооой косыль. Копайся сам. Тут строчек мало, но я уже хз что тут писал...
# Я покопался, ничего не понял. Будущему мне удачи!
# Я всё равно ничего не понимаю... надежда только на тебя, ещё более будущий я...
class Proxy:
    def __enter__(self, show=False):
        self.process = Popen(f"{MITMWEB_COMMAND} --no-web-open-browser", shell=True, stdout=PIPE, text=True, stderr=PIPE)
        data_curl = self.process.stdout.readline()
        data = self.process.stdout.readline()
        host, port = data.split("//")[-1].split(":")
        if host == "*":
            host = "localhost"
        # noinspection HttpUrlsUsage
        self.proxy = f"{host}:{port[:-1]}"
        # noinspection HttpUrlsUsage
        self.address = "http://" + data_curl[:-1].split("//")[-1]
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        kill_proc_with_childs(self.process.pid)

    def restart(self):
        """
        Эта функция должна (по идее) открывать и закрывать прокси.
        Перезапуск, короче
        """
        self.__exit__(None, None, None)
        self.__enter__()
