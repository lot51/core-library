import copy
import inspect

import services
import sims4.random
from autonomy.autonomy_modifier import TunableAutonomyModifier
from event_testing.tests import TunableTestSet
from interactions import ParticipantType
from interactions.utils.tunable_provided_affordances import TunableProvidedAffordances
from lot51_core import logger
from lot51_core.tunables.base_injection import BaseTunableInjection, InjectionTiming
from lot51_core.tunables.object_query import ObjectSearchMethodVariant
from lot51_core.utils.collections import AttributeDict
from lot51_core.utils.injection import add_affordances, add_phone_affordances, obj_has_affordance, merge_list, \
    merge_dict, merge_mapping_lists, inject_list, inject_dict, merge_affordance_filter
from lot51_core.utils.tunables import create_factory_wrapper, clone_factory_wrapper_with_overrides, \
    clone_factory_with_overrides
from objects.components.idle_component import IdleComponent
from objects.components.inventory_enums import InventoryType
from objects.components.locking_components import ObjectLockingComponent
from objects.components.name_component import NameComponent
from objects.components.object_relationship_component import ObjectRelationshipComponent
from objects.components.state import StateTrigger, TunableStateValueReference, StateChangeOperation, \
    TestedStateValueReference, ObjectStateMetaclass, StateComponent, TunableStateComponent
from objects.components.tooltip_component import TooltipComponent
from objects.components.types import IDLE_COMPONENT, OBJECT_ROUTING_COMPONENT, STATE_COMPONENT, PROXIMITY_COMPONENT, OBJECT_LOCKING_COMPONENT, RoutingComponent
from routing.object_routing.object_routing_component import ObjectRoutingComponent
from sims4.tuning.tunable import Tunable, TunableList, TunableReference, TunableTuple, TunableMapping, TunableVariant, \
    OptionalTunable, TunableSimMinute, TunableEnumSet, HasTunableSingletonFactory, AutoFactoryInit, TunableSet
from sims4.resources import Types, get_resource_key
from singletons import UNSET
from snippets import TunableAffordanceFilterSnippet
from statistics.tunable import CommodityDecayModifierMapping
from tag import Tag


# 1.116 Backwards Compatibility
try:
    from objects.components.state import TunableClientStateTestedOverrides
except:
    class TunableClientStateTestedOverrides(HasTunableSingletonFactory, AutoFactoryInit):
        pass


class BaseTunableObjectInjection(BaseTunableInjection):

    FACTORY_TUNABLES = {
        'affordances': TunableList(
            description='List of affordances to inject',
            tunable=TunableReference(
                description='Affordance to inject',
                manager=services.get_instance_manager(Types.INTERACTION),
                pack_safe=True,
            )
        ),
        'phone_affordances': TunableList(
            description='List of affordances to inject to object phone affordance list',
            tunable=TunableReference(
                description='Affordance to inject',
                manager=services.get_instance_manager(Types.INTERACTION),
                pack_safe=True,
            )
        ),
        'relation_panel_affordances': TunableList(
            description='List of affordances to inject to Sim relationship panel',
            tunable=TunableReference(
                description='Affordance to inject',
                manager=services.get_instance_manager(Types.INTERACTION),
                pack_safe=True,
            )
        ),
        'preroll_super_affordances': TunableList(
            description='List of affordances to inject to _preroll_super_affordances',
            tunable=TunableReference(
                description='Affordance to inject',
                manager=services.get_instance_manager(Types.INTERACTION),
                pack_safe=True,
            )
        ),
        'proximity_buffs': TunableList(
            description="Proximity Buffs to inject to the proximity component",
            tunable=TunableReference(manager=services.get_instance_manager(Types.BUFF), pack_safe=True),
        ),
        'state_triggers': TunableList(StateTrigger.TunableFactory()),
        'states': TunableList(description='\n                Supported states for this object\n                ',
              tunable=TunableTuple(description='\n                    A supported state for this object\n                    ',
              default_value=TunableVariant(description='\n                        The default value for the state.\n                        ',
              reference=TunableStateValueReference(pack_safe=True),
              random=TunableList(description='\n                            A weighted list of object states to randomly choose\n                            between as the default for this state.\n                            ',
              tunable=TunableTuple(state=TunableStateValueReference(pack_safe=True),
              weight=Tunable(tunable_type=float,
              default=1.0))),
              default='reference'),
              client_states=TunableMapping(description='\n                        A list of client states. Although ObjectStateValues\n                        have their own State Change Operations (Audio effect\n                        state, Broadcaster, etc), those operations will be\n                        overriden by operations specified here.\n                        ',
              key_type=TunableStateValueReference(description='\n                            A state value\n                            ',
              pack_safe=True),
              value_type=(StateChangeOperation.TunableFactory())),
              client_states_overrides=TunableMapping(description='\n                        A list of slot-based overrides for client states. \n                        ',
              key_type=TunableStateValueReference(description='\n                            A state value\n                            ',
              pack_safe=True),
              value_type=TunableList(description='\n                            A list of possible override conditions for this state.\n                            ',
              tunable=(TunableClientStateTestedOverrides.TunableFactory()))),
              reset_to_default=Tunable(description='\n                        If checked, when the object is reset, the state will be\n                        reset to the default value. Otherwise, it will keep the\n                        current value. This can be overridden by states tuned\n                        in tested_states_on_reset.\n                        ',
              tunable_type=bool,
              default=False),
              reset_on_load_if_time_passes=Tunable(description='\n                        If checked then the object is saved with the default\n                        state rather than the current state.  If we want it\n                        to return to this state we need an interaction that\n                        is saved to put it back into it.\n                        ',
              tunable_type=bool,
              default=False),
              tested_states_on_add=OptionalTunable(description="\n                        The first test that passes will have its state applied.\n                        If no tests pass, the fallback state will be applied.\n                        This can be used to conditionally apply a state to an\n                        object.  For example, the Tree Rabbit Hale needs to \n                        default to the open state when it's on the Slyvan Glade\n                        venue.\n                        This runs when the object is added to the world.\n                        ",
              tunable=(TestedStateValueReference.TunableFactory())),
              tested_states_post_load=OptionalTunable(description='\n                        The first test that passes will have its state applied.\n                        If no tests pass, the fallback state will be applied.\n                        This can be used to conditionally apply a state to an\n                        object.\n                        This will run after the zone is fully loaded. \n                        This test is mostly used for conditionally applying\n                        a state after loading in, or when taking the object\n                        out of inventory. (The object has to be previously existing,\n                        it will not work for newly created objects.)\n                        For example, the previously active gnomes in our HH inventory \n                        needs to be reset to the inactive state if we place \n                        them after Harvest Fest ends.\n                        ',
              tunable=(TestedStateValueReference.TunableFactory())),
              tested_states_on_location_changed=OptionalTunable(description="\n                        The first test that passes will have its state applied.\n                        If no tests pass, the fallback state will be applied.\n                        This can be used to conditionally apply a state to an\n                        object.  For example, the boat needs to be set to it's\n                        on water state if it is placed on water.\n                        This runs when the location of the object changes as\n                        long as the object isn't currently routing.\n                        ",
              tunable=(TestedStateValueReference.TunableFactory())),
              tested_states_on_reset=OptionalTunable(description='\n                        This is a set of override states for reset_to_default,\n                        run when the owner is reset.\n                        \n                        The first test that passes will have its state applied.\n                        If no tests pass, the fallback state will be applied.\n                        This can be used to conditionally apply a state to an\n                        object.  For example, if a chicken parented to the coop\n                        is moved in B/B, it should be reset to an InCoop state.\n                        ',
              tunable=TestedStateValueReference.TunableFactory(locked_args={'fallback_state': None})),
              tested_states_on_save=OptionalTunable(description='\n                        This is a set of override states for \n                        reset_on_load_if_time_passes, run when the owner is \n                        saved.\n                        \n                        The first test that passes will have its state applied.\n                        If no tests pass, behavior falls back to the condition\n                        in reset_on_load_if_time_passes.\n                        This can be used to conditionally apply a state to an\n                        object.  For example, if a chicken is in the coop on\n                        save, it should be reset to an InCoop state.\n                        ',
              tunable=TestedStateValueReference.TunableFactory(locked_args={'fallback_state': None})))
        ),
        'timed_state_triggers': OptionalTunable(description='\n                If enabled, when states in this key mapping get triggered, it\n                will trigger states changes at each of the tuned intervals.\n                ',
              tunable=TunableMapping(description='\n                    Map of state when the timed state triggers will be active\n                    and the states to trigger, specific trigger times, and\n                    the options of whether to trigger on load.\n                    ',
              key_type=TunableStateValueReference(pack_safe=True),
              value_type=TunableTuple(trigger_on_load=Tunable(description='\n                            If set to True, when the state in the key mapping\n                            is set on an object on load the changes are triggered.\n                            ',
              tunable_type=bool,
              default=False),
              ops=TunableList(description='\n                            List of multiple states and times when they can be \n                            triggered.\n                            ',
              tunable=TunableTuple(description='\n                                Pair of trigger time and states to trigger when \n                                the time has passed.\n                                ',
              trigger_time=TunableSimMinute(description='\n                                    How many sim minutes past entering the trigger state that this trigger will be\n                                    enabled.  Each entry must occur at a later time than the previous, including the \n                                    maximum potential of the random offset time. \n                                    Ex: Entry 1 has a trigger time of 10 and a random offset of 5.  Entry 2 must have a\n                                    trigger time of at least 16.\n                                    ',
              default=10,
              minimum=0),
              trigger_time_random_offset=TunableSimMinute(description='\n                                    A random time offset to be applied to the trigger time.\n                                    Ex: Trigger Time is 5 and the random offset is 3, the trigger would occur in 5-8 sim minutes.\n                                    ',
              default=0,
              minimum=0),
              states_to_trigger=TunableList(description='\n                                    List of states to trigger.\n                                    ',
              tunable=TunableStateValueReference(pack_safe=True)),
              random_states_to_trigger=TunableList(description='\n                                    List of randomly weighted states to trigger.  Only one will be selected and entries\n                                    that fail their tests will not be eligible for selection.\n                                    ',
              tunable=TunableTuple(weight=Tunable(tunable_type=int,
              default=1),
              tests=(TunableTestSet()),
              state_value=(TunableStateValueReference()))),
              loot_list=TunableList(description='\n                                    A list of loot operations to apply when a state change is triggered.\n                                    Note:   Loot will only be applied IF\n                                            there are any tuned states_to_trigger OR \n                                            at least one entry in random_states_to_trigger passes its tests\n                                    ',
              tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.ACTION)),
              class_restrictions=('LootActions', ),
              pack_safe=True)),
              trigger_tests=TunableTuple(description='\n                                    After this trigger is activated, these tests will run before any loot or state transitions\n                                    are processed.  Failing these tests will either skip to the next tuned trigger or cause\n                                    the current trigger to be rescheduled if tuned to do so.\n                                    ',
              tests=(TunableTestSet()),
              reschedule_on_failure=Tunable(description='\n                                        If tuned to true, this trigger will reschedule on test failure instead of skipping\n                                        to the next trigger.\n                                        ',
              tunable_type=bool,
              default=False))))))
        ),
        'idle_animation_map': OptionalTunable(
            tunable=TunableMapping(key_type=TunableReference(manager=services.get_instance_manager(Types.OBJECT_STATE), class_restrictions='ObjectStateValue'), value_type=TunableReference(manager=services.get_instance_manager(Types.ANIMATION), class_restrictions='ObjectAnimationElement'))
        ),
        'carryable_component': OptionalTunable(
            tunable=TunableTuple(
                provided_affordances=TunableProvidedAffordances(class_restrictions=('SuperInteraction',), locked_args={'allow_self': False, 'target': ParticipantType.Object, 'carry_target': ParticipantType.CarriedObject})
            )
        ),
        'inventory_item_component': OptionalTunable(
            tunable=TunableTuple(
                valid_inventory_types=TunableEnumSet(enum_type=InventoryType, enum_default=InventoryType.UNDEFINED, invalid_enums=(InventoryType.UNDEFINED)),
            ),
        ),
        'inventory_component': OptionalTunable(
            tunable=TunableTuple(
                starting_objects=TunableList(tunable=TunableReference(manager=services.definition_manager(), pack_safe=True)),
            ),
        ),
        'name_component_override': OptionalTunable(
            tunable=NameComponent.TunableFactory(),
        ),
        'object_locking_component': OptionalTunable(
            tunable=TunableTuple(
                super_affordances=TunableList(tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True)),
            )
        ),
        'object_relationship_component_override': OptionalTunable(
            tunable=ObjectRelationshipComponent.TunableFactory(),
        ),
        'portal_component': OptionalTunable(
            tunable=TunableTuple(
                _portal_data=TunableList(
                    tunable=TunableReference(manager=services.get_instance_manager(Types.SNIPPET))
                ),
                _replace_existing_portal_data=Tunable(tunable_type=bool, default=False),
                state_values_which_disable_portals=TunableMapping(
                    description='A mapping between object state values and portals which should be disabled when those state values are active. Disabling a portal requires a full refresh of the owning objects portals.',
                    key_type=TunableReference(manager=services.get_instance_manager(Types.OBJECT_STATE), pack_safe=True),
                    value_type=TunableList(tunable=TunableReference(manager=services.get_instance_manager(Types.SNIPPET), pack_safe=True))
                ),
            )
        ),
        'routing_component': OptionalTunable(
            tunable=TunableTuple(
                routing_behavior_map=TunableMapping(key_type=TunableReference(manager=services.get_instance_manager(Types.OBJECT_STATE), class_restrictions='ObjectStateValue'), value_type=OptionalTunable(tunable=TunableReference(manager=services.get_instance_manager(Types.SNIPPET), class_restrictions=('ObjectRoutingBehavior',)), enabled_by_default=True, enabled_name='Start_Behavior', disabled_name='Stop_All_Behavior', disabled_value=UNSET))
            )
        ),
        'slot_component': OptionalTunable(
            tunable=TunableTuple(
                additional_autonomy_modifiers=TunableList(tunable=TunableAutonomyModifier(locked_args={'relationship_multipliers': None})),
                inject_to_autonomy_modifier=TunableList(
                    tunable=TunableTuple(
                        index=Tunable(tunable_type=int, default=0),
                        affordance_compatibility=OptionalTunable(tunable=TunableAffordanceFilterSnippet()),
                        decay_modifiers=CommodityDecayModifierMapping(),
                        provided_affordance_compatibility=OptionalTunable(tunable=TunableAffordanceFilterSnippet()),
                        state_values_tuning=TunableSet(
                            tunable=TunableTuple(
                                required_slot_types=TunableList(
                                    tunable=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.SLOT_TYPE)), pack_safe=True)
                                ),
                                state_to_set=TunableReference(manager=(services.get_instance_manager(sims4.resources.Types.OBJECT_STATE)), class_restrictions=('ObjectStateValue',))
                            )
                        ),
                    )
                ),
                slot_provided_affordances=TunableProvidedAffordances(),
            )
        ),
        'tooltip_component_override': OptionalTunable(
            tunable=TooltipComponent.TunableFactory(),
        ),
    }

    __slots__ = ('affordances', 'phone_affordances', 'preroll_super_affordances', 'relation_panel_affordances', 'proximity_buffs', 'state_triggers', 'states', 'timed_state_triggers', 'idle_animation_map',  'portal_component', 'routing_component', 'carryable_component', 'inventory_item_component', 'object_locking_component', 'name_component_override', 'object_relationship_component_override', 'tooltip_component_override',)

    def get_objects_gen(self):
        raise NotImplementedError

    def _add_affordances(self, obj):
        if len(self.affordances) > 0:
            add_affordances(obj, self.affordances)
        if len(self.phone_affordances) > 0:
            add_phone_affordances(obj, self.phone_affordances)
        if len(self.preroll_super_affordances) > 0:
            add_affordances(obj, self.preroll_super_affordances, key="_preroll_super_affordances")
        if len(self.relation_panel_affordances) > 0:
            add_affordances(obj, self.relation_panel_affordances, key='_relation_panel_affordances')

    def _inject_idle_component(self, obj, should_create_component=True):
        if self.idle_animation_map is not None:
            if hasattr(obj, '_components') and hasattr(obj._components, 'idle_component') and obj._components.idle_component is not None:
                idle_component = obj._components.idle_component
                new_idle_component = clone_factory_wrapper_with_overrides(idle_component, idle_animation_map=merge_dict(idle_component.idle_animation_map, new_items=self.idle_animation_map))
                inject_dict(obj, '_components', idle_component=new_idle_component)
            elif should_create_component:
                idle_component = create_factory_wrapper(IdleComponent, idle_animation_map=self.idle_animation_map)
                inject_dict(obj, '_components', idle_component=idle_component)

    def _inject_routing_component(self, obj, should_create_component=True):
        if self.routing_component is not None:
            if hasattr(obj, '_components') and hasattr(obj._components, 'routing_component'):
                routing_component = obj._components.routing_component

                new_object_routing_component = clone_factory_wrapper_with_overrides(
                    routing_component.object_routing_component,
                    routing_behavior_map=merge_dict(routing_component.object_routing_component.routing_behavior_map, new_items=self.routing_component.routing_behavior_map)
                )

                new_routing_component = clone_factory_wrapper_with_overrides(routing_component, object_routing_component=new_object_routing_component)
                inject_dict(obj, '_components', routing_component=new_routing_component)
            elif should_create_component:
                object_routing_component = create_factory_wrapper(ObjectRoutingComponent, routing_behavior_map=self.routing_component.routing_behavior_map)
                routing_component = create_factory_wrapper(RoutingComponent, object_routing_component=object_routing_component)
                inject_dict(obj, '_components', routing_component=routing_component)

    def _inject_state_component(self, obj, should_create_component=True):
        if hasattr(obj, '_components') and getattr(obj._components, 'state', None) is not None:
            state_component = obj._components.state
            overrides = AttributeDict()
            if len(self.states):
                overrides.states = merge_list(state_component.states, self.states)

            if len(self.state_triggers):
                overrides.state_triggers = merge_list(state_component.state_triggers, self.state_triggers)

            if self.timed_state_triggers is not None:
                overrides.timed_state_triggers = merge_dict(state_component.timed_state_triggers, new_items=self.timed_state_triggers)

            if len(overrides):
                new_state_component = clone_factory_wrapper_with_overrides(state_component, **overrides)
                inject_dict(obj, '_components', state=new_state_component)
        elif should_create_component and (len(self.states) or len(self.state_triggers) or self.timed_state_triggers is not None):
            state_component = create_factory_wrapper(TunableStateComponent, states=self.states, state_triggers=self.state_triggers, timed_state_triggers=self.timed_state_triggers)
            inject_dict(obj, '_components', state=state_component)

    def _inject_proximity_component(self, obj):
        if len(self.proximity_buffs) > 0 and hasattr(obj, '_components') and getattr(obj._components, 'proximity_component', None) is not None:
            proximity_component = obj._components.proximity_component
            new_proximity_component = clone_factory_wrapper_with_overrides(proximity_component, buffs=merge_list(proximity_component.buffs, self.proximity_buffs))
            inject_dict(obj, '_components', proximity_component=new_proximity_component)

    def _inject_carryable_component(self, obj):
        if self.carryable_component is not None and hasattr(obj, '_components') and getattr(obj._components, 'carryable', None) is not None:
            carryable_component = obj._components.carryable
            new_carryable_component = clone_factory_wrapper_with_overrides(carryable_component, provided_affordances=merge_list(carryable_component.provided_affordances,  self.carryable_component.provided_affordances))
            inject_dict(obj, '_components', carryable=new_carryable_component)

    def _inject_portal_component(self, obj):
        if self.portal_component is not None and hasattr(obj, '_components') and getattr(obj._components, 'portal', None) is not None:
            portal_component = obj._components.portal
            # Portal Data
            if self.portal_component._replace_existing_portal_data:
                portal_data = merge_list(self.portal_component._portal_data, ())
            else:
                portal_data = merge_list(portal_component._portal_data, self.portal_component._portal_data)

            # State Values
            state_values_which_disable_portals = merge_mapping_lists(portal_component.state_values_which_disable_portals, self.portal_component.state_values_which_disable_portals)

            new_portal_component = clone_factory_wrapper_with_overrides(portal_component, _portal_data=portal_data, state_values_which_disable_portals=state_values_which_disable_portals)
            inject_dict(obj, '_components', portal=new_portal_component)

    def _inject_inventory_item_component(self, obj):
        if self.inventory_item_component is not None and hasattr(obj, '_components') and getattr(obj._components, 'inventory_item', None) is not None:
            inventory_item_component = obj._components.inventory_item
            new_inventory_item_component = clone_factory_wrapper_with_overrides(inventory_item_component, valid_inventory_types=merge_list(inventory_item_component.valid_inventory_types, self.inventory_item_component.valid_inventory_types))
            inject_dict(obj, '_components', inventory_item=new_inventory_item_component)

    def _inject_inventory_component(self, obj):
        if self.inventory_component is not None and hasattr(obj, '_components') and getattr(obj._components, 'inventory', None) is not None:
            inventory_component = obj._components.inventory
            new_inventory_component = clone_factory_wrapper_with_overrides(inventory_component, starting_objects=merge_list(inventory_component.starting_objects, self.inventory_component.starting_objects))
            inject_dict(obj, '_components', inventory=new_inventory_component)

    def _inject_object_locking_component(self, obj, should_create_component=True):
        if self.object_locking_component is not None and hasattr(obj, '_components') and getattr(obj._components, 'object_locking_component', None) is not None:
            object_locking_component = obj._components.object_locking_component
            new_object_locking_component = clone_factory_wrapper_with_overrides(object_locking_component, super_affordances=merge_list(object_locking_component.super_affordances, self.object_locking_component.super_affordances))
            inject_dict(obj, '_components', object_locking_component=new_object_locking_component)
        elif self.object_locking_component is not None and should_create_component:
            object_locking_component = create_factory_wrapper(ObjectLockingComponent, super_affordances=self.object_locking_component.super_affordances)
            inject_dict(obj, '_components', object_locking_component=object_locking_component)

    def _inject_tooltip_component(self, obj):
        if self.tooltip_component_override is not None:
            inject_dict(obj, '_components', tooltip_component=self.tooltip_component_override)

    def _inject_name_component(self, obj):
        if self.name_component_override is not None:
            inject_dict(obj, '_components', name=self.name_component_override)

    def _inject_object_relationship_component_override(self, obj):
        if self.object_relationship_component_override is not None:
            inject_dict(obj, '_components', object_relationships=self.object_relationship_component_override)

    def _inject_slot_component(self, obj):
        if self.slot_component is None:
            return
        if obj._components_native.Slot is None:
            return
        # logger.info("Injecting Slot Component")
        slot_component = obj._components_native.Slot
        default_slot = slot_component.default_slot

        autonomy_modifiers = merge_list(default_slot.autonomy_modifiers, list_type=list, new_items=self.slot_component.additional_autonomy_modifiers)
        for inject_data in self.slot_component.inject_to_autonomy_modifier:
            original_modifier = autonomy_modifiers[inject_data.index]
            if original_modifier is None:
                logger.warn("Invalid Autonomy Modifier index ({}) when injecting to Slot Component for obj {}".format(inject_data.index, obj))
                continue

            # logger.info("Injecting to index {} {}".format(inject_data.index, inspect.getmembers(original_modifier)))
            new_modifier = copy.copy(original_modifier)
            if inject_data.affordance_compatibility is not None:
                new_modifier._affordance_compatibility = merge_affordance_filter(original_modifier._affordance_compatibility, other_filter=inject_data.affordance_compatibility)
            if inject_data.provided_affordance_compatibility is not None:
                new_modifier._provided_affordance_compatibility = merge_affordance_filter(original_modifier._provided_affordance_compatibility, other_filter=inject_data.provided_affordance_compatibility)
            if inject_data.decay_modifiers:
                new_modifier._decay_modifiers = merge_mapping_lists(original_modifier._decay_modifiers, inject_data.decay_modifiers)

            # logger.debug("New Modifier: {}".format(inspect.getmembers(new_modifier)))
            autonomy_modifiers[inject_data.index] = new_modifier

        slot_provided_affordances = merge_list(default_slot.slot_provided_affordances, new_items=self.slot_component.slot_provided_affordances)
        state_values_tuning = merge_list(default_slot.state_values_tuning, new_items=self.slot_component.state_values_tuning)

        new_default_slot = clone_factory_with_overrides(
            default_slot,
            autonomy_modifiers=tuple(autonomy_modifiers),
            slot_provided_affordances=slot_provided_affordances,
            state_values_tuning=state_values_tuning,
        )
        new_slot_component = clone_factory_wrapper_with_overrides(slot_component, default_slot=new_default_slot)
        inject_dict(obj, '_components_native', Slot=new_slot_component)
        # logger.info("After: {}".format(obj._components_native.Slot.default_slot.slot_provided_affordances))

    def _inject(self, obj):
        self._add_affordances(obj)
        self._inject_idle_component(obj)
        self._inject_routing_component(obj)
        self._inject_state_component(obj)
        self._inject_portal_component(obj)
        self._inject_proximity_component(obj)
        self._inject_carryable_component(obj)
        self._inject_inventory_item_component(obj)
        self._inject_inventory_component(obj)
        self._inject_object_locking_component(obj)
        self._inject_tooltip_component(obj)
        self._inject_name_component(obj)
        self._inject_object_relationship_component_override(obj)
        self._inject_slot_component(obj)

    def inject(self):
        for obj in self.get_objects_gen():
            if obj is not None:
                self._inject(obj)


class TunableObjectInjectionByTuningId(BaseTunableObjectInjection):
    FACTORY_TUNABLES = {
        'query': Tunable(
            description='Object tuning to query',
            tunable_type=int,
            default=0
        ),
    }

    __slots__ = ('query',)

    def get_objects_gen(self):
        if self.query is not None:
            tuning = services.get_instance_manager(Types.OBJECT).types.get(get_resource_key(self.query, Types.OBJECT))
            if tuning is not None:
                yield tuning


class TunableObjectInjectionByTags(BaseTunableObjectInjection):
    FACTORY_TUNABLES = {
        'tags': TunableEnumSet(enum_type=Tag, invalid_enums=(Tag.INVALID,)),
        'exclude_tags': TunableEnumSet(enum_type=Tag, invalid_enums=(Tag.INVALID,)),
    }

    __slots__ = ('tags', 'exclude_tags',)

    def _get_definitions_gen(self):
        for definition in services.definition_manager().get_definitions_for_tags_gen(self.tags):
            if self.exclude_tags is None or not definition.has_build_buy_tag(self.exclude_tags):
                yield definition

    def get_objects_gen(self):
        _yield_cache = set()
        for definition in self._get_definitions_gen():
            tuning = services.get_instance_manager(Types.OBJECT).types.get(get_resource_key(definition.tuning_file_id, Types.OBJECT))
            if tuning is not None and tuning not in _yield_cache:
                _yield_cache.add(tuning)
                yield tuning


class TunableObjectInjectionByManyTuningId(BaseTunableObjectInjection):
    FACTORY_TUNABLES = {
        'query': TunableList(
            tunable=Tunable(
                description='Object tuning to query',
                tunable_type=int,
                default=0
            )
        )
    }

    __slots__ = ('query',)

    def get_objects_gen(self):
        manager = services.get_instance_manager(Types.OBJECT)
        for tuning_id in self.query:
            tuning = manager.types.get(get_resource_key(tuning_id, Types.OBJECT))
            if tuning is not None:
                yield tuning


class TunableObjectInjectionByDefinitions(BaseTunableObjectInjection):
    FACTORY_TUNABLES = {
        'definitions': TunableList(tunable=TunableReference(manager=services.definition_manager())),
    }

    __slots__ = ('definitions',)

    def get_objects_gen(self):
        _yield_cache = set()
        for definition in self.definitions:
            if definition is not None and definition.tuning_file_id is not None:
                tuning = services.get_instance_manager(Types.OBJECT).types.get(get_resource_key(definition.tuning_file_id, Types.OBJECT))
                if tuning is not None and tuning not in _yield_cache:
                    _yield_cache.add(tuning)
                    yield tuning


class TunableObjectInjectionByAffordance(BaseTunableObjectInjection):
    FACTORY_TUNABLES = {
        'query': TunableReference(
            description='Affordance to query in object',
            manager=services.get_instance_manager(Types.INTERACTION)
        )
    }

    __slots__ = ('query',)

    def get_objects_gen(self):
        for obj in services.get_instance_manager(Types.OBJECT)._tuned_classes.values():
            if self.query is not None and obj_has_affordance(obj, self.query):
                yield obj


class TunableObjectInjectionByObjectSource(BaseTunableObjectInjection):
    FACTORY_TUNABLES = {
        'object_source': ObjectSearchMethodVariant(),
    }

    __slots__ = ('object_source',)

    @property
    def injection_timing(self):
        return InjectionTiming.ZONE_LOAD

    def get_objects_gen(self):
        yield from self.object_source.get_objects_gen(resolver=None)

    def _inject_idle_component(self, obj, should_create_component=True):
        if self.idle_animation_map is not None:
            idle_component = obj.get_component(IDLE_COMPONENT)
            if idle_component is None and should_create_component:
                idle_component = create_factory_wrapper(IdleComponent, idle_animation_map=self.idle_animation_map)
                obj.add_component(idle_component(obj))
            else:
                inject_dict(idle_component, 'idle_animation_map', self.idle_animation_map)

    def _inject_routing_component(self, obj, should_create_component=True):
        if self.routing_component is not None:
            routing_component = obj.get_component(OBJECT_ROUTING_COMPONENT)
            if routing_component is None and should_create_component:
                routing_component = create_factory_wrapper(RoutingComponent, routing_behavior_map=self.routing_component.routing_behavior_map)
                object_routing_component = create_factory_wrapper(ObjectRoutingComponent, routing_component=routing_component)
                obj.add_component(object_routing_component(obj))
            else:
                inject_dict(routing_component, 'routing_behavior_map', self.routing_component.routing_behavior_map)

    def _inject_state_component(self, obj, should_create_component=True):
        state_component = obj.get_component(STATE_COMPONENT)
        if state_component is None and should_create_component:
            state_component = create_factory_wrapper(StateComponent, states=self.states, state_triggers=self.state_triggers, timed_state_triggers=self.timed_state_triggers)
            obj.add_component(state_component(obj))
        elif state_component is not None:
            for state_info in self.states:
                default_value = state_info.default_value
                if default_value:
                    # This code is from the StateComponent constructor in state.py
                    if not isinstance(default_value, ObjectStateMetaclass):
                        default_value = sims4.random.weighted_random_item([(entry.weight, entry.state) for entry in default_value])
                    if default_value is not None:
                        state = default_value.state
                        if state not in state_component._states:
                            state_component._states[state] = default_value
                            if state_info.reset_to_default:
                                state_component._state_reset_values[state] = default_value
                            if state_info.reset_on_load_if_time_passes:
                                state_component._state_reset_if_time_passes_values[state] = default_value
                            state_component._client_states[state] = state_info.client_states
                            if state_info.tested_states_on_add is not None:
                                state_component._tested_states_on_add[state] = state_info.tested_states_on_add
                            if state_info.tested_states_post_load is not None:
                                state_component._tested_states_post_load[state] = state_info.tested_states_post_load
                            if state_info.tested_states_on_location_changed is not None:
                                state_component._tested_states_on_location_changed[state] = state_info.tested_states_on_location_changed
                            if state_info.tested_states_on_reset is not None:
                                state_component._tested_states_on_reset[state] = state_info.tested_states_on_reset
                            if state_info.tested_states_on_save is not None:
                                state_component._tested_states_on_save[state] = state_info.tested_states_on_save
                            state_component._do_first_time_state_added_actions(state)

            if len(self.state_triggers):
                inject_list(state_component, '_state_triggers', self.state_triggers, unique_entries=False)

            if self.timed_state_triggers is not None:
                inject_dict(state_component, '_timed_state_triggers', self.timed_state_triggers)

    def _inject_proximity_component(self, obj):
        proximity_component = obj.get_component(PROXIMITY_COMPONENT)
        if proximity_component is not None:
            inject_list(proximity_component, 'buffs', self.proximity_buffs)

    def _inject_object_locking_component(self, obj, should_create_component=True):
        if self.object_locking_component is not None:
            locking_component = obj.get_component(OBJECT_LOCKING_COMPONENT)
            if locking_component is not None:
                add_affordances(locking_component, self.object_locking_component.super_affordances, key='super_affordances')
            elif should_create_component:
                locking_component = create_factory_wrapper(ObjectLockingComponent, super_affordances=self.object_locking_component.super_affordances)
                obj.add_component(locking_component(obj))
