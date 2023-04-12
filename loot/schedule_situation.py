import random
from collections import namedtuple
import alarms
from date_and_time import create_time_span
from interactions.utils.loot_basic_op import BaseLootOperation
from lot51_core import logger
from sims4.tuning.tunable import TunableInterval, TunableVariant
from situations.tunable import TunableSituationStart


class ScheduleSituationWithDelayLoot(BaseLootOperation):
    SITUATION_HANDLES = {}
    create_situation_handle = namedtuple('SituationHandle', ('create_situation',))

    FACTORY_TUNABLES = {
        'create_situation': TunableSituationStart(),
        'time_delay': TunableInterval(default_lower=0, default_upper=0, tunable_type=int),
    }

    @classmethod
    def handle_situation_alarm(cls, handle):
        try:
            if handle in cls.SITUATION_HANDLES:
                situation_handle = cls.SITUATION_HANDLES[handle]
                situation_handle.create_situation()
                del cls.SITUATION_HANDLES[handle]
        except:
            logger.exception("[ScheduleSituationWithDelayLoot] failed on alarm handle")

    def __init__(self, create_situation=None, time_delay=None, **kwargs):
        self._create_situation = create_situation
        self._time_delay = time_delay
        super().__init__(**kwargs)

    def _apply_to_subject_and_target(self, subject, target, resolver):
        situation_handle = self.create_situation_handle(self._create_situation(resolver))
        delay = random.randint(self._time_delay.lower_bound, self._time_delay.upper_bound)
        time_span = create_time_span(minutes=delay)

        alarm_handle = alarms.add_alarm(subject, time_span, self.handle_situation_alarm)

        ScheduleSituationWithDelayLoot.SITUATION_HANDLES[alarm_handle] = situation_handle


class ScheduleSituationVariant(TunableVariant):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, time_delay=ScheduleSituationWithDelayLoot.TunableFactory(), default='time_delay', **kwargs)
