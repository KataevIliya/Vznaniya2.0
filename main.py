from os import environ
from pprint import pprint

from vznaniyaAPI import User
from vznaniyaAPI.proxy import Proxy
from vznaniyaAPI.solve_manager import SolveManager
from vznaniyaAPI.solvers import *

# Предупрежу, в подклассах солвера тестов комментов нет, так как всё по аналогии с другими солверами.


# Логины и пароли
TestUser = ("Login", "Password")



# Это красивый, удобный способ открыть прокси так, чтоб ничего не упало...
# Есть и другие способы, но их использование требует знания кода, да и вряд ли они вам будут нужны.
with Proxy() as proxy:
    # Эту строчку расскомменть, если хочешь убрать окошечко браузера
    # environ["IS_CHROME_BROWSER_HEADLESS"] = "Да чё угодно тут напиши, хоть PIN-код от MasterCard"

    # Просто отладочные данные, может, они вам чего-то да скажут
    print("============DEBUG DATA===========")
    print("Proxy:", proxy.proxy)
    print("Monitor:", proxy.address)

    # Создаём юзера
    I = User(*TestUser)

    # Получаем модуль с заданным именем
    # (самый быстрый способ, но он всё равно ооооочень медленно работает, если этот модуль просрочен или уже сделан.)
    # for mod in I.get_modules(True):
    #     if mod.name == "Имя модуля прям точь-в-точь...":
    #         break

    # Получение списка модулей и выбор соответствующего
    mods = I.get_active_modules()
    print("==========ACTIVE MODULES=========")
    for i, mod in enumerate(mods, 1):
        print(f"{i}.\t\"{mod.name}\"")
    print("=================================")
    n = 0
    while n > len(mods) or n < 1:
        n = int(input("Please, write module num:\n>> "))
        if n > len(mods):
            print("Incorrect Index!")
            print("=================================")
    mod = mods[n - 1]

    # Немного отладочных данных... которые вам не нужны
    # pprint(mod.data)

    # Собираем решалку для модуля
    solve_manager = SolveManager(I, mod, proxy, debug=True)

    # Решить все задачи в этом модуле
    solve_manager.add_all()

    # Как пример, решить два раза "скрэмбл", один раз "послушай" и тест
    # solve_manager.add_solver(UnscrambleSolver)
    # solve_manager.add_solver(UnscrambleSolver)
    # solve_manager.add_solver(ListenSolver)
    # solve_manager.add_solver(TestSolver)

    # Пока ещё осталось что решать
    while solve_manager:
        # Решаем
        solve_manager.next()

    # И вырубаем всё нафиг!
    solve_manager.close()

    print("=================================")
