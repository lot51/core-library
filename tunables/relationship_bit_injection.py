import services
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import add_affordances, inject_mapping_lists, inject_list

from buffs.tunable import TunableBuffReference
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableList, TunableSet, TunableMapping


class TunableRelationshipBitInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'bits': TunableList(
            description="The bits to inject to",
            tunable=TunableReference(manager=services.get_instance_manager(Types.RELATIONSHIP_BIT), pack_safe=True)
        ),
        'bit_added_loot_list': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.ACTION), pack_safe=True)
        ),
        'provided_mixers': TunableMapping(
            key_type=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True),
            value_type=TunableSet(tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True))
        ),
        'super_affordances': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True)
        ),
        'buffs_to_add_if_on_active_lot': TunableList(
            tunable=TunableBuffReference(pack_safe=True)
        ),
    }

    __slots__ = ('bits', 'bit_added_loot_list', 'provided_mixers', 'super_affordances', 'buffs_to_add_if_on_active_lot')

    def inject(self):
        for bit in self.bits:
            inject_list(bit, 'bit_added_loot_list', self.bit_added_loot_list)
            inject_mapping_lists(bit, 'provided_mixers', self.provided_mixers)
            add_affordances(bit, self.super_affordances, key='super_affordances')
            inject_list(bit, 'buffs_to_add_if_on_active_lot', self.buffs_to_add_if_on_active_lot)
