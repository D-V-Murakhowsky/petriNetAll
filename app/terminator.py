import numpy as np

from .models import Element


class Terminator(Element):

    def __init__(self, parent, str_id: str):
        super().__init__(capacity=np.inf, parent=parent, str_id=str_id)

    def __repr__(self):
        return f'{self._id if self._id != "" else "Terminator"}. Arrived {self.load} elements'

    def append(self, num: int = 1):
        self._load += num
