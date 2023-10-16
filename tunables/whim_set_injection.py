import services
from lot51_core.tunables.base_injection import BaseTunableInjection
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference
from whims.whim import TunableWeightedWhimCollection


class TunableWhimSetInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'whim_set': TunableReference(manager=services.get_instance_manager(Types.ASPIRATION)),
        'whims': TunableWeightedWhimCollection()
    }

    __slots__ = ('whim_set', 'whims',)

    def inject(self):
        self.whim_set.whims += self.whims
