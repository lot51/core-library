from event_testing.results import TestResult
from event_testing.test_base import BaseTest
from lot51_hotels import logger
from services import get_instance_manager
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableReference


class ValidPickerChoiceTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {
        'affordance': TunableReference(manager=get_instance_manager(Types.INTERACTION)),
    }

    __slots__ = ('affordance',)

    def get_expected_args(self):
        return {}

    def __call__(self, **kwargs):

        if self.affordance is None or not hasattr(self.affordance, 'has_valid_choice'):
            return TestResult(False, "Invalid picker interaction: {}".format(self.affordance))

        if not self.affordance.has_valid_choice():
            return TestResult(False, "Picker interaction does not have any valid choices: {}".format(self.affordance), tooltip=self.tooltip)

        logger.debug("Affordance has valid picker choices {}".format(self.affordance))

        return TestResult.TRUE


class ValidPurchasePickerChoiceTest(HasTunableSingletonFactory, AutoFactoryInit, BaseTest):
    FACTORY_TUNABLES = {
        'snippet': TunableReference(manager=get_instance_manager(Types.SNIPPET)),
    }

    __slots__ = ('snippet',)

    def get_expected_args(self):
        return {}

    def __call__(self, **kwargs):

        if self.snippet is None or not hasattr(self.snippet, 'has_valid_choice'):
            return TestResult(False, "Invalid picker snippet: {}".format(self.snippet))

        if not self.snippet.has_valid_choice():
            return TestResult(False, "Picker does not have any valid choices: {}".format(self.snippet), tooltip=self.tooltip)

        logger.debug("Snippet has valid picker choices {}".format(self.snippet))

        return TestResult.TRUE
