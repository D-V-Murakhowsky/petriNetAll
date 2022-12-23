from unittest import TestCase

from app.simulation_1 import Simulation_1
from random import seed


class TestTransition(TestCase):

    def setUp(self) -> None:
        self.simulation = Simulation_1(max_time=500)
        seed(101)

    def test_transition(self):
        self.simulation._generator.process(timer=0)
        times = self.simulation.transitions[0].process(timer=0)
        self.assertEqual(1, self.simulation.places[1].load)
        self.assertEqual(3, self.simulation.places[2].load)
