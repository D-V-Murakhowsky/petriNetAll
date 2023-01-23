from numpy.random import default_rng
from .models import Distribution

from . import SEED


class _TimeGenerator:

    _np_generator = default_rng() if SEED == -1 else default_rng(SEED)

    @classmethod
    def generate_time(cls, distro: Distribution):
        match distro.type_of_distribution:
            case 'const':
                return distro.loc
            case 'norm':
                return cls._np_generator.normal(loc=distro.loc, scale=distro.scale)
            case 'exp':
                return cls._np_generator.exponential(scale=distro.scale)
            case 'uniform':
                return cls._np_generator.uniform(low=distro.loc - distro.scale,
                                                 high=distro.loc + distro.scale)
            case 'erlang':
                return cls._np_generator.gamma(shape=distro.loc, scale=distro.scale)
            case '_':
                raise NotImplementedError
