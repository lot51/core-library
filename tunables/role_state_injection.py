import services
from buffs.tunable import TunableBuffReference
from lot51_core.tunables.base_injection import BaseTunableInjection
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableList
from lot51_core.utils.injection import add_affordances


class TunableRoleStateInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'role_state':TunableReference(manager=services.get_instance_manager(Types.ROLE_STATE)),
        'buffs': TunableList(tunable=TunableBuffReference(pack_safe=True)),
        'loot_on_load': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.ACTION), pack_safe=True)
        ),
        'role_affordances': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True),
        ),
        'role_target_affordances': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True),
        ),
        'preroll_affordances': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True),
        ),
    }

    __slots__ = ('role_state', 'role_affordances', 'role_target_affordances', 'preroll_affordances', 'loot_on_load', 'buffs',)

    def inject(self):
        if self.role_state is not None:
            self.role_state._buffs += self.buffs
            self.role_state.loot_on_load += self.loot_on_load
            add_affordances(self.role_state, self.role_affordances, key='role_affordances')
            add_affordances(self.role_state, self.role_target_affordances, key='role_target_affordances')
            add_affordances(self.role_state, self.preroll_affordances, key='preroll_affordances')
