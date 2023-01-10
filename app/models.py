from abc import ABC
from typing import NoReturn, Any, Iterable
from typing import TYPE_CHECKING

from sortedcontainers import SortedList

if TYPE_CHECKING:
    from .base_simulation import Simulation

import numpy as np


class SortedQueue:

    def __init__(self):
        self._list: SortedList = SortedList()

    def __len__(self):
        return len(self._list)

    def __repr__(self):
        return f'SortedQueue: {str(self._list)}'

    @property
    def is_empty(self):
        return len(self._list) == 0

    @property
    def values(self):
        return self._list

    def check_insert(self, value: Any) -> bool:
        if value in self._list:
            return False
        else:
            self.insert(value)
            return True

    def check_update(self, list_of_values: Iterable) -> NoReturn:
        list_of_values = list(filter(lambda x: x not in self._list, list_of_values))
        self.update(set(list_of_values))

    def insert(self, value: Any) -> NoReturn:
        self._list.add(value)

    def get(self) -> Any:
        value = self._list[0]
        self._list.pop(0)
        return value

    def update(self, list_of_values: Iterable) -> NoReturn:
        self._list.update(list_of_values)

    def contains(self, value):
        return value in self._list


class Element(ABC):

    def __init__(self, parent: "Simulation", capacity: int = np.inf, str_id: str = ''):
        self._capacity = capacity
        self._parent = parent
        self._id = str_id

        self._inputs = []
        self._outputs = []

        self._load = 0

    @property
    def is_full(self):
        return False

    @property
    def load(self):
        return self._load

    @property
    def str_id(self):
        return self._id

    def add_input(self, element: "Element", multiplicity: int):
        self._inputs.append((element, multiplicity))

    def add_output(self, element: "Element", multiplicity: int):
        self._outputs.append((element, multiplicity))

    def process(self, timer: int):
        pass


