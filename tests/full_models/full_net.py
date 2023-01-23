from typing import Tuple
from unittest import TestCase

import matplotlib.pyplot as plt
import numpy as np
from numpy.random import default_rng

from app.place import Place
from app.simulation import Simulation
from app.transition import Transition

import pickle


class FullSimulation_Zero(Simulation):

    def __init__(self, max_time: int, intergeneration_time: Tuple = (1, 1), containers_per_minute: int = 2,
                 small_full_load: int = 80):
        super().__init__(max_time, default_generator=True, default_stock=False,
                         intergeneration_time=intergeneration_time)
        self._create_model(containers_per_minute, small_full_load)
        self._stock_monitor = []
        self._generator = default_rng()

    def _create_model(self, containers_per_minute: int, small_max_load: int):
        def special_func():
            value = 0
            while (value < 120) | (value > 240):
                value = self._generator.normal(loc=180, scale=60)
            return value

        self._places.extend([
            Place(parent=self, capacity=np.inf, str_id='Arrival'),
            Place(parent=self, capacity=np.inf, str_id='OnConveyor', save_stats=True, operate_as_queue=True),
            Place(parent=self, capacity=1, str_id='SmallLoaded'),
            Place(parent=self, capacity=3, str_id='SmallFree', initial_load=3, save_stats=True),
            Place(parent=self, capacity=1, str_id='BigLoaded'),
            Place(parent=self, capacity=2, str_id='BigFree', initial_load=2, save_stats=True)
        ])

        self._transitions.extend([
            Transition(parent=self, str_id='PutOnConveyor', priority=1, distribution_type='const', loc=0),
            Transition(parent=self, str_id='LoadSmall', priority=2, distribution_type='const', loc=0),
            Transition(parent=self, str_id='FlightSmall', priority=4, distribution_type='func', func=special_func,
                       save_stats=True),
            Transition(parent=self, str_id='LoadBig', priority=3, distribution_type='const', loc=0),
            Transition(parent=self, str_id='FlightBig', priority=4, distribution_type='func', func=special_func,
                       save_stats=True),
        ])

        self.set_arcs([
            ('Generator', 'Arrival', containers_per_minute),
            ('Arrival', 'PutOnConveyor', 1),
            ('PutOnConveyor', 'OnConveyor', 1),
            ('OnConveyor', 'LoadSmall', small_max_load),
            ('LoadSmall', 'SmallLoaded', 1),
            ('SmallLoaded', 'FlightSmall', 1),
            ('FlightSmall', 'SmallFree', 1),
            ('SmallFree', 'LoadSmall', 1),
            ('OnConveyor', 'LoadBig', 140),
            ('LoadBig', 'BigLoaded', 1),
            ('BigLoaded', 'FlightBig', 1),
            ('FlightBig', 'BigFree', 1),
            ('BigFree', 'LoadBig', 1)
        ])


class FullSimulation_One(Simulation):

    def __init__(self, max_time: int, intergeneration_time: Tuple = (1, 1), containers_per_minute: int = 2,
                 small_full_load: int = 80):
        super().__init__(max_time, default_generator=True, default_stock=False,
                         intergeneration_time=intergeneration_time)
        self._create_model(containers_per_minute, small_full_load)
        self._stock_monitor = []
        self._generator = default_rng()

    def _create_model(self, containers_per_minute: int, small_max_load: int):
        def special_func():
            value = 0
            while (value < 120) | (value > 240):
                value = self._generator.normal(loc=180, scale=60)
            return value

        self._places.extend([
            Place(parent=self, capacity=np.inf, str_id='Arrival'),
            Place(parent=self, capacity=np.inf, str_id='OnConveyor', save_stats=True, operate_as_queue=True),
            Place(parent=self, capacity=1, str_id='SmallLoaded'),
            Place(parent=self, capacity=3, str_id='SmallFree', initial_load=3, save_stats=True),
            Place(parent=self, capacity=1, str_id='BigLoaded'),
            Place(parent=self, capacity=2, str_id='BigFree', initial_load=2, save_stats=True)
        ])

        self._transitions.extend([
            Transition(parent=self, str_id='PutOnConveyor', priority=1, distribution_type='const', loc=1),
            Transition(parent=self, str_id='LoadSmall', priority=2, distribution_type='const', loc=0),
            Transition(parent=self, str_id='FlightSmall', priority=4, distribution_type='func', func=special_func,
                       save_stats=True),
            Transition(parent=self, str_id='LoadBig', priority=3, distribution_type='const', loc=0),
            Transition(parent=self, str_id='FlightBig', priority=4, distribution_type='func', func=special_func,
                       save_stats=True),
        ])

        self.set_arcs([
            ('Generator', 'Arrival', containers_per_minute),
            ('Arrival', 'PutOnConveyor', 1),
            ('PutOnConveyor', 'OnConveyor', 1),
            ('OnConveyor', 'LoadSmall', small_max_load),
            ('LoadSmall', 'SmallLoaded', 1),
            ('SmallLoaded', 'FlightSmall', 1),
            ('FlightSmall', 'SmallFree', 1),
            ('SmallFree', 'LoadSmall', 1),
            ('OnConveyor', 'LoadBig', 140),
            ('LoadBig', 'BigLoaded', 1),
            ('BigLoaded', 'FlightBig', 1),
            ('FlightBig', 'BigFree', 1),
            ('BigFree', 'LoadBig', 1)
        ])


class TestFullSimulation(TestCase):

    def setUp(self) -> None:
        self.simulation_zero = FullSimulation_Zero(max_time=10000, intergeneration_time=(1, 1))
        self.simulation_one = FullSimulation_One(max_time=10000, intergeneration_time=(1, 1))

    @staticmethod
    def process_response(response: dict, model_time: int) -> dict:
        append = np.array(response['Place_OnConveyor']['append'][:len(response['Place_OnConveyor']['exclude'])])
        exclude = np.array(response['Place_OnConveyor']['exclude'])
        wait_time = exclude - append
        process_time_mean = np.mean(wait_time)
        process_time_std = np.std(wait_time)

        small_time = response['Place_SmallFree']['current_load'][:, 0]
        big_time = response['Place_SmallFree']['current_load'][:, 0]
        small_load = 3 - (response['Place_SmallFree']['current_load'][1:, 1].dot(small_time[1:] - small_time[:-1])) \
                     / model_time
        big_load = 2 - response['Place_BigFree']['current_load'][1:, 1].dot(big_time[1:] - big_time[:-1]) \
                   / model_time
        return {"process_mean": process_time_mean, "process_std": process_time_std,
                "small_load": small_load, "big_load": big_load}

    def test_one_simulation(self):
        simulation_zero = FullSimulation_One(max_time=16000, intergeneration_time=(1, 1), small_full_load=100)
        print(self.process_response(simulation_zero.run(), simulation_zero._max_time))

    def test_run_zero_simulation(self):
        response = self.simulation_zero.run()
        with open('../sim_result_0.pickle', 'wb') as f:
            pickle.dump(response, f)

    def test_run_one_simulation(self):
        response = self.simulation_one.run()
        with open('../sim_result_1.pickle', 'wb') as f:
            pickle.dump(response, f)

    def test_find_edge_effect(self):

        data_0, data_1 = [], []

        for load in range(40, 140, 10):
            for trial_n in range(2):
                simulation_0 = FullSimulation_Zero(max_time=16000, intergeneration_time=(1, 1),
                                                   small_full_load=load)
                simulation_1 = FullSimulation_One(max_time=16000, intergeneration_time=(1, 1),
                                                  small_full_load=load)

                response_0 = self.process_response(simulation_0.run(), simulation_0._max_time)
                response_1 = self.process_response(simulation_1.run(), simulation_1._max_time)

                data_0.append({'load': load, 'trial_n': trial_n,
                               'process_time_mean': response_0['process_mean'],
                               'process_time_std': response_0['process_std'],
                               'small_load': response_0['small_load'],
                               'big_load': response_0['big_load']})

                data_1.append({'load': load, 'trial_n': trial_n,
                               'process_time_mean': response_1['process_mean'],
                               'process_time_std': response_1['process_std'],
                               'small_load': response_1['small_load'],
                               'big_load': response_1['big_load']})

        with open('../sim_result_load_0.pickle', 'wb') as f:
            pickle.dump(data_0, f)
        with open('../sim_result_load_1.pickle', 'wb') as f:
            pickle.dump(data_1, f)
