from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import inject_list
from services import get_instance_manager
from sims4.common import Pack
from sims4.resources import Types
from sims4.tuning.tunable import TunableList, TunableReference, TunableTuple


class TunableUniversityInjection(BaseTunableInjection):

    FACTORY_TUNABLES = {
        'university': TunableReference(
            description="The university to inject to",
            manager=get_instance_manager(Types.UNIVERSITY)
        ),
        'prestige_degrees': TunableList(
            description="Additional prestige degrees. This does not update the SimData.",
            tunable=TunableTuple(
                elective=TunableReference(manager=get_instance_manager(Types.UNIVERSITY_MAJOR))
            ),
            unique_entries=True,
        ),
    }

    __slots__ = ('university', 'prestige_degrees',)

    @property
    def required_packs(self):
        return (Pack.EP08,)

    def inject(self):
        if self.university is not None:
            inject_list(self.university, 'prestige_degrees', self.prestige_degrees)