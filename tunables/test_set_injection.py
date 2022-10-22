import services
from event_testing.tests import TunableTestSet
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableReference


class TunableTestSetInjection(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'test_set': TunableReference(manager=services.get_instance_manager(Types.SNIPPET)),
        'tests': TunableTestSet(),
    }

    __slots__ = ('test_set', 'tests',)

    def inject(self):
        if self.test_set is not None and self.tests is not None:
            self.test_set.test += self.tests
