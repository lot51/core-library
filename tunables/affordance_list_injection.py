import services
from interactions.base.super_interaction import SuperInteraction
from lot51_core import logger
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import add_affordances
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableList
from snippets import TunableAffordanceListReference


class TunableAffordanceListInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'affordance_list': TunableAffordanceListReference(),
        'affordance_lists': TunableList(
            description="Additional affordance lists to inject to",
            tunable=TunableAffordanceListReference(pack_safe=True)
        ),
        'affordances': TunableList(
            description="The affordances to inject to the list",
            tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True),
        )
    }

    __slots__ = ('affordance_list', 'affordance_lists', 'affordances',)

    def _get_affordance_lists_gen(self):
        if self.affordance_list is not None:
            yield self.affordance_list
        yield from self.affordance_lists

    def inject(self):
        affordances_to_add = list()
        for affordance in self.affordances:
            # Check if subclass instead of using strict class_restrictions in TunableReference
            # to allow modded subclasses
            if not issubclass(affordance, SuperInteraction):
                logger.warn("Class does not extend SuperInteraction: {}, skipping in affordance list injection".format(affordance))
                continue
            affordances_to_add.append(affordance)

        for affordance_list in self._get_affordance_lists_gen():
            add_affordances(affordance_list, affordances_to_add, key='value')
