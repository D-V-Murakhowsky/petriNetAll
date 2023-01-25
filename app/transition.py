from typing import NoReturn, Union, Dict, List
from typing import TYPE_CHECKING

import numpy as np
from numpy.random import default_rng
from sortedcontainers import SortedList

from .models import Element, Distribution
from . import SEED

if TYPE_CHECKING:
    from .simulation import Simulation


class Transition(Element):

    _local_rng = default_rng(SEED) if SEED > -1 else default_rng()

    def __init__(self, time_distro: Union["Distribution", Dict],
                 parent: "Simulation", str_id: str, priority: int = 1000, **kwargs):
        super().__init__(str_id=str_id, parent=parent,
                         save_stats=kwargs['save_stats'] if 'save_stats' in kwargs else False)
        self._time_distro = Distribution.from_dict(time_distro) if isinstance(time_distro, dict) else time_distro
        self._storage = SortedList()
        self._priority = priority
        self._probability = kwargs['prob'] if 'prob' in kwargs else 1
        self._capacity = kwargs['capacity'] if 'capacity' in kwargs else np.inf
        self._is_conflict: bool = False
        self._statistics = {'holds': [],
                            'releases': []}

    def __repr__(self):
        return f'Transition: {self._id}, type={self._time_distro.type_of_distribution}, load={self.load},' \
               f' {"is conflict" if self._is_conflict else ""}'

    @property
    def element_type(self):
        return 'Transition'

    @property
    def is_conflict(self):
        return self._is_conflict

    @is_conflict.setter
    def is_conflict(self, value):
        self._is_conflict = value

    @property
    def load(self):
        return len(self._storage)

    @property
    def priority(self):
        return self._priority

    @property
    def statistics(self):
        return None

    @property
    def storage(self):
        return self._storage

    def process(self, timer: float) -> List[float]:
        """
        Основний метод
        :param timer: поточний модельний час
        :return: моменти часу, що мають бути додані до черги модельних моментів часу,
         в які відбуваються зміни стану системи
        """

        # кроки процесу функціонування переходу
        if self.load == 0:
            free_cells = self._capacity
        else:
            free_cells = self._capacity - len(list(filter(lambda x: x > timer, self._storage)))
        future_release_moments = self._hold(timer, free_cells) if self._check_hold_condition(timer) else None
        self._update_storage(future_release_moments)
        self._release(timer)

        # перевірка коректності роботи алгоритму
        # після виконання усіх кроків в списку моментів не повинно залишатися поточного моменту
        if timer in self._storage:
            raise RuntimeError

        return future_release_moments

    def _check_hold_condition(self, timer: float):
        """
        Перевірка умови активації переходу. За умови активації зменшується відповідна кількість фішок у місцях,
        що поєднані із входом переходу
        :return: True - перехід активується, False - перехід не активується
        """
        if self._probability < 1:
            if self._local_rng.uniform(0, 1) > self._probability:
                return False

        for _input in self._inputs:
            if _input[0].load < _input[1]:
                return False
        return True

    def _update_storage(self, new_time_moments: List[float]) -> NoReturn:
        """
        Оновлення списку моментів
        :return: None
        """
        if new_time_moments is not None:
            self._storage.update(new_time_moments)

    def _filter_and_sort(self, timer: float) -> NoReturn:
        """
        Фільтр моментів модельного часу
        :param timer: поточне значення модельного часу
        :return: None
        """
        if len(self._storage) > 0:
            self._storage = sorted(list(filter(lambda x: x >= timer, self._storage)))

    def _hold(self, timer: float, free_cells: int) -> Union[List, None]:
        """
        Отримання маркерів з місць, що поєднані з входами переходу
        :param timer: поточне значення модельного часу
        :return: кількість транзакцій, що має бути виконана
        """

        transition_quantity = min([int(_input[0].load / _input[1]) for _input in self._inputs] + [free_cells])
        transition_quantity = min(transition_quantity, 1) if self._is_conflict else transition_quantity
        generated_time_moments = []

        if transition_quantity > 0:
            self._statistics['holds'].append((timer, transition_quantity))
            for _input in self._inputs:
                _input[0].exclude(timer, transition_quantity * _input[1])
            for _ in range(transition_quantity):
                generated_time_moments.append(self._time_distro.get_value() + timer)
            return generated_time_moments
        else:
            return None

    def _release(self, timer: float) -> NoReturn:
        """
        Додавання маркерів до місць, що поєднані з виходами з переходу
        :param timer: поточний час імітації
        :return: None
        """
        transition_quantity = len(list(filter(lambda x: x == timer, self._storage)))
        if transition_quantity > 0:
            self._statistics['releases'].append((timer, transition_quantity))
            for output in self._outputs:
                output[0].append(timer, transition_quantity * output[1])
                for _ in range(transition_quantity):
                    self._storage.pop(0)



