import services
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.tunables.interaction_of_interest_injection import TunableInteractionOfInterestInjection
from lot51_core.utils.collections import AttributeDict
from lot51_core.utils.injection import inject_list, inject_mapping_lists, merge_list, merge_dict
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableList, OptionalTunable, TunableEnumEntry, Tunable, \
    TunableEnumWithFilter, TunableSet, TunableMapping, TunableTuple, TunableVariant
from situations.situation_goal import TunableWeightedSituationGoalReference
from situations.situation_types import SituationDisplayType
from tag import Tag


class TunableSituationGoalInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'situation_goals': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.SITUATION_GOAL), pack_safe=True),
        ),
        'goal_test': TunableVariant(
            interaction_of_interest=TunableInteractionOfInterestInjection.TunableFactory(),
            locked_args={'none': None},
            default='none',
        ),
    }

    __slots__ = ('situation_goals', 'goal_test',)

    def _inject_to_goal(self, situation_goal):
        if self.goal_test is not None:
            self.goal_test.inject_to(situation_goal, '_goal_test')

    def inject(self):
        for situation_goal in self.situation_goals:
            self._inject_to_goal(situation_goal)
