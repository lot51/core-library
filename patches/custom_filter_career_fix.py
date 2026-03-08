import services
from interactions.utils.tunable import TunableCareerCustomSimFilter
from lot51_core import logger
from lot51_core.utils.injection import inject_to
from sims4.math import MAX_UINT32


@inject_to(TunableCareerCustomSimFilter, 'get_sim_filter_values')
def _get_sim_filter_values(original, *args, **kwargs):
    result = original(*args, **kwargs)
    for key, value in dict(result).items():
        if key > MAX_UINT32:
            logger.warn("A 64 bit career was removed from custom sim filter: {} {}".format(key, value))
            del result[key]
    return result
