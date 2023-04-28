import services
from routing.route_enums import RouteEventPriority
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, Tunable, TunableReference, OptionalTunable, TunableTuple
from lot51_core.utils.injection import inject_to_enum


class TunableRouteEventInjection(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'route_event':TunableReference(manager=services.get_instance_manager(Types.SNIPPET)),
        'priority': OptionalTunable(
            tunable=TunableTuple(
                key=Tunable(tunable_type=str, default='DEFAULT'),
                value=Tunable(tunable_type=int, default=0),
            ),
        ),
    }

    __slots__ = ('route_event', 'priority',)

    def inject(self):
        if self.priority is not None:
            # inject to RouteEventPriority enum
            enum_data = {self.priority.key: self.priority.value}
            inject_to_enum(enum_data, RouteEventPriority)

            # get resolved enum
            priority = RouteEventPriority[self.priority.key]
            # set priority
            self.route_event.priority = priority