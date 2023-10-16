from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from interactions import ParticipantType, ParticipantTypeSingle
from lot51_core import logger
from lot51_core.services.events import event_handler, CoreEvent
from lot51_core.snippets.lock_out import AffordanceLockOutSnippet
from lot51_core.services.lock_out_registry import lock_out_registry
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
            if lock_out_registry.is_locked_out(actor, affordance, target=target):
                return TestResult(False, 'Super affordance is locked out')
        return TestResult.TRUE


@event_handler(CoreEvent.TUNING_LOADED)
def _inject_lock_out(*args, **kwargs):
    test = AffordanceLockOutTest(subject=ParticipantType.Actor, target=ParticipantType.Object)
    for snippet in AffordanceLockOutSnippet.all_snippets_gen():
        for row in snippet.lock_out:
            for affordance in row.affordances:
                if affordance is not None:
                    affordance.add_additional_test(test)
                    logger.debug("[AffordanceLockOutSnippet] added test to affordance {} in snippet: {}".format(affordance, snippet))
                else:
                    logger.debug("[AffordanceLockOutSnippet] an affordance was None in snippet: {}".format(snippet))
