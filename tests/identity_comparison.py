from caches import cached_test
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from interactions import ParticipantTypeSingle
from sims4.tuning.tunable import AutoFactoryInit, Tunable, TunableEnumEntry, HasTunableSingletonFactory


class IdentityComparisonTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    """
    An alternative to the Maxis `identity` test that only works within an Interaction context.

    Also fixes a potential bug when using `use_part_owner` in combination with `use_definition`
    """
    test_events = ()
    FACTORY_TUNABLES = {
        'description': 'Require the specified participants to be the same, or, alternatively, require them to be different.',
        'subject_a': TunableEnumEntry(
            description='The participant to be compared to subject_b.',
            tunable_type=ParticipantTypeSingle,
            default=ParticipantTypeSingle.Actor
        ),
        'subject_b': TunableEnumEntry(
            description='The participant to be compared to subject_a.',
            tunable_type=ParticipantTypeSingle,
            default=ParticipantTypeSingle.Object
        ),
        'subjects_match': Tunable(
            description='If True, subject_a must match subject_b. If False, they must not.',
            tunable_type=bool,
            default=False
        ),
        'use_definition': Tunable(
            description='If checked, the two subjects will only compare definition. Not the instance. This will mean two different types of chairs, for instance, can return True if they use the same chair object definition.',
            tunable_type=bool,
            default=False
        ),
        'use_part_owner': Tunable(
            description='If checked, the two subjects will compare based on the part owner if either are a part.',
            tunable_type=bool, default=False
        )
    }

    __slots__ = ('subject_a', 'subject_b', 'use_part_owner', 'use_definition', 'subjects_match',)

    def get_expected_args(self):
        return {
            'subject_a': self.subject_a,
            'subject_b': self.subject_b,
        }

    @cached_test
    def __call__(self, subject_a=None, subject_b=None, **kwargs):
        subject_a = next(iter(subject_a), None)
        subject_b = next(iter(subject_b), None)
        if self.use_part_owner:
            if subject_a and subject_a.is_part:
                subject_a = subject_a.part_owner
            if subject_b and subject_b.is_part:
                subject_b = subject_b.part_owner
        if self.use_definition:
            if subject_a:
                subject_a = subject_a.definition
            if subject_b:
                subject_b = subject_b.definition
        if self.subjects_match:
            if subject_a != subject_b:
                return TestResult(False, '{} must match {}, but {} is not {}', self.subject_a, self.subject_b, subject_a, subject_b, tooltip=self.tooltip)
        elif subject_a == subject_b:
            return TestResult(False, '{} must not match {}, but {} is {}', self.subject_a, self.subject_b, subject_a, subject_b, tooltip=self.tooltip)
        return TestResult.TRUE
