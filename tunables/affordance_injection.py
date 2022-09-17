import services
from event_testing.tests import TunableTestVariant, TunableGlobalTestSet
from interactions.base.basic import TunableBasicExtras
from interactions.utils.display_name import TunableDisplayNameVariant
from sims.household_utilities.utility_types import Utilities
from sims.outfits.outfit_change import TunableOutfitChange
from sims.outfits.outfit_generator import TunableOutfitGeneratorSnippet
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableReference, TunableList, TunableMapping, TunableTuple, TunableVariant, OptionalTunable, TunableEnumEntry


class BaseTunableAffordanceInjection(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'basic_extras': TunableBasicExtras(),
        'display_name_overrides': TunableDisplayNameVariant(description='Set name modifiers or random names.'),
        'tests': TunableList(
            tunable=TunableTestVariant(description="Test to inject into the list of affordances"),
        ),
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
        )
    }

    __slots__ = ('basic_extras', 'display_name_overrides', 'tests', 'outfit_change_on_exit',)

    def get_affordances_gen(self):
        raise NotImplementedError

    def inject(self):
        # inject to DeathType enum
        for affordance in self.get_affordances_gen():
            if affordance is None:
                continue
            for test in self.tests:
                if test is not None:
                    affordance.add_additional_test(test)

            for (posture, outfit_change) in self.outfit_change_on_exit.items():
                if affordance.outfit_change is not None:
                    if affordance.outfit_change.posture_outfit_change_overrides is not None:
                        on_exit = affordance.outfit_change.posture_outfit_change_overrides[posture].on_exit
                        affordance.outfit_change.posture_outfit_change_overrides[
                            posture].on_exit = on_exit + (outfit_change,)
                        # logger.debug("{}".format(affordance.outfit_change.posture_outfit_change_overrides[posture].on_exit))

            if self.basic_extras is not None:
                affordance.basic_extras += self.basic_extras
                # logger.debug("affordance: {} basic_extras: {}".format(affordance, row.basic_extras))


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


class TunableAffordanceInjectionByUtility(BaseTunableAffordanceInjection):
    FACTORY_TUNABLES = {
        'utility': OptionalTunable(tunable=TunableEnumEntry(tunable_type=Utilities, default=None)),
    }

    __slots__ = ('utility',)

    def get_affordances_gen(self):
        if self.utility is None:
            yield from []
            return

        for affordance in services.get_instance_manager(Types.INTERACTION).get_ordered_types():
            if affordance.utility_info is not None:
                if self.utility in affordance.utility_info:
                    yield affordance