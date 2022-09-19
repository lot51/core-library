from drama_scheduler.drama_enums import DramaNodeScoringBucket, WeeklySchedulingGroup
from drama_scheduler.drama_scheduler import NodeSelectionOption, DramaScheduleService
from lot51_core import logger
from lot51_core.utils.injection import inject_to_enum
from scheduler_utils import TunableDayAvailability
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, Tunable, TunableVariant, TunableTuple, TunableRange, TunableMapping, TunableEnumEntry, TunableEnumSet


def add_to_scoring_buckets_enum(kvp):
    return inject_to_enum(kvp, DramaNodeScoringBucket)


def add_to_weekly_scheduling_groups_enum(kvp):
    return inject_to_enum(kvp, WeeklySchedulingGroup)


class TunableCustomDramaBucketRule(HasTunableSingletonFactory, AutoFactoryInit):
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
        DramaScheduleService.BUCKET_SCORING_RULES[bucket] = self


class TunableCustomWeeklySchedulingRule(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'weeks_to_schedule_in_advance': TunableRange(tunable_type=int, default=1, minimum=1),
        'weeks_gap': TunableRange(tunable_type=int, default=1, minimum=1),
    }

    __slots__ = ('weeks_to_schedule_in_advance', 'weeks_gap',)

    def inject(self, scheduling_group: WeeklySchedulingGroup):
        DramaScheduleService.WEEKLY_SCHEDULING_RULES[scheduling_group] = self


class TunableDramaSchedulerInjection(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        "bucket_rules": TunableMapping(
            key_type=TunableEnumEntry(tunable_type=DramaNodeScoringBucket, default=DramaNodeScoringBucket.DEFAULT),
            value_type=TunableCustomDramaBucketRule.TunableFactory()
        ),
        "weekly_scheduling_rules": TunableMapping(
            key_type=TunableEnumEntry(tunable_type=WeeklySchedulingGroup, default=WeeklySchedulingGroup.DEFAULT),
            value_type=TunableCustomWeeklySchedulingRule.TunableFactory()
        ),
        "startup_buckets": TunableEnumSet(enum_type=DramaNodeScoringBucket),
    }

    __slots__ = ('bucket_rules', 'weekly_scheduling_rules', 'startup_buckets',)

    def inject(self):

        for bucket, bucket_rule in self.bucket_rules.items():
            try:
                bucket_rule.inject(bucket)
            except:
                logger.exception("Failed injecting bucket rule")

        for schedule_group, schedule_rule in self.weekly_scheduling_rules.items():
            try:
                schedule_rule.inject(schedule_group)
            except:
                logger.exception("Failed injecting schedule rule")

        try:
            new_buckets = set(DramaScheduleService.STARTUP_BUCKETS)
            new_buckets.update(self.startup_buckets)
            DramaScheduleService.STARTUP_BUCKETS = frozenset(new_buckets)
        except:
            logger.exception("Failed injecting startup buckets")