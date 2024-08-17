import services
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import inject_list, merge_mapping_lists
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableList, OptionalTunable, TunableEnumEntry, Tunable, \
    TunableEnumWithFilter, TunableSet, TunableMapping, TunableTuple
from situations.situation_goal import TunableWeightedSituationGoalReference
from situations.situation_types import SituationDisplayType
from tag import Tag


class TunableSituationInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'situations': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.SITUATION), pack_safe=True),
        ),
        'additional_activity_goals': TunableMapping(
            key_name='Activity',
            key_type=TunableReference(
                manager=services.get_instance_manager(Types.HOLIDAY_TRADITION),
                class_restrictions=('SituationActivity',),
                pack_safe=True
            ),
            value_type=TunableList(
                tunable=TunableWeightedSituationGoalReference(
                    pack_safe=True
                )
            ),
        ),
        'additional_activity_selection': OptionalTunable(
            tunable=TunableTuple(
                available_activities=TunableList(
                    tunable=TunableReference(
                        manager=services.get_instance_manager(Types.HOLIDAY_TRADITION),
                        class_restrictions=('SituationActivity',),
                        pack_safe=True
                    )
                ),
                required_activities=OptionalTunable(
                    tunable=TunableSet(
                        tunable=TunableReference(
                            manager=services.get_instance_manager(Types.HOLIDAY_TRADITION),
                            class_restrictions=('SituationActivity',),
                            pack_safe=True
                        )
                    )
                ),
                randomize_activities=OptionalTunable(
                    tunable=TunableTuple(
                        randomizable_activities=TunableSet(
                            tunable=TunableReference(
                                manager=services.get_instance_manager(Types.HOLIDAY_TRADITION),
                                class_restrictions=('SituationActivity',),
                                pack_safe=True
                            )
                        )
                    )
                )
            )
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

    __slots__ = ('situations', 'additional_activity_goals', 'additional_activity_selection', 'disallows_curfew_violation', 'duration', 'duration_randomizer', 'situation_display_type_override', 'tags',)

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

            merge_mapping_lists(situation_type, self.additional_activity_goals)

            # if self.additional_activity_selection is not None and situation_type.activity_selection is not None:
            #     if len(self.additional_activity_selection.available_activities):
            #         inject_list(situation_type.activity_selection, 'available_activities', self.additional_activity_selection.available_activities)
            #
            #     if self.additional_activity_selection.required_activities is not None:
            #         if situation_type.activity_selection.required_activities is not None:
            #             inject_list(situation_type.activity_selection, 'required_activities', self.additional_activity_selection.required_activities)
            #
            #     if self.additional_activity_selection.randomize_activities is not None:
            #         if situation_type.activity_selection.randomize_activities is not None:
            #             inject_list(situation_type.activity_selection.randomize_activities, 'randomizable_activities', self.additional_activity_selection.randomize_activities.randomizable_activities)