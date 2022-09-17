# Learn how to create your own tests following Frankk's guide
# at https://frankkmods.medium.com/custom-tuning-tests-sims-4-script-modding-3837e214fb68
from lot51_core.tests.lock_out import AffordanceLockOutTest
from sims4.common import Pack, are_packs_available
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from caches import cached_test
from interactions import ParticipantTypeSingle
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry
from event_testing.tests import TestSetInstance, TunableTestVariant, _TunableTestSetBase


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


class LotFiftyOneCoreTestSet(_TunableTestSetBase, is_fragment=True):
    MY_TEST_VARIANTS = {
        'has_pack': PackTest,
        'affordance_lock_out': AffordanceLockOutTest,
    }

    def __init__(self, **kwargs):
        for test_name, test in self.MY_TEST_VARIANTS.items():
            TunableTestVariant.TEST_VARIANTS[test_name] = test.TunableFactory
        super().__init__(test_locked_args={}, **kwargs)


class LotFiftyOneLibTestSetInstance(TestSetInstance):
    INSTANCE_TUNABLES = {'test': LotFiftyOneCoreTestSet()}
