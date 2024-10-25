import services
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import inject_list
from sims4.resources import Types
from sims4.tuning.tunable import TunableList, TunableReference, TunableTuple, Tunable
from traits.trait_tracker import TraitTracker


class TunableTraitTrackerInjection(BaseTunableInjection):

    FACTORY_TUNABLES = {
        'trait_inheritance': TunableList(
            description="Injects to TraitTracker.TRAIT_INHERITANCE in traits/trait_tracker.py",
            tunable=TunableTuple(
                parent_a_whitelist=TunableList(
                    tunable=TunableReference(manager=services.get_instance_manager(Types.TRAIT), pack_safe=True),
                    allow_none=True
                ),
                parent_a_blacklist=TunableList(
                    tunable=TunableReference(manager=services.get_instance_manager(Types.TRAIT), pack_safe=True),
                ),
                parent_b_whitelist=TunableList(
                    tunable=TunableReference(manager=services.get_instance_manager(Types.TRAIT), pack_safe=True),
                    allow_none=True
                ),
                parent_b_blacklist=TunableList(
                    tunable=TunableReference(manager=services.get_instance_manager(Types.TRAIT), pack_safe=True),
                ),
                outcomes=TunableList(
                    tunable=TunableTuple(
                        weight=Tunable(
                            tunable_type=float,
                            default=1
                        ),
                        trait=TunableReference(manager=services.get_instance_manager(Types.TRAIT), pack_safe=True, allow_none=True),
                    )
                )
            )
        ),
    }

    __slots__ = ('trait_inheritance',)

    def inject(self):
        inject_list(TraitTracker, 'TRAIT_INHERITANCE', self.trait_inheritance)
