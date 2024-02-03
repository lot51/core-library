import services
from holidays.holiday_globals import TraditionPreference
from holidays.holiday_tradition import TunablePreferenceTestList, ModifyAllItems, StartSituation, TraditionActions
from lot51_core.tunables.base_injection import BaseTunableInjection
from sims4.localization import TunableLocalizedString
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableList, TunableTuple, TunableEnumEntry, OptionalTunable, TunableVariant
from tunable_time import TunableTimeOfDay


class TunableHolidayTraditionInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'tradition': TunableReference(manager=services.get_instance_manager(Types.HOLIDAY_TRADITION)),
        'drama_nodes_to_run': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.DRAMA_NODE), pack_safe=True),
        ),
        'drama_nodes_to_score': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.DRAMA_NODE), pack_safe=True),
        ),
        'events': TunableList(
            tunable=TunableTuple(
                time=TunableTimeOfDay(),
                event=TunableVariant(
                    modify_items=ModifyAllItems(),
                    start_situation=StartSituation(),
                    default='start_situation'
                )
            )
        ),
        'holiday_buffs': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.BUFF), pack_safe=True),
        ),
        'lifecycle_actions': TunableList(
            tunable=TraditionActions.TunableFactory()
        ),
        'pre_holiday_buffs': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.BUFF), pack_safe=True),
        ),
        'preference': TunableList(
            tunable=TunableTuple(
                 preference=TunableEnumEntry(tunable_type=TraditionPreference, default=TraditionPreference.LIKES),
                 tests=TunablePreferenceTestList(),
                 reason=OptionalTunable(tunable=TunableLocalizedString())
            )
        )
    }

    __slots__ = ('tradition', 'drama_nodes_to_run', 'drama_nodes_to_score', 'events', 'holiday_buffs', 'lifecycle_actions', 'pre_holiday_buffs', 'preference',)

    def inject(self):
        if self.tradition is not None:
            self.tradition.drama_nodes_to_run += tuple(self.drama_nodes_to_run)
            self.tradition.drama_nodes_to_score += tuple(self.drama_nodes_to_score)
            self.tradition.events += tuple(self.events)
            self.tradition.holiday_buffs += tuple(self.holiday_buffs)
            self.tradition.lifecycle_actions += tuple(self.lifecycle_actions)
            self.tradition.pre_holiday_buffs += tuple(self.pre_holiday_buffs)
            self.tradition.preference += tuple(self.preference)
