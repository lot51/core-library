from crafting.food_restrictions_utils import FoodRestrictionUtils
from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from caches import cached_test
from interactions import ParticipantTypeSingleSim, ParticipantTypeSingle
from objects.components.types import CRAFTING_COMPONENT
from sims4.tuning.tunable import TunableVariant, HasTunableSingletonFactory, TunableEnumEntry, AutoFactoryInit, OptionalTunable, Tunable


class CustomFoodRestrictionTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    NO_RESTRICTIONS = 1
    HAS_RESTRICTIONS = 2
    FACTORY_TUNABLES = {
        'sim': TunableEnumEntry(description='The sim to check food restrictions for.', tunable_type=ParticipantTypeSingleSim, default=ParticipantTypeSingleSim.Actor),
        'object': TunableEnumEntry(description='The food object to check food restrictions against.', tunable_type=ParticipantTypeSingle, default=ParticipantTypeSingle.Object),
        'test': TunableVariant(description='The test to perform.', locked_args={'no_restrictions': NO_RESTRICTIONS, 'has_restrictions': HAS_RESTRICTIONS}, default='no_restrictions'),
        'specific_restriction': OptionalTunable(
            tunable=Tunable(tunable_type=str, default='')
        )
    }

    def get_expected_args(self):
        return {'sim': self.sim, 'object': self.object}

    def recipe_has_restriction(self, tracker, recipe, restriction=None):
        if recipe is None:
            return False
        if not tracker._food_restriction_ingredients:
            return False
        if restriction is not None:
            if restriction in recipe.food_restriction_ingredients and restriction in tracker._food_restriction_ingredients:
                return True
            return False
        return any(ingredient in tracker._food_restriction_ingredients for ingredient in recipe.food_restriction_ingredients)

    @cached_test
    def __call__(self, sim=None, object=None):
        sim = next(iter(sim), None)
        object = next(iter(object), None)
        if sim is None or object is None:
            return TestResult(False, 'The sim or the object is none', self.tooltip)
        tracker = sim.food_restriction_tracker
        if not (tracker and object.has_component(CRAFTING_COMPONENT)):
            if self.test == self.NO_RESTRICTIONS:
                return TestResult.TRUE
            if self.test == self.HAS_RESTRICTIONS:
                return TestResult(False, 'Sim {} does not have a food restriction against {}', sim, object, self.tooltip)
        crafting_process = object.get_crafting_process()
        recipe = crafting_process.get_order_or_recipe()

        if self.restriction is not None:
            restriction_type = FoodRestrictionUtils.FoodRestrictionEnum[self.restriction]
        else:
            restriction_type = None

        has_restriction = self.recipe_has_restriction(tracker, recipe, restriction=restriction_type)
        if self.test == self.NO_RESTRICTIONS and has_restriction:
            return TestResult(False, 'Sim {} has a food restriction against {}', sim, object, self.tooltip)
        if self.test == self.HAS_RESTRICTIONS and not has_restriction:
            return TestResult(False, 'Sim {} does not have a food restriction against {}', sim, object, self.tooltip)
        return TestResult.TRUE

