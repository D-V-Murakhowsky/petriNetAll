from typing import NoReturn, Union, Dict, List
from typing import TYPE_CHECKING

import numpy as np
from numpy.random import default_rng

from app.models import Element, Distribution

if TYPE_CHECKING:
    from .simulation import Simulation


class Transition(Element):

    def __init__(self, time_distro: Union["Distribution", Dict],
                 parent: "Simulation", str_id: str, priority: int = 1000, **kwargs):
        super().__init__(str_id=str_id, parent=parent,
                         save_stats=kwargs['save_stats'] if 'save_stats' in kwargs else False)
        self._time_distro = Distribution.from_dict(time_distro) if isinstance(time_distro, dict) else time_distro
        self._random_generator = default_rng()
        self._storage = []
        self._priority = priority
        self._holds, self._releases = [], []
        self._probability = kwargs['prob'] if 'prob' in kwargs else 1
        self._capacity = kwargs['capacity'] if 'capacity' in kwargs else np.inf
        self._is_conflict: bool = False

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

    def process(self, timer: float) -> List[float]:
        """
        Main method
        :param timer: current imitation time
        :return: time moments to add in general time moments queue
        """
        value = 1 if self._probability == 1 else self._random_generator.uniform(0, 1)
        transactions_counter = self._hold(timer) if value <= self._probability else 0
        self._release(timer)
        self._filter_and_sort_storage(timer)
        response = None if ((len(self._storage) == 0) | (transactions_counter == 0)) else self._storage
        self._storage = list(filter(lambda x: x != timer, self._storage))
        return response

    def _check_hold_condition(self):
        for _input in self._inputs:
            if _input[0].load < _input[1]:
                return False
        return True

    def _filter_and_sort_storage(self, timer: float) -> NoReturn:
        """
        Time moments' storage cleaner
        :param timer: current imitation time
        :return: None
        """
        if len(self._storage) > 0:
            self._storage = sorted(list(filter(lambda x: x >= timer, self._storage)))

    def _hold(self, timer: float) ->int:
        """
        Gets markers from inputs
        :param timer: current imitation time
        :return: number of made transactions
        """
        transactions_counter: int = 0
        if self._check_hold_condition():
            transition_quantity = min([int(_input[0].load / _input[1]) for _input in self._inputs])
            transition_quantity = min(transition_quantity, 1) if self._is_conflict else transition_quantity
            if transition_quantity > 0:
                self._holds.append(timer)
                for _input in self._inputs:
                    _input[0].exclude(timer, transition_quantity * _input[1])
                for _ in range(transition_quantity):
                    self._storage.append(self._time_distro.get_value() + timer)
                    transactions_counter += 1
        return transactions_counter

    def _release(self, timer: float) -> NoReturn:
        """
        Put markers in the outputs
        :param timer: current imitation time
        :return: None
        """
        if (transition_quantity := len(list(filter(lambda x: x == timer, self._storage)))) > 0:
            self._releases.append(timer)
            for output in self._outputs:
                output[0].append(timer, transition_quantity * output[1])



