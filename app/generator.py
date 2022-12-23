from typing import TYPE_CHECKING

from .models import Entity, Element

if TYPE_CHECKING:
    from .base_simulation import Simulation

import numpy as np


class Generator(Element):

    def __init__(self, simulation_time: int, parent: "Simulation"):
        super().__init__(capacity=np.inf, parent=parent, str_id='Generator')
        self._max_time = simulation_time
        self._generated_entities = None
        self._total_generation = 0

        self._parent = parent

    @property
    def total_elements(self):
        return self._total_generation

    def generate_tokens(self):
        generation_list, timer_list = [], []
        timer = 0
        while timer < self._max_time:
            generation_list.extend([Entity(timer=timer) for _ in range(4)])
            timer_list.append(timer)
            timer += 1
        self._generated_entities = generation_list
        self._parent.init_time_intervals(time_intervals=timer_list)
        self._total_generation = len(generation_list)
        return generation_list, timer_list

    def process(self, timer: int):
        list(map(lambda x: self._outputs[0].put(x),
                 value := list(filter(lambda x: x._start_time <= timer, self._generated_entities))))
        self._generated_entities = list(filter(lambda x: x not in value, self._generated_entities))


