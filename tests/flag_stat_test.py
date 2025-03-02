import services
from caches import cached_test
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from event_testing.test_events import TestEvent
from interactions import ParticipantTypeSingle
from lot51_core.utils.flags import Flag
from sims4.math import MAX_INT32
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry, Tunable, \
    TunableReference, TunableRange


class FlagStatTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    test_events = (TestEvent.StatValueUpdate,)
    FACTORY_TUNABLES = {
        'subject': TunableEnumEntry(
            description='The subject of the test.',
            tunable_type=ParticipantTypeSingle,
            default=ParticipantTypeSingle.Object
        ),
        'stat_type': TunableReference(manager=services.get_instance_manager(Types.STATISTIC)),
        'flag_value': TunableRange(tunable_type=int, default=1, minimum=0, maximum=MAX_INT32),
        'has_value': Tunable(tunable_type=bool, default=True),
        'pass_if_flag_null': Tunable(tunable_type=bool, default=False),
    }

    __slots__ = ('subject', 'stat_type', 'flag_value', 'has_value', 'pass_if_flag_null',)

    def get_expected_args(self):
        return {'subjects': self.subject}

    @cached_test
    def __call__(self, subjects=(), **kwargs):
        subject = next(iter(subjects))
        if self.stat_type is not None:
            stat = subject.get_tracker(self.stat_type).get_statistic(self.stat_type)
            if stat is not None:
                flag = Flag(stat.get_value())
                if flag.has(1 << self.flag_value) == self.has_value:
                    return TestResult.TRUE
                if flag.get() == 0 and self.pass_if_flag_null:
                    return TestResult.TRUE
            elif not self.has_value:
                return TestResult.TRUE
            elif self.pass_if_flag_null:
                return TestResult.TRUE

        return TestResult(False, "Flag value ({}) failed, expected to have? {}".format(self.flag_value, self.has_value))
