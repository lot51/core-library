import services
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import inject_dict
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableMapping, TunableRange


class TunableCharacteristicPreferenceItemInjection(BaseTunableInjection):
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
            inject_dict(self.preference_item, 'trait_map', new_items=self.trait_map, force_frozen=True)