from unittest import TestCase
from app.simulation_1 import Simulation_1


class TestSimulation_1(TestCase):

    def test_creation(self):
        simulation = Simulation_1(max_time=1000)
        self.assertIsNotNone(simulation)

    def test_run(self):
        simulation = Simulation_1(max_time=30)
        simulation.run()
        pass