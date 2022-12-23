from abc import ABC
from typing import NoReturn, Any, Iterable
from typing import TYPE_CHECKING

from sortedcontainers import SortedList

if TYPE_CHECKING:
    from .base_simulation import Simulation

import numpy as np


class Entity:

    def __init__(self, timer: int):
        self._start_time = timer
        self._fin_time = -1
        self._transition_time = -1

    @property
    def is_marked(self):
        return self._transition_time != -1

    @property
    def transition_time(self):
        return self._transition_time

    @transition_time.setter
    def transition_time(self, value):
        self._transition_time = value

    def reset_transition_time(self):
        self._transition_time = -1

    def __repr__(self):
        return f'Entity (gen_time={self._start_time}, marked={self.is_marked})'


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
        self._storage = []
        self._parent = parent
        self._id = str_id

        self._inputs = []
        self._outputs = []

    @property
    def elements(self):
        return self._storage

    @property
    def is_full(self):
        return False

    @property
    def load(self):
        return len(self._storage)

    @property
    def non_marked(self):
        return sum(list(map(lambda x: 0 if x.is_marked else 1, self._storage)))

    def add_input(self, element: "Element"):
        self._inputs.append(element)

    def add_output(self, element: "Element"):
        self._outputs.append(element)

    def process(self, timer: int):
        pass

    def put(self, entity: Entity):
        self._storage.append(entity)



