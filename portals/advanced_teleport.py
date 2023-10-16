import services
from caches import cached
from event_testing.resolver import DoubleObjectResolver
from event_testing.tests import TunableTestSet
from routing.portals.portal_data_teleport import _PortalTypeDataTeleport
from routing.route_enums import RouteEventType
from routing.route_events.route_event_provider import RouteEventProviderMixin
from services import get_instance_manager
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, Tunable, TunableList, TunableTuple


class _PortalTypeDataAdvancedTeleport(RouteEventProviderMixin, _PortalTypeDataTeleport):

    FACTORY_TUNABLES = {
        'route_events': TunableList(
            tunable=TunableTuple(
                route_event=TunableReference(manager=get_instance_manager(Types.SNIPPET)),
                offset=Tunable(tunable_type=float, default=0),
            )
        ),
        'destination_object_tests': TunableTestSet(),
    }

    @cached
    def get_portal_locations(self, obj):
        object_manager = services.object_manager()
        locations = []
        for connected_object in object_manager.get_objects_with_tags_gen(*self.destination_object_tags):
            resolver = DoubleObjectResolver(obj, connected_object)
            if connected_object is not obj and self.destination_object_tests.run_tests(resolver):
                for portal_entry in self.object_portals:
                    entry_location = portal_entry.location_entry(obj)
                    exit_location = portal_entry.location_exit(connected_object)
                    if portal_entry.is_bidirectional:
                        locations.append((entry_location, exit_location, exit_location, entry_location, 0))
                    else:
                        locations.append((entry_location, exit_location, None, None, 0))
        return locations

    def provide_route_events(self, route_event_context, sim, path, is_mirrored=True, node=None, **kwargs):
        for route_event_data in self.route_events:
            if route_event_context.route_event_already_scheduled(route_event_data.route_event, provider=self) or not route_event_context.route_event_already_fully_considered(route_event_data.route_event, self):
                route_event_context.add_route_event(RouteEventType.HIGH_SINGLE, route_event_data.route_event(provider=self, time=node.time + route_event_data.offset))

    def is_route_event_valid(self, route_event, time, sim, path):
        return True
