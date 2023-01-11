from .models import Element
from typing import Literal, NoReturn
from typing import TYPE_CHECKING
from numpy.random import default_rng
from numpy import ceil

if TYPE_CHECKING:
    from .simulation import Simulation


class Transition(Element):

    def __init__(self, distribution_type: Literal['const', 'norm', 'exp', 'uni', 'func'],
                 parent: "Simulation", str_id: str, priority: int = 1000, **kwargs):
        super().__init__(capacity=1, str_id=str_id, parent=parent)
        self._dist_type = distribution_type
        match distribution_type:
            case 'const':
                if 'loc' in kwargs:
                    self._loc = kwargs['loc']
                else:
                    self._loc = 0
            case 'norm':
                self._scale = kwargs['scale']
                self._loc = kwargs['loc']
            case 'exp':
                self._scale = kwargs['scale']
            case 'uni':
                self._loc = kwargs['loc']
                self._scale = kwargs['scale']
            case '_':
                raise ValueError('Unknown distribution type')

        self._random_generator = default_rng()
        self._storage = []
        self._priority = priority
        self._holds, self._releases = [], []

    @property
    def hold_times(self):
        return self._holds

    @property
    def release_times(self):
        return self._releases

    @property
    def load(self):
        return len(self._storage)

    @property
    def priority(self):
        return self._priority

    def __repr__(self):
        return f'Transition: {self._id}, type={self._dist_type}, load={self.load}'

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

    def _filter_and_sort_storage(self, timer: int) -> NoReturn:
        """
        Time momemts' storage cleaner
        :param timer: current imitation time
        :return: None
        """
        if len(self._storage) > 0:
            self._storage = sorted(list(filter(lambda x: x > timer, self._storage)))

    def _hold(self, timer: int) -> NoReturn:
        """
        Gets markers from inputs
        :param timer: current imitation time
        :return: None
        """
        if (transition_quantity := min([_input[0].load for _input in self._inputs])) > 0:
            self._holds.append(timer)
            for _input in self._inputs:
                _input[0].exclude(transition_quantity)
            for _ in range(transition_quantity):
                self._storage.append(self._generate_fin_time(timer))

    def _release(self, timer: int) -> NoReturn:
        """
        Put markers in the outputs
        :param timer: current imitation time
        :return: None
        """
        if (transition_quantity := len(list(filter(lambda x: x == timer, self._storage)))) > 0:
            self._releases.append(timer)
            for output in self._outputs:
                output[0].append(transition_quantity * output[1])

    def _generate_fin_time(self, timer: int) -> int:
        """
        Generates final procession time for a marker
        :param timer: current imitation time
        :return: time moment
        """
        match self._dist_type:
            case 'const':
                return int(timer + self._loc)
            case 'norm':
                return int(timer + ceil(self._random_generator.normal(loc=self._loc, scale=self._scale)))
            case 'exp':
                return int(timer + ceil(self._random_generator.exponential(scale=self._scale)))
            case 'uni':
                return int(timer + ceil(self._random_generator.uniform(low=self._loc - self._scale,
                                                                       high=self._loc + self._scale)))
            case 'func':
                pass



