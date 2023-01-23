import logging
from abc import ABC
from typing import List, Tuple

import numpy as np

from .generator import Generator
from .models import SortedQueue


class Simulation(ABC):

    def __init__(self, max_time: int, default_generator: bool = True):
        self._max_time = max_time
        self._time_moments = SortedQueue()

        if default_generator:
            self._generators = [Generator(simulation_time=max_time, parent=self, str_id='Generator')]
        else:
            self._generators = []

        self._places = []
        self._transitions = []

    @property
    def generators(self):
        return self._generators

    @property
    def iterate_elements(self):
        for element in (self.places + self.transitions):
            yield element

    @property
    def places(self):
        return self._places

    @property
    def statistics(self):
        return '; '.join(f'Place: {place.str_id}, load={place.load}' for place in self._places)

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
        logging.info('Simulation has started')
        counter = 1

        self._sort_transitions()

        for generator in self._generators:
            arrivals = generator.generate_tokens()
            self._time_moments.check_update(arrivals)

        timer = self._time_moments.pop()

        while True:
            logging.debug(f'Time = {timer}')

            for generator in self._generators:
                generator.process(timer=timer)

            for transition in self.transitions:
                self._time_moments.check_update(transition.process(timer=timer))

            for place in self._places:
                place.process(timer)

            logging.info(f'Step {counter}')
            logging.info(f'Simulation time = {timer}')
            logging.info(f'Total entities arrived: {sum([generator.total_arrivals for generator in self._generators])}')
            for stock in self._stocks:
                logging.info(f'{stock.str_id}: {stock.load}')

            if not self._time_moments.is_empty:

                if (value := self._time_moments.pop()) > self._max_time:
                    break
                else:
                    timer = value
                    counter += 1
            else:
                break

        print(f'Total simulation_zero time = {timer}')
        print(f'Total entities arrived: {sum([generator.total_arrivals for generator in self._generators])}')

        return self._return_statistics()

    def _create_model(self):
        pass

    def _return_statistics(self):
        response = {}
        for element in self.iterate_elements:
            if element.save_stats:
                response.update({f'{element.element_type}_{element.str_id}': element.statistics})
        return response

    def _sort_transitions(self):
        self._transitions = sorted(self._transitions, key=lambda x: x.priority)
