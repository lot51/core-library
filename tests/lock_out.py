from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from caches import cached_test
from event_testing.test_events import TestEvent
from interactions import ParticipantType, ParticipantTypeSingle
from lot51_core import logger
from lot51_core.snippets.lock_out import AffordanceLockOutRegistry
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry


class AffordanceLockOutTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    test_events = (TestEvent.InteractionComplete,)
    FACTORY_TUNABLES = {
        'subject': TunableEnumEntry(
            description='The subject of the test.',
            tunable_type=ParticipantTypeSingle,
            default=ParticipantTypeSingle.Actor
        ),
    }

    __slots__ = ('subject',)

    def get_expected_args(self):
        return {'subjects': self.subject, 'affordance': ParticipantType.Affordance}

    @cached_test
    def __call__(self, subjects=(), affordance=None, **kwargs):
        actor = next(iter(subjects))
        if actor and affordance:
            if AffordanceLockOutRegistry.is_locked_out(actor, affordance):
                logger.debug("test failed affordance is locked out {} {}".format(actor, affordance))
                return TestResult(False, 'Super affordance is locked out')
        return TestResult.TRUE

