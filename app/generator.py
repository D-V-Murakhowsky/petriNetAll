from typing import TYPE_CHECKING, Tuple

from .models import Entity, Element

if TYPE_CHECKING:
    from .base_simulation import Simulation

import numpy as np
from random import randint


class Generator(Element):

    def __init__(self, simulation_time: int, parent: "Simulation", str_id: str, intergeneration_time: Tuple):
        super().__init__(capacity=np.inf, parent=parent, str_id=str_id)
        self._max_time = simulation_time
        self._generated_entities = None
        self._total_generation = 0
        self._min_generation_time, self._max_generation_time = intergeneration_time

        self._parent = parent

    def __repr__(self):
        return f'{self._id}'

    @property
    def total_elements(self):
        return self._total_generation

    def generate_tokens(self):
        generation_list, timer_list = [], []
        timer = 0
        while timer < self._max_time:
            generation_list.extend([Entity(timer=timer) for _ in range(1)])
            timer_list.append(timer)
            timer += self._min_generation_time if (self._min_generation_time == self._max_generation_time) else randint(self._min_generation_time, self._max_generation_time)
        self._generated_entities = generation_list
        self._parent.init_time_intervals(time_intervals=timer_list)
        self._total_generation = len(generation_list)
        return generation_list, timer_list

    def process(self, timer: int):
        list(map(lambda x: self._outputs[0][0].put(x),
                 value := list(filter(lambda x: x._start_time <= timer, self._generated_entities))))
        self._generated_entities = list(filter(lambda x: x not in value, self._generated_entities))


