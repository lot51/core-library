from lot51_core import logger
from services import get_instance_manager
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableList, TunableReference


class TunableCraftingInteractionInjection(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'recipes': TunableList(tunable=TunableReference(manager=get_instance_manager(Types.RECIPE), pack_safe=True)),
    }

    __slots__ = ('recipes',)

    def inject_to_affordance(self, affordance):
        if affordance is None:
            logger.error("Failed to inject to crafting interaction, affordance not found")
            return

        if getattr('recipes', affordance, None) is not None:
            affordance.recipes += self.recipes