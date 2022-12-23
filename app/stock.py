import numpy as np

from .models import Element


class Stock(Element):

    def __init__(self, parent):
        super().__init__(capacity=np.inf, parent=parent, str_id='Stock')

    def __repr__(self):
        return f'Stock. Arrived {self.load} elements'
