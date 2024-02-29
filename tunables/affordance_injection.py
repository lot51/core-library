import services
from animation.animation_overrides_liability import AnimationOverridesLiability
from buffs.tunable import RemoveBuffLiability
from careers.career_event_liabilities import CareerEventTravelLiability
from crafting.crafting_station_liability import CraftingStationLiability
from event_testing.tests import TunableTestVariant, TunableGlobalTestSet
from interactions.base.basic import TunableBasicExtras
from interactions.object_liabilities import TemporaryHiddenInventoryTransferLiability
from interactions.object_retrieval_liability import ObjectRetrievalLiability
from interactions.rabbit_hole import HideSimLiability
from interactions.utils.change_clock_speed_liability import ChangeClockSpeedsLiability
from interactions.utils.custom_camera_liability import CustomCameraLiability
from interactions.utils.display_name import TunableDisplayNameVariant, TunableDisplayNameWrapper, TestableDisplayName, \
    RandomDisplayName
from interactions.utils.lighting_liability import LightingLiability
from interactions.utils.route_goal_suppression_liability import RouteGoalSuppressionLiability
from interactions.utils.teleport_liability import TeleportLiability
from interactions.utils.temporary_state_change_liability import TemporaryStateChangeLiability
from interactions.utils.tunable import TunableStatisticAdvertisements, TimeoutLiability
from interactions.utils.user_cancelable_chain_liability import UserCancelableChainLiability
from interactions.vehicle_liabilities import VehicleLiability
from lot51_core import logger
from lot51_core.constants import SIM_OBJECT_ID
from lot51_core.tunables.base_injection import BaseTunableInjection, InjectionTiming
from lot51_core.tunables.crafting_interaction_injection import TunableCraftingInteractionInjection
from lot51_core.tunables.purchase_interaction_injection import TunablePurchaseInteractionInjection
from lot51_core.tunables.test_injection import TestInjectionVariant
from objects.components.game.game_challenge_liability import GameChallengeLiability
from pets.missing_pets_liability import MissingPetLiability
from postures.proxy_posture_owner_liability import ProxyPostureOwnerLiability
from restaurants.restaurant_liabilities import RestaurantDeliverFoodLiability
from sims.daycare import DaycareLiability
from sims.household_utilities.utility_types import Utilities
from sims.outfits.outfit_change import TunableOutfitChange, InteractionOnRouteOutfitChange, ChangeOutfitLiability
from sims.outfits.outfit_generator import TunableOutfitGeneratorSnippet
from sims4.localization import TunableLocalizedStringFactory
from sims4.resources import Types, get_resource_key
from sims4.tuning.tunable import TunableReference, TunableList, TunableMapping, TunableTuple, TunableVariant, \
    OptionalTunable, TunableEnumEntry, Tunable, TunableSet
from situations.situation_liabilities import CreateSituationLiability, RunningSituationLiability
from snippets import TunableAffordanceListReference
from tag import Tag
from interactions.utils.tunable import TimeoutLiability, SaveLockLiability, CriticalPriorityLiability, GameSpeedLiability, PushAffordanceOnRouteFailLiability
from teleport.teleport_type_liability import TeleportStyleLiability
from whims.whims_tracker import HideWhimsLiability


class BasicLiabilityVariant(TunableVariant):
    def __init__(self):
        super().__init__(
            timeout=TimeoutLiability.TunableFactory(),
            save_lock=SaveLockLiability.TunableFactory(),
            teleport=TeleportLiability.TunableFactory(),
            lighting=LightingLiability.TunableFactory(),
            crafting_station=CraftingStationLiability.TunableFactory(),
            daycare=DaycareLiability.TunableFactory(),
            critical_priority=CriticalPriorityLiability.TunableFactory(),
            career_event_travel=CareerEventTravelLiability.TunableFactory(),
            game_speed=GameSpeedLiability.TunableFactory(),
            hide_whims=HideWhimsLiability.TunableFactory(),
            remove_buff=RemoveBuffLiability.TunableFactory(),
            push_affordance_on_route_fail=PushAffordanceOnRouteFailLiability.TunableFactory(),
            route_goal_suppression=RouteGoalSuppressionLiability.TunableFactory(),
            outfit_change=ChangeOutfitLiability.TunableFactory(),
            object_retrieval=ObjectRetrievalLiability.TunableFactory(),
            game_challenge_liability=GameChallengeLiability.TunableFactory(),
            restaurant_deliver_food_liability=RestaurantDeliverFoodLiability.TunableFactory(),
            teleport_style_liability=TeleportStyleLiability.TunableFactory(),
            animation_overrides=AnimationOverridesLiability.TunableFactory(),
            hide_sim_liability=HideSimLiability.TunableFactory(),
            user_cancelable_chain=UserCancelableChainLiability.TunableFactory(),
            create_situation=CreateSituationLiability.TunableFactory(),
            running_situation=RunningSituationLiability.TunableFactory(),
            missing_pet=MissingPetLiability.TunableFactory(),
            proxy_posture_owner=ProxyPostureOwnerLiability.TunableFactory(),
            vehicles=VehicleLiability.TunableFactory(),
            temporary_state_change=TemporaryStateChangeLiability.TunableFactory(),
            temporary_hidden_inventory_transfer=TemporaryHiddenInventoryTransferLiability.TunableFactory(),
            enable_custom_camera=CustomCameraLiability.TunableFactory(),
            change_clock_speeds_liability=ChangeClockSpeedsLiability.TunableFactory()
        )


class BaseTunableAffordanceInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'allow_user_directed_override': OptionalTunable(tunable=Tunable(tunable_type=bool, default=True)),
        'allow_autonomous_override': OptionalTunable(tunable=Tunable(tunable_type=bool, default=True)),
        'allow_forward_from_object_inventory_override': OptionalTunable(tunable=Tunable(tunable_type=bool, default=True)),
        'allow_from_portrait_override': OptionalTunable(tunable=Tunable(tunable_type=bool, default=True)),
        'allow_from_sim_inventory_override': OptionalTunable(tunable=Tunable(tunable_type=bool, default=True)),
        'allow_from_world_override': OptionalTunable(tunable=Tunable(tunable_type=bool, default=True)),
        'basic_extras': TunableBasicExtras(),
        'basic_liabilities': TunableList(tunable=BasicLiabilityVariant()),
        'cheat_override': OptionalTunable(tunable=Tunable(tunable_type=bool, default=True)),
        'debug_override': OptionalTunable(tunable=Tunable(tunable_type=bool, default=True)),
        'category_override': OptionalTunable(
            tunable=TunableTuple(
                pie_menu_category=TunableReference(manager=services.get_instance_manager(Types.PIE_MENU_CATEGORY))
            ),
        ),
        'display_name_overrides': TunableDisplayNameVariant(description='Set name modifiers or random names.'),
        'display_name_wrappers': OptionalTunable(
            description='If enabled, the first wrapper within the list to pass tests will be applied to the display name.',
            tunable=TunableDisplayNameWrapper.TunableFactory()
        ),
        'false_advertisements': OptionalTunable(
            tunable=TunableStatisticAdvertisements()
        ),
        'inject_to_purchase_interaction': OptionalTunable(tunable=TunablePurchaseInteractionInjection.TunableFactory()),
        'inject_to_crafting_interaction': OptionalTunable(tunable=TunableCraftingInteractionInjection.TunableFactory()),
        'interaction_category_tags': TunableSet(
            description='This attribute is used to tag an interaction to allow for searching, testing, and categorization. An example would be using a tag to selectively test certain interactions. On each of the interactions you want to test together you would add the same tag, then the test routine would only test interactions with that tag. Interactions can have multiple tags. This attribute has no effect on gameplay.',
            tunable=TunableEnumEntry(description='These tag values are used for searching, testing, and categorizing interactions.', tunable_type=Tag, default=Tag.INVALID, pack_safe=True)
        ),
        'modify_autonomous_tests': TestInjectionVariant(description="Lists of tests to replace/append to the affordance's `test_autonomous` compound list."),
        'modify_global_tests': TestInjectionVariant(description="Lists of tests to replace/append to the affordance's `test_globals` list", global_tests=True),
        'modify_tests': TestInjectionVariant(description="Lists of tests to replace/append to the affordance's `tests` compound list."),
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
        ),
        'pie_menu_priority': OptionalTunable(
            tunable=Tunable(tunable_type=int, default=0)
        ),
        'static_commodities': OptionalTunable(
            tunable=TunableList(
                tunable=TunableTuple(
                    static_commodity=TunableReference(manager=services.get_instance_manager(Types.STATIC_COMMODITY), pack_safe=True, reload_dependent=True),
                    desire=Tunable(tunable_type=float, default=1)
                ),
            )
        ),
        'tests': TunableList(
            description="These are 'additional tests' added to the affordance (not an injection). They must all pass separately from test_autonomous, test_globals, tests",
            tunable=TunableTestVariant(),
        ),
        'utility_info': OptionalTunable(
            tunable=TunableMapping(
                key_type=Tunable(tunable_type=str, default='POWER'),
                value_type=TunableTuple(
                    _remove=Tunable(
                        description="If True, this utility requirement will be removed. Supports custom Utilities added to the Utilities enum.",
                        tunable_type=bool,
                        default=False
                    ),
                    shutoff_tooltip_override=TunableLocalizedStringFactory()
                ),
            ),
        )
    }

    __slots__ = ( 'allow_user_directed_override', 'allow_autonomous_override', 'allow_forward_from_object_inventory_override', 'allow_from_portrait_override', 'allow_from_sim_inventory_override', 'allow_from_world_override', 'basic_extras', 'basic_liabilities', 'cheat_override', 'debug_override', 'category_override', 'interaction_category_tags', 'display_name_overrides', 'display_name_wrappers', 'false_advertisements', 'modify_tests', 'modify_autonomous_tests', 'modify_global_tests', 'static_commodities', 'tests', 'outfit_change', 'outfit_change_on_exit', 'pie_menu_priority', 'inject_to_purchase_interaction', 'inject_to_crafting_interaction', 'utility_info',)

    def get_affordances_gen(self):
        raise NotImplementedError

    def _inject_display_name_wrappers(self, affordance):
        if affordance.display_name_wrappers is None:
            affordance.display_name_wrappers = self.display_name_wrappers
        else:
            display_name_wrappers = affordance.display_name_wrappers
            new_wrappers = tuple(self.display_name_wrappers.wrappers) + display_name_wrappers.wrappers

            if isinstance(affordance.display_name_wrappers, TestableDisplayName):
                display_name_wrappers = TestableDisplayName(wrappers=new_wrappers)
            elif isinstance(affordance.display_name_wrappers, RandomDisplayName):
                display_name_wrappers = RandomDisplayName(wrappers=new_wrappers, timeout=affordance.display_name_wrappers.timeout)
            elif isinstance(affordance.display_name_wrappers, TunableDisplayNameWrapper):
                display_name_wrappers = TunableDisplayNameWrapper()
            # Prepend injection
            affordance.display_name_wrappers = display_name_wrappers

    def inject(self):
        for affordance in self.get_affordances_gen():
            if self.allow_autonomous_override is not None:
                affordance.allow_autonomous = self.allow_autonomous_override

            if self.allow_user_directed_override is not None:
                affordance.allow_user_directed = self.allow_user_directed_override

            if self.allow_forward_from_object_inventory_override is not None:
                affordance.allow_forward_from_object_inventory = self.allow_forward_from_object_inventory_override

            if self.allow_from_portrait_override is not None:
                affordance.allow_from_portrait = self.allow_from_portrait_override

            if self.allow_from_sim_inventory_override is not None:
                affordance.allow_from_sim_inventory = self.allow_from_sim_inventory_override

            if self.allow_from_world_override is not None:
                affordance.allow_from_world = self.allow_from_world_override

            if self.basic_extras is not None:
                affordance.basic_extras += self.basic_extras

            if self.basic_liabilities is not None:
                affordance.basic_liabilities += self.basic_liabilities

            if self.cheat_override is not None:
                affordance.cheat = self.cheat_override

            if self.debug_override is not None:
                affordance.debug = self.debug_override

            if self.false_advertisements is not None:
                affordance._false_advertisements += self.false_advertisements

            if self.static_commodities is not None:
                affordance._static_commodities += self.static_commodities

            if self.category_override is not None:
                affordance.category = self.category_override.pie_menu_category

            if self.display_name_overrides is not None:
                if affordance.display_name_overrides is None:
                    affordance.display_name_overrides = self.display_name_overrides
                else:
                    affordance.display_name_overrides.overrides += self.display_name_overrides.overrides

            if self.display_name_wrappers is not None:
                if affordance.display_name_wrappers is None:
                    affordance.display_name_wrappers = self.display_name_wrappers
                else:
                    # Prepend injection
                    affordance.display_name_wrappers.wrappers = tuple(self.display_name_wrappers.wrappers) + affordance.display_name_wrappers.wrappers

            if self.interaction_category_tags is not None:
                affordance.interaction_category_tags = set(affordance.interaction_category_tags) | self.interaction_category_tags

            for test in self.tests:
                if test is not None:
                    affordance.add_additional_test(test)

            if self.modify_autonomous_tests is not None:
                self.modify_autonomous_tests.inject(affordance, 'test_autonomous')

            if self.modify_global_tests is not None:
                self.modify_global_tests.inject(affordance, 'test_globals')

            if self.modify_tests is not None:
                self.modify_tests.inject(affordance, 'tests')

            for (posture, outfit_change) in self.outfit_change_on_exit.items():
                if affordance.outfit_change is not None:
                    if affordance.outfit_change.posture_outfit_change_overrides is not None:
                        on_exit = affordance.outfit_change.posture_outfit_change_overrides[posture].on_exit
                        affordance.outfit_change.posture_outfit_change_overrides[posture].on_exit = on_exit + (outfit_change,)

            if self.outfit_change is not None:
                affordance.outfit_change = self.outfit_change

            if self.pie_menu_priority is not None:
                affordance.pie_menu_priority = self.pie_menu_priority

            if self.inject_to_purchase_interaction is not None:
                self.inject_to_purchase_interaction.inject_to_affordance(affordance)

            if self.inject_to_crafting_interaction is not None:
                self.inject_to_crafting_interaction.inject_to_affordance(affordance)

            if self.utility_info is not None:
                for utility_key, utility_info in self.utility_info.items():
                    # Resolve enum to support custom utilities
                    utility = Utilities[utility_key]
                    if utility is None:
                        continue
                    if utility_info._remove:
                        del affordance.utility_info[utility]
                    else:
                        affordance.utility_info[utility] = utility_info


class TunableAffordanceInjectionByAffordances(BaseTunableAffordanceInjection):
    FACTORY_TUNABLES = {
        'affordances': TunableList(
            description='List of affordances to inject to',
            tunable=TunableReference(
                description='Affordance to inject to',
                manager=services.get_instance_manager(Types.INTERACTION),
                pack_safe=True,
            ),
        ),
    }

    __slots__ = ('affordances',)

    def get_affordances_gen(self):
        yield from self.affordances


class TunableAffordanceInjectionByAffordanceList(BaseTunableAffordanceInjection):
    FACTORY_TUNABLES = {
        'affordance_lists': TunableList(
            description='List of affordances to inject to',
            tunable=TunableAffordanceListReference(pack_safe=True),
        ),
        'exclude_affordances': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True),
        ),
    }

    __slots__ = ('affordance_lists', 'exclude_affordances',)

    def get_affordances_gen(self):
        for affordance_list in self.affordance_lists:
            for affordance in affordance_list.value:
                if affordance not in self.exclude_affordances:
                    yield affordance


class TunableAffordanceInjectionByUtility(BaseTunableAffordanceInjection):
    FACTORY_TUNABLES = {
        'exclude_affordances': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True),
        ),
        'utility': OptionalTunable(tunable=TunableEnumEntry(tunable_type=Utilities, default=None)),
    }

    __slots__ = ('utility', 'exclude_affordances',)

    @property
    def injection_timing(self):
        return InjectionTiming.POST_TUNING_LOADED

    def get_affordances_gen(self):
        if self.utility is not None:
            for affordance in services.get_instance_manager(Types.INTERACTION).get_ordered_types():
                if affordance.utility_info is not None:
                    if self.utility in affordance.utility_info and affordance not in self.exclude_affordances:
                        yield affordance


class TunableAffordanceInjectionByCategory(BaseTunableAffordanceInjection):
    FACTORY_TUNABLES = {
        'exclude_affordances': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True),
        ),
        'pie_menu_categories': TunableSet(tunable=TunableReference(manager=services.get_instance_manager(Types.PIE_MENU_CATEGORY))),
    }

    __slots__ = ('pie_menu_categories', 'exclude_affordances',)

    @property
    def injection_timing(self):
        return InjectionTiming.POST_TUNING_LOADED

    def get_affordances_gen(self):
        for affordance in services.get_instance_manager(Types.INTERACTION).get_ordered_types():
            if affordance.category in self.pie_menu_categories and affordance not in self.exclude_affordances:
                yield affordance


class TunableAffordanceInjectionByCategoryTags(BaseTunableAffordanceInjection):
    FACTORY_TUNABLES = {
        'category_tags': TunableSet(
            description='This attribute is used to tag an interaction to allow for searching, testing, and categorization. An example would be using a tag to selectively test certain interactions. On each of the interactions you want to test together you would add the same tag, then the test routine would only test interactions with that tag. Interactions can have multiple tags. This attribute has no effect on gameplay.',
            tunable=TunableEnumEntry(description='These tag values are used for searching, testing, and categorizing interactions.', tunable_type=Tag, default=Tag.INVALID, pack_safe=True)
        ),
        'exclude_affordances': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True),
        ),
    }

    __slots__ = ('category_tags', 'exclude_affordances',)

    @property
    def injection_timing(self):
        return InjectionTiming.POST_TUNING_LOADED

    def get_affordances_gen(self):
        for affordance in services.get_instance_manager(Types.INTERACTION).get_ordered_types():
            if affordance.interaction_category_tags.intersection(self.category_tags) and affordance not in self.exclude_affordances:
                yield affordance


class TunableAffordanceInjectionToAllPhoneAffordances(BaseTunableAffordanceInjection):
    FACTORY_TUNABLES = {
        'exclude_affordances': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION), pack_safe=True),
        ),
    }

    __slots__ = ('exclude_affordances',)

    @property
    def injection_timing(self):
        return InjectionTiming.POST_TUNING_LOADED

    def get_affordances_gen(self):
        sim_obj = services.get_instance_manager(Types.OBJECT).types.get(get_resource_key(SIM_OBJECT_ID, Types.OBJECT))
        for affordance in sim_obj.phone_affordances:
            if affordance not in self.exclude_affordances:
                yield affordance
