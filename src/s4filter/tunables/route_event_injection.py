import services
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.tunables.test_injection import TestInjectionVariant
from routing.route_enums import RouteEventPriority
from sims4.resources import Types
from sims4.tuning.tunable import Tunable, TunableReference, OptionalTunable, TunableTuple
from lot51_core.utils.injection import inject_to_enum


class TunableRouteEventInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'route_event':TunableReference(manager=services.get_instance_manager(Types.SNIPPET)),
        'priority': OptionalTunable(
            tunable=TunableTuple(
                key=Tunable(tunable_type=str, default='DEFAULT'),
                value=Tunable(tunable_type=int, default=0),
            ),
        ),
        'modify_tests': TestInjectionVariant(),
    }

    __slots__ = ('route_event', 'priority', 'modify_tests',)

    def inject(self):
        if self.route_event is not None:
            if self.priority is not None:
                # inject to RouteEventPriority enum
                enum_data = {self.priority.key: self.priority.value}
                inject_to_enum(enum_data, RouteEventPriority)

                # get resolved enum
                priority = RouteEventPriority[self.priority.key]
                # set priority
                self.route_event.priority = priority

            if self.modify_tests is not None:
                self.modify_tests.inject(self.route_event, 'tests')
