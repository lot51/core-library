import services
from lot51_core import logger
from lot51_core.loot import LotFiftyOneCoreLootActionVariant
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.tunables.test_injection import TestInjectionVariant
from lot51_core.utils.injection import inject_list
from sims4.resources import Types
from interactions.utils.loot_ops import DoNothingLootOp
from sims4.tuning.tunable import TunableReference, TunableList, TunableTuple
from tunable_multiplier import TunableMultiplier


class TunableLootInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'loot': TunableReference(manager=services.get_instance_manager(Types.ACTION)),
        'ops': TunableList(tunable=LotFiftyOneCoreLootActionVariant()),
        'modify_tests': TestInjectionVariant(),
    }

    __slots__ = ('loot', 'ops', 'modify_tests',)

    def inject(self):
        if self.loot is None:
            logger.warn("Failed to inject ops, loot not found")
            return

        inject_list(self.loot, 'loot_actions', self.ops)

        if self.modify_tests is not None:
            self.modify_tests.inject(self.loot.tests)


class TunableRandomWeightedLootInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'loot': TunableReference(manager=services.get_instance_manager(Types.ACTION)),
        'random_loot_actions': TunableList(
            tunable=TunableTuple(
                action=LotFiftyOneCoreLootActionVariant(do_nothing=DoNothingLootOp.TunableFactory()),
                weight=TunableMultiplier.TunableFactory(),
            )
        )
    }

    __slots__ = ('loot', 'random_loot_actions',)

    def inject(self):
        if self.loot is None:
            logger.warn("Failed to inject loot actions, random weighted loot not found")
            return

        inject_list(self.loot, 'random_loot_actions', self.random_loot_actions)
