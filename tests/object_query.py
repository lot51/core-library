from caches import cached_test
from event_testing.resolver import RESOLVER_PARTICIPANT
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from event_testing.test_events import TestEvent
from lot51_core import logger
from lot51_core.tunables.object_query import ObjectSearchMethodVariant
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableThreshold


class ObjectQueryTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    test_events = (TestEvent.ObjectAdd, TestEvent.ObjectDestroyed, TestEvent.OnExitBuildBuy, TestEvent.OnBuildBuyReset, TestEvent.OnInventoryChanged, TestEvent.ObjectStateChange, TestEvent.OnInventoryChanged, TestEvent.TraitAddEvent, TestEvent.TraitRemoveEvent, TestEvent.BuffUpdateEvent,)

    FACTORY_TUNABLES = {
        'object_query': ObjectSearchMethodVariant(),
        'threshold': TunableThreshold(description="The threshold that must be met based on the number of objects returned from the query")
    }

    __slots__ = ('object_query', 'threshold',)

    def get_expected_args(self):
        return {'resolver': RESOLVER_PARTICIPANT}

    @cached_test
    def __call__(self, resolver=None, **kwargs):
        results = tuple(self.object_query.get_objects_gen(resolver=resolver))
        total_items = len(results)
        threshold_met = self.threshold.compare(total_items)
        # logger.debug("object query test: {} {}, results: {}, total items {}, threshold met? {}".format(self, resolver, results, total_items, threshold_met))
        if not threshold_met:
            return TestResult(False, "Object query does not meet threshold", tooltip=self.tooltip)
        return TestResult.TRUE