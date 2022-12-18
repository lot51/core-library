from event_testing.tests import TunableTestSet
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, Tunable, TunableList, TunableTuple


class LotFiftyOneTunableModifiers(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'base_rate': Tunable(tunable_type=int, default=0, allow_empty=True),
        'modifiers': TunableList(
            tunable=TunableTuple(
                modifier=Tunable(description="Modifier to add to the base rate", tunable_type=int, default=0, allow_empty=True),
                tests=TunableTestSet(description="Tests that must pass for this modifier to be applied")
            )
        )
    }

    __slots__ = ('base_rate', 'modifiers',)

    def get_modifier(self, resolver):
        rate = self.base_rate
        if resolver is None:
            return rate
        for potential_modifier in self.modifiers:
            if potential_modifier.tests.run_tests(resolver):
                rate += potential_modifier.modifier
        return rate
