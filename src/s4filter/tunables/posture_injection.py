import services
from event_testing.tests import TunableGlobalTestSet
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import inject_list
from postures.posture import Posture
from postures.posture_cost import _PostureCostCustom
from sims.outfits.outfit_change import TunableOutfitChange
from sims4.resources import Types
from sims4.tuning.tunable import Tunable, TunableReference, TunableList, OptionalTunable, TunableTuple


class TunablePostureInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'postures': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.POSTURE), pack_safe=True)
        ),
        'cost': OptionalTunable(
            description="This is mainly used for a fix to prevent Sims from dancing near Stereos/TVs when they should be using a different posture.",
            tunable=Tunable(tunable_type=int, default=0)
        ),
        'prepend_override_outfit_changes': TunableList(
            description='Define override outfits for entering this posture. The first override that passes its tests will be applied.',
            tunable=TunableTuple(
                outfit_change=TunableOutfitChange(),
                tests=TunableGlobalTestSet(description='Tests to determine if this override should be applied.')
            )
        ),
    }

    __slots__ = ('postures', 'cost', 'prepend_override_outfit_changes',)

    def inject(self):
        if self.cost is not None:
            for (source, dest), transition_data in Posture._posture_transitions.items():
                if dest is not None and dest in self.postures:
                    Posture._posture_transitions[(source, dest)] = transition_data._replace(transition_cost=_PostureCostCustom(cost=self.cost))

        for posture in self.postures:
            inject_list(posture, 'override_outfit_changes', self.prepend_override_outfit_changes, prepend=True)