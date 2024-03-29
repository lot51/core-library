import services
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import inject_list
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableList, OptionalTunable, TunableEnumEntry, Tunable, \
    TunableEnumWithFilter, TunableSet
from situations.situation_types import SituationDisplayType
from tag import Tag


class TunableSituationInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'situations': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.SITUATION), pack_safe=True),
        ),
        'disallows_curfew_violation': OptionalTunable(
            tunable=Tunable(tunable_type=bool, default=False)
        ),
        'duration': OptionalTunable(
            tunable=Tunable(tunable_type=int, default=0)
        ),
        'duration_randomizer': OptionalTunable(
            tunable=Tunable(tunable_type=int, default=0)
        ),
        'situation_display_type_override': OptionalTunable(
            tunable=TunableEnumEntry(tunable_type=SituationDisplayType, default=SituationDisplayType.NORMAL)
        ),
        'tags': TunableSet(
            tunable=TunableEnumWithFilter(tunable_type=Tag, filter_prefixes=['situation'], default=Tag.INVALID, pack_safe=True)
        ),
    }

    __slots__ = ('situations', 'disallows_curfew_violation', 'duration', 'duration_randomizer', 'situation_display_type_override', 'tags',)

    def inject(self):
        for situation_type in self.situations:
            if self.disallows_curfew_violation is not None:
                situation_type.disallows_curfew_violation = self.disallows_curfew_violation

            if self.duration is not None:
                situation_type.duration = self.duration

            if self.duration_randomizer is not None:
                situation_type.duration_randomizer = self.duration_randomizer

            if self.situation_display_type_override is not None:
                situation_type.situation_display_type_override = self.situation_display_type_override

            if len(self.tags):
                inject_list(situation_type, 'tags', self.tags)
