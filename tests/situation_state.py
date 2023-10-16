import services
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from interactions import ParticipantTypeSingle
from services import get_instance_manager
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry, Tunable, TunableReference


class CustomStateSituationTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    """
    Tests if the subject is in the provided CustomStatesSituation and in the provided situation state.
    """
    FACTORY_TUNABLES = {
        'situation': TunableReference(manager=get_instance_manager(Types.SITUATION)),
        'state_key': Tunable(tunable_type=str, default='Invalid'),
        'subject': TunableEnumEntry(tunable_type=ParticipantTypeSingle, default=ParticipantTypeSingle.Actor),
    }

    __slots__ = ('subject', 'situation', 'state_key',)

    def get_expected_args(self):
        return {'subjects': self.subject,}

    def __call__(self, subjects=(), **kwargs):
        subject = next(iter(subjects))
        situation_manager = services.get_zone_situation_manager()
        if situation_manager is not None:
            for situation in situation_manager.get_situations_sim_is_in(subject):
                if situation.guid64 == self.situation.guid64:
                    if getattr(situation, '_current_state_key', None) == self.state_key:
                        return TestResult.TRUE

        return TestResult(False, "Subject is not in situation, or the situation is not in the specified state", tooltip=self.tooltip)