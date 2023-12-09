from interactions.interaction_cancel_compatibility import InteractionCancelReason, InteractionCancelCompatibility
from lot51_core.tunables.base_injection import BaseTunableInjection
from services import get_instance_manager
from sims4.resources import Types
from sims4.tuning.tunable import TunableList, TunableReference, TunableEnumEntry


class InteractionCancelCompatibilityInjection(BaseTunableInjection):

    FACTORY_TUNABLES = {
        'reason': TunableEnumEntry(InteractionCancelReason, default=InteractionCancelReason.FIRE),
        'include_affordances': TunableList(
            tunable=TunableReference(manager=get_instance_manager(Types.INTERACTION), pack_safe=True),
        )
    }

    def inject(self):
        filter = InteractionCancelCompatibility.INTERACTION_CANCEL_COMPATIBILITY.get(self.reason, None)
        if filter is not None:
            new_included_list = filter._tuned_values.default_inclusion.include_affordances + self.include_affordances
            new_default_inclusion = filter._tuned_values.default_inclusion.clone_with_overrides(include_affordances=new_included_list)
            filter._tuned_values = filter._tuned_values.clone_with_overrides(default_inclusion=new_default_inclusion)