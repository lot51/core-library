from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import merge_list, merge_dict
from services import get_instance_manager
from sims.pregnancy.pregnancy_enums import PregnancyOrigin
from sims.pregnancy.pregnancy_tracker import PregnancyTracker
from sims4.common import Pack
from sims4.resources import Types
from sims4.tuning.tunable import TunableList, TunableReference, TunableTuple, TunableMapping, Tunable, TunableEnumEntry, TunablePercent


class TunablePregnancyTrackerInjection(BaseTunableInjection):

    FACTORY_TUNABLES = {
        'pregnancy_origin_modifiers': TunableMapping(
            description="Injects to PregnancyTracker.PREGNANCY_ORIGIN_MODIFIERS in sims/pregnancy/pregnancy_tracker.py",
            key_type=TunableEnumEntry(
                tunable_type=PregnancyOrigin,
                default=PregnancyOrigin.DEFAULT,
                pack_safe=True
            ),
            value_type=TunableTuple(
                trait_entries=TunableList(
                    tunable=TunableTuple(
                        chance=TunablePercent(
                            default=100
                        ),
                        traits=TunableList(
                            tunable=TunableTuple(
                                weight=Tunable(
                                    tunable_type=float,
                                    default=1
                                ),
                                trait=TunableReference(
                                    manager=get_instance_manager(Types.TRAIT),
                                    pack_safe=True
                                )
                            )
                        )
                    )
                )
            ),
        ),
        'pregnancy_origin_trait_mapping': TunableMapping(
            description="Injects to PregnancyTracker.PREGNANCY_ORIGIN_TRAIT_MAPPING in sims/pregnancy/pregnancy_tracker.py",
            key_type=TunableEnumEntry(
                tunable_type=PregnancyOrigin,
                default=PregnancyOrigin.DEFAULT,
                pack_safe=True
            ),
            value_type=TunableTuple(
                pack=TunableEnumEntry(tunable_type=Pack, default=Pack.BASE_GAME),
                traits=TunableList(
                    tunable=TunableReference(
                        manager=get_instance_manager(Types.TRAIT),
                        pack_safe=True
                    )
                ),
            ),
        )
    }

    __slots__ = ('pregnancy_origin_modifiers', 'pregnancy_origin_trait_mapping',)

    def inject(self):
        for origin, origin_modifiers in self.pregnancy_origin_modifiers.items():
            if origin in PregnancyTracker.PREGNANCY_ORIGIN_MODIFIERS:
                updated_origin_modifiers = merge_dict(PregnancyTracker.PREGNANCY_ORIGIN_MODIFIERS[origin], trait_entries=merge_list(PregnancyTracker.PREGNANCY_ORIGIN_MODIFIERS[origin].trait_entries, new_items=origin_modifiers.trait_entries))
                PregnancyTracker.PREGNANCY_ORIGIN_MODIFIERS = merge_dict(PregnancyTracker.PREGNANCY_ORIGIN_MODIFIERS, new_items={origin: updated_origin_modifiers})
            else:
                PregnancyTracker.PREGNANCY_ORIGIN_MODIFIERS = merge_dict(PregnancyTracker.PREGNANCY_ORIGIN_MODIFIERS, new_items={origin: origin_modifiers})

        for origin, trait_mapping in self.pregnancy_origin_trait_mapping.items():
            if origin not in PregnancyTracker.PREGNANCY_ORIGIN_TRAIT_MAPPING:
                PregnancyTracker.PREGNANCY_ORIGIN_TRAIT_MAPPING = merge_dict(PregnancyTracker.PREGNANCY_ORIGIN_TRAIT_MAPPING, new_items={origin: trait_mapping})
            else:
                origin_data = PregnancyTracker.PREGNANCY_ORIGIN_TRAIT_MAPPING.get(origin)
                new_origin_data = merge_dict(origin_data, traits=merge_list(origin_data.traits, new_items=trait_mapping.traits))
                PregnancyTracker.PREGNANCY_ORIGIN_TRAIT_MAPPING = merge_dict(PregnancyTracker.PREGNANCY_ORIGIN_TRAIT_MAPPING, new_items={origin: new_origin_data})
