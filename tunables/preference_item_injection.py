import services
from _sims4_collections import frozendict
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableReference, TunableMapping, TunableRange


class TunableCharacteristicPreferenceItemInjection(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'preference_item': TunableReference(manager=services.get_instance_manager(Types.CAS_PREFERENCE_ITEM)),
        'trait_map': TunableMapping(
            key_type=TunableReference(manager=services.get_instance_manager(Types.TRAIT), pack_safe=True),
            value_type=TunableRange(tunable_type=float, default=1.0)
        )
    }

    __slots__ = ('preference_item', 'trait_map',)

    def inject(self):
        if self.preference_item is not None:
            trait_map = dict(self.preference_item.trait_map)
            for trait, weight in self.trait_map.items():
                trait_map[trait] = weight

            self.preference_item.trait_map = frozendict(trait_map)