from lot51_core import logger
from services import get_instance_manager
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableList, TunableReference


class TunableInteractionOfInterestInjection(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'affordances': TunableList(
            tunable=TunableReference(manager=get_instance_manager(Types.INTERACTION), pack_safe=True)
        ),
    }

    __slots__ = ('affordances',)

    def inject_to(self, target, key):
        if target is None:
            logger.error("Failed to inject to interaction of interest, target is none")
            return

        tunable = getattr(target, key, None)
        if tunable is None:
            logger.error("Failed to inject to interaction of interest, key {} on target is none".format(key))
            return

        # logger.info(inspect.getmembers(tunable))
        # new_affordances = merge_list(tunable.affordances, self.affordances)
        # factory = TunableSingletonFactory.create_auto_factory(tunable.__class__, affordances=new_affordances)
        # new_tunable = factory()
        # logger.info(inspect.getmembers(new_tunable))
        # new_tunable = clone_factory_with_overrides(tunable, affordances=new_affordances)
        # setattr(target, key, new_tunable)