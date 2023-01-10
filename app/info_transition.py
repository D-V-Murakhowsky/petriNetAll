from .transition import Transition
from .models import Entity

from typing import Callable


class InfoTransition(Transition):

    def _make_transitions(self, timer: int, condition: Callable):
        if condition:
            self._outputs[0].append(Entity(timer=timer))
        else:
            self._outputs[1].append(Entity(timer=timer))
