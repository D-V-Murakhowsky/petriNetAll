import logging
from abc import ABC
from typing import List, Tuple

from .generator import Generator
from .models import SortedQueue
from .terminator import Terminator


class Simulation(ABC):

    def __init__(self, max_time: int, default_generator: bool = True, default_stock: bool = True,
                 intergeneration_time: Tuple[int, int] = (1, 1)):
        self._max_time = max_time
        self._time_moments = SortedQueue()

        if default_generator:
            self._generators = [Generator(simulation_time=max_time, parent=self, str_id='Generator',
                                          intergeneration_time=intergeneration_time)]
        else:
            self._generators = []

        self._places = []
        self._transitions = []

        if default_stock:
            self._stocks = [Terminator(parent=self, str_id='Terminator')]
        else:
            self._stocks = []

    @property
    def generators(self):
        return self._generators

    @property
    def places(self):
        return self._places

    @property
    def stocks(self):
        return self._stocks

    @property
    def transitions(self):
        return self._transitions

    def add_generators(self, names: List[str]):
        for name in names:
            self._generators.append(Generator(simulation_time=self._max_time, parent=self, str_id=name))

    def add_stocks(self, names: List[str]):
        for name in names:
            self._stocks.append(Terminator(parent=self, str_id=name))

    def set_arcs(self, list_of_arcs: List[Tuple[str, str, int]]):
        for arc_in, arc_out, multiplicity in list_of_arcs:
            self._set_arc(arc_in, arc_out, multiplicity)

    def _set_arc(self, start: str, fin: str, multiplicity: int):
        start_element = self.get_element_by_id(start)
        fin_element = self.get_element_by_id(fin)
        start_element.add_output(fin_element, multiplicity)
        fin_element.add_input(start_element, multiplicity)

    def get_element_by_id(self, str_id: str):
        if str_id == 'Generator':
            return self._generators[0]
        elif str_id == 'Terminator':
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
                    if len(self._stocks) == 1:
                        raise ValueError(f'Element {str_id} not found')
                    else:
                        element = list(filter(lambda x: x._id == str_id, self._stocks))
                        if element:
                            return element[0]
                        else:
                            raise ValueError(f'Element {str_id} not found')

    def run(self):
        logging.debug('Simulation has started')

        self._sort_transitions()

        for generator in self._generators:
            self._time_moments.check_update(generator.generate_tokens())

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
        for stock in self._stocks:
            print(f'{stock.str_id}: {stock.load}')

    def _create_model(self):
        pass

    def _sort_transitions(self):
        self._transitions = sorted(self._transitions, key=lambda x: x.priority)
