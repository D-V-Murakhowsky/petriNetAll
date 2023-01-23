from typing import TYPE_CHECKING, Union

import numpy as np

from .models import Element

if TYPE_CHECKING:
    from .simulation import Simulation


class Place(Element):

    _num_id = 0

    def __init__(self, parent: "Simulation", capacity: int = 1, str_id: str = '', initial_load: int = 0,
                 stats: bool = False):
        super().__init__(parent, str_id, stats)

        self._num_id = Place._num_id
        Place._num_id += 1

        if initial_load > 0:
            self._load = initial_load

        self._capacity = capacity
        self._statistics = {'load': np.array([]),
                            'append': np.array([]),
                            'exclude': np.array([])} if stats is True else None

    def __repr__(self):
        return f'Place: {self._id}, capacity={self._capacity}, load={self.load}'

    @property
    def element_type(self):
        return 'Place'

    @property
    def is_full(self):
        return self.load == self._capacity

    @property
    def load(self):
        return self._load

    @property
    def statistics(self):
        return self._statistics

    def exclude(self, timer: int, num: int = 1):
        self._load -= num
        if self._load < 0:
            raise RuntimeError(f'Place {self.str_id} has negative load')
        if self._statistics is not None:
            self._save_statistics(cell='exclude', value=num, timer=timer)

    def append(self, timer: float, num: int = 1):
        if self._load < self._capacity:
            self._load += num
            if self._statistics is not None:
                self._save_statistics(cell='append', value=num, timer=timer)
        else:
            return False

    def get_statistics(self):
        return self._statistics

    def process(self, timer: int):
        if self._statistics is not None:
            self._save_statistics(cell='load', value=self.load, timer=timer)

    def _save_statistics(self, cell: str, value: Union[int, float], timer: float):
        if self._statistics[cell].size == 0:
            self._statistics[cell] = np.array([timer, value]).reshape(1, -1)
        else:
            self._statistics[cell] = np.append(self._statistics[cell],
                                               np.array([timer, value]).reshape(1, -1),
                                               axis=0)


