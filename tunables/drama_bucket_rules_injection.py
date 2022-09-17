from drama_scheduler.drama_enums import DramaNodeScoringBucket
from drama_scheduler.drama_scheduler import NodeSelectionOption
from scheduler_utils import TunableDayAvailability
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, Tunable, TunableVariant, TunableTuple, TunableRange


class TunableCustomDramaBucketRule(HasTunableSingletonFactory, AutoFactoryInit):
    DEATH_TYPE_AFFORDANCE_LIST_ID = 16338
    FACTORY_TUNABLES = {
        'days': TunableDayAvailability(),
        'score_if_no_nodes_are_scheduled': Tunable(tunable_type=bool, default=False),
        'number_to_schedule': TunableVariant(
            based_on_household=TunableTuple(
                locked_args={'option': NodeSelectionOption.BASED_ON_HOUSEHOLD}
            ),
            fixed_amount=TunableTuple(
                number_of_nodes=TunableRange(tunable_type=int, default=1, minimum=0),
                locked_args={'option': NodeSelectionOption.STATIC_AMOUNT}
            )
        ),
        'refresh_nodes_on_scheduling': Tunable(tunable_type=bool, default=False)
    }

    __slots__ = ('days', 'score_if_no_nodes_are_scheduled', 'number_to_schedule', 'refresh_nodes_on_scheduling',)


    def inject(self, bucket: DramaNodeScoringBucket):
        pass