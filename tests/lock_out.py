from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from interactions import ParticipantType, ParticipantTypeSingle
from lot51_core.snippets.lock_out import lock_out_service
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry


class AffordanceLockOutTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {
        'subject': TunableEnumEntry(
            description='The subject of the test.',
            tunable_type=ParticipantTypeSingle,
            default=ParticipantTypeSingle.Actor
        ),
        'target': TunableEnumEntry(
            description='The target of the test.',
            tunable_type=ParticipantTypeSingle,
            default=ParticipantTypeSingle.Object
        ),
    }

    __slots__ = ('subject', 'target',)

    def get_expected_args(self):
        return {'subjects': self.subject, 'targets': self.target, 'affordance': ParticipantType.Affordance}

    def __call__(self, subjects=(), targets=(), affordance=None, **kwargs):
        actor = next(iter(subjects))
        target = next(iter(targets))
        if actor and affordance:
            if lock_out_service.is_locked_out(actor, affordance, target=target):
                return TestResult(False, 'Super affordance is locked out')
        return TestResult.TRUE

