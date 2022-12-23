from typing import TYPE_CHECKING, List

from .models import Element, Entity
if TYPE_CHECKING:
    from .base_simulation import Simulation

import numpy as np


class Place(Element):

    _num_id = 0

    def __init__(self, parent: "Simulation", capacity: int = np.inf, str_id: str = ''):
        super().__init__(parent, capacity, str_id)

        self._num_id = Place._num_id
        Place._num_id += 1

    def __repr__(self):
        return f'Place: {self._id}, capacity={self._capacity}, load={self.load}'

    @property
    def is_full(self):
        return self.load == self._capacity

    def exclude(self, entities: List[Entity]):
        self._storage = list(filter(lambda x: x not in entities, self._storage))

    def put(self, entity: Entity):
        if len(self._storage) < self._capacity:
            self._storage.append(entity)
            return True
        else:
            return False

    def pop_first(self):
        return self._storage.pop(0)
