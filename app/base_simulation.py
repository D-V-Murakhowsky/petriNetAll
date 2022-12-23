import logging
from abc import ABC
from typing import List, Tuple

from .generator import Generator
from .models import SortedQueue
from .stock import Stock
from collections import Counter


class Simulation(ABC):

    def __init__(self, max_time: int, default_generator: bool = True, default_stock: bool = True):
        self._max_time = max_time
        self._time_moments = SortedQueue()

        if default_generator:
            self._generators = [Generator(simulation_time=max_time, parent=self)]
        else:
            self._generators = []

        self._places = []
        self._transitions = []

        if default_stock:
            self._stocks = [Stock(parent=self)]
        else:
            self._stocks = []

    @property
    def generators(self):
        return self._generators

    @property
    def most_common_time_moment(self):
        return Counter(self._time_moments.values).most_common(1)[0][1]

    @property
    def places(self):
        return self._places

    @property
    def stocks(self):
        return self._stocks

    @property
    def time_moments(self):
        return self._time_moments

    @property
    def total_load(self):
        return sum(place.load for place in self._places)

    @property
    def transitions(self):
        return self._transitions

    def init_time_intervals(self, time_intervals: List[int]):
        self._time_moments.update(time_intervals)

    def set_arcs(self, list_of_arcs: List[Tuple[str, str, int]]):
        for arc_in, arc_out, _ in list_of_arcs:
            self._set_arc(arc_in, arc_out)

    def _set_arc(self, start: str, fin: str):
        start_element = self._get_element_by_id(start)
        fin_element = self._get_element_by_id(fin)
        start_element.add_output(fin_element)
        fin_element.add_input(start_element)

    def _get_element_by_id(self, str_id: str):
        if str_id == 'Generator':
            return self._generators[0]
        elif str_id == 'Stock':
            return self._stocks[0]
        else:
            element = list(filter(lambda x: x._id == str_id, self._places))
            if element:
                return element[0]
            else:
                element = list(filter(lambda x: x._id == str_id, self._transitions))
                if element:
                    return element[0]
                else:
                    raise ValueError(f'Element {str_id} not found')

    def run(self):
        for generator in self._generators:
            generator.generate_tokens()

        timer = self._time_moments.get()

        while not self._time_moments.is_empty:
            logging.debug(f'Time = {timer}')

            for generator in self._generators:
                generator.process(timer=timer)
            for transition in self.transitions:
                times = list(filter(lambda x: self._max_time >= x > timer, transition.process(timer=timer)))
                self._time_moments.check_update(times)

            timer = self._time_moments.get()

        print(f'Simulation time = {self._max_time}')
        print(f'Total entities arrived: {sum([generator.total_elements for generator in self._generators])}')
        print(f'Total entities processed: {sum([stock.load for stock in self._stocks])}')

    def _create_model(self):
        pass

    def _describe_step(self):
        for place in self._places:
            print(place)
        for stock in self._stocks:
            print(stock)
        print(f'Model total load is {self.total_load}')
