from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import merge_list
from services import get_instance_manager
from sims.pregnancy.pregnancy_enums import PregnancyOrigin
from sims.pregnancy.pregnancy_tracker import PregnancyTracker
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
    }

    __slots__ = ('pregnancy_origin_modifiers',)

    def inject(self):
        for origin, origin_modifiers in self.pregnancy_origin_modifiers.items():
            if origin in PregnancyTracker.PREGNANCY_ORIGIN_MODIFIERS:
                PregnancyTracker.PREGNANCY_ORIGIN_MODIFIERS[origin].trait_entries = merge_list(PregnancyTracker.PREGNANCY_ORIGIN_MODIFIERS[origin].trait_entries, origin_modifiers.trait_entries)
            else:
                PregnancyTracker.PREGNANCY_ORIGIN_MODIFIERS[origin] = origin_modifiers