from typing import TYPE_CHECKING

import numpy as np

from .models import Element

if TYPE_CHECKING:
    from .simulation import Simulation


class Place(Element):

    _num_id = 0

    def __init__(self, parent: "Simulation", capacity: int = 1, str_id: str = '', initial_load: int = 0,
                 save_stats: bool = False, operate_as_queue: bool = False):
        super().__init__(parent, str_id, save_stats)

        self._num_id = Place._num_id
        Place._num_id += 1

        if initial_load > 0:
            self._load = initial_load

        self._capacity = capacity
        self._statistics = {'current_load': np.array([]),
                            'append': np.array([]),
                            'exclude': np.array([])}

        self._operate_as_queue = operate_as_queue
        if operate_as_queue:
            self._queue = []

    def __repr__(self):
        return f'Place: {self._id}, capacity={self._capacity}, load={self.load}'

    @property
    def element_type(self):
        return 'Place'

    @property
    def is_full(self):
        return self.load == self._capacity

    @property
    def statistics(self):
        return self._statistics

    def exclude(self, timer: int, num: int = 1):
        self._load -= num
        if self._operate_as_queue:
            for _ in range(num):
                self._statistics['exclude'] = np.append(self._statistics['exclude'], timer)

    def append(self, timer: float, num: int = 1):
        if self._load < self._capacity:
            self._load += num
            if self._operate_as_queue:
                for _ in range(num):
                    self._statistics['append'] = np.append(self._statistics['append'], timer)
            return True
        else:
            return False

    def get_statistics(self):
        return self._statistics

    def process(self, timer: int):
        if self._save_stats:
            self._save_statistics(timer)

    def _save_statistics(self, timer: int):
        if self._statistics['current_load'].size == 0:
            self._statistics['current_load'] = np.array([timer, self.load]).reshape(1, -1)
        else:
            self._statistics['current_load'] = np.append(self._statistics['current_load'],
                                                         np.array([timer, self.load]).reshape(1, -1),
                                                         axis=0)


