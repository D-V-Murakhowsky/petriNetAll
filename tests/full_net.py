from typing import Tuple
from unittest import TestCase

from app.base_simulation import Simulation
from app.place import Place
from app.transition import Transition


class FullSimulation(Simulation):

    def __init__(self, max_time: int, intergeneration_time: Tuple):
        super().__init__(max_time, default_generator=True, default_stock=False,
                         intergeneration_time=intergeneration_time)
        self.add_stocks(['Successful', 'Unsuccessful', 'NormalStock', 'StockReplenished'])
        self._create_model()

    def _create_model(self):
        self._places.extend([
            Place(capacity=1, str_id='Arrival', parent=self),
            Place(capacity=20, str_id='Stock_qty', parent=self, initial_load=20),
            Place(capacity=1, str_id='Check_stock', parent=self),
            Place(capacity=1, str_id='Request_completed', parent=self),
            Place(capacity=1, str_id='Request_complected', parent=self),
            ])

        self._transitions.extend([
            Transition(distribution_type='const', parent=self, str_id='Arrival->Successful', priority=3),
            Transition(distribution_type='const', parent=self, str_id='Arrival->Unsuccessful', priority=4),
            Transition(distribution_type='const', parent=self, str_id='Control->Request_completed', priority=1),
            Transition(distribution_type='const', parent=self, str_id='Request_completed->Request_complected',
                       priority=5),
            Transition(distribution_type='const', parent=self, str_id='Delivery',
                       priority=6),
            Transition(distribution_type='const', parent=self, str_id='Control->NormalStock', priority=2),
        ])

        self.set_arcs([
            ('Generator', 'Arrival', 1),
            ('Arrival', 'Arrival->Successful', 1),
            ('Stock_qty', 'Arrival->Successful', 1),
            ('Arrival', 'Arrival->Unsuccessful', 1),
            ('Arrival->Successful', 'Successful', 1),
            ('Arrival->Unsuccessful', 'Unsuccessful', 1),
            ('Generator', 'Check_stock', 1),
            ('Check_stock', 'Control->Request_completed', 1),
            ('Check_stock', 'Control->NormalStock', 1),
            ('Control->Request_completed', 'Request_completed', 1),
            ('Request_completed', 'Request_completed->Request_complected', 1),
            ('Request_completed->Request_complected', 'Request_complected', 1),
            ('Request_complected', 'Delivery', 1),
            ('Delivery', 'StockReplenished', 1),
            ('Delivery', 'Stock_qty', 17)
        ])


class TestEasySimulation(TestCase):

    def setUp(self) -> None:
        self.simulation = FullSimulation(max_time=6000, intergeneration_time=(50, 70))

    def test_run_simulation(self):
        self.simulation.run()