import placement
import services
import sims4.math
import sims4.random
from objects.object_enums import ResetReason
from placement import create_starting_location
from routing import get_routing_surface_at_or_below_position, SurfaceType, SurfaceIdentifier
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, Tunable

DEFAULT_ON_LOT_SEARCH_FLAGS = placement.FGLSearchFlag.CALCULATE_RESULT_TERRAIN_HEIGHTS | placement.FGLSearchFlag.DONE_ON_MAX_RESULTS | placement.FGLSearchFlag.STAY_OUTSIDE | placement.FGLSearchFlag.STAY_IN_LOT


class TunableCoordinates(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'x': Tunable(
            tunable_type=float,
            default=None,
            allow_empty=True,
        ),
        'z': Tunable(
            tunable_type=float,
            default=None,
            allow_empty=True,
        ),
    }

    __slots__ = ('x', 'z',)

    @classmethod
    def create_from_target(cls, obj):
        return cls.create_from_position(obj.position)

    @classmethod
    def create_from_position(cls, position):
        return cls(x=position.x, z=position.z)

    def move_sim_to(self, sim, facing_coordinates=None):
        orientation = self._get_orientation(facing_coordinates)
        location = self._get_location(orientation)

        sim.routing_component.on_slot = None
        sim.set_location(location)
        sim.reset(ResetReason.RESET_EXPECTED, None, 'Command')
        return True

    def move_object_to(self, obj, facing_coordinates=None, use_fgl=False, search_flags=DEFAULT_ON_LOT_SEARCH_FLAGS):
        orientation = self._get_orientation(facing_coordinates)

        if use_fgl:
            location = self._get_starting_location()
            fgl_context = placement.create_fgl_context_for_object(location, obj, search_flags=search_flags)
            (position, _, _) = fgl_context.find_good_location()
        else:
            location = self._get_location(orientation)
            position = location.transform.translation

        if position is None:
            return False
        obj.move_to(translation=position, orientation=orientation, routing_surface=location.routing_surface)
        obj.reset(ResetReason.RESET_EXPECTED)
        return True

    def move_object_to_off_lot(self, obj, facing_coordinates=None, use_fgl=False, max_distance=3):
        orientation = self._get_orientation(facing_coordinates)
        use_world_routing_surface = True
        if use_fgl:
            self.set_object_location(obj, orientation, use_world_routing_surface=use_world_routing_surface)
            location = self.get_starting_location(use_world_routing_surface=use_world_routing_surface)
            fgl_context = placement.create_fgl_context_for_object_off_lot(location, obj, max_distance=max_distance)
            (position, _, _) = fgl_context.find_good_location()
        else:
            location = self.get_location(orientation, use_world_routing_surface=use_world_routing_surface)
            position = location.transform.translation

        if position is None:
            return False

        obj.move_to(translation=position, orientation=orientation, routing_surface=location.routing_surface)
        obj.reset(ResetReason.RESET_EXPECTED)
        return True

    def _get_y_axis(self):
        return services.terrain_service.terrain_object().get_height_at(self.x, self.z)

    def _get_position(self):
        return sims4.math.Vector3(self.x, self._get_y_axis(), self.z)

    def _get_routing_surface(self):
        position = self._get_position()
        return get_routing_surface_at_or_below_position(position)

    def _get_world_routing_surface(self):
        return SurfaceIdentifier(services.current_zone_id(), 0, SurfaceType.SURFACETYPE_WORLD)

    def _get_starting_location(self, use_world_routing_surface=False):
        position = self._get_position()
        routing_surface = self._get_world_routing_surface() if use_world_routing_surface else self._get_routing_surface()
        return create_starting_location(position=position, routing_surface=routing_surface)

    def _get_orientation_to_position(self, target_position):
        starting_position = self._get_position()
        vec_to_target = starting_position - target_position
        theta = sims4.math.vector3_angle(vec_to_target)
        return sims4.math.angle_to_yaw_quaternion(theta)

    def _get_transform(self, orientation):
        starting_location = self._get_starting_location()
        return sims4.math.Transform(starting_location.position, orientation)

    def _get_orientation(self, facing_coordinates=None):
        if facing_coordinates:
            facing_position = facing_coordinates.get_position()
            return self._get_orientation_to_position(facing_position)
        else:
            return sims4.random.random_orientation()

    def _get_location(self, orientation, use_world_routing_surface=False):
        transform = self._get_transform(orientation)
        routing_surface = self._get_world_routing_surface() if use_world_routing_surface else self._get_routing_surface()
        return sims4.math.Location(transform, routing_surface)

    def _set_object_location(self, obj, orientation, use_world_routing_surface=False):
        obj.location = self._get_location(orientation, use_world_routing_surface=use_world_routing_surface)
