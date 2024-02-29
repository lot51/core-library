import services
from interactions import ParticipantType
from interactions.base.mixer_interaction import MixerInteraction
from interactions.utils.tunable import TunableAffordanceLinkList
from interactions.utils.tunable_provided_affordances import TunableProvidedAffordances
from lot51_core.tunables.base_injection import BaseTunableInjection
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableList, TunableMapping, TunableSet, OptionalTunable, Tunable
from sims4.collections import  make_immutable_slots_class


class TunableBuffInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'buff': TunableReference(manager=services.get_instance_manager(Types.BUFF)),
        'loot_on_addition': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.ACTION), pack_safe=True)
        ),
        'loot_on_instance': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.ACTION), pack_safe=True)
        ),
        'loot_on_removal': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.ACTION), pack_safe=True)
        ),
        'actor_mixers': TunableMapping(
            key_type=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True),
            value_type=TunableSet(tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True))
        ),
        'interaction_items': TunableAffordanceLinkList(class_restrictions=(MixerInteraction,)),
        'provided_mixers': TunableMapping(
            key_type=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True),
            value_type=TunableSet(tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True))
        ),
        'refresh_lock': OptionalTunable(
            description="If True, all portals on the lot will refresh their locks when this buff is added or removed from a sim. Note: This is not a tunable and will not appear in the buff tdesc.",
            tunable=Tunable(tunable_type=bool, default=True),
        ),
        'super_affordances': TunableList(tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True)),
        'target_super_affordances': TunableProvidedAffordances(locked_args={'target': ParticipantType.Object, 'carry_target': ParticipantType.Invalid, 'is_linked': False, 'unlink_if_running': False})
    }

    __slots__ = ('buff', 'actor_mixers', 'interaction_items', 'loot_on_addition', 'loot_on_instance', 'loot_on_removal', 'provided_mixers', 'super_affordances', 'target_super_affordances', 'refresh_lock',)

    _create_interaction_items = make_immutable_slots_class({'interaction_items', 'scored_commodity', 'weight'})

    def inject(self):
        self.buff._loot_on_addition += tuple(self.loot_on_addition)
        self.buff._loot_on_instance += tuple(self.loot_on_instance)
        self.buff._loot_on_removal += tuple(self.loot_on_removal)

        for super_affordance, mixers in self.actor_mixers.items():
            if super_affordance in self.buff.actor_mixers:
                self.buff.actor_mixers[super_affordance] += tuple(mixers)
            else:
                self.buff.actor_mixers[super_affordance] = tuple(mixers)

        for super_affordance, mixers in self.provided_mixers.items():
            if super_affordance in self.buff.provided_mixers:
                self.buff.provided_mixers[super_affordance] += tuple(mixers)
            else:
                self.buff.provided_mixers[super_affordance] = tuple(mixers)

        if self.refresh_lock is not None:
            self.buff.refresh_lock = self.refresh_lock

        self.buff.super_affordances = set(self.buff.super_affordances) | set(self.super_affordances)

        if self.target_super_affordances is not None:
            self.buff.target_super_affordances += tuple(self.target_super_affordances)

        if self.interaction_items is not None:
            if self.buff.interactions is not None:
                interaction_items = self.buff.interactions.interaction_items + self.interaction_items
                self.buff.interactions = self.buff.interactions.clone_with_overrides(interaction_items=interaction_items)
            else:
                self.buff.interactions = self._create_interaction_items({'interaction_items': self.actor_mixers, 'scored_commodity': None, 'weight': 1, })
