import logging
from collections import Counter
from typing import List, Tuple, Dict, NoReturn, Union, Any

from .generator import Generator
from .models import SortedQueue
from .place import Place
from .transition import Transition


class Simulation:

    # TODO Extract scheme from Simulation. Use it as a mediator.

    def __init__(self, max_time: float, generator: Dict, places: List[Dict], transitions: List[Dict], arcs: List[Tuple]):
        # призначення полів екземпляру класу
        self._max_time: float = max_time
        self._time_moments = SortedQueue(iterable=[0])
        self._generator, self._places, self._transitions = self._create_elements(generator, places, transitions)
        self._has_conflict_transitions: bool = False
        self._active_elements = None

        # ініціалізація моделі
        self._check_and_modify_elements()
        self._set_connections(arcs)
        self._generate_iteration_sequence()

    def __repr__(self):
        return f'Simulation with duration={self.max_time}, number of places: {len(self.places)},' \
               f' number of transitions: {len(self.transitions)}.'

    @property
    def generator(self):
        return self._generator

    @property
    def elements(self):
        for element in (self.places + self.transitions):
            yield element

    @property
    def max_time(self):
        return self._max_time

    @property
    def places(self):
        return self._places

    @property
    def transitions(self):
        return self._transitions

    def run(self):
        """
        Основний метод, що виконує прогін симуляції
        :return: повертає статистику прогону симуляції
        """
        logging.info('Simulation has started')
        counter = 1
        timer = self._time_moments.pop()

        while True:
            logging.debug(f'Time = {timer}')

            for element in self._active_elements:

                if isinstance(element, list):
                    # виконання ітераційного циклу конфліктних переходів
                    # у циклі з пост умовою
                    while True:
                        moments_sequence = []
                        for conflict_element in element:
                            if (moment := conflict_element.process(timer=timer)) is not None:
                                moments_sequence.append(moment)
                                break

                        if len(moments_sequence) == 0:
                            break
                    self._time_moments.check_update(list(filter(lambda x: x > timer, moments_sequence)))

                else:
                    # виконання процесу генератора / звичайного переходу
                    if (values := element.process(timer=timer)) is not None:
                        self._time_moments.check_update(list(filter(lambda x: x > timer, values)))
                    pass

            for place in self._places:
                place.process(timer)

            if not self._time_moments.is_empty:

                if (value := self._time_moments.pop()) > self._max_time:
                    break
                else:
                    timer = value
                    counter += 1
            else:
                break

        print(f'Total simulation_zero time = {timer}')
        print(f'Total entities arrived: {self._generator.total_arrivals}')

        return self._return_statistics()

    def _get_element_by_id(self, str_id: str) -> Union[Any, None]:
        """
        Повертає посилання на елемент імітаційної моделі по символьному ідентифікатору
        :param str_id: символьний ідентифікатор елемента схеми
        :return: посилання на елемент, або None, якщо елемент не знайдено
        """
        if str_id == 'Generator':
            return self._generator
        else:
            element = list(filter(lambda x: x.str_id == str_id, self.elements))
            if element:
                return element[0]
            else:
                raise ValueError(f'Element {str_id} not found')

    def _set_connections(self, list_of_arcs: List[Tuple[str, str, int]]) -> NoReturn:
        """
        Встановлення зв'язків між елементами імітаційної моделі
        :param list_of_arcs: перелік дуг
        :return:
        """
        for arc_in, arc_out, multiplicity in list_of_arcs:
            self._set_arc(arc_in, arc_out, multiplicity)

    def _set_arc(self, start: str, fin: str, multiplicity: int) -> NoReturn:
        """
        Встановлення дуги (зв'язку) між елементами за символьними ідентифікаторами
        :param start: ідентифікатор елементу, що відповідає початку дуги
        :param fin: ідентифікатор елементу, що відповідає кінцю дуги
        :param multiplicity: кратність зв'язку
        :return: None
        """
        start_element = self._get_element_by_id(start)
        fin_element = self._get_element_by_id(fin)
        start_element.add_output(fin_element, multiplicity)
        fin_element.add_input(start_element, multiplicity)

    def _create_elements(self, generator: Dict, places: List[Dict], transitions: List[Dict]) \
            -> Tuple[Generator, List, List]:
        """
        Створює елементи на основі словників властивостей елементів
        :param generator: властивості генератора
        :param places: список властивостей місць
        :param transitions: список властивостей переходів
        :return:
        """
        return Generator(parent=self, **generator),\
               [Place(parent=self, **value) for value in places],\
               [Transition(parent=self, **value) for value in transitions]

    def _return_statistics(self) -> Dict:
        """
        Повертає статистику після прогону імітаційної моделі
        :return:
        """
        response = {}
        for element in self.elements:
            if element.save_stats:
                response.update({f'{element.element_type}_{element.str_id}': element.statistics})
        return response

    def _check_and_modify_elements(self):
        """
        Метод перевірки коректності встановлених аргументів елементів імітаційної схеми,
        а також встановлення додаткових аргументів під час перевірки елементів.
        Для реалізації конфліктних переходів проставляє прапорці конфліктних переходів у відповідних переходів
        :return:
        """
        # TODO Add elements correctness check
        self._has_conflict_transitions = (priorities_count := Counter([item.priority for item in self._transitions])).most_common(1)[0][1] > 1
        if self._has_conflict_transitions:
            conflict_priorities_numbers = dict(filter(lambda x: x[1] > 1, priorities_count.items())).keys()
            for element in self._transitions:
                if element.priority in conflict_priorities_numbers:
                    element.is_conflict = True

    def _generate_iteration_sequence(self) -> NoReturn:
        """
        Генерація послідовності активних елементів (генератор та переходи).
        Конфліктні переходи поєднуються у єдину групу
        :return: None
        """
        if not self._has_conflict_transitions:
            # якщо немає конфліктних переходів, список може бути створений без додаткового ітераційного циклу
            return [self._generator] + self._transitions

        else:
            self._active_elements = [self._generator]
            priorities_count = Counter([item.priority for item in self._transitions])
            sub_list = []
            for element in self._transitions:
                if priorities_count[element.priority] == 1:
                    if len(sub_list) > 0:
                        self._active_elements.append(sub_list)
                    self._active_elements.append(element)
                    sub_list = []
                else:
                    sub_list.append(element)
            if len(sub_list) > 0:
                self._active_elements.append(sub_list)


