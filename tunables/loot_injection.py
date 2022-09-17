import services
from interactions.utils.loot import LootActionVariant
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableReference, TunableList


class TunableLootInjection(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'loot': TunableReference(manager=services.get_instance_manager(Types.ACTION)),
        'ops': TunableList(tunable=LootActionVariant())
    }

    __slots__ = ('loot', 'ops',)

    def inject(self):
        if self.loot is None:
            return
        self.loot.loot_actions = self.loot.loot_actions + self.ops
