from event_testing.tests import TunableTestSet, TunableTestVariant, TunableGlobalTestSet
from lot51_core import logger
from lot51_core.utils.injection import clone_test_set
from sims4.tuning.tunable import TunableVariant, HasTunableSingletonFactory, AutoFactoryInit, TunableList, Tunable


class TestReplaceMixin:
    def inject(self, target, key):
        logger.debug("replacing {} with {}".format(getattr(target, key, None), self.tests))
        setattr(target, key, self.tests)


class TunableTestReplaceInjection(TestReplaceMixin, HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'tests': TunableTestSet(),
    }


class TunableTestReplaceGlobalsInjection(TestReplaceMixin, HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'tests': TunableGlobalTestSet(),
    }


class TunableTestMergeInjection(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'prepend_and': Tunable(
            description="If True, the AND tests will be prepended instead of appending.",
            tunable_type=bool,
            default=False
        ),
        'AND': TunableList(
            tunable=TunableTestVariant(),
            description="Additional tests added to each original OR list. Warning: this does not affect the lists defined in this injector's `OR`"
        ),
        'OR': TunableTestSet(
            description="Additional AND lists added to the compound test list. Note: This does not apply to injections to test_globals."
        ),
    }

    def inject(self, target, key):
        original_list = getattr(target, key, None)
        new_list = clone_test_set(original_list, additional_and=self.AND, additional_or=self.OR, prepend_and=self.prepend_and)
        setattr(target, key, new_list)
        logger.debug("tuned_values {}".format(getattr(target, '_tuned_values', None)))
        logger.debug("original {}: final {}".format(original_list, getattr(target, key, None)))


class TestInjectionVariant(TunableVariant):
    def __init__(self, global_tests=False, **kwargs):
        if global_tests:
            replace_factory = TunableTestReplaceGlobalsInjection
        else:
            replace_factory = TunableTestReplaceInjection

        super().__init__(
            add_tests=TunableTestMergeInjection.TunableFactory(),
            replace_tests=replace_factory.TunableFactory(),
            locked_args={'disabled': None},
            default='disabled',
            **kwargs
        )