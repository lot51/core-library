import services
from postures.posture import Posture
from postures.posture_cost import _PostureCostCustom
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, Tunable, TunableReference, TunableList, OptionalTunable



class TunablePostureInjection(HasTunableSingletonFactory, AutoFactoryInit):
    """
    This is mainly used for a fix to prevent Sims from dancing near Stereos/TVs
    when they should be using a different posture.
    """
    FACTORY_TUNABLES = {
        'postures': TunableList(tunable=TunableReference(manager=services.get_instance_manager(Types.POSTURE), pack_safe=True)),
        'cost': OptionalTunable(tunable=Tunable(tunable_type=int, default=0))
    }

    __slots__ = ('postures', 'cost',)

    def inject(self):
        if self.cost is not None:
            for (source, dest), transition_data in Posture._posture_transitions.items():
                if dest is not None and dest in self.postures:
                    Posture._posture_transitions[(source, dest)] = transition_data._replace(transition_cost=_PostureCostCustom(cost=self.cost))