import services
from caches import cached_test
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from event_testing.test_events import TestEvent
from event_testing.tests import TestList
from interactions import ParticipantTypeSingle, ParticipantType
from sims.sim_info_tests import SimInfoTest
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry, Tunable


class HomeOwnerWithRequirementsOnLot(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    """
    Tests if a lot owner (of the current lot) is instanced and passes the sim info test.
    """
    test_events = (TestEvent.InteractionStart,)
    FACTORY_TUNABLES = {
        'subject': TunableEnumEntry(
            description='The subject of the test.',
            tunable_type=ParticipantTypeSingle,
            default=ParticipantTypeSingle.Actor
        ),
        'invert': Tunable(
            description="If true, the result of the test will be inverted.",
            tunable_type=bool,
            default=False
        ),
        'sim_info': SimInfoTest.TunableFactory(locked_args={'tooltip': None, 'who': ParticipantType.Actor})
    }

    __slots__ = ('subject', 'invert', 'sim_info')

    def get_expected_args(self):
        return {'subjects': self.subject}

    @cached_test
    def __call__(self, **kwargs):
        if self.sim_info is not None:
            household = services.active_household()
            for sim in household.instanced_sims_gen():
                resolver = sim.get_resolver()
                # check sim info test
                if resolver(self.sim_info):
                    if self.invert:
                        return TestResult(False, "Home owner on lot with requirements and is not the desired result")
                    return TestResult.TRUE
        if self.invert:
            return TestResult.TRUE
        return TestResult(False, "Home owner not on lot with requirements and is not the desired result")
