import services
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableReference, TunableList
from sims4.collections import  make_immutable_slots_class


class TunableBuffInjection(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'buff': TunableReference(manager=services.get_instance_manager(Types.BUFF)),
        'loot_on_addition': TunableList(tunable=TunableReference(manager=services.get_instance_manager(Types.ACTION))),
        'actor_mixers': TunableList(tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION)))
    }

    __slots__ = ('buff', 'loot_on_addition', 'actor_mixers',)

    _create_interaction_items = make_immutable_slots_class({'interaction_items'})

    def inject(self):
        self.buff._loot_on_addition += self.loot_on_addition

        if self.actor_mixers is not None:
            if self.buff.interactions is not None:
                interaction_items = self.buff.interactions.interaction_items + self.actor_mixers
                self.buff.interactions = self.buff.interactions.clone_with_overrides(interaction_items=interaction_items)
            else:
                self.buff.interactions = self._create_interaction_items({'interaction_items': self.actor_mixers})