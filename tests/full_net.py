from typing import Tuple
from unittest import TestCase

from app.simulation import Simulation
from app.place import Place
from app.transition import Transition
from app.conditional_transition import ConditionalTransition

import matplotlib.pyplot as plt
from random import seed
import numpy as np
import seaborn as sns
import scipy.stats as stats


class FullSimulation(Simulation):

    def __init__(self, max_time: int, intergeneration_time: Tuple, stock_min: int = 3):
        super().__init__(max_time, default_generator=True, default_stock=False,
                         intergeneration_time=intergeneration_time)
        self._stock_min = stock_min
        self.add_stocks(['Successful', 'Unsuccessful', 'NormalStock', 'StockReplenished'])
        self._create_model()
        self._stock_monitor = []

    def _create_model(self):
        self._places.extend([
            Place(capacity=1, str_id='Arrival', parent=self),
            Place(capacity=20, str_id='Stock_qty', parent=self, initial_load=20),
            Place(capacity=1, str_id='Check_stock', parent=self),
            Place(capacity=1, str_id='Request_completed', parent=self),
            Place(capacity=1, str_id='Request_complected', parent=self),
            Place(capacity=1, str_id='NoDelivery', parent=self, initial_load=1)
            ])

        self._transitions.extend([
            Transition(distribution_type='const', parent=self, str_id='Arrival->Successful', priority=3),
            Transition(distribution_type='const', parent=self, str_id='Arrival->Unsuccessful', priority=4),
            ConditionalTransition(distribution_type='const', loc=60,
                                  parent=self, str_id='Control->Request_completed',
                                  priority=1, place='Stock_qty',
                                  condition=lambda x: x <= self._stock_min),
            Transition(distribution_type='uni', loc=60, scale=20,
                       parent=self, str_id='Request_completed->Request_complected',
                       priority=5),
            Transition(distribution_type='uni', loc=60, scale=5,
                       parent=self, str_id='Delivery',
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
            ('Control->NormalStock', 'NormalStock', 1),
            ('Control->Request_completed', 'Request_completed', 1),
            ('Request_completed', 'Request_completed->Request_complected', 1),
            ('Request_completed->Request_complected', 'Request_complected', 1),
            ('Request_complected', 'Delivery', 1),
            ('Delivery', 'StockReplenished', 1),
            ('Delivery', 'Stock_qty', 17),
            ('Delivery', 'NoDelivery', 1),
            ('NoDelivery', 'Control->Request_completed', 1)
        ])

    def run(self):
        super().run()
        print(f'Ймовірність простою: {(prob_value := self.get_element_by_id("Unsuccessful").load/ sum([generator.total_elements for generator in self._generators])):.3f}')
        return prob_value, self._get_stock_load()

    def _state_monitoring(self, timer: int):
        self._stock_monitor.append((timer, self.get_element_by_id('Stock_qty').load))

    def _show_monitoring(self):
        start_delivery = self.get_element_by_id('Control->Request_completed').hold_times
        stop_delivery = self.get_element_by_id('Delivery').release_times
        delivery_times = np.array(stop_delivery) - np.array(start_delivery)
        print(f'\nДоставку розпочато: {len(start_delivery)} разів')
        print(f'Доставку виконано: {len(stop_delivery)} разів')
        print(f'Мінімальний час доставки: {delivery_times.min()}')
        print(f'Максимальний час доставки: {delivery_times.max()}')
        print(f'Середнє завантаження складу: {self._get_stock_load(plot=False):.3f}')

    def _get_stock_load(self, plot=False):
        times, stock = [], []
        for moment in self._stock_monitor:
            times.append(moment[0])
            stock.append(moment[1])
        times = np.array(times)
        if plot:
            plt.step(times, stock)
            plt.show()
        return np.dot(np.array(stock)[:-1], times[1:] - times[:-1]) / self._max_time


class TestFullSimulation(TestCase):

    def setUp(self) -> None:
        self.simulation = FullSimulation(max_time=30000, intergeneration_time=(50, 70), stock_min=5)

    def test_run_simulation(self):
        self.simulation.run()

    def test_run_simulation_series(self):
        results_prob, results_avg_load = [], []
        times = np.linspace(0, 6, 7)
        for time in times:
            simulation = FullSimulation(max_time=35000, intergeneration_time=(50, 70), stock_min=time)
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


