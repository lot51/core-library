import services
from clubs.club_tuning import ClubTunables
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import inject_list
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableList, TunableSet
from snippets import TunableAffordanceListReference


class TunableClubTuningInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'club_traits': TunableSet(
            description='Traits to inject to CLUB_TRAITS.',
            tunable=TunableReference(
                manager=services.get_instance_manager(Types.TRAIT),
                pack_safe=True
            )
        ),
    }

    __slots__ = ('club_traits',)

    def inject(self):
        if self.club_traits is not None:
            inject_list(ClubTunables, 'CLUB_TRAITS', new_items=self.club_traits)
