import numpy as np

from .base_simulation import Simulation
from .place import Place
from .transition import Transition


class Simulation_2_1(Simulation):

    def __init__(self, max_time: int):
        super().__init__(max_time)
        self._create_model()

    def _create_model(self):
        self._places.extend([])

        self._transitions.extend([])

        self.set_arcs([])