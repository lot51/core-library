import services
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import add_affordances
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableList, TunableSet, TunableMapping


class TunableRelationshipBitInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'bits': TunableList(
            description="The bits to inject to",
            tunable=TunableReference(manager=services.get_instance_manager(Types.RELATIONSHIP_BIT), pack_safe=True)
        ),
        'bit_added_loot_list': TunableList(tunable=TunableReference(manager=services.get_instance_manager(Types.ACTION), pack_safe=True)),
        'provided_mixers': TunableMapping(
            key_type=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True),
            value_type=TunableSet(tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True))
        ),
        'super_affordances': TunableList(tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True)),
    }

    __slots__ = ('bits', 'bit_added_loot_list', 'provided_mixers', 'super_affordances',)

    def inject(self):
        for bit in self.bits:
            bit.bit_added_loot_list += tuple(self.bit_added_loot_list)

            for super_affordance, mixers in self.provided_mixers.items():
                if super_affordance in bit.provided_mixers:
                    bit.provided_mixers[super_affordance] += tuple(mixers)
                else:
                    bit.provided_mixers[super_affordance] = tuple(mixers)

            add_affordances(bit, self.super_affordances, key='super_affordances')