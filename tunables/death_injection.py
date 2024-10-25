import services
from lot51_core import logger
from lot51_core.tunables.base_injection import BaseTunableInjection
from sims4.resources import Types
from sims4.tuning.tunable import Tunable, TunableReference
from interactions.utils.death import DeathTracker
from sims4.collections import  make_immutable_slots_class
from _sims4_collections import frozendict
from lot51_core.utils.injection import inject_to_enum, add_affordance

# Backwards compatibility for <1.110
try:
    from interactions.utils.death_enums import DeathType
except:
    from interactions.utils.death import DeathType


class TunableCustomDeath(BaseTunableInjection):
    DEATH_TYPE_AFFORDANCE_LIST_ID = 16338
    FACTORY_TUNABLES = {
        'death_type_key': Tunable(tunable_type=str, default=''),
        'death_type_id': Tunable(tunable_type=int, default=0),
        'affordance': TunableReference(manager=services.get_instance_manager(Types.INTERACTION)),
        'trait': TunableReference(manager=services.get_instance_manager(Types.TRAIT)),
    }

    __slots__ = ('death_type_key', 'death_type_id', 'affordance', 'trait',)

    _create_death_info = make_immutable_slots_class({'death_type', 'set_to_minimum_lod'})

    @classmethod
    def get_death_type_affordance_list(cls):
        return services.get_instance_manager(Types.SNIPPET).get(cls.DEATH_TYPE_AFFORDANCE_LIST_ID)

    def inject(self):
        if self.affordance is None or self.trait is None:
            logger.warn("Unable to inject death type, missing trait and/or affordance")
            return

        # inject to DeathType enum
        enum_data = {self.death_type_key: self.death_type_id}
        inject_to_enum(enum_data, DeathType)

        # get resolved enum
        death_type = DeathType[self.death_type_key]

        # Replicate Death Info slots and add to interaction death info
        death_info = {'death_type': death_type, 'set_to_minimum_lod': self.affordance.death_info.set_to_minimum_lod}
        self.affordance.death_info = self._create_death_info(death_info)

        # add affordance to death type list
        affordance_list = self.get_death_type_affordance_list()
        add_affordance(affordance_list, self.affordance, key='value')

        # add trait to death trait map
        trait_map = dict(DeathTracker.DEATH_TYPE_GHOST_TRAIT_MAP)
        trait_map[death_type] = self.trait
        DeathTracker.DEATH_TYPE_GHOST_TRAIT_MAP = frozendict(trait_map)
