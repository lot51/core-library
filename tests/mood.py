from event_testing.test_events import TestEvent
from lot51_core import logger
from services import get_instance_manager
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from caches import cached_test
from interactions import ParticipantTypeSingle
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry, TunableThreshold, TunableReference, OptionalTunable


class MoodIntensityTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    test_events = (TestEvent.MoodChange, TestEvent.SimTravel)

    FACTORY_TUNABLES = {
        'subject': TunableEnumEntry(
            description='The subject of the test.',
            tunable_type=ParticipantTypeSingle,
            default=ParticipantTypeSingle.Actor
        ),
        'mood': OptionalTunable(tunable=TunableReference(manager=get_instance_manager(Types.MOOD))),
        'threshold': TunableThreshold()
    }

    __slots__ = ('subject', 'threshold', 'mood',)

    def get_expected_args(self):
        return {'subjects': self.subject,}

    @cached_test
    def __call__(self, subjects=(), affordance=None, **kwargs):
        actor = next(iter(subjects))
        if actor:
            if actor.get_mood() != self.mood:
                return TestResult(False, "Sim's mood does not match required mood for intensity test", tooltip=self.tooltip)

            intensity = actor.get_mood_intensity()
            if self.threshold.compare(intensity):
                return TestResult.TRUE

        return TestResult(False, "Mood intensity does not meet threshold", tooltip=self.tooltip)


class MoodWeightTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    test_events = (TestEvent.MoodChange, TestEvent.SimTravel)

    FACTORY_TUNABLES = {
        'subject': TunableEnumEntry(
            description='The subject of the test.',
            tunable_type=ParticipantTypeSingle,
            default=ParticipantTypeSingle.Actor
        ),
        'mood': OptionalTunable(tunable=TunableReference(manager=get_instance_manager(Types.MOOD))),
        'threshold': TunableThreshold()
    }

    __slots__ = ('subject', 'threshold', 'mood',)

    def get_expected_args(self):
        return {'subjects': self.subject,}

    @cached_test
    def __call__(self, subjects=(), **kwargs):
        try:
            actor = next(iter(subjects))
            if actor and hasattr(actor, 'Buffs'):
                buff_component = actor.Buffs
                if self.mood is not None:
                    active_mood = self.mood
                else:
                    active_mood = buff_component._active_mood
                total_weight = sum(buff_entry.mood_weight for buff_entry in buff_component._active_buffs.values() if buff_entry.mood_type is active_mood)
                if self.threshold.compare(total_weight):
                    return TestResult.TRUE
            return TestResult(False, "Mood weight does not meet threshold", tooltip=self.tooltip)
        except:
            logger.exception("Failed during mood weight test")
            return TestResult(False, "Mood weight does not meet threshold", tooltip=self.tooltip)
