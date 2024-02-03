import services
from _sims4_collections import frozendict
from autonomy.content_sets import ContentSet
from buffs.tunable import TunableBuffReference
from crafting.food_restrictions_utils import FoodRestrictionUtils
from interactions import ParticipantType
from interactions.utils.tunable_provided_affordances import TunableProvidedAffordances
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import add_affordances, inject_to_enum
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableList, TunableMapping, TunableSet, OptionalTunable, TunableEnumEntry, TunableTuple, Tunable
from sims4.localization import TunableLocalizedString
from traits.traits import TraitBuffReplacementPriority
from whims.whim_set import ObjectivelessWhimSet


class TunableTraitInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'trait': TunableReference(manager=services.get_instance_manager(Types.TRAIT)),
        'actor_mixers': TunableMapping(
            key_type=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True),
            value_type=TunableSet(
                tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True))
        ),
        'buffs': TunableList(
            tunable=TunableBuffReference(pack_safe=True)
        ),
        'buffs_proximity': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.BUFF), pack_safe=True)
        ),
        'buff_replacements': TunableMapping(
            key_type=TunableReference(
                manager=services.get_instance_manager(Types.BUFF),
                reload_dependent=True,
                pack_safe=True
            ),
            value_type=TunableTuple(
                buff_type=TunableReference(
                    manager=services.get_instance_manager(Types.BUFF),
                    reload_dependent=True,
                    pack_safe=True
                ),
                buff_reason=OptionalTunable(tunable=TunableLocalizedString()),
                buff_replacement_priority=TunableEnumEntry(
                    tunable_type=TraitBuffReplacementPriority,
                    default=TraitBuffReplacementPriority.NORMAL
                )
            )
        ),
        'interactions': OptionalTunable(
            tunable=ContentSet.TunableFactory(locked_args={'phase_affordances': frozendict(), 'phase_tuning': None})
        ),
        'loot_on_trait_add': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.ACTION), pack_safe=True),
        ),
        'provided_mixers': TunableMapping(
            key_type=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True),
            value_type=TunableSet(
                tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True))
        ),
        'restricted_ingredients': TunableList(
            tunable=TunableEnumEntry(tunable_type=FoodRestrictionUtils.FoodRestrictionEnum, default=FoodRestrictionUtils.FoodRestrictionEnum.INVALID, invalid_enums=(FoodRestrictionUtils.FoodRestrictionEnum.INVALID,))
        ),
        'super_affordances': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True),
        ),
        'target_super_affordances': TunableProvidedAffordances(
            locked_args={'target': ParticipantType.Object, 'carry_target': ParticipantType.Invalid, 'is_linked': False, 'unlink_if_running': False}
        ),
        'whim_set': OptionalTunable(
            tunable=TunableReference(manager=services.get_instance_manager(Types.ASPIRATION), class_restrictions=(ObjectivelessWhimSet,))
        ),
        'custom_food_restrictions': TunableList(
            tunable=TunableTuple(
                restriction_key=Tunable(tunable_type=str, default=''),
                restriction_id=Tunable(tunable_type=int, default=0),
                recipes=TunableList(
                    tunable=TunableReference(manager=services.get_instance_manager(Types.RECIPE), pack_safe=True),
                ),
            )
        )
    }

    __slots__ = ('trait', 'actor_mixers', 'buffs', 'buffs_proximity', 'buff_replacements', 'interactions', 'loot_on_trait_add', 'provided_mixers', 'restricted_ingredients', 'super_affordances', 'target_super_affordances', 'whim_set', 'custom_food_restrictions',)

    def inject(self):
        if self.trait is not None:

            for super_affordance, mixers in self.actor_mixers.items():
                if super_affordance in self.trait.actor_mixers:
                    self.trait.actor_mixers[super_affordance] += tuple(mixers)
                else:
                    self.trait.actor_mixers[super_affordance] = tuple(mixers)

            for (buff, replacement_buff) in self.buff_replacements.items():
                if buff.trait_replacement_buffs is None:
                    buff.trait_replacement_buffs = {}
                buff.trait_replacement_buffs[self.trait] = replacement_buff

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
                add_affordances(self.trait, self.target_super_affordances, key='target_super_affordances')

            if self.loot_on_trait_add is not None:
                if self.trait.loot_on_trait_add is None:
                    self.trait.loot_on_trait_add = tuple(self.loot_on_trait_add)
                else:
                    self.trait.loot_on_trait_add += tuple(self.loot_on_trait_add)

            if self.whim_set is not None:
                self.trait.whim_set = self.whim_set

            # Custom Food Restrictions
            for food_restriction in self.custom_food_restrictions:
                # inject to FoodRestrictionEnum
                enum_data = {food_restriction.restriction_key: food_restriction.restriction_id}
                inject_to_enum(FoodRestrictionUtils.FoodRestrictionEnum, enum_data)

                # get resolved enum
                restriction_type = FoodRestrictionUtils.FoodRestrictionEnum[food_restriction.restriction_key]

                # add to trait restrictions
                self.trait.restricted_ingredients += (restriction_type,)

                # apply to recipes
                for recipe in food_restriction.recipes:
                    if hasattr(recipe, 'food_restriction_ingredients'):
                        recipe.food_restriction_ingredients += (restriction_type,)
