from typing import Tuple
from unittest import TestCase

from app.simulation import Simulation
from app.place import Place
from app.transition import Transition
from app.conditional_transition import ConditionalTransition

import matplotlib.pyplot as plt
from random import randint
import numpy as np
import seaborn as sns
import scipy.stats as stats
from numpy.random import default_rng


class FullSimulation(Simulation):

    def __init__(self, max_time: int, intergeneration_time: Tuple):
        super().__init__(max_time, default_generator=True, default_stock=False,
                         intergeneration_time=intergeneration_time)
        self.add_stocks(['Successful', 'Unsuccessful', 'NormalStock', 'StockReplenished'])
        self._create_model()
        self._stock_monitor = []
        self._generator = default_rng()

    def _create_model(self):
        def special_func():
            value = 0
            while 2 <= value <= 4:
                value = self._generator.normal(loc=3, scale=1)
            return value

        self._places.extend([
            Place(parent=self, capacity=np.inf, str_id='Arrival'),
            Place(parent=self, capacity=np.inf, str_id='OnConveyor'),
            Place(parent=self, capacity=1, str_id='SmallLoaded'),
            Place(parent=self, capacity=3, str_id='SmallFree'),
            Place(parent=self, capacity=1, str_id='BigLoaded'),
            Place(parent=self, capacity=2, str_id='BigFree')
            ])

        self._transitions.extend([
            Transition(parent=self, str_id='PutOnConveyor', priority=1, distribution_type='const', loc=0),
            Transition(parent=self, str_id='LoadSmall', priority=2, distribution_type='const', loc=0),
            Transition(parent=self, str_id='FlightSmall', priority=4, distribution_type='func', func=special_func),
            Transition(parent=self, str_id='LoadBig', priority=3,  distribution_type='const', loc=0),
            Transition(parent=self, str_id='FlightBig', priority=4, distribution_type='func', func=special_func),
        ])

        self.set_arcs([
            ('Generator', 'Arrival', 2),
            ('Arrival', 'PutOnConveyor', 1),
            ('PutOnConveyor', 'OnConveyor', 1),
            ('OnConveyor', 'LoadSmall', 80),
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

    def run(self):
        super().run()

    def _state_monitoring(self, timer: int):
        pass

    def _show_monitoring(self):
        pass

    def _get_stock_load(self, plot=False):
        pass


class TestFullSimulation(TestCase):

    def setUp(self) -> None:
        self.simulation = FullSimulation(max_time=1000, intergeneration_time=(1, 1))

    def test_run_simulation(self):
        self.simulation.run()

    def test_run_simulation_series(self):
        results_prob, results_avg_load = [], []
        times = np.linspace(0, 6, 7)
        for time in times:
            simulation = FullSimulation(max_time=35000, intergeneration_time=(50, 70))
            prob, avg_load = simulation.run()
            results_prob.append(prob)
            results_avg_load.append(avg_load)

        fig, ax = plt.subplots(2, 1)
        ax[0].plot(times, results_prob)
        ax[0].set_xlabel('Пороговий залишок, шт')
        ax[0].set_ylabel('Середня ймовірність простою')
        ax[1].plot(times, results_avg_load)
        ax[1].set_xlabel('Пороговий залишок, шт')
        ax[1].set_ylabel('Середнє завантаження складу')
        plt.subplots_adjust(wspace=0.6, hspace=0.6)
        plt.show()


