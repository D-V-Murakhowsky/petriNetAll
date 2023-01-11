from .models import Element
from typing import Literal, NoReturn
from typing import TYPE_CHECKING
from numpy.random import default_rng
from numpy import ceil

if TYPE_CHECKING:
    from .base_simulation import Simulation


class Transition(Element):

    def __init__(self, distribution_type: Literal['const', 'norm', 'exp', 'uni', 'func'],
                 parent: "Simulation", str_id: str, priority: int = 1000, **kwargs):
        super().__init__(capacity=1, str_id=str_id, parent=parent)
        self._dist_type = distribution_type
        match distribution_type:
            case 'const':
                if 'time' in kwargs:
                    self._loc = kwargs['time']
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
        self._filter_and_sort_storage(timer)
        self._hold(timer)
        self._release(timer)
        return self._storage

    def _filter_and_sort_storage(self, timer: int) -> NoReturn:
        """
        Time momemts' storage cleaner
        :param timer: current imitation time
        :return: None
        """
        if len(self._storage) > 0:
            self._storage = sorted(list(filter(lambda x: x >= timer, self._storage)))

    def _hold(self, timer: int) -> NoReturn:
        """
        Gets markers from inputs
        :param timer: current imitation time
        :return: None
        """
        transition_quantity = min([_input[0].load for _input in self._inputs])
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
        transition_quantity = len(list(filter(lambda x: x == timer, self._storage)))
        for output in self._outputs:
            output[0].append(transition_quantity * output[1])

    def _generate_fin_time(self, timer: int) -> float:
        """
        Generates final procession time for a marker
        :param timer: current imitation time
        :return: time moment
        """
        match self._dist_type:
            case 'const':
                return timer + self._loc
            case 'norm':
                return timer + ceil(self._random_generator.normal(loc=self._loc, scale=self._scale))
            case 'exp':
                return timer + ceil(self._random_generator.exponential(scale=self._scale))
            case 'uni':
                return timer + ceil(self._random_generator.uniform(low=self._loc - self._scale,
                                                                   high=self._loc + self._scale))
            case 'func':
                pass



