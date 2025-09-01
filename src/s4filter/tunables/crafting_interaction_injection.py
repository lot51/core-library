from _sims4_collections import frozendict
from bucks.bucks_enums import BucksType
from lot51_core import logger
from lot51_core.tunables.multiplier_injection import TunableMultiplierInjection
from lot51_core.utils.injection import inject_list
from services import get_instance_manager
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableList, TunableReference, \
    OptionalTunable, TunableMapping, TunableEnumEntry


class TunableCraftingInteractionInjection(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'recipes': TunableList(tunable=TunableReference(manager=get_instance_manager(Types.RECIPE), pack_safe=True)),
        'bucks_price_multipliers': TunableMapping(
            key_type=TunableEnumEntry(tunable_type=BucksType, default=BucksType.INVALID),
            value_type=TunableMultiplierInjection.TunableFactory(),
        ),
        'price_multiplier': OptionalTunable(
            tunable=TunableMultiplierInjection.TunableFactory(),
        ),
    }

    __slots__ = ('bucks_price_multipliers', 'price_multiplier', 'recipes',)

    def inject_to_affordance(self, affordance):
        if affordance is None:
            logger.error("Failed to inject to crafting interaction, affordance not found")
            return

        if hasattr(affordance, 'recipes'):
            inject_list(affordance, 'recipes', self.recipes)

        if hasattr(affordance, 'price_multiplier') and self.price_multiplier is not None:
            self.price_multiplier.inject(affordance, 'price_multiplier')

        if hasattr(affordance, 'bucks_price_multipliers') and len(self.bucks_price_multipliers):
            bucks_price_multipliers = dict(affordance.bucks_price_multipliers)
            for bucks_type, price_multiplier_injection in self.bucks_price_multipliers.items():
                price_multiplier_injection.inject(bucks_price_multipliers, bucks_type)
            affordance.bucks_price_multipliers = frozendict(bucks_price_multipliers)
