import services
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import add_affordances
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableList


class TunableClubInteractionGroupInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'query': TunableReference(manager=services.get_instance_manager(Types.CLUB_INTERACTION_GROUP)),
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
            add_affordances(self.query, self.affordances, key='affordances')
