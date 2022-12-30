from sims4.common import Pack, are_packs_available
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from caches import cached_test
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry


class PackTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {
        'pack': TunableEnumEntry(
            description='Pack required for this test to pass.',
            tunable_type=Pack,
            default=Pack.BASE_GAME
        )
    }

    __slots__ = ('pack',)

    def get_expected_args(self):
        return {}

    @cached_test
    def __call__(self, **kwargs):
        if are_packs_available(self.pack):
            return TestResult.TRUE
        return TestResult(False, "Pack not installed", tooltip=self.tooltip)