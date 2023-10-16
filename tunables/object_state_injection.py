import services
from lot51_core import logger
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import add_affordances
from objects.components.state import ObjectStateValue
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableReference, TunableList


class TunableObjectStateInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'object_state': TunableReference(manager=services.get_instance_manager(Types.OBJECT_STATE)),
        'state_values': TunableList(
            tunable=TunableReference(services.get_instance_manager(Types.OBJECT_STATE))
        )
    }

    __slots__ = ('object_state', 'state_values',)

    def inject(self):
        if self.object_state is None:
            return

        state_values_to_add = list()
        for obj_state_value in self.state_values:
            if obj_state_value is not None:
                if not issubclass(obj_state_value, ObjectStateValue):
                    logger.error("Class does not extend ObjectStateValue: {}, skipping in object state injection to {}".format(obj_state_value, self.object_state))
                    continue
                obj_state_value.state = self.object_state
                state_values_to_add.append(obj_state_value)

        self.object_state._values = tuple(self.object_state._values) + tuple(state_values_to_add)


class TunableObjectStateValueInjection(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'object_state_value': TunableReference(manager=services.get_instance_manager(Types.OBJECT_STATE)),
        'affordances': TunableList(
            tunable=TunableReference(services.get_instance_manager(Types.INTERACTION))
        )
    }

    __slots__ = ('object_state_value', 'affordances',)

    def inject(self):
        if self.object_state_value is None:
            return
        add_affordances(self.object_state_value, self.affordances, key="super_affordances")
