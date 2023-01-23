from typing import TYPE_CHECKING, NoReturn, Union

from .models import Element

if TYPE_CHECKING:
    from .simulation import Simulation
    from .place import Place

from .models import Distribution


class Generator(Element):
    """
    Додає визначену кількість маркерів в позицію входу
    """

    def __init__(self, parent: "Simulation", time_distro: Distribution, n_per_arrival: int = 1):
        super().__init__(parent)
        self._input = None
        self._output: Union[Place, None] = None
        self._n_per_arrival = n_per_arrival
        self._next_arrival = -1
        self._distro = time_distro

    @staticmethod
    def get_generator(parent: Simulation, setup_data: dict):
        """
        Фабрика, що вертає генератор, створений з переданими параметрами
        :param parent: екземпляр симуляції, до якого належить генератор
        :param setup_data: параметри генератора для створення нового екземпляру класу
        :return: екземпляр класу Generator
        """
        return Generator(parent=parent, **setup_data)

    def process(self, timer: float) -> Union[float, None]:
        """
        Базовий метод
        :param timer: поточний модельний час
        :return: новий момент модельного часу, в який буде створений наступний екземпляр сутності
        """
        if self._next_arrival in [0, timer]:
            if self._output:
                self._output.append(timer=timer, num=self._n_per_arrival)
            self._next_arrival = timer + self._distro.get_value()
            return self._next_arrival
        else:
            return None

    def set_output(self, place: Place) -> NoReturn:
        """
        Поєднання виходу із входом наступного елемента
        :param place: наступний елемент
        :return:
        """
        self._output = place


