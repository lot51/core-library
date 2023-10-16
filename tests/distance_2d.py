import sims4
from caches import cached_test
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from interactions import ParticipantTypeSingle
from sims.sim_info import SimInfo
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry, TunableThreshold


class Distance2dTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    """
    Performs a distance test using only X and Z. Use the level difference modifier to increase/decrease the Y axis distance.
    """

    FACTORY_TUNABLES = {
        'subject': TunableEnumEntry(
            description='The subject of the test.',
            tunable_type=ParticipantTypeSingle,
            default=ParticipantTypeSingle.Actor
        ),
        'target': TunableEnumEntry(
            description='The subject of the test.',
            tunable_type=ParticipantTypeSingle,
            default=ParticipantTypeSingle.Object
        ),
        'radius_threshold': TunableThreshold(),
        'level_difference_threshold':TunableThreshold(),
    }

    __slots__ = ('subject', 'target', 'radius_threshold', 'level_difference_threshold',)

    def get_expected_args(self):
        return {'subjects': self.subject, 'targets': self.target}

    @cached_test
    def __call__(self, subjects=(), targets=(), **kwargs):
        subject = next(iter(subjects))
        target = next(iter(targets))
        if isinstance(subject, SimInfo):
            subject = subject.get_sim_instance()
        if isinstance(target, SimInfo):
            target = target.get_sim_instance()

        if subject is None or target is None:
            return TestResult(False, 'Subject or target missing', tooltip=self.tooltip)

        subject_position = sims4.math.Vector2(subject.position.x, subject.position.z)
        target_position = sims4.math.Vector2(target.position.x, target.position.z)

        distance = (target_position - subject_position).magnitude()
        if not self.radius_threshold.compare(distance):
            return TestResult(False, 'Distance between subject and target did not meet threshold. Actual: {}'.format(distance), tooltip=self.tooltip)

        level_difference = abs(subject.level - target.level)
        if not self.level_difference_threshold.compare(level_difference):
            return TestResult(False, 'Level difference between subject and target did not meet threshold. Actual: {}'.format(level_difference), tooltip=self.tooltip)

        return TestResult.TRUE