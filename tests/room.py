from build_buy import get_room_id
from caches import cached_test
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from event_testing.test_events import TestEvent
from interactions import ParticipantTypeSingle
from lot51_core.tunables.object_query import ObjectSearchMethodVariant
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry


class ObjectInRoomTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    test_events = (TestEvent.InteractionStart,)

    FACTORY_TUNABLES = {
        'subject': TunableEnumEntry(tunable_type=ParticipantTypeSingle, default=ParticipantTypeSingle.Actor),
        'object_source': ObjectSearchMethodVariant()
    }

    __slots__ = ('subject', 'object_source')

    def get_expected_args(self):
        return {'subjects': self.subject}

    @cached_test
    def __call__(self, subjects=(), **kwargs):
        subject = next(iter(subjects))
        sim = subject.get_sim_instance()

        for obj in self.object_source.get_objects_gen():
            if obj.level == sim.level and get_room_id(sim.zone_id, sim.position, sim.level) == get_room_id(obj.zone_id, obj.position, obj.level):
                return TestResult.TRUE

        return TestResult(False, "No object found in room", tooltip=self.tooltip)