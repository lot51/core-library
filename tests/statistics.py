from caches import cached_test
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from event_testing.test_events import TestEvent
from interactions import ParticipantTypeSingle
from objects.components.types import STATISTIC_COMPONENT
from services import get_instance_manager
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry, TunableReference
from statistics.commodity import Commodity


class StatisticLockedTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    test_events = (TestEvent.ObjectStateChange,)

    FACTORY_TUNABLES = {
        'subject': TunableEnumEntry(
            description='The subject of the test.',
            tunable_type=ParticipantTypeSingle,
            default=ParticipantTypeSingle.Object
        ),
        'stat': TunableReference(manager=get_instance_manager(Types.STATISTIC), class_restrictions=(Commodity,)),
    }

    __slots__ = ('subject', 'stat',)

    def get_expected_args(self):
        return {'subjects': self.subject}

    @cached_test
    def __call__(self, subjects=(), **kwargs):
        subject = next(iter(subjects))
        if subject is None or self.stat is None:
            return TestResult.NONE

        statistic_component = subject.get_component(STATISTIC_COMPONENT)
        if statistic_component is None:
            return TestResult.NONE

        if self.stat in statistic_component._locked_commodities:
            return TestResult.TRUE

        for modifier in subject.autonomy_modifiers:
            if modifier._locked_stats is not None and self.stat in modifier._locked_stats:
                return TestResult.TRUE

        return TestResult(False, "Commodity is not locked", tooltip=self.tooltip)
