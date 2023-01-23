from typing import NoReturn
from typing import TYPE_CHECKING

from numpy.random import default_rng

from .models import Element

if TYPE_CHECKING:
    from .simulation import Simulation
    from .models import Distribution


class Transition(Element):

    def __init__(self, time_distro: "Distribution",
                 parent: "Simulation", str_id: str, priority: int = 1000, **kwargs):
        super().__init__(str_id=str_id, parent=parent,
                         save_stats=kwargs['save_stats'] if 'save_stats' in kwargs else False)
        self._time_distro = time_distro
        self._random_generator = default_rng()
        self._storage = []
        self._priority = priority
        self._holds, self._releases = [], []

    def __repr__(self):
        return f'Transition: {self._id}, type={self._time_distro.type_of_distribution}, load={self.load}'

    @property
    def element_type(self):
        return 'Transition'

    @property
    def load(self):
        return len(self._storage)

    @property
    def priority(self):
        return self._priority

    @property
    def statistics(self):
        return None

    def process(self, timer: int):
        """
        Main method
        :param timer: current imitation time
        :return: time moments to add in general time moments queue
        """
        self._hold(timer)
        self._release(timer)
        self._filter_and_sort_storage(timer)
        return self._storage

    def _check_hold_condition(self):
        for _input in self._inputs:
            if _input[0].load < _input[1]:
                return False
        return True

    def _filter_and_sort_storage(self, timer: int) -> NoReturn:
        """
        Time moments' storage cleaner
        :param timer: current imitation time
        :return: None
        """
        if len(self._storage) > 0:
            self._storage = sorted(list(filter(lambda x: x > timer, self._storage)))

    def _hold(self, timer: float) -> NoReturn:
        """
        Gets markers from inputs
        :param timer: current imitation time
        :return: None
        """
        if self._check_hold_condition():
            if (transition_quantity := min([int(_input[0].load / _input[1]) for _input in self._inputs])) > 0:
                self._holds.append(timer)
                for _input in self._inputs:
                    _input[0].exclude(timer, transition_quantity * _input[1])
                for _ in range(transition_quantity):
                    self._storage.append(self._time_distro.get_value + timer)

    def _release(self, timer: int) -> NoReturn:
        """
        Put markers in the outputs
        :param timer: current imitation time
        :return: None
        """
        if (transition_quantity := len(list(filter(lambda x: x == timer, self._storage)))) > 0:
            self._releases.append(timer)
            for output in self._outputs:
                output[0].append(timer, transition_quantity * output[1])



