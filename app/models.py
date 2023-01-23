from abc import ABC
from dataclasses import dataclass
from typing import NoReturn, Any, Iterable, Literal, Dict
from typing import TYPE_CHECKING

from dacite import from_dict
from sortedcontainers import SortedList

from .helpers import _TimeGenerator

if TYPE_CHECKING:
    from .simulation import Simulation


@dataclass
class Distribution:
    """
    Визначає закон розподілу випадкових величин за типом та параметрами розподілу
    Дозволяє отримати екземпляр класу за заданими параметрами
     та згенерувати випадкове число за заданим законом розподілу
    """

    type_of_distribution: Literal['const', 'uniform', 'norm', 'exp']
    loc: float = 1
    scale: float = 1

    @staticmethod
    def from_dict(data: Dict) -> "Distribution":
        """
        Фабрика екземплярів класу
        :param data: параметри розподілу у вигляді словника
        :return: екземпляр класу
        """
        # TODO convert Dict into TypedDict
        return from_dict(Distribution, data)

    def get_value(self) -> float:
        """
        Генерує випадкове число на підставі характеристик розподілу
        :return:
        """
        return _TimeGenerator.generate_time(self)

    @staticmethod
    def make_sample_distribution(distro_type: Literal['const', 'uniform', 'norm', 'exp']):
        """
        Швидко генерує екземпляр класу із заданим розподілом та одиничними параметрами
        Використовується в тестах.
        :param distro_type: тип розподілу
        :return: екземпляр класу
        """
        return Distribution(type_of_distribution=distro_type, loc=1, scale=1)


class SortedQueue:
    """
    Черга з сортованими елементами. Фактично є сортованим списком, в кінець якого додається елемент,
    або з початку якого видаляється елемент. Реалізувати як повноцінну чергу не є можливим з причини необхідності
    сортування елементів.
    Включає методи, яки дозволяють уникати дублікатів при додаванні
    """

    def __init__(self):
        self._list: SortedList = SortedList()

    def __len__(self):
        return len(self._list)

    def __repr__(self):
        return f'SortedQueue: {str(self._list)}'

    @property
    def is_empty(self):
        return len(self._list) == 0

    @property
    def values(self):
        return self._list

    def check_insert(self, value: Any) -> bool:
        """
        Додавання одного елементу з перевіркою дублювання
        :param value: значення, що додається
        :return: True, якщо елемент додано, False в іншому випадку
        """
        if value in self._list:
            return False
        else:
            self.insert(value)
            return True

    def check_update(self, list_of_values: Iterable) -> NoReturn:
        """
        Додавання з перевіркою декількох елементів
        :param list_of_values: список значень
        :return: None
        """
        list_of_values = list(filter(lambda x: x not in self._list, list_of_values))
        self.update(set(list_of_values))

    def insert(self, value: Any) -> NoReturn:
        """
        Додавання елементу без перевірки дублікатів
        :param value: значення
        :return:None
        """
        self._list.add(value)

    def pop(self) -> Any:
        """
        Вилучення початкового елементу
        :return: повертає вилучений елемент
        """
        value = self._list[0]
        self._list.pop(0)
        return value

    def update(self, list_of_values: Iterable) -> NoReturn:
        """
        Додавання декількох елементів без перевірки унікальності
        :param list_of_values: перелік значень, що додаються
        :return:
        """
        self._list.update(list_of_values)

    def contains(self, value):
        """
        Перевірка входження значення
        :param value: значення
        :return: True, якщо значення знайдено, інакше False
        """
        return value in self._list


class Element(ABC):

    def __init__(self, parent: "Simulation", str_id: str = '', save_stats: bool = False):
        """
        Конструктор
        :param parent: батьківський елемент
        :param str_id: унікальний ідентифікатор елементу
        :param save_stats: прапорець збереження статистики для елементу
        """
        self._parent = parent
        self._id = str_id

        self._inputs = []
        self._outputs = []

        self._load = 0
        self._stats = [] if save_stats else None

    @property
    def load(self):
        return self._load

    @property
    def save_stats(self):
        return self._stats is not None

    @property
    def str_id(self):
        return self._id

    @property
    def statistics(self):
        return self._stats

    @property
    def str_id(self):
        return self._id

    def add_input(self, element: "Element", multiplicity: int):
        """
        Додавання входу
        :param element: елемент, що є входом
        :param multiplicity: кількість зв'язків (дуг)
        :return: None
        """
        self._inputs.append((element, multiplicity))

    def add_output(self, element: "Element", multiplicity: int):
        """
        Додавання виходу
        :param element: елемент, що є виходом
        :param multiplicity: кількість зв'язків (дуг)
        :return: None
        """
        self._outputs.append((element, multiplicity))

    def process(self, timer: int):
        """
        Виконання дій у визначений елемент модельного часу
        :param timer: момент модельного часу
        :return:
        """
        pass

    def _save_statistics(self, timer: int):
        """
        Збереження статистики
        :param timer: момент модельного часу
        :return:
        """
        pass

