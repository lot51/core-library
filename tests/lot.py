import services
from sims4.tuning.tunable import TunableThreshold, HasTunableSingletonFactory, AutoFactoryInit
from event_testing.test_events import TestEvent
from event_testing.test_base import BaseTest
from event_testing.results import TestResult
from caches import cached_test


class LotSizeTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    test_events = (TestEvent.SimTravel, TestEvent.HouseholdChanged,)
    FACTORY_TUNABLES = {
        'threshold': TunableThreshold(description="The lot size threshold the current lot must meet")
    }

    __slots__ = ('threshold',)

    def get_expected_args(self):
        return {}

    @cached_test
    def __call__(self, **kwargs):
        lot = services.current_zone().lot
        total_size = lot.size_x * lot.size_z
        if not self.threshold.compare(total_size):
            return TestResult(False, "Lot size does not meet threshold", tooltip=self.tooltip)
        return TestResult.TRUE
