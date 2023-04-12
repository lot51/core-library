from event_testing.resolver import SingleSimResolver
from interactions.constraints import Circle
from interactions.jog_interaction import WaypointInteraction
from lot51_core import logger
from lot51_core.tunables.object_query import ObjectSearchMethodVariant
from routing.waypoints.waypoint_generator import _WaypointGeneratorBase
from routing.waypoints.waypoint_generator_object_mixin import _WaypointGeneratorMultipleObjectMixin


class WaypointGeneratorMultipleObjectByObjectSource(_WaypointGeneratorMultipleObjectMixin):
    FACTORY_TUNABLES = {
        'object_source': ObjectSearchMethodVariant(),
    }

    def __init__(self, *args, **kwargs):
        _WaypointGeneratorBase.__init__(self, *args, **kwargs)
        self._sim = self._context.sim
        self._valid_objects = self._get_objects()
        logger.debug("Waypoint targets: {}".format(self._valid_objects))
        if not self._valid_objects:
            self._start_constraint = Circle(self._sim.position, self.constrain_radius, routing_surface=self._sim.routing_surface, los_reference_point=None)
            return
        starting_object = self._valid_objects.pop(0)
        self._start_constraint = Circle(starting_object.position, self.constrain_radius, routing_surface=starting_object.routing_surface, los_reference_point=None)
        self._start_constraint = self._start_constraint.intersect(self.get_water_constraint())

    def _get_objects(self):
        resolver = SingleSimResolver(self._sim)
        return list(self.object_source.get_objects_gen(resolver=resolver))


class ObjectSourceWaypointInteraction(WaypointInteraction):
    INSTANCE_TUNABLES = {
        'waypoint_constraint': WaypointGeneratorMultipleObjectByObjectSource.TunableFactory()
    }