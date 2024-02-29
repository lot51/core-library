import services
import sims4
from lot51_core import logger, __version__
from lot51_core.services.events import event_handler, CoreEvent
from lot51_core.tunables.affordance_injection import TunableAffordanceInjectionByAffordances, \
    TunableAffordanceInjectionByUtility, TunableAffordanceInjectionByAffordanceList, \
    TunableAffordanceInjectionByCategory, TunableAffordanceInjectionToAllPhoneAffordances, \
    TunableAffordanceInjectionByCategoryTags
from lot51_core.tunables.affordance_list_injection import TunableAffordanceListInjection
from lot51_core.tunables.base_injection import BaseTunableInjection, InjectionTiming
from lot51_core.tunables.interaction_cancel_compatibility_injection import InteractionCancelCompatibilityInjection
from lot51_core.tunables.part_injection import TunableObjectPartInjection
from lot51_core.tunables.pregnancy_tracker_injector import TunablePregnancyTrackerInjection
from lot51_core.tunables.relationship_bit_injection import TunableRelationshipBitInjection
from lot51_core.tunables.role_state_injection import TunableRoleStateInjection
from lot51_core.tunables.sim_info_injection import TunableSimInfoInjection
from lot51_core.tunables.buff_injection import TunableBuffInjection
from lot51_core.tunables.club_injection import TunableClubInteractionGroupInjection
from lot51_core.tunables.death_injection import TunableCustomDeath
from lot51_core.tunables.loot_injection import TunableLootInjection, TunableRandomWeightedLootInjection
from lot51_core.tunables.mixer_list_injection import TunableMixerListInjection
from lot51_core.tunables.object_injection import TunableObjectInjectionByAffordance, TunableObjectInjectionByTuningId, TunableObjectInjectionByDefinitions, TunableObjectInjectionByObjectSource, TunableObjectInjectionByTags
from lot51_core.tunables.object_state_injection import TunableObjectStateInjection, TunableObjectStateValueInjection
from lot51_core.tunables.posture_injection import TunablePostureInjection
from lot51_core.tunables.preference_item_injection import TunableCharacteristicPreferenceItemInjection
from lot51_core.tunables.region_injection import TunableRegionInjection
from lot51_core.tunables.route_event_injection import TunableRouteEventInjection
from lot51_core.tunables.satisfaction_store_injection import TunableSatisfactionStoreInjection
from lot51_core.tunables.service_picker_injection import TunableServicePickerInjection, TunableHireableServicePickerInjection
from lot51_core.tunables.situation_job_injection import TunableSituationJobInjection
from lot51_core.tunables.social_bunny_injection import TunableSocialBunnyInjection
from lot51_core.tunables.test_set_injection import TunableTestSetInjection
from lot51_core.tunables.tradition_injection import TunableHolidayTraditionInjection
from lot51_core.tunables.trait_injection import TunableTraitInjection
from lot51_core.tunables.trait_tracker_injector import TunableTraitTrackerInjection
from lot51_core.tunables.university_injection import TunableUniversityInjection
from lot51_core.tunables.university_tuning_injection import TunableUniversityTuningInjection
from lot51_core.tunables.whim_set_injection import TunableWhimSetInjection
from lot51_core.utils.injection_tracker import injection_tracker
from lot51_core.utils.semver import Version
from services import get_instance_manager
from sims4.common import Pack
from sims4.localization import LocalizationHelperTuning
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableReference, TunableList, Tunable, TunableEnumSet
from sims4.resources import Types
from ui.ui_dialog_notification import UiDialogNotification


with sims4.reload.protected(globals()):
    SHOWN_VERSION_NOTIFICATION = False


class TuningInjector(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(Types.SNIPPET)):
    VERSION_DIALOG = UiDialogNotification.TunableFactory()
    INVALID_SNIPPETS = set()

    INSTANCE_TUNABLES = {
        "_required_packs": TunableEnumSet(enum_type=Pack, default_enum_list=(Pack.BASE_GAME,)),
        "minimum_core_version": Tunable(tunable_type=str, allow_empty=True, default='1.0.0'),
        "creator_name": Tunable(tunable_type=str, allow_empty=True, default='N/A'),
        "mod_name": Tunable(tunable_type=str, allow_empty=True, default='N/A'),
        "inject_by_affordance": TunableList(
            description="Inject to object tuning based on an existing affordance",
            tunable=TunableObjectInjectionByAffordance.TunableFactory(),
        ),
        "inject_by_definitions": TunableList(
            description="Inject to affordances",
            tunable=TunableObjectInjectionByDefinitions.TunableFactory()
        ),
        "inject_by_object_tuning": TunableList(
            description="Inject to object tuning",
            tunable=TunableObjectInjectionByTuningId.TunableFactory(),
        ),
        "inject_by_object_tags": TunableList(
            description="Inject to object tuning by tags",
            tunable=TunableObjectInjectionByTags.TunableFactory(),
        ),
        "inject_by_object_source": TunableList(
            description="Inject to objects on zone load",
            tunable=TunableObjectInjectionByObjectSource.TunableFactory(),
        ),
        "inject_to_affordances": TunableList(
            description="Inject to affordances",
            tunable=TunableAffordanceInjectionByAffordances.TunableFactory()
        ),
        "inject_to_affordances_by_list": TunableList(
            description="Inject to affordances in an affordance list snippet",
            tunable=TunableAffordanceInjectionByAffordanceList.TunableFactory(),
        ),
        "inject_to_affordances_by_utility_info": TunableList(
            description="Inject to affordances by their required utility",
            tunable=TunableAffordanceInjectionByUtility.TunableFactory()
        ),
        "inject_to_affordances_by_category": TunableList(
            description="Inject to affordances by their category, accepts multiple categories",
            tunable=TunableAffordanceInjectionByCategory.TunableFactory()
        ),
        "inject_to_affordances_by_category_tags": TunableList(
            description="Inject to affordances by interaction_category_tags if there is at least one match",
            tunable=TunableAffordanceInjectionByCategoryTags.TunableFactory()
        ),
        "inject_to_all_phone_affordances": TunableList(
            description="Inject to all phone affordances",
            tunable=TunableAffordanceInjectionToAllPhoneAffordances.TunableFactory()
        ),
        "inject_by_utility_info": TunableList(
            description="Inject to affordances by their required utility",
            tunable=TunableAffordanceInjectionByUtility.TunableFactory(),
            deprecated=True,
        ),
        "inject_to_club_interaction_group": TunableList(
            tunable=TunableClubInteractionGroupInjection.TunableFactory()
        ),
        "inject_to_affordance_list": TunableList(
            description="Inject super interactions to affordance list snippet",
            tunable=TunableAffordanceListInjection.TunableFactory()
        ),
        "inject_to_mixer_list": TunableList(
            description="Inject mixers to affordance list snippet",
            tunable=TunableMixerListInjection.TunableFactory()
        ),
        "inject_to_buffs": TunableList(
            tunable=TunableBuffInjection.TunableFactory(),
        ),
        "inject_to_characteristic_preferences": TunableList(
            description="A mapping of the desired traits associated with this PreferenceItem, and the corresponding scores.",
            tunable=TunableCharacteristicPreferenceItemInjection.TunableFactory()
        ),
        "inject_to_holiday_traditions": TunableList(
            tunable=TunableHolidayTraditionInjection.TunableFactory(),
        ),
        "inject_to_loot": TunableList(
            tunable=TunableLootInjection.TunableFactory()
        ),
        "inject_to_object_parts": TunableList(
            tunable=TunableObjectPartInjection.TunableFactory(),
        ),
        "inject_to_object_state_values": TunableList(
            tunable=TunableObjectStateValueInjection.TunableFactory(),
        ),
        "inject_to_object_states": TunableList(
            tunable=TunableObjectStateInjection.TunableFactory()
        ),
        "inject_to_postures": TunableList(
            tunable=TunablePostureInjection.TunableFactory()
        ),
        "inject_to_random_weighted_loot": TunableList(
            tunable=TunableRandomWeightedLootInjection.TunableFactory()
        ),
        "inject_to_regions": TunableList(
            tunable=TunableRegionInjection.TunableFactory(),
        ),
        "inject_to_relbits": TunableList(
            tunable=TunableRelationshipBitInjection.TunableFactory(),
        ),
        "inject_to_role_states": TunableList(
            tunable=TunableRoleStateInjection.TunableFactory(),
        ),
        "inject_to_route_events": TunableList(
            tunable=TunableRouteEventInjection.TunableFactory(),
        ),
        "inject_to_service_picker": TunableList(
            description="Inject to non_service_npcs in the hire a service picker",
            tunable=TunableServicePickerInjection.TunableFactory(),
        ),
        "inject_to_service_picker_hireable": TunableList(
            description="Inject to service_npcs in the hire a service picker",
            tunable=TunableHireableServicePickerInjection.TunableFactory(),
        ),
        "inject_to_situation_jobs": TunableList(
            tunable=TunableSituationJobInjection.TunableFactory(),
        ),
        "inject_to_test_sets": TunableList(
            tunable=TunableTestSetInjection.TunableFactory()
        ),
        "inject_to_traits": TunableList(
            tunable=TunableTraitInjection.TunableFactory(),
        ),
        "inject_to_universities": TunableList(
            tunable=TunableUniversityInjection.TunableFactory(),
        ),
        "inject_to_whim_sets": TunableList(
            tunable=TunableWhimSetInjection.TunableFactory(),
        ),
        "custom_death_types": TunableList(
            tunable=TunableCustomDeath.TunableFactory(),
        ),
        "inject_to_sim_info": TunableSimInfoInjection.TunableFactory(),
        "interaction_cancel_compatibility": TunableList(
            tunable=InteractionCancelCompatibilityInjection.TunableFactory()
        ),
        "pregnancy_tracker": TunablePregnancyTrackerInjection.TunableFactory(),
        "satisfaction_store": TunableSatisfactionStoreInjection.TunableFactory(),
        "social_bunny": TunableSocialBunnyInjection.TunableFactory(),
        "trait_tracker": TunableTraitTrackerInjection.TunableFactory(),
        "university": TunableUniversityTuningInjection.TunableFactory(),
    }

    __injectors__ = tuple(INSTANCE_TUNABLES.keys())


    @classmethod
    def to_str(cls):
        return '<TuningInjector {} by {} ({}); minimum core version {}>'.format(cls.mod_name, cls.creator_name, cls.__name__, cls.minimum_core_version)

    @classmethod
    def _tuning_loaded_callback(cls):
        logger.info('[tuning_loaded_callback] {}'.format(cls.to_str()))

    @classmethod
    def all_snippets_gen(cls):
        yield from get_instance_manager(Types.SNIPPET).get_ordered_types(only_subclasses_of=cls)

    @classmethod
    def get_core_version(cls):
        return Version.parse(__version__, optional_minor_and_patch=True)

    @classmethod
    def get_minimum_version(cls):
        return Version.parse(cls.minimum_core_version, optional_minor_and_patch=True)

    @classmethod
    def is_valid_version(cls):
        return cls.get_core_version() >= cls.get_minimum_version()

    @classmethod
    def are_packs_available(cls):
        return sims4.common.are_packs_available(cls._required_packs)

    @classmethod
    def _get_injectors_gen(cls):
        for key in cls.__injectors__:
            injector = getattr(cls, key)
            if type(injector) == tuple:
                for subinjector in injector:
                    if isinstance(subinjector, BaseTunableInjection) and subinjector.is_available():
                        yield key, subinjector
            elif isinstance(injector, BaseTunableInjection) and injector.is_available():
                yield key, injector

    @classmethod
    def perform_injections(cls, timing: InjectionTiming):
        if not cls.are_packs_available():
            logger.warn("[TuningInjector] skipping injector due to missing packs: {}".format(cls.to_str()))
            return

        logger.info('[TuningInjector] starting injections for timing {}: {}'.format(timing, cls.to_str()))

        total = 0
        for key, injector in cls._get_injectors_gen():
            try:
                if injector.injection_timing == timing:
                    injector.inject()
                    total += 1
            except:
                logger.exception('[TuningInjector] injector failed: {}'.format(key))

        logger.info('[TuningInjector] completed injections; total {}'.format(total))

    @classmethod
    def show_version_dialog(cls):
        active_sim = services.get_active_sim()
        dialog = cls.VERSION_DIALOG(active_sim)
        dialog.title = lambda *_: LocalizationHelperTuning.get_raw_text("Lot 51 Core Library Issue Detected")
        text = "{} by {} requires a newer version of Core Library.\n\n" \
               "Current Version: {}\nRequired Version: {}\n\nPlease download the latest version from https://lot51.cc/core to use this mod.\n\n" \
               "If you still experience issues, join the Lot 51 Discord.".format(cls.mod_name, cls.creator_name, __version__, cls.minimum_core_version)
        dialog.text = lambda *_: LocalizationHelperTuning.get_raw_text(text)
        dialog.urgency = UiDialogNotification.UiDialogNotificationUrgency.URGENT
        dialog.show_dialog()


@event_handler(CoreEvent.TUNING_LOADED)
def _do_injections(*args, **kwargs):
    # This allows definitions to be queried by tag
    # Thank you Scumbumbo
    definition_manager = services.definition_manager()
    definition_manager.refresh_build_buy_tag_cache(refresh_definition_cache=False)

    # Perform initial injections when instance managers have loaded,
    # and track invalid snippets to notify when loading screen is lifted
    for snippet in TuningInjector.all_snippets_gen():
        try:
            if snippet.is_valid_version():
                snippet.perform_injections(InjectionTiming.TUNING_LOADED)
            else:
                TuningInjector.INVALID_SNIPPETS.add(snippet)
                logger.warn("Snippet {} version is incompatible with the current Core Library version. {} < {}".format(snippet.__name__, snippet.minimum_core_version, __version__))
        except:
            logger.exception("TUNING_LOADED Injection Failure for Snippet: {}".format(snippet.to_str()))

    # Perform post load injections that are dependent
    # upon the initial injections.
    for snippet in TuningInjector.all_snippets_gen():
        try:
            if snippet.is_valid_version():
                snippet.perform_injections(InjectionTiming.POST_TUNING_LOADED)
        except:
            logger.exception("POST_TUNING_LOADED Injection Failure for Snippet: {}".format(snippet.to_str()))

    injection_tracker.cleanup()


@event_handler(CoreEvent.ZONE_CLEANUP_OBJECTS)
def _do_zone_dependent_injections(*args, **kwargs):
    for snippet in TuningInjector.all_snippets_gen():
        try:
            if snippet.is_valid_version():
                snippet.perform_injections(InjectionTiming.ZONE_LOAD)
        except:
            logger.exception("ZONE_LOAD Injection Failure for Snippet: {}".format(snippet.to_str()))


@event_handler(CoreEvent.LOADING_SCREEN_LIFTED)
def _do_version_notifier(*args, **kwargs):
    global SHOWN_VERSION_NOTIFICATION
    if not SHOWN_VERSION_NOTIFICATION:
        for snippet in TuningInjector.INVALID_SNIPPETS:
            snippet.show_version_dialog()
        SHOWN_VERSION_NOTIFICATION = True
        TuningInjector.INVALID_SNIPPETS.clear()
