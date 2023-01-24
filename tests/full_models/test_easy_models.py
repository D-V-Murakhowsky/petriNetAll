from app.simulation import Simulation
from unittest import TestCase

GENERATOR_SETUP = {'time_distro': {'type_of_distribution': 'exp',
                                   'loc': 1},
                   'n_per_arrival': 2}

PLACES = [{'str_id': 'Arrival', "stats": True},
          {'str_id': 'Pre_exit', 'stats': True},
          {'str_id': "Exit", "stats": True}]

TRANSITIONS_TIMES = [{'str_id': 'prob_06', 'prob': 0.6, "stats": True, 'priority': 1,
                      'time_distro': {'type_of_distribution': 'norm',
                                      'loc': 2, 'scale': 1}},
               {'str_id': 'prob_04', "stats": True, 'priority': 1,
                'time_distro': {'type_of_distribution': 'uniform',
                                'loc': 3, 'scale': 2}},
               {'str_id': 'to_exit', 'stats': True, 'priority': 2,
                'time_distro': {'type_of_distribution': 'const', 'loc': 1}}]

TRANSITIONS_ZEROS = [{'str_id': 'prob_06', 'prob': 0.6, "stats": True, 'priority': 1,
                      'time_distro': {'type_of_distribution': 'const', 'loc': 0}},
                     {'str_id': 'prob_04', "stats": True, 'priority': 1,
                      'time_distro': {'type_of_distribution': 'const', 'loc': 0}},
                     {'str_id': 'to_exit', 'stats': True, 'priority': 2,
                      'time_distro': {'type_of_distribution': 'exp', 'scale': 0.5}}]

TRANSITIONS_LIMITED_CAPACITY = [{'str_id': 'prob_06', 'prob': 0.6, "stats": True, 'priority': 1,
                                 'time_distro': {'type_of_distribution': 'const', 'loc': 0}},
                                {'str_id': 'prob_04', "stats": True, 'priority': 1,
                                 'time_distro': {'type_of_distribution': 'const', 'loc': 0}},
                                {'str_id': 'to_exit', 'stats': True, 'priority': 2, 'capacity': 1,
                                 'time_distro': {'type_of_distribution': 'exp', 'scale': 0.5}}]

ARCS = [('Generator', 'Arrival', 1),
        ('Arrival', 'prob_06', 2),
        ('Arrival', 'prob_04', 1),
        ('prob_06', 'Pre_exit', 1),
        ('prob_04', 'Pre_exit', 3),
        ('Pre_exit', 'to_exit', 1),
        ('to_exit', 'Exit', 1)]


class EasySimulation(TestCase):

    def test_run_conflict_transitions_with_zero_time(self):
        simulation = Simulation(max_time=1000,
                                generator=GENERATOR_SETUP,
                                places=PLACES,
                                transitions=TRANSITIONS_ZEROS,
                                arcs=ARCS)
        response = simulation.run()
        pass

    def test_run_conflict_transitions_with_zero_time_and_capacity(self):
        simulation = Simulation(max_time=1000,
                                generator=GENERATOR_SETUP,
                                places=PLACES,
                                transitions=TRANSITIONS_LIMITED_CAPACITY,
                                arcs=ARCS)
        response = simulation.run()
        pass

    def test_run_conflict_transitions_with_non_zero_time(self):
        simulation = Simulation(max_time=1000,
                                generator=GENERATOR_SETUP,
                                places=PLACES,
                                transitions=TRANSITIONS_TIMES,
                                arcs=ARCS)
        response = simulation.run()
        pass