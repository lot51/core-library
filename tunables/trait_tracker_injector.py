from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.collections import AttributeDict
from lot51_core.utils.injection import inject_list
from relationships.relationship_tracker_tuning import DefaultGenealogyLink
from services import get_instance_manager
from sims.pregnancy.pregnancy_enums import PregnancyOrigin
from sims.pregnancy.pregnancy_tracker import PregnancyTracker
from sims.university.university_commands import UniversityCommandTuning
from sims.university.university_tuning import University
from sims4.common import Pack
from sims4.resources import Types
from sims4.tuning.tunable import TunableList, TunableReference, TunableTuple, TunableMapping, Tunable, OptionalTunable, \
    TunableInterval, TunableEnumEntry, TunablePercent
from traits.trait_tracker import TraitTracker
from traits.traits import Trait
from tunable_multiplier import TunableMultiplier


class TunableTraitTrackerInjection(BaseTunableInjection):

    FACTORY_TUNABLES = {
        'trait_inheritance': TunableList(
            description="Injects to TraitTracker.TRAIT_INHERITANCE in traits/trait_tracker.py",
            tunable=TunableTuple(
                parent_a_whitelist=TunableList(
                    tunable=Trait.TunablePackSafeReference(),
                    allow_none=True
                ),
                parent_a_blacklist=TunableList(
                    tunable=Trait.TunableReference(
                        pack_safe=True
                    )
                ),
                parent_b_whitelist=TunableList(
                    tunable=Trait.TunablePackSafeReference(),
                    allow_none=True
                ),
                parent_b_blacklist=TunableList(
                    tunable=Trait.TunableReference(
                        pack_safe=True
                    )
                ),
                outcomes=TunableList(
                    tunable=TunableTuple(
                        weight=Tunable(
                            tunable_type=float,
                            default=1
                        ),
                        trait=Trait.TunableReference(
                            allow_none=True,
                            pack_safe=True
                        )
                    )
                )
            )
        ),
    }

    __slots__ = ('trait_inheritance',)

    def inject(self):
        inject_list(TraitTracker, 'TRAIT_INHERITANCE', self.trait_inheritance)
