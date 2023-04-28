import services
import sims4.random
from event_testing.tests import TunableTestSet
from interactions import ParticipantType
from interactions.utils.tunable_provided_affordances import TunableProvidedAffordances
from lot51_core.tunables.definition_query import TaggedDefinitionsSource
from lot51_core.tunables.object_query import ObjectSearchMethodVariant
from lot51_core.utils.injection import add_affordances, add_phone_affordances, obj_has_affordance
from objects.components.idle_component import IdleComponent
from objects.components.state import StateTrigger, TunableStateValueReference, StateChangeOperation, TestedStateValueReference, TunableStateComponent, ObjectStateMetaclass
from objects.components.types import IDLE_COMPONENT, OBJECT_ROUTING_COMPONENT, STATE_COMPONENT, PROXIMITY_COMPONENT
from routing.object_routing.object_routing_behavior import ObjectRoutingBehavior
from routing.object_routing.object_routing_component import ObjectRoutingComponent
from sims4.tuning.tunable import Tunable, TunableList, TunableReference, TunableTuple, TunableMapping, TunableVariant, \
    OptionalTunable, HasTunableSingletonFactory, AutoFactoryInit, TunableSimMinute, TunableEnumSet
from sims4.resources import Types, get_resource_key
from sims4.utils import classproperty
from singletons import UNSET
from lot51_core import logger
from tag import Tag


class BaseTunableObjectInjection(HasTunableSingletonFactory, AutoFactoryInit):
    IDLE_COMPONENT = IdleComponent.TunableFactory()
    ROUTING_COMPONENT = ObjectRoutingComponent.TunableFactory()
    STATE_COMPONENT = TunableStateComponent()

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
        'carryable_component': OptionalTunable(
            tunable=TunableTuple(
                provided_affordances=TunableProvidedAffordances(class_restrictions=('SuperInteraction',), locked_args={'allow_self': False, 'target': ParticipantType.Object, 'carry_target': ParticipantType.CarriedObject})
            )
        )
    }

    __slots__ = ('affordances', 'phone_affordances', 'relation_panel_affordances', 'proximity_buffs', 'state_triggers', 'states', 'timed_state_triggers', 'idle_animation_map', 'routing_component', 'carryable_component')

    @classproperty
    def requires_zone(cls):
        """
        If true, this injector will run on every zone load instead
        of a single injection when the instance managers are loaded
        """
        return False

    def get_objects_gen(self):
        raise NotImplementedError

    def _add_affordances(self, obj):
        if len(self.affordances) > 0:
            add_affordances(obj, self.affordances)
        if len(self.phone_affordances) > 0:
            add_phone_affordances(obj, self.phone_affordances)
        if len(self.relation_panel_affordances) > 0:
            add_affordances(obj, self.relation_panel_affordances, key='_relation_panel_affordances')

    def _inject_idle_component(self, obj, should_create_component=True):
        if self.idle_animation_map is not None:
            if hasattr(obj, '_components') and hasattr(obj._components, 'idle_component') and obj._components.idle_component is not None:
                idle_component = obj._components.idle_component
                idle_animation_map = dict(idle_component.idle_animation_map)
                for key, idle in self.idle_animation_map.items():
                    idle_animation_map[key] = idle
                idle_component._tuned_values = idle_component._tuned_values.clone_with_overrides(idle_animation_map=idle_animation_map)
            elif should_create_component:
                obj._components = obj._components.clone_with_overrides(idle_component=self.IDLE_COMPONENT)
                self._inject_idle_component(obj, should_create_component=False)

    def _inject_routing_component(self, obj, should_create_component=True):
        if self.routing_component is not None:
            if hasattr(obj, '_components') and hasattr(obj._components, 'routing_component'):
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
            elif should_create_component:
                obj._components = obj._components.clone_with_overrides(routing_component=self.ROUTING_COMPONENT)
                self._inject_routing_component(obj, should_create_component=False)

    def _inject_state_component(self, obj, should_create_component=True):
        if hasattr(obj, '_components') and hasattr(obj._components, 'state'):
            state_component = obj._components.state
            if state_component is not None and len(self.states) > 0:
                new_states = tuple(state_component._tuned_values.states) + tuple(self.states)
                state_component._tuned_values = state_component._tuned_values.clone_with_overrides(states=new_states)
                # logger.debug("injected states: {} {}".format(obj, self.states))

            if state_component is not None and len(self.state_triggers) > 0:
                new_state_triggers = tuple(state_component._tuned_values.state_triggers) + tuple(self.state_triggers)
                state_component._tuned_values = state_component._tuned_values.clone_with_overrides(state_triggers=new_state_triggers)

            if state_component is not None and self.timed_state_triggers is not None:
                new_timed_state_triggers = dict(state_component._tuned_values.timed_state_triggers)
                for key, value in self.timed_state_triggers.items():
                    new_timed_state_triggers[key] = value
                state_component._tuned_values = state_component._tuned_values.clone_with_overrides(timed_state_triggers=new_timed_state_triggers)
        elif should_create_component:
            obj._components = obj._components.clone_with_overrides(state=self.STATE_COMPONENT)
            self._inject_state_component(obj, should_create_component=False)

    def _inject_proximity_component(self, obj):
        if len(self.proximity_buffs) > 0 and hasattr(obj, '_components') and hasattr(obj._components, 'proximity_component'):
            proximity_component = obj._components.proximity_component
            if proximity_component is not None:
                proximity_buffs = tuple(proximity_component._tuned_values.buffs) + self.proximity_buffs
                proximity_component._tuned_values = proximity_component._tuned_values.clone_with_overrides(buffs=proximity_buffs)

    def _inject_carryable_component(self, obj):
        if self.carryable_component is not None and hasattr(obj, '_components') and hasattr(obj._components, 'carryable_component'):
            carryable_component = obj._components.carryable_component
            if carryable_component is not None:
                provided_affordances = tuple(carryable_component._tuned_values.buffs) + self.carryable_component.provided_affordances
                carryable_component._tuned_values = carryable_component._tuned_values.clone_with_overrides(provided_affordances=provided_affordances)

    def _inject(self, obj):
        self._add_affordances(obj)
        self._inject_idle_component(obj)
        self._inject_routing_component(obj)
        self._inject_state_component(obj)
        self._inject_proximity_component(obj)
        self._inject_carryable_component(obj)

    def inject(self):
        for obj in self.get_objects_gen():
            self._inject(obj)


class TunableObjectInjectionByTuningId(BaseTunableObjectInjection):
    FACTORY_TUNABLES = {
        'query': Tunable(
            description='Object tuning to query',
            tunable_type=int,
            default=0
        )
    }

    __slots__ = ('query',)

    def get_objects_gen(self):
        if self.query is not None:
            yield services.get_instance_manager(Types.OBJECT).types.get(get_resource_key(self.query, Types.OBJECT))


class TunableObjectInjectionByTags(BaseTunableObjectInjection):
    FACTORY_TUNABLES = {
        'tags': TunableEnumSet(enum_type=Tag, invalid_enums=(Tag.INVALID,)),
    }

    __slots__ = ('tags',)

    def _get_definitions_gen(self):
        for definition in services.definition_manager().get_definitions_for_tags_gen(self.tags):
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
        for tuning_id in self.query:
            tuning = services.get_instance_manager(Types.OBJECT).types.get(get_resource_key(tuning_id, Types.OBJECT))
            if tuning is not None:
                yield tuning

class TunableObjectInjectionByDefinitions(BaseTunableObjectInjection):
    FACTORY_TUNABLES = {
        'definitions': TunableList(tunable=TunableReference(manager=services.definition_manager())),
    }

    __slots__ = ('definitions',)

    def get_objects_gen(self):
        for definition in self.definitions:
            if definition.tuning_file_id is not None:
                tuning = services.get_instance_manager(Types.OBJECT).types.get(get_resource_key(definition.tuning_file_id, Types.OBJECT))
                if tuning is not None:
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
        for obj in services.get_instance_manager(Types.OBJECT).get_ordered_types():
            if self.query is not None and obj_has_affordance(obj, self.query):
                yield obj

class TunableObjectInjectionByObjectSource(BaseTunableObjectInjection):
    FACTORY_TUNABLES = {
        'object_source': ObjectSearchMethodVariant(),
    }

    __slots__ = ('object_source',)

    @classproperty
    def requires_zone(cls):
        return True

    def get_objects_gen(self):
        yield from self.object_source.get_objects_gen(resolver=None)

    def _inject_idle_component(self, obj, should_create_component=True):
        if self.idle_animation_map is not None:
            idle_component = obj.get_component(IDLE_COMPONENT)
            if idle_component is None and should_create_component:
                obj.add_component(self.IDLE_COMPONENT(obj, idle_animation_map=self.idle_animation_map))
            else:
                for key, idle in self.idle_animation_map.items():
                    idle_component.idle_animation_map[key] = idle

    def _inject_routing_component(self, obj, should_create_component=True):
        if self.routing_component is not None:
            routing_component = obj.get_component(OBJECT_ROUTING_COMPONENT)
            if routing_component is None and should_create_component:
                obj.add_component(self.ROUTING_COMPONENT(obj, routing_behavior_map=self.routing_component.routing_behavior_map))

    def _inject_state_component(self, obj, should_create_component=True):
        state_component = obj.get_component(STATE_COMPONENT)
        if state_component is None and should_create_component:
            obj.add_component(self.STATE_COMPONENT(obj, states=self.states, state_triggers=self.state_triggers, timed_state_triggers=self.timed_state_triggers))
        else:
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
                state_component._state_triggers += tuple(self.state_triggers)

            if self.timed_state_triggers:
                for key, value in self.timed_state_triggers.items():
                    state_component._timed_state_triggers[key] = value

    def _inject_proximity_component(self, obj):
        proximity_component = obj.get_component(PROXIMITY_COMPONENT)
        if proximity_component is not None and len(self.proximity_buffs):
            proximity_component.buffs += tuple(self.proximity_buffs)
