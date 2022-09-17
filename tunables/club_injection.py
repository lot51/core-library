import services
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableReference, TunableList


class TunableClubInteractionGroupInjection(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'query': TunableReference(manager=services.get_instance_manager(Types.TUNING)),
        'affordances': TunableList(
            description='List of affordances to inject',
            tunable=TunableReference(
                description='Affordance to inject',
                manager=services.get_instance_manager(Types.INTERACTION)
            )
        ),
    }

    __slots__ = ('query', 'affordances',)

    def inject(self):
        if self.query is not None:
            self.query.affordances += self.affordances