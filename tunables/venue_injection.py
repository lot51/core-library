import services
from buffs.tunable import TunableBuffReference
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import inject_list, merge_list
from lot51_core.utils.tunables import clone_factory_wrapper_with_overrides
from scheduler import SituationWeeklySchedule
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableList, TunableSet, OptionalTunable


class TunableVenueInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'venues': TunableList(
            description="The Venues to inject to",
            tunable=TunableReference(manager=services.get_instance_manager(Types.VENUE), pack_safe=True)
        ),
        'venue_buffs': TunableList(
            tunable=TunableBuffReference(pack_safe=True)
        ),
        'zone_modifiers': TunableSet(
            tunable=TunableReference(manager=services.get_instance_manager(Types.ZONE_MODIFIER), pack_safe=True)
        ),
        'background_event_schedule': OptionalTunable(
            tunable=SituationWeeklySchedule.TunableFactory(),
        ),
        'special_event_schedule': OptionalTunable(
            tunable=SituationWeeklySchedule.TunableFactory(),
        ),
    }

    __slots__ = ('venues', 'zone_modifiers', 'venue_buffs', 'background_event_schedule', 'special_event_schedule',)

    def inject(self):
        for tuning in self.venues:
            inject_list(tuning, 'zone_modifiers', self.zone_modifiers)
            inject_list(tuning, 'venue_buffs', self.venue_buffs)

            self._inject_schedule(tuning, 'background_event_schedule')
            self._inject_schedule(tuning, 'special_event_schedule')

    def _inject_schedule(self, tuning, key):
        snippet_schedule = getattr(self, key, None)
        if snippet_schedule is None:
            return

        tuning_schedule = getattr(tuning, key)
        merged_entries = merge_list(tuning_schedule.schedule_entries, new_items=snippet_schedule.schedule_entries)
        cloned_schedule = clone_factory_wrapper_with_overrides(tuning_schedule, schedule_entries=merged_entries)
        setattr(tuning, key, cloned_schedule)