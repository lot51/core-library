from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from interactions import ParticipantTypeSingle
from objects.components.types import STORED_SIM_INFO_COMPONENT
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry, Tunable, OptionalTunable


class StoredSimComponentTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    """
    Tests if the subject has a stored sim component
    """

    FACTORY_TUNABLES = {
        'require_stored_sim': OptionalTunable(
            tunable=Tunable(tunable_type=bool, default=True),
        ),
        'target': TunableEnumEntry(tunable_type=ParticipantTypeSingle, default=ParticipantTypeSingle.Object),
    }

    __slots__ = ('target', 'require_stored_sim',)

    def get_expected_args(self):
        return {'targets': self.target,}

    def __call__(self, targets=(), **kwargs):
        target = next(iter(targets))

        component = target.get_component(STORED_SIM_INFO_COMPONENT)
        has_stored_sim = component is not None
        if self.require_stored_sim is not None and has_stored_sim != self.require_stored_sim:
            return TestResult(False, "Target does not match required stored sim value: {}".format(self.require_stored_sim), tooltip=self.tooltip)

        return TestResult.TRUE
