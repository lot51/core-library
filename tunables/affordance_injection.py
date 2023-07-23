import services
from event_testing.tests import TunableTestVariant, TunableGlobalTestSet, TunableTestSet, TestList
from interactions.base.basic import TunableBasicExtras
from interactions.utils.display_name import TunableDisplayNameVariant
from interactions.utils.tunable import TunableStatisticAdvertisements
from lot51_core import logger
from sims.household_utilities.utility_types import Utilities
from sims.outfits.outfit_change import TunableOutfitChange, InteractionOnRouteOutfitChange
from sims.outfits.outfit_generator import TunableOutfitGeneratorSnippet
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableReference, TunableList, \
    TunableMapping, TunableTuple, TunableVariant, OptionalTunable, TunableEnumEntry, Tunable
from snippets import TunableAffordanceListReference


class BaseTunableAffordanceInjection(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'allow_user_directed_override': OptionalTunable(tunable=Tunable(tunable_type=bool, default=True)),
        'allow_autonomous_override': OptionalTunable(tunable=Tunable(tunable_type=bool, default=True)),
        'category_override': OptionalTunable(
            tunable=TunableTuple(
                category=TunableReference(manager=services.get_instance_manager(Types.PIE_MENU_CATEGORY))
            ),
        ),
        'false_advertisements': OptionalTunable(
            tunable=TunableStatisticAdvertisements()
        ),
        'static_commodities': OptionalTunable(
            tunable=TunableList(
                tunable=TunableTuple(
                    static_commodity=TunableReference(manager=services.get_instance_manager(Types.STATIC_COMMODITY), pack_safe=True, reload_dependent=True),
                    desire=Tunable(tunable_type=float, default=1)
                ),
            )
        ),
        'basic_extras': TunableBasicExtras(),
        'display_name_overrides': TunableDisplayNameVariant(description='Set name modifiers or random names.'),
        'tests': TunableList(
            tunable=TunableTestVariant(description="Test to inject into the list of affordances"),
        ),
        'autonomous_tests': TunableTestSet(description="Lists of tests to append to the affordance test_autonomous list"),
        'outfit_change_on_exit': TunableMapping(
            description="Append an outfit change to an existing posture",
            key_type=TunableReference(manager=services.get_instance_manager(Types.POSTURE)),
            value_type=TunableTuple(
                description='A tuple of clothing changes and tests for whether they should happen or not. ',
                outfit_to_modify=TunableVariant(
                    description='The outfit we want to generate over.',
                    current=TunableOutfitChange._OutfitChangeForTags.OutfitTypeCurrent.TunableFactory(),
                    outfit_category=TunableOutfitChange._OutfitChangeForTags.OutfitTypeCategory.TunableFactory(),
                    special=TunableOutfitChange._OutfitChangeForTags.OutfitTypeSpecial.TunableFactory(),
                    default='special'
                ),
                generator=TunableOutfitGeneratorSnippet(),
                tests=TunableGlobalTestSet(description=' Tests to run when deciding which clothing change entry to use. All of the tests must pass in order for the item to pass.')
            )
        ),
        'outfit_change': OptionalTunable(
            tunable=TunableTuple(
                description='A structure of outfit change tunables.',
                on_route_change=InteractionOnRouteOutfitChange(description='An outfit change to execute on the first mobile node of the transition to this interaction.'),
                posture_outfit_change_overrides=OptionalTunable(
                    tunable=TunableMapping(
                        description='A mapping of postures to outfit change entry and exit reason overrides.',
                        key_type=TunableReference(description="If the Sim encounters this posture during this interaction's transition sequence, the posture's outfit change reasons will be the ones specified here.", manager=services.get_instance_manager(Types.POSTURE)),
                        value_type=TunableOutfitChange(description='Define what outfits the Sim is supposed to wear when entering or exiting this posture.')
                    )
                ),
            )
        )
    }

    __slots__ = ('basic_extras', 'allow_user_directed_override', 'category_override', 'allow_autonomous_override', 'autonomous_tests', 'display_name_overrides', 'false_advertisements', 'static_commodities', 'tests', 'outfit_change', 'outfit_change_on_exit',)

    def get_affordances_gen(self):
        raise NotImplementedError

    def inject(self):
        for affordance in self.get_affordances_gen():
            if affordance is None:
                continue

            if self.allow_autonomous_override is not None:
                affordance.allow_autonomous = self.allow_autonomous_override

            if self.allow_user_directed_override is not None:
                affordance.allow_user_directed = self.allow_user_directed_override

            if self.false_advertisements is not None:
                affordance._false_advertisements += self.false_advertisements

            if self.static_commodities is not None:
                affordance._static_commodities += self.static_commodities

            if self.category_override is not None:
                affordance.category = self.category_override.category

            for test in self.tests:
                if test is not None:
                    affordance.add_additional_test(test)

            if len(self.autonomous_tests):
                tests = TestList(affordance.test_autonomous)
                tests.extend(self.autonomous_tests)
                affordance.test_autonomous = tests
                logger.debug("adding autonomous tests: {}, final result: {}".format(self.autonomous_tests, affordance.test_autonomous))

            for (posture, outfit_change) in self.outfit_change_on_exit.items():
                if affordance.outfit_change is not None:
                    if affordance.outfit_change.posture_outfit_change_overrides is not None:
                        on_exit = affordance.outfit_change.posture_outfit_change_overrides[posture].on_exit
                        affordance.outfit_change.posture_outfit_change_overrides[posture].on_exit = on_exit + (outfit_change,)

            if self.outfit_change is not None:
                affordance.outfit_change = self.outfit_change

            if self.basic_extras is not None:
                affordance.basic_extras += self.basic_extras


class TunableAffordanceInjectionByAffordances(BaseTunableAffordanceInjection):
    FACTORY_TUNABLES = {
        'affordances': TunableList(
            description='List of affordances to inject to',
            tunable=TunableReference(
                description='Affordance to inject to',
                manager=services.get_instance_manager(Types.INTERACTION)
            )
        ),
    }

    __slots__ = ('affordances',)

    def get_affordances_gen(self):
        yield from self.affordances


class TunableAffordanceInjectionByAffordanceList(BaseTunableAffordanceInjection):
    FACTORY_TUNABLES = {
        'affordance_lists': TunableList(
            description='List of affordances to inject to',
            tunable=TunableAffordanceListReference(),
        ),
    }

    __slots__ = ('affordance_lists',)

    def get_affordances_gen(self):
        for affordance_list in self.affordance_lists:
            if affordance_list is not None:
                yield from affordance_list.value


class TunableAffordanceInjectionByUtility(BaseTunableAffordanceInjection):
    FACTORY_TUNABLES = {
        'utility': OptionalTunable(tunable=TunableEnumEntry(tunable_type=Utilities, default=None)),
    }

    __slots__ = ('utility',)

    def get_affordances_gen(self):
        if self.utility is not None:
            for affordance in services.get_instance_manager(Types.INTERACTION).get_ordered_types():
                if affordance.utility_info is not None:
                    if self.utility in affordance.utility_info:
                        yield affordance