import services
from lot51_core import logger
from lot51_core.loot import LotFiftyOneCoreLootActionVariant
from lot51_core.tunables.base_injection import BaseTunableInjection
from sims4.resources import Types
from interactions.utils.loot_ops import DoNothingLootOp
from sims4.tuning.tunable import TunableReference, TunableList, TunableTuple
from tunable_multiplier import TunableMultiplier


class TunableLootInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'loot': TunableReference(manager=services.get_instance_manager(Types.ACTION)),
        'ops': TunableList(tunable=LotFiftyOneCoreLootActionVariant())
    }

    __slots__ = ('loot', 'ops',)

    def inject(self):
        if self.loot is None:
            logger.error("Failed to inject ops, loot not found")
            return

        self.loot.loot_actions += self.ops


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
            logger.error("Failed to inject loot actions, random weighted loot not found")
            return

        self.loot.random_loot_actions += self.random_loot_actions
