from unittest import TestCase

from app.simulation_1 import Simulation_1


class TestGenerator(TestCase):

    def setUp(self) -> None:
        self.simulation = Simulation_1(max_time=500)

    def test_generator(self):
        self.simulation._generator.process(timer=2)
        self.assertEqual(12, self.simulation.places[0].load)