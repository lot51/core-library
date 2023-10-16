import services
from interactions.base.super_interaction import SuperInteraction
from lot51_core import logger
from lot51_core.tunables.base_injection import BaseTunableInjection
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableList
from snippets import TunableAffordanceListReference


class TunableAffordanceListInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'affordance_list': TunableAffordanceListReference(),
        'affordances': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION)),
        )
    }

    __slots__ = ('affordance_list', 'affordances',)

    def inject(self):
        if self.affordance_list is not None:
            affordances_to_add = list()
            for affordance in self.affordances:
                # Check if subclass instead of using strict class_restrictions in TunableReference
                # to allow modded subclasses
                if affordance is not None:
                    if not issubclass(affordance, SuperInteraction):
                        logger.error("Class does not extend SuperInteraction: {}, skipping in affordance list injection".format(affordance))
                        continue
                    affordances_to_add.append(affordance)
            self.affordance_list.value += tuple(affordances_to_add)
