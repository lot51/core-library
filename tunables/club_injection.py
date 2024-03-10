import services
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import inject_list
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableList, TunableSet
from snippets import TunableAffordanceListReference


class TunableClubInteractionGroupInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'query': TunableReference(manager=services.get_instance_manager(Types.CLUB_INTERACTION_GROUP)),
        'affordance_lists': TunableSet(
            description='A set of affordance lists associated with this interaction group.',
            tunable=TunableAffordanceListReference(
                pack_safe=True
            )
        ),
        'affordances': TunableList(
            description='List of affordances to inject',
            tunable=TunableReference(
                description='Affordance to inject',
                manager=services.get_instance_manager(Types.INTERACTION),
                pack_safe=True,
            )
        ),
    }

    __slots__ = ('query', 'affordance_lists', 'affordances',)

    def inject(self):
        if self.query is not None:
            inject_list(self.query, 'affordance_lists', self.affordance_lists)
            inject_list(self.query, 'affordances', self.affordances)
