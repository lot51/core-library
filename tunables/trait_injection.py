import services
from _sims4_collections import frozendict
from autonomy.content_sets import ContentSet
from buffs.tunable import TunableBuffReference
from crafting.food_restrictions_utils import FoodRestrictionUtils
from interactions import ParticipantType
from interactions.utils.tunable_provided_affordances import TunableProvidedAffordances
from lot51_core.utils.injection import add_affordances
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableReference, TunableList, \
    TunableMapping, TunableSet, OptionalTunable, TunableEnumEntry
from whims.whim_set import ObjectivelessWhimSet


class TunableTraitInjection(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'trait': TunableReference(manager=services.get_instance_manager(Types.TRAIT)),
        'actor_mixers': TunableMapping(
            key_type=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True),
            value_type=TunableSet(
                tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True))
        ),
        'buffs': TunableList(tunable=TunableBuffReference(pack_safe=True)),
        'buffs_proximity': TunableList(tunable=TunableReference(manager=services.get_instance_manager(Types.BUFF))),
        'interactions': OptionalTunable(tunable=ContentSet.TunableFactory(locked_args={'phase_affordances': frozendict(), 'phase_tuning': None})),
        'loot_on_trait_add': TunableList(tunable=TunableReference(manager=services.get_instance_manager(Types.ACTION))),
        'provided_mixers': TunableMapping(
            key_type=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True),
            value_type=TunableSet(
                tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True))
        ),
        'restricted_ingredients': TunableList(
            tunable=TunableEnumEntry(tunable_type=FoodRestrictionUtils.FoodRestrictionEnum, default=FoodRestrictionUtils.FoodRestrictionEnum.INVALID, invalid_enums=(FoodRestrictionUtils.FoodRestrictionEnum.INVALID,))
        ),
        'super_affordances': TunableList(tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION))),
        'target_super_affordances': TunableProvidedAffordances(locked_args={'target': ParticipantType.Object, 'carry_target': ParticipantType.Invalid, 'is_linked': False, 'unlink_if_running': False}),
        'whim_set': OptionalTunable(
            tunable=TunableReference(manager=services.get_instance_manager(Types.ASPIRATION), class_restrictions=(ObjectivelessWhimSet,))
        )
    }

    __slots__ = ('trait', 'actor_mixers', 'buffs', 'buffs_proximity', 'interactions', 'loot_on_trait_add', 'provided_mixers', 'restricted_ingredients', 'super_affordances', 'target_super_affordances', 'whim_set',)

    def inject(self):
        if self.trait is not None:

            for super_affordance, mixers in self.actor_mixers.items():
                if super_affordance in self.trait.actor_mixers:
                    self.trait.actor_mixers[super_affordance] += tuple(mixers)
                else:
                    self.trait.actor_mixers[super_affordance] = tuple(mixers)

            self.trait.buffs += tuple(self.buffs)

            self.trait.buffs_proximity += tuple(self.buffs_proximity)

            if self.interactions is not None:
                if self.trait.interactions is None:
                    self.trait.interactions = self.interactions
                else:
                    self.trait.interactions._affordance_links += tuple(self.interactions._affordance_links)
                    self.trait.interactions._affordance_lists += tuple(self.interactions._affordance_lists)

            for super_affordance, mixers in self.provided_mixers.items():
                if super_affordance in self.trait.provided_mixers:
                    self.trait.provided_mixers[super_affordance] += tuple(mixers)
                else:
                    self.trait.provided_mixers[super_affordance] = tuple(mixers)

            if self.restricted_ingredients is not None:
                self.trait.restricted_ingredients += tuple(self.restricted_ingredients)

            if self.super_affordances is not None:
                add_affordances(self.trait, self.super_affordances, key='super_affordances')

            if self.target_super_affordances is not None:
                add_affordances(self.trait, self.target_super_affordances, 'target_super_affordances')

            if self.loot_on_trait_add is not None:
                if self.trait.loot_on_trait_add is None:
                    self.trait.loot_on_trait_add = tuple(self.loot_on_trait_add)
                else:
                    self.trait.loot_on_trait_add += tuple(self.loot_on_trait_add)

            if self.whim_set is not None:
                self.trait.whim_set = self.whim_set
