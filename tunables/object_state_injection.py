import services
from lot51_core import logger
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import inject_list
from objects.components.state import ObjectStateValue, StateChangeOperation, ObjectState
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableList, OptionalTunable
from singletons import UNSET


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
        elif not isinstance(self.object_state, ObjectState):
            logger.warn("Skipping object state injection. Expecting ObjectState but {} is invalid".format(self.object_state))
            return

        state_values_to_add = set()
        for obj_state_value in self.state_values:
            if obj_state_value is not None:
                # Note: changed from issubclass as the OBJECT_STATE manager now holds instances instead of templates
                # as of game version 1.105 and core version 1.16
                if not isinstance(obj_state_value, ObjectStateValue):
                    logger.warn("Skipping `state_values` item in object state injection to {}. {} is not an ObjectStateValue.".format(self.object_state, obj_state_value))
                    continue
                obj_state_value.state = self.object_state
                state_values_to_add.add(obj_state_value)

        inject_list(self.object_state, '_values', state_values_to_add)


class TunableObjectStateValueInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'object_state_value': TunableReference(manager=services.get_instance_manager(Types.OBJECT_STATE)),
        'affordances': TunableList(
            description="Inject to super_affordances",
            tunable=TunableReference(services.get_instance_manager(Types.INTERACTION), pack_safe=True)
        ),
        'new_client_state': OptionalTunable(
            tunable=StateChangeOperation.TunableFactory()
        ),
    }

    __slots__ = ('object_state_value', 'affordances', 'new_client_state',)

    def inject(self):
        if self.object_state_value is None:
            return
        elif not isinstance(self.object_state_value, ObjectStateValue):
            logger.warn("Skipping object state value injection. Expecting ObjectStateValue but {} is invalid".format(self.object_state_value))
            return

        inject_list(self.object_state_value, 'super_affordances', self.affordances)

        if self.new_client_state is not None:
            for key, op in self.new_client_state.ops.items():
                if op is not UNSET:
                    self.object_state_value.new_client_state.opts[key] = op
