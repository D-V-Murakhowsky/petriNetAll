import logging
from abc import ABC
from typing import List, Tuple, Dict

from .generator import Generator
from .models import SortedQueue
from .place import Place
from .transition import Transition


class Simulation(ABC):

    def __init__(self, max_time: int, generator: Dict, places: List[Dict], transitions: List[Dict], arcs: List[Tuple]):
        self._max_time: float = max_time
        self._time_moments = SortedQueue()
        self._generator, self._places, self._transitions = self._create_elements(generator, places, transitions)
        self._set_connections(arcs)

    @property
    def generator(self):
        return self._generator

    @property
    def elements(self):
        for element in (self.places + self.transitions):
            yield element

    @property
    def places(self):
        return self._places

    @property
    def statistics(self):
        return '; '.join(f'Place: {place.str_id}, load={place.load}' for place in self._places)

    @property
    def transitions(self):
        return self._transitions

    def _set_connections(self, list_of_arcs: List[Tuple[str, str, int]]):
        for arc_in, arc_out, multiplicity in list_of_arcs:
            self._set_arc(arc_in, arc_out, multiplicity)

    def _set_arc(self, start: str, fin: str, multiplicity: int):
        start_element = self.get_element_by_id(start)
        fin_element = self.get_element_by_id(fin)
        start_element.add_output(fin_element, multiplicity)
        fin_element.add_input(start_element, multiplicity)

    def get_element_by_id(self, str_id: str):
        if str_id == 'Generator':
            return self._generator
        else:
            element = list(filter(lambda x: x.str_id == str_id, self.elements))
            if element:
                return element[0]
            else:
                raise ValueError(f'Element {str_id} not found')

    def run(self):
        logging.info('Simulation has started')
        counter = 1

        self._sort_transitions()

        for generator in self._generators:
            arrivals = self.generator.generate_tokens()
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

    def _create_elements(self, generator: Dict, places: List[Dict], transitions: List[Dict]) -> Tuple[Generator, List, List]:
        return Generator(parent=self, **generator),\
               [Place(parent=self, **value) for value in places],\
               [Transition(parent=self, **value) for value in transitions]

    def _return_statistics(self):
        response = {}
        for element in self.elements:
            if element.save_stats:
                response.update({f'{element.element_type}_{element.str_id}': element.statistics})
        return response

    def _sort_transitions(self):
        self._transitions = sorted(self._transitions, key=lambda x: x.priority)
