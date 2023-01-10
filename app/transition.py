from .models import Element, Entity
from typing import Literal, List
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

    def __repr__(self):
        return f'Transition: {self._id}, type={self._dist_type}, load={self.load}'

    def process(self, timer: int):
        self._hold(timer)
        self._release(timer)


        # times = self._generate_transition_times(timer)
        # self._make_transitions(timer)
        # self._storage = list(filter(lambda x: x[0] > timer, self._storage))
        # return times

    def _hold(self, timer: int):
        transition_quantity = min([_input[0].load for _input in self._inputs])
        for _input in self._inputs:
            quota


    def _release(self, timer: int):
        pass

    def _generate_transition_times(self, timer: int):
        times = []
        while self._check_condition():
            for input_element in self._inputs:
                for element in self._get_quota(input_element[0].elements):
                    if element.transition_time == -1:
                        element.transition_time = self._generate_fin_time(timer)
                        times.append(element.transition_time)
        return times

    def _make_transitions(self, timer: int):
        list_to_unload, transited = [], []
        for element_input in self._inputs:
            values = list(filter(lambda x: x.transition_time == timer, element_input.elements))
            list_to_unload.extend(values)
        if len(self._outputs) > 0:
            for output in self._outputs:
                while (not output.is_full) & (len(list_to_unload) > 0):
                    output.put(value := list_to_unload.pop(0))
                    value.reset_transition_time()
                    transited.append(value)
        for input_element in self._inputs:
            input_element.exclude(transited)
        pass

    def _check_condition(self):
        for input_element in self._inputs:
            if input_element[0].non_marked == 0:
                return False
        return True

    @staticmethod
    def _get_quota(elements: List[Entity], quota: int = -1):
        if (quota <= 0) | (len(elements) <= quota):
            return elements
        else:
            return elements[:quota]

    def _generate_fin_time(self, timer: int):
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



