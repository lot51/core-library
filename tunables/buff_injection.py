import services
from game_effect_modifier.game_effect_modifiers import TunableGameEffectVariant, GameEffectModifiers
from interactions import ParticipantType
from interactions.base.mixer_interaction import MixerInteraction
from interactions.utils.tunable import TunableAffordanceLinkList
from interactions.utils.tunable_provided_affordances import TunableProvidedAffordances
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.tunables.test_injection import TestInjectionVariant
from lot51_core.utils.injection import inject_mapping_lists, inject_list, merge_list, inject_dict, get_tuned_value
from lot51_core.utils.tunables import create_factory_wrapper
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableList, TunableMapping, TunableSet, OptionalTunable, Tunable
from sims4.collections import make_immutable_slots_class


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
        'game_effect_modifiers': TunableList(description='A list of game effect modifiers', tunable=TunableGameEffectVariant()),
        'interaction_items': TunableAffordanceLinkList(class_restrictions=(MixerInteraction,)),
        'modify_add_test_set': TestInjectionVariant(),
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

    __slots__ = ('buff', 'actor_mixers', 'interaction_items', 'loot_on_addition', 'loot_on_instance', 'loot_on_removal', 'game_effect_modifiers', 'modify_add_test_set', 'provided_mixers', 'super_affordances', 'target_super_affordances', 'refresh_lock',)

    _create_interaction_items = make_immutable_slots_class({'interaction_items', 'scored_commodity', 'weight'})

    def inject(self):
        if self.buff is not None:
            buff_type = self.buff

            inject_list(buff_type, '_loot_on_addition', self.loot_on_addition)
            inject_list(buff_type, '_loot_on_instance', self.loot_on_instance)
            inject_list(buff_type, '_loot_on_removal', self.loot_on_removal)

            inject_mapping_lists(buff_type, 'actor_mixers', self.actor_mixers)
            inject_mapping_lists(buff_type, 'provided_mixers', self.provided_mixers)

            if len(self.game_effect_modifiers):
                original_modifiers = get_tuned_value(buff_type.game_effect_modifier, '_game_effect_modifiers')

                game_effect_modifier = create_factory_wrapper(
                    GameEffectModifiers,
                    locked_args={'_game_effect_modifiers': merge_list(original_modifiers, self.game_effect_modifiers)}
                )
                buff_type.game_effect_modifier = game_effect_modifier

            if self.refresh_lock is not None:
                buff_type.refresh_lock = self.refresh_lock

            inject_list(buff_type, 'super_affordances', self.super_affordances)

            if self.modify_add_test_set is not None:
                self.modify_add_test_set.inject(buff_type, '_add_test_set')

            if self.target_super_affordances is not None:
                inject_list(buff_type, 'target_super_affordances', self.target_super_affordances)

            if self.interaction_items is not None:
                if buff_type.interactions is not None:
                    inject_dict(buff_type, 'interactions', interaction_items=merge_list(buff_type.interactions.interaction_items, self.interaction_items, list_type=tuple))
                else:
                    buff_type.interactions = self._create_interaction_items({'interaction_items': self.actor_mixers, 'scored_commodity': None, 'weight': 1, })
