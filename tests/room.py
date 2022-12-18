import services
from build_buy import get_room_id
from event_testing.resolver import RESOLVER_PARTICIPANT
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from interactions import ParticipantTypeSingle
from lot51_core.tunables.object_query import ObjectSearchMethodVariant
from objects.terrain import TerrainPoint
from sims.sim_info import SimInfo
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry


class ObjectInRoomTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    test_events = ()

    FACTORY_TUNABLES = {
        'subject': TunableEnumEntry(tunable_type=ParticipantTypeSingle, default=ParticipantTypeSingle.Actor),
        'object_source': ObjectSearchMethodVariant()
    }

    __slots__ = ('subject', 'object_source')

    def get_expected_args(self):
        return {'subjects': self.subject, 'resolver': RESOLVER_PARTICIPANT}

    def __call__(self, subjects=(), resolver=None, **kwargs):
        subject = next(iter(subjects))

        if isinstance(subject, SimInfo):
            subject = subject.get_sim_instance()
            if subject is None:
                return TestResult(False, "Target sim is not instanced", tooltip=self.tooltip)
            zone_id = subject.zone_id
        elif isinstance(subject, TerrainPoint):
            zone_id = services.current_zone_id()
        else:
            zone_id = subject.zone_id

        all_results = list()
        for obj in self.object_source.get_objects_gen(resolver=resolver):
            result = obj.level == subject.level and get_room_id(zone_id, subject.position, subject.level) == get_room_id(obj.zone_id, obj.position, obj.level)
            all_results.append(result)

        if len(all_results) and any(all_results):
            return TestResult.TRUE

        return TestResult(False, "No object found in room", tooltip=self.tooltip)
