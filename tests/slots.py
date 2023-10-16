from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from interactions import ParticipantTypeSingle
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry


class ObjectSlotInUseTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    """
    Tests if the subject has any object slotted into it
    """

    FACTORY_TUNABLES = {
        'subject': TunableEnumEntry(tunable_type=ParticipantTypeSingle, default=ParticipantTypeSingle.Object),
    }

    __slots__ = ('subject',)

    def get_expected_args(self):
        return {'subjects': self.subject}

    def __call__(self, subjects=(), **kwargs):
        subject = next(iter(subjects))
        for runtime_slot in subject.get_runtime_slots_gen():
            for child in runtime_slot.children:
                return TestResult.TRUE

        return TestResult(False, "Subject does not have a slot in use", tooltip=self.tooltip)


