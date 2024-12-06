from event_testing.resolver import DoubleObjectResolver
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from event_testing.tests import TunableTestSet
from interactions import ParticipantTypeSingle
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry


class InventoryOwnerTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    """
    Tests if the subject is in an inventory, and runs additional tests against the inventory owner
    """
    test_events = ()

    FACTORY_TUNABLES = {
        'target': TunableEnumEntry(tunable_type=ParticipantTypeSingle, default=ParticipantTypeSingle.Object),
        'inventory_tests': TunableTestSet()
    }

    __slots__ = ('target', 'inventory_tests')

    def get_expected_args(self):
        return {'targets': self.target}

    def __call__(self, targets=(), **kwargs):
        target = next(iter(targets))
        if target is None or not target.is_in_inventory():
            return TestResult(False, "Object not found, or not in inventory", tooltip=self.tooltip)

        inventory_owner = target.inventoryitem_component.get_inventory().owner
        resolver = DoubleObjectResolver(target, inventory_owner)
        result =  self.inventory_tests.run_tests(resolver)
        if not result:
            return TestResult(False, "Inventory tests failed: {}".format(result), tooltip=self.tooltip)

        return TestResult.TRUE