import services
from _sims4_collections import frozendict
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import inject_dict
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableTuple, TunableMapping, Tunable, TunableEnumEntry
from satisfaction.satisfaction_tracker import SatisfactionTracker


class TunableSatisfactionStoreInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'rewards': TunableMapping(
            description='A list of Sim based Tunable Rewards offered from the Satisfaction Store.',
            key_type=TunableReference(
                description='Reward to inject',
                manager=services.get_instance_manager(Types.REWARD),
                pack_safe=True,
            ),
            value_type=TunableTuple(
                cost=Tunable(tunable_type=int, default=100),
                award_type=TunableEnumEntry(
                    description='The type of the award.',
                    tunable_type=SatisfactionTracker.SatisfactionAwardTypes,
                    default=SatisfactionTracker.SatisfactionAwardTypes.MONEY
                )
            )
        ),
    }

    __slots__ = ('rewards',)

    def inject(self):
        inject_dict(SatisfactionTracker, 'SATISFACTION_STORE_ITEMS', new_items=self.rewards)
