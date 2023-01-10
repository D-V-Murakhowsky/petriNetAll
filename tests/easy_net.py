from typing import Tuple
from unittest import TestCase

from app.base_simulation import Simulation
from app.place import Place
from app.transition import Transition


class EasySimulation(Simulation):

    def __init__(self, max_time: int, intergeneration_time: Tuple):
        super().__init__(max_time, default_generator=True, default_stock=False,
                         intergeneration_time=intergeneration_time)
        self.add_stocks(['Successful', 'Unsuccessful'])
        self._create_model()

    def _create_model(self):
        self._places.extend([
            Place(capacity=1, str_id='Arrival', parent=self),
            Place(capacity=20, str_id='Stock_qty', parent=self, initial_load=20),
            ])

        self._transitions.extend([
            Transition(distribution_type='const', parent=self, str_id='Arrival->Successful', priority=1),
            Transition(distribution_type='const', parent=self, str_id='Arrival->Unsuccessful', priority=2)
        ])

        self.set_arcs([
            ('Generator', 'Arrival', 1),
            ('Arrival', 'Arrival->Successful', 1),
            ('Arrival', 'Arrival->Unsuccessful', 1),
            ('Arrival->Successful', 'Successful', 1),
            ('Arrival->Unsuccessful', 'Unsuccessful', 1),
        ])


class TestEasySimulation(TestCase):

    def setUp(self) -> None:
        self.simulation = EasySimulation(max_time=6000, intergeneration_time=(50, 70))

    def test_run_simulation(self):
        self.simulation.run()