from build_buy import FloorFeatureType, find_floor_feature
from terrain import is_terrain_tag_at_position
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from interactions import ParticipantTypeSingle
from sims.sim_info import SimInfo
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry, Tunable, OptionalTunable, TunableEnumSet
from world.terrain_enums import TerrainTag


class TerrainTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    """
    Tests against terrain features/tags at the location of the subject
    """
    test_events = ()

    FACTORY_TUNABLES = {
        'subject': TunableEnumEntry(tunable_type=ParticipantTypeSingle, default=ParticipantTypeSingle.Actor),
        'terrain_feature': OptionalTunable(
            description='Tune this if you want to require a floor feature to be present',
            tunable=TunableEnumEntry(
                tunable_type=FloorFeatureType,
                default=FloorFeatureType.BURNT
            )
        ),
        'terrain_feature_radius': Tunable(
            description='The radius to look for the floor feature, if one is tuned in terrain_feature',
            tunable_type=float, default=2.0
        ),
        'terrain_tags': OptionalTunable(
            description='If checked, will verify the location of the test is currently on one of the tuned terrain tags.',
            tunable=TunableEnumSet(
                description='A set of terrain tags. Only one of these tags needs to be present at this location. Although it is not tunable, there is a threshold weight underneath which a terrain tag will not appear to be present.',
                enum_type=TerrainTag, enum_default=TerrainTag.INVALID
            )
        ),
    }

    __slots__ = ('subject', 'terrain_feature', 'terrain_tags', 'terrain_feature_radius')

    def get_expected_args(self):
        return {'subjects': self.subject}

    def __call__(self, subjects=(), **kwargs):
        subject = next(iter(subjects))

        if isinstance(subject, SimInfo):
            subject = subject.get_sim_instance()

        if self.terrain_feature is not None:
            if not find_floor_feature(subject.zone_id, self.terrain_feature, subject.location, subject.level, self.terrain_feature_radius):
                return TestResult(False, "Floor feature not found near subject", tooltip=self.tooltip)

        if self.terrain_tags is not None:
            if not is_terrain_tag_at_position(subject.position.x, subject.position.z, self.terrain_tags, level=subject.level):
                return TestResult(False, 'Terrain tag not found near subject', tooltip=self.tooltip)

        return TestResult.TRUE
