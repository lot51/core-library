import services
from event_testing.tests import TunableTestSet
from lot51_core.utils.injection import add_affordances, add_phone_affordances, obj_has_affordance
from objects.components.state import StateTrigger, TunableStateValueReference, StateChangeOperation, TestedStateValueReference
from routing.object_routing.object_routing_behavior import ObjectRoutingBehavior
from sims4.tuning.tunable import Tunable, TunableList, TunableReference, TunableTuple, TunableMapping, TunableVariant, OptionalTunable, HasTunableSingletonFactory, AutoFactoryInit, TunableSimMinute
from sims4.resources import Types, get_resource_key
from singletons import UNSET
from lot51_core import logger


class BaseTunableObjectInjection(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'affordances': TunableList(
            description='List of affordances to inject',
            tunable=TunableReference(
                description='Affordance to inject',
                manager=services.get_instance_manager(Types.INTERACTION)
            )
        ),
        'phone_affordances': TunableList(
            description='List of affordances to inject to object phone affordance list',
            tunable=TunableReference(
                description='Affordance to inject',
                manager=services.get_instance_manager(Types.INTERACTION)
            )
        ),
        'relation_panel_affordances': TunableList(
            description='List of affordances to inject to Sim relationship panel',
            tunable=TunableReference(
                description='Affordance to inject',
                manager=services.get_instance_manager(Types.INTERACTION)
            )
        ),
        'proximity_buffs': TunableList(
            description="Proximity Buffs to inject to the proximity component",
            tunable=TunableReference(manager=services.get_instance_manager(Types.BUFF)),
        ),
        'state_triggers': TunableList(StateTrigger.TunableFactory()),
        'states': TunableList(tunable=TunableTuple(default_value=TunableVariant(reference=TunableStateValueReference(pack_safe=True), random=TunableList(tunable=TunableTuple(state=TunableStateValueReference(pack_safe=True), weight=Tunable(tunable_type=float, default=1.0))), default='reference'), client_states=TunableMapping(key_type=TunableStateValueReference(description='\n                            A state value\n                            ', pack_safe=True), value_type=StateChangeOperation.TunableFactory()), reset_to_default=Tunable(tunable_type=bool, default=False), reset_on_load_if_time_passes=Tunable(tunable_type=bool, default=False), tested_states_on_add=OptionalTunable(tunable=TestedStateValueReference.TunableFactory()), tested_states_post_load=OptionalTunable(tunable=TestedStateValueReference.TunableFactory()), tested_states_on_location_changed=OptionalTunable(tunable=TestedStateValueReference.TunableFactory()), tested_states_on_reset=OptionalTunable(tunable=TestedStateValueReference.TunableFactory(locked_args={'fallback_state': None})), tested_states_on_save=OptionalTunable(tunable=TestedStateValueReference.TunableFactory(locked_args={'fallback_state': None})))),
        'timed_state_triggers': OptionalTunable(tunable=TunableMapping(key_type=TunableStateValueReference(pack_safe=True), value_type=TunableTuple(trigger_on_load=Tunable(tunable_type=bool, default=False), ops=TunableList(tunable=TunableTuple(trigger_time=TunableSimMinute(default=10, minimum=0), trigger_time_random_offset=TunableSimMinute(default=0, minimum=0), states_to_trigger=TunableList(tunable=TunableStateValueReference(pack_safe=True)),random_states_to_trigger=TunableList(    tunable=TunableTuple(weight=Tunable(tunable_type=int, default=1),                         tests=TunableTestSet(),                         state_value=TunableStateValueReference())),loot_list=TunableList(    tunable=TunableReference(        manager=services.get_instance_manager(Types.ACTION),        class_restrictions=('LootActions',), pack_safe=True)),trigger_tests=TunableTuple(tests=TunableTestSet(), reschedule_on_failure=Tunable(tunable_type=bool, default=False))))))),
        'idle_animation_map': OptionalTunable(tunable=TunableMapping(key_type=TunableReference(manager=services.get_instance_manager(Types.OBJECT_STATE), class_restrictions='ObjectStateValue'), value_type=TunableReference(manager=services.get_instance_manager(Types.ANIMATION), class_restrictions='ObjectAnimationElement'))),
        'routing_component': OptionalTunable(
            tunable=TunableTuple(
                routing_behavior_map=TunableMapping(key_type=TunableReference(manager=services.get_instance_manager(Types.OBJECT_STATE), class_restrictions='ObjectStateValue'), value_type=OptionalTunable(tunable=ObjectRoutingBehavior.TunableReference(), enabled_by_default=True, enabled_name='Start_Behavior', disabled_name='Stop_All_Behavior', disabled_value=UNSET))
            )
        ),
    }

    __slots__ = ('affordances', 'phone_affordances', 'relation_panel_affordances', 'proximity_buffs', 'state_triggers', 'states', 'timed_state_triggers', 'idle_animation_map', 'routing_component',)

    def get_objects_gen(self):
        raise NotImplementedError

    def _add_affordances(self, obj):
        if len(self.affordances) > 0:
            add_affordances(obj, self.affordances)
        if len(self.phone_affordances) > 0:
            add_phone_affordances(obj, self.phone_affordances)
        if len(self.relation_panel_affordances) > 0:
            add_affordances(obj, self.relation_panel_affordances, key='_relation_panel_affordances')

    def _inject_idle_component(self, obj):
        if self.idle_animation_map is not None and hasattr(obj, '_components') and hasattr(obj._components, 'idle_component'):
            idle_component = obj._components.idle_component
            idle_animation_map = dict(idle_component.idle_animation_map)
            for key, idle in self.idle_animation_map.items():
                idle_animation_map[key] = idle
            idle_component._tuned_values = idle_component._tuned_values.clone_with_overrides(idle_animation_map=idle_animation_map)

    def _inject_routing_component(self, obj):
        if self.routing_component is not None and hasattr(obj, '_components') and hasattr(obj._components, 'routing_component'):
            routing_component = obj._components.routing_component

            # get nested component
            object_routing_component = routing_component._tuned_values.object_routing_component
            routing_behavior_map = dict(object_routing_component.routing_behavior_map)
            for key, behavior in self.routing_component.routing_behavior_map.items():
                routing_behavior_map[key] = behavior

            # add routing behaviors
            object_routing_component._tuned_values = object_routing_component._tuned_values.clone_with_overrides(routing_behavior_map=routing_behavior_map)
            # then add object routing component
            routing_component._tuned_values = routing_component._tuned_values.clone_with_overrides(object_routing_component=object_routing_component)

    def _inject_state_component(self, obj):
        if hasattr(obj, '_components') and hasattr(obj._components, 'state'):
            state_component = obj._components.state
            if state_component is not None and len(self.states) > 0:
                new_states = state_component._tuned_values.states + self.states
                state_component._tuned_values = state_component._tuned_values.clone_with_overrides(states=new_states)
                # logger.debug("injected states: {} {}".format(obj, self.states))

            if state_component is not None and len(self.state_triggers) > 0:
                new_state_triggers = state_component._tuned_values.state_triggers + self.state_triggers
                state_component._tuned_values = state_component._tuned_values.clone_with_overrides(state_triggers=new_state_triggers)

            if state_component is not None and self.timed_state_triggers is not None:
                new_timed_state_triggers = dict(state_component._tuned_values.timed_state_triggers)
                for key, value in self.timed_state_triggers.items():
                    new_timed_state_triggers[key] = value
                state_component._tuned_values = state_component._tuned_values.clone_with_overrides(timed_state_triggers=new_timed_state_triggers)

    def _inject_proximity_component(self, obj):
        if len(self.proximity_buffs) > 0 and hasattr(obj, '_components') and hasattr(obj._components, 'proximity_component'):
            proximity_component = obj._components.proximity_component
            if proximity_component is not None:
                proximity_buffs = tuple(proximity_component._tuned_values.buffs) + self.proximity_buffs
                proximity_component._tuned_values = proximity_component._tuned_values.clone_with_overrides(buffs=proximity_buffs)

    def inject(self):
        for obj in self.get_objects_gen():
            self._add_affordances(obj)
            self._inject_idle_component(obj)
            self._inject_routing_component(obj)
            self._inject_state_component(obj)
            self._inject_proximity_component(obj)


class TunableObjectInjectionByTuningId(BaseTunableObjectInjection):
    FACTORY_TUNABLES = {
        'query': Tunable(
            description='Object tuning to query',
            tunable_type=int,
            default=0
        )
    }

    def get_objects_gen(self):
        if self.query is not None:
            yield services.get_instance_manager(Types.OBJECT).types.get(get_resource_key(self.query, Types.OBJECT))


class TunableObjectInjectionByAffordance(BaseTunableObjectInjection):
    FACTORY_TUNABLES = {
        'query': TunableReference(
            description='Affordance to query in object',
            manager=services.get_instance_manager(Types.INTERACTION)
        )
    }

    def get_objects_gen(self):
        for obj in services.get_instance_manager(Types.OBJECT).get_ordered_types():
            if self.query is not None and obj_has_affordance(obj, self.query):
                yield obj