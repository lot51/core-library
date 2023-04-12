import services
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableReference
from whims.whim import TunableWeightedWhimCollection


class TunableWhimSetInjection(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'whim_set': TunableReference(manager=services.get_instance_manager(Types.ASPIRATION)),
        'whims': TunableWeightedWhimCollection()
    }

    __slots__ = ('whim_set', 'whims',)

    def inject(self):
        self.whim_set.whims += self.whims
