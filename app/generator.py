from typing import TYPE_CHECKING, Tuple

from .models import Element

if TYPE_CHECKING:
    from .base_simulation import Simulation

import numpy as np
from random import randint


class Generator(Element):

    def __init__(self, simulation_time: int, parent: "Simulation", str_id: str, intergeneration_time: Tuple):
        super().__init__(capacity=np.inf, parent=parent, str_id=str_id)
        self._max_time = simulation_time
        self._total_generation = 0
        self._min_generation_time, self._max_generation_time = intergeneration_time
        self._timer_list = []
        self._parent = parent

    def __repr__(self):
        return f'{self._id}'

    @property
    def total_elements(self):
        return self._total_generation

    def generate_tokens(self):
        timer = 0
        while timer < self._max_time:
            self._timer_list.append(timer)
            timer += self._min_generation_time \
                if (self._min_generation_time == self._max_generation_time) else\
                randint(self._min_generation_time, self._max_generation_time)
        self._total_generation = len(self._timer_list)
        return self._timer_list

    def process(self, timer: int):
        for _ in list(filter(lambda x: x <= timer, self._timer_list)):
            for output in self._outputs:
                output[0].append(output[1])


