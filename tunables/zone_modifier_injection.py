import services
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import inject_list, merge_list
from lot51_core.utils.tunables import clone_factory_with_overrides
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableList, TunableSet
from zone_modifier.zone_modifier_actions import ZoneModifierUpdateAction


class TunableZoneModifierInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'zone_modifiers': TunableList(
            description="The Lot Traits to inject to",
            tunable=TunableReference(manager=services.get_instance_manager(Types.ZONE_MODIFIER), pack_safe=True)
        ),
        'enter_lot_loot': TunableSet(
            tunable=TunableReference(manager=services.get_instance_manager(Types.ACTION), pack_safe=True),
        ),
        'exit_lot_loot': TunableSet(
            tunable=TunableReference(manager=services.get_instance_manager(Types.ACTION), pack_safe=True),
        ),
        'zone_wide_loot':ZoneModifierUpdateAction.TunableFactory(description='Loots applied when spawning into a zone with this zone modifier. This loot is also applied to all sims, objects, etc. in the zone when this zone modifier is added to a lot.'),
        'cleanup_loot':ZoneModifierUpdateAction.TunableFactory(description='Loots applied when this zone modifier is removed.'),
        'on_add_loot':ZoneModifierUpdateAction.TunableFactory(description='Loots applied when this zone modifier is added.'),
        'spin_up_lot_loot':ZoneModifierUpdateAction.TunableFactory(description='Loots applied when the zone spins up.'),
    }

    __slots__ = ('zone_modifiers', 'enter_lot_loot', 'exit_lot_loot', 'zone_wide_loot', 'cleanup_loot', 'on_add_loot', 'spin_up_lot_loot')

    def inject(self):
        for tuning in self.zone_modifiers:
            inject_list(tuning, 'enter_lot_loot', self.enter_lot_loot)
            inject_list(tuning, 'exit_lot_loot', self.exit_lot_loot)
            self._inject_actions(tuning, 'zone_wide_loot')
            self._inject_actions(tuning, 'cleanup_loot')
            self._inject_actions(tuning, 'on_add_loot')
            self._inject_actions(tuning, 'spin_up_lot_loot')

    def _inject_actions(self, tuning, key):
        snippet_update_action = getattr(self, key)
        if not snippet_update_action.actions:
            return
        tuning_update_action = getattr(tuning, key)
        merged_actions = merge_list(tuning_update_action.actions, new_items=snippet_update_action.actions)
        cloned_update_action = clone_factory_with_overrides(tuning_update_action, actions=merged_actions)
        setattr(tuning, key, cloned_update_action)