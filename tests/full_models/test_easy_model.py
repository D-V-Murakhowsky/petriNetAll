from app.simulation import Simulation
from unittest import TestCase

GENERATOR_SETUP = {'time_distro': {'type_of_distribution': 'exp',
                                   'loc': 1},
                   'n_per_arrival': 3}

PLACES = [{'str_id': 'Arrival', "stats": True},
          {'str_id': "Exit", "stats": True}]

TRANSITIONS = [{'str_id': 'prob_06', 'prob': 0.6, "stats": True, 'priority': 1,
                'time_distro': {'type_of_distribution': 'norm',
                                'loc': 2, 'scale': 1}},
               {'str_id': 'prob_04', 'prob': 0.4, "stats": True, 'priority': 1,
                'time_distro': {'type_of_distribution': 'uniform',
                                'loc': 3, 'scale': 2}}]

ARCS = [('Generator', 'Arrival', 1),
        ('Arrival', 'prob_06', 2),
        ('Arrival', 'prob_04', 1),
        ('prob_06', 'Exit', 1),
        ('prob_04', 'Exit', 2)]


class EasySimulation(TestCase):

    def setUp(self) -> None:
        self.simulation = Simulation(max_time=1000,
                                     generator=GENERATOR_SETUP,
                                     places=PLACES,
                                     transitions=TRANSITIONS,
                                     arcs=ARCS)

    def test_run(self):
        response = self.simulation.run()
        pass