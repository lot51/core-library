import random
import services
import sims4.math
from interactions import ParticipantType
from interactions.utils.loot_basic_op import BaseLootOperation
from lot51_core import logger
from lot51_core.utils.math import circular_coordinates_by_count_gen
from lot51_core.utils.placement import get_random_orientation
from objects import ALL_HIDDEN_REASONS
from objects.system import create_object
from sims.sim_info import SimInfo
from sims4.resources import Types
from sims4.tuning.tunable import TunableInterval, TunableReference, Tunable, TunableList, HasTunableSingletonFactory, \
    AutoFactoryInit, TunableVariant


class ActiveHouseholdOwnership(HasTunableSingletonFactory, AutoFactoryInit):

    def set_owner(self, obj, **kwargs):
        active_household = services.active_household_id()
        obj.set_household_owner_id(active_household)


class InheritOwnership(HasTunableSingletonFactory, AutoFactoryInit):

    def set_owner(self, obj, **kwargs):
        target = kwargs['target']
        if target is not None:
            household_owner_id = target.get_household_owner_id()
            obj.set_household_owner_id(household_owner_id)


class CreateObjectRingLoot(BaseLootOperation):
    FACTORY_TUNABLES = {
        'definitions': TunableList(tunable=TunableReference(manager=services.definition_manager())),
        'radius': Tunable(tunable_type=float, default=1),
        'count': TunableInterval(tunable_type=int, default_lower=5, default_upper=7),
        'initial_x_offset': TunableInterval(tunable_type=float, default_lower=0, default_upper=0),
        'initial_z_offset': TunableInterval(tunable_type=float, default_lower=0, default_upper=0),
        'x_jitter': TunableInterval(tunable_type=float, default_lower=0, default_upper=0),
        'z_jitter': TunableInterval(tunable_type=float, default_lower=0, default_upper=0),
        'states': TunableList(tunable=TunableReference(manager=services.get_instance_manager(Types.OBJECT_STATE)))
    }

    def __init__(self, definitions=(), radius=1, count=None, x_jitter=None, z_jitter=None, initial_x_offset=None, initial_z_offset=None, states=(), **kwargs):
        self._definitions = definitions
        self._radius = radius
        self._count = count
        self._x_jitter = x_jitter
        self._z_jitter = z_jitter
        self._initial_x_offset = initial_x_offset
        self._initial_z_offset = initial_z_offset
        self._states = states
        super().__init__(**kwargs)

    def _apply_to_subject_and_target(self, subject, target, resolver):
        source = resolver.get_participant(ParticipantType.Object)
        if isinstance(source, SimInfo):
            source = source.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)

        count = random.randint(self._count.lower_bound, self._count.upper_bound)
        initial_x = random.uniform(self._initial_x_offset.lower_bound, self._initial_x_offset.upper_bound)
        initial_z = random.uniform(self._initial_z_offset.lower_bound, self._initial_z_offset.upper_bound)

        for x, z in circular_coordinates_by_count_gen(radius=self._radius, count=count):
            definition = random.choice(self._definitions)
            obj = create_object(definition)
            if obj is not None:
                obj.opacity = 0
                x_jitter = random.uniform(self._x_jitter.lower_bound, self._x_jitter.upper_bound) if self._x_jitter is not None else 0
                z_jitter = random.uniform(self._z_jitter.lower_bound, self._z_jitter.upper_bound) if self._z_jitter is not None else 0
                position = sims4.math.Vector3(0, 0, 0)
                position += source.position
                position.x += initial_x + x + x_jitter
                position.z += initial_z + z + z_jitter

                obj.move_to(translation=position, orientation=get_random_orientation(), routing_surface=source.routing_surface)

                for state_value in self._states:
                    if state_value is not None:
                        obj.set_state(state_value.state, state_value)

                obj.fade_in()


class SpawnObjectLoot(BaseLootOperation):
    FACTORY_TUNABLES = {
        'definition': TunableReference(manager=services.definition_manager()),
        'initial_x_offset': TunableInterval(tunable_type=float, default_lower=0, default_upper=0),
        'initial_z_offset': TunableInterval(tunable_type=float, default_lower=0, default_upper=0),
        'x_jitter': TunableInterval(tunable_type=float, default_lower=0, default_upper=0),
        'z_jitter': TunableInterval(tunable_type=float, default_lower=0, default_upper=0),
        'states': TunableList(tunable=TunableReference(manager=services.get_instance_manager(Types.OBJECT_STATE))),
        'owner': TunableVariant(active_household=ActiveHouseholdOwnership.TunableFactory(), inherit=InheritOwnership.TunableFactory())
    }

    def __init__(self, definition=None, x_jitter=None, z_jitter=None, initial_x_offset=None, initial_z_offset=None, states=(), owner=None, **kwargs):
        self._definition = definition
        self._x_jitter = x_jitter
        self._z_jitter = z_jitter
        self._initial_x_offset = initial_x_offset
        self._initial_z_offset = initial_z_offset
        self._states = states
        self._owner = owner
        super().__init__(**kwargs)

    def _apply_to_subject_and_target(self, subject, target, resolver):
        source = resolver.get_participant(ParticipantType.Object)
        if isinstance(source, SimInfo):
            source = source.get_sim_instance(allow_hidden_flags=ALL_HIDDEN_REASONS)

        initial_x = random.uniform(self._initial_x_offset.lower_bound, self._initial_x_offset.upper_bound)
        initial_z = random.uniform(self._initial_z_offset.lower_bound, self._initial_z_offset.upper_bound)

        obj = create_object(self._definition)
        if obj is not None:
            obj.opacity = 0
            x_jitter = random.uniform(self._x_jitter.lower_bound, self._x_jitter.upper_bound) if self._x_jitter is not None else 0
            z_jitter = random.uniform(self._z_jitter.lower_bound, self._z_jitter.upper_bound) if self._z_jitter is not None else 0
            position = sims4.math.Vector3(0, 0, 0)
            position += source.position
            position.x += initial_x + x_jitter
            position.z += initial_z + z_jitter

            obj.move_to(translation=position, orientation=get_random_orientation(), routing_surface=source.routing_surface)

            for state_value in self._states:
                if state_value is not None:
                    obj.set_state(state_value.state, state_value)

            if self._owner is not None:
                self._owner.set_owner(obj, target=source)

            obj.fade_in()
