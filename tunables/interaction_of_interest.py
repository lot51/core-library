import event_testing
from event_testing.results import TestResult
from services import get_instance_manager
from sims4.resources import Types
from sims4.tuning.tunable import AutoFactoryInit, TunableList, TunableReference, TunableSet, TunableEnumEntry, TunableSingletonFactory
from snippets import TunableAffordanceListReference
from tag import Tag


class InteractionOfInterest(AutoFactoryInit):
    """
    This InteractionOfInterest class is identical to EA's except
    it allows a list of affordance_lists
    """
    FACTORY_TUNABLES = {
        'affordances': TunableList(
            tunable=TunableAffordanceListReference(pack_safe=True),
        ),
        'affordance_lists': TunableList(
            tunable=TunableReference(manager=get_instance_manager(Types.SNIPPET))
        ),
        'tags': TunableSet(
            tunable=TunableEnumEntry(Tag, Tag.INVALID)
        )
    }

    expected_kwargs = (('interaction', event_testing.test_constants.FROM_EVENT_DATA),)

    def get_expected_args(self):
        return dict(self.expected_kwargs)

    def __call__(self, interaction=None):
        if interaction is None:
            return TestResult(False, 'No affordance to check against {}', self.affordances)
        if self.tags & interaction.get_category_tags():
            return TestResult.TRUE
        if interaction.affordance in list(self.get_affordances_gen()):
            return TestResult.TRUE
        return TestResult(False, 'Failed affordance check: {} not in {}', interaction.affordance, self.affordances)

    def get_affordances_gen(self):
        yield from self.affordances
        for snippet in self.affordance_lists:
            yield from snippet

    def custom_keys_gen(self):
        for affordance in self.get_affordances_gen():
            yield affordance
        for tag in self.tags:
            yield tag

TunableInteractionOfInterest = TunableSingletonFactory.create_auto_factory(InteractionOfInterest)