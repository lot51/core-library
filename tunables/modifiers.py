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

    def get_modifier(self, resolver):
        if resolver is None:
            return 0
        rate = self.base_rate
        for potential_modifer in self.modifiers:
            if potential_modifer.tests.run_tests(resolver):
                rate += potential_modifer.modifier

        return rate