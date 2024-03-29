import services
from _sims4_collections import frozendict
from autonomy.content_sets import ContentSet
from buffs.tunable import TunableBuffReference
from crafting.food_restrictions_utils import FoodRestrictionUtils
from interactions import ParticipantType
from interactions.utils.tunable_provided_affordances import TunableProvidedAffordances
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import inject_to_enum, inject_mapping_lists, inject_list, inject_tuned_values, \
    merge_list, get_tuned_value
from lot51_core.utils.injection_tracker import injection_tracker
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableList, TunableMapping, TunableSet, OptionalTunable, TunableEnumEntry, TunableTuple, Tunable
from sims4.localization import TunableLocalizedString
from statistics.commodity import Commodity
from traits.traits import TraitBuffReplacementPriority
from whims.whim_set import ObjectivelessWhimSet


class TunableTraitInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'trait': TunableReference(manager=services.get_instance_manager(Types.TRAIT)),
        'actor_mixers': TunableMapping(
            key_type=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True),
            value_type=TunableSet(
                tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True)
            )
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
        'initial_commodities': TunableSet(
            tunable=TunableReference(manager=services.get_instance_manager(Types.STATISTIC), pack_safe=True),
        ),
        'initial_commodities_blacklist': TunableSet(
            tunable=TunableReference(manager=services.get_instance_manager(Types.STATISTIC), pack_safe=True),
        ),
        'interactions': OptionalTunable(
            tunable=ContentSet.TunableFactory(locked_args={'phase_affordances': frozendict(), 'phase_tuning': None})
        ),
        'loot_on_trait_add': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.ACTION), pack_safe=True),
        ),
        'provided_mixers': TunableMapping(
            key_type=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True),
            value_type=TunableSet(tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True))
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
        'ui_commodity_sort_override': OptionalTunable(
            description="Warning! this tunable will replace the existing list.",
            tunable=TunableList(tunable=Commodity.TunableReference(pack_safe=True)),
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

    __slots__ = ('trait', 'actor_mixers', 'buffs', 'buffs_proximity', 'buff_replacements', 'initial_commodities', 'initial_commodities_blacklist', 'interactions', 'loot_on_trait_add', 'provided_mixers', 'restricted_ingredients', 'super_affordances', 'target_super_affordances', 'ui_commodity_sort_override', 'whim_set', 'custom_food_restrictions',)

    def inject(self):
        if self.trait is not None:

            inject_mapping_lists(self.trait, 'actor_mixers', self.actor_mixers)
            inject_mapping_lists(self.trait, 'provided_mixers', self.provided_mixers)

            for (buff, replacement_buff) in self.buff_replacements.items():
                if buff.trait_replacement_buffs is None:
                    buff.trait_replacement_buffs = {}
                buff.trait_replacement_buffs[self.trait] = replacement_buff

            inject_list(self.trait, 'buffs', self.buffs)
            inject_list(self.trait, 'buffs_proximity', self.buffs_proximity)

            if self.initial_commodities is not None:
                inject_list(self.trait, 'initial_commodities', self.initial_commodities)

            if self.initial_commodities_blacklist is not None:
                inject_list(self.trait, 'initial_commodities_blacklist', self.initial_commodities_blacklist)

            if self.interactions is not None:
                if self.trait.interactions is None:
                    self.trait.interactions = self.interactions
                else:
                    inject_tuned_values(
                        self.trait.interactions,
                        affordance_links=merge_list(get_tuned_value(self.trait.interactions, 'affordance_links'), get_tuned_value(self.interactions, 'affordance_links')),
                        affordance_lists=merge_list(get_tuned_value(self.trait.interactions, 'affordance_lists'), get_tuned_value(self.interactions, 'affordance_lists')),
                    )

            if self.restricted_ingredients is not None:
                inject_list(self.trait, 'restricted_ingredients', self.restricted_ingredients)

            if self.super_affordances is not None:
                inject_list(self.trait, 'super_affordances', self.super_affordances)

            if self.target_super_affordances is not None:
                inject_list(self.trait, 'target_super_affordances', self.target_super_affordances)

            if self.loot_on_trait_add is not None:
                inject_list(self.trait, 'loot_on_trait_add', self.loot_on_trait_add)

            if self.ui_commodity_sort_override is not None:
                if injection_tracker.inject(self.trait, 'ui_commodity_sort_override'):
                    self.trait.ui_commodity_sort_override = self.ui_commodity_sort_override

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
                inject_list(self.trait, 'restricted_ingredients', (restriction_type,))

                # apply to recipes
                for recipe in food_restriction.recipes:
                    if hasattr(recipe, 'food_restriction_ingredients'):
                        inject_list(recipe, 'food_restriction_ingredients', (restriction_type,))
