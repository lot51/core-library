import services
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.tunables.test_injection import TestInjectionVariant
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference


class TunableTestSetInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'test_set': TunableReference(manager=services.get_instance_manager(Types.SNIPPET)),
        'modify_test': TestInjectionVariant(),
    }

    __slots__ = ('test_set', 'modify_test',)

    def inject(self):
        if self.test_set is not None:
            self.modify_test.inject(self.test_set, 'test')
