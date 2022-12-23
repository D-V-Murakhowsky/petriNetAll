import numpy as np

from .base_simulation import Simulation
from .place import Place
from .transition import Transition


class Simulation_1(Simulation):

    def __init__(self, max_time: int):
        super().__init__(max_time)
        self._create_model()

    def _create_model(self):
        self._places.extend([
            Place(capacity=np.inf, str_id='LineStart', parent=self),
            Place(capacity=1, str_id='FirstAggregateFree', parent=self),
            Place(capacity=np.inf, str_id='FirstAggregateBusy', parent=self),
            Place(capacity=1, str_id='SecondAggregateFree', parent=self),
            Place(capacity=np.inf, str_id='SecondAggregateBusy', parent=self),
            Place(capacity=1, str_id='ThirdAggregateFree', parent=self),
            Place(capacity=np.inf, str_id='ThirdAggregateBusy', parent=self),
            Place(capacity=1, str_id='ForthAggregateFree', parent=self),
            Place(capacity=np.inf, str_id='ForthAggregateBusy', parent=self),
            Place(capacity=1, str_id='FifthAggregateFree', parent=self),
            Place(capacity=np.inf, str_id='FifthAggregateBusy', parent=self)
            ]
        )

        self._transitions.extend([
            Transition(parent=self, str_id='Start->FirstAggregate', distribution_type='const', time=0),
            Transition(parent=self, str_id='FirstAggregate->SecondAggregate', distribution_type='const', time=1),
            Transition(parent=self, str_id='SecondAggregate->ThirdAggregate', distribution_type='const', time=1),
            Transition(parent=self, str_id='ThirdAggregate->ForthAggregate', distribution_type='const', time=1),
            Transition(parent=self, str_id='ForthAggregate->FifthAggregate', distribution_type='const', time=1),
            Transition(parent=self, str_id='FifthAggregate->LineStart', distribution_type='const', time=5),
            Transition(parent=self, str_id='Process_1', distribution_type='exp', scale=1),
            Transition(parent=self, str_id='Process_2', distribution_type='exp', scale=1),
            Transition(parent=self, str_id='Process_3', distribution_type='exp', scale=1),
            Transition(parent=self, str_id='Process_4', distribution_type='exp', scale=1),
            Transition(parent=self, str_id='Process_5', distribution_type='exp', scale=1)
        ])

        self.set_arcs([('Generator', 'LineStart', 1),

                       ('LineStart', 'Start->FirstAggregate', 1),
                       ('Start->FirstAggregate', 'FirstAggregateFree', 1),
                       ('Start->FirstAggregate', 'FirstAggregateBusy', 1),

                       ('FirstAggregateBusy', 'FirstAggregate->SecondAggregate', 1),
                       ('FirstAggregate->SecondAggregate', 'SecondAggregateFree', 1),
                       ('FirstAggregate->SecondAggregate', 'SecondAggregateBusy', 1),

                       ('SecondAggregateBusy', 'SecondAggregate->ThirdAggregate', 1),
                       ('SecondAggregate->ThirdAggregate', 'ThirdAggregateFree', 1),
                       ('SecondAggregate->ThirdAggregate', 'ThirdAggregateBusy', 1),

                       ('ThirdAggregateBusy', 'ThirdAggregate->ForthAggregate', 1),
                       ('ThirdAggregate->ForthAggregate', 'ForthAggregateFree', 1),
                       ('ThirdAggregate->ForthAggregate', 'ForthAggregateBusy', 1),

                       ('ForthAggregateBusy', 'ForthAggregate->FifthAggregate', 1),
                       ('ForthAggregate->FifthAggregate', 'FifthAggregateFree', 1),
                       ('ForthAggregate->FifthAggregate', 'FifthAggregateBusy', 1),

                       ('FirstAggregateFree', 'Process_1', 1),
                       ('Process_1', 'Stock', 1),

                       ('SecondAggregateFree', 'Process_2', 1),
                       ('Process_2', 'Stock', 1),

                       ('ThirdAggregateFree', 'Process_3', 1),
                       ('Process_3', 'Stock', 1),

                       ('ForthAggregateFree', 'Process_4', 1),
                       ('Process_4', 'Stock', 1),

                       ('FifthAggregateFree', 'Process_5', 1),
                       ('Process_5', 'Stock', 1),

                       ('FifthAggregateBusy', 'FifthAggregate->LineStart', 1),
                       ('FifthAggregate->LineStart', 'LineStart', 1)])


