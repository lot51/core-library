import services
from event_testing.tests import TunableTestSet
from lot51_core import logger
from lot51_core.tunables.affordance_injection import TunableAffordanceInjectionByAffordances, TunableAffordanceInjectionByUtility
from lot51_core.tunables.buff_injection import TunableBuffInjection
from lot51_core.tunables.club_injection import TunableClubInteractionGroupInjection
from lot51_core.tunables.death_injection import TunableCustomDeath
from lot51_core.tunables.drama_scheduler_injection import TunableDramaSchedulerInjection
from lot51_core.tunables.loot_injection import TunableLootInjection
from lot51_core.tunables.mixer_list_injection import TunableMixerListInjection
from lot51_core.tunables.object_injection import TunableObjectInjectionByAffordance, TunableObjectInjectionByTuningId
from lot51_core.tunables.object_state_injection import TunableObjectStateInjection, TunableObjectStateValueInjection
from lot51_core.tunables.posture_injection import TunablePostureInjection
from lot51_core.tunables.service_picker_injection import TunableServicePickerInjection
from lot51_core.tunables.social_bunny_injection import TunableSocialBunnyInjection
from lot51_core.utils.injection import on_load_complete
from services import get_instance_manager
from sims4.tuning.instance_manager import InstanceManager
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableReference, TunableList, TunableReference, TunableTuple
from sims4.resources import Types


class TuningInjector(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(Types.SNIPPET)):
    INSTANCE_TUNABLES = {
        "inject_by_affordance": TunableList(
            description="Inject affordances to objects based on an existing affordance",
            tunable=TunableObjectInjectionByAffordance.TunableFactory(),
        ),
        "inject_by_object_tuning": TunableList(
            description="Inject affordances to object tuning",
            tunable=TunableObjectInjectionByTuningId.TunableFactory(),
        ),
        "inject_to_affordances": TunableList(
            description="Inject to affordances",
            tunable=TunableAffordanceInjectionByAffordances.TunableFactory()
        ),
        "inject_by_utility_info": TunableList(
            description="Inject to affordances",
            tunable=TunableAffordanceInjectionByUtility.TunableFactory()
        ),
        "inject_to_service_picker": TunableList(
            description="Inject affordances to phone service npc picker",
            tunable=TunableServicePickerInjection.TunableFactory(),
        ),
        "inject_to_club_interaction_group": TunableList(
            tunable=TunableClubInteractionGroupInjection.TunableFactory()
        ),
        "inject_to_mixer_list": TunableList(
            description="Inject mixers to affordance list snippet",
            tunable=TunableMixerListInjection.TunableFactory()
        ),
        "inject_to_object_states": TunableList(
            tunable=TunableObjectStateInjection.TunableFactory()
        ),
        "inject_to_object_state_values": TunableList(
            tunable=TunableObjectStateValueInjection.TunableFactory(),
        ),
        "inject_to_loot": TunableList(
            tunable=TunableLootInjection.TunableFactory()
        ),
        "inject_to_test_sets": TunableList(
            tunable=TunableTuple(
                test_set=TunableReference(manager=services.get_instance_manager(Types.SNIPPET)),
                tests=TunableTestSet(),
            )
        ),
        "inject_to_buffs": TunableList(
            tunable=TunableBuffInjection.TunableFactory(),
        ),
        "inject_to_postures": TunableList(
            tunable=TunablePostureInjection.TunableFactory()
        ),
        "inject_to_drama_scheduler": TunableDramaSchedulerInjection.TunableFactory(),
        "custom_death_types": TunableList(
            tunable=TunableCustomDeath.TunableFactory(),
        ),
        "social_bunny": TunableSocialBunnyInjection.TunableFactory(),
    }

    __slots__ = ('inject_by_affordance', 'inject_by_object_tuning', 'inject_to_affordances', 'inject_by_utility_info', 'inject_to_service_picker', 'inject_to_club_interaction_group', 'inject_to_mixer_list', 'inject_to_object_states', 'inject_to_object_state_values', 'inject_to_loot', 'inject_to_test_sets', 'inject_to_buffs', 'inject_to_drama_scheduler', 'inject_to_postures', 'custom_death_types', 'social_bunny',)

    def __repr__(self):
        return str(self.__name__)

    @classmethod
    def _tuning_loaded_callback(cls):
        logger.info('[TuningInjector] {}'.format(cls))

    @classmethod
    def perform_injections(cls):
        logger.info('[TuningInjector] starting snippet injections {}'.format(cls))

        for row in cls.inject_by_object_tuning:
            try:
                row.inject()
            except:
                logger.exception("Object injections by tuning failed")

        for row in cls.inject_by_affordance:
            try:
                row.inject()
            except:
                logger.exception("Object injections by affordance failed")

        for row in cls.inject_to_object_states:
            try:
                row.inject()
            except:
                logger.exception("Object state injections failed")

        for row in cls.inject_to_object_state_values:
            try:
                row.inject()
            except:
                logger.exception("Object state value injections failed")

        for test_set_data in cls.inject_to_test_sets:
            try:
                if test_set_data.test_set is None or test_set_data.tests is None:
                    continue
                test_set_data.test_set.test += test_set_data.tests
            except:
                logger.exception("Object state value injections failed")

        for row in cls.inject_to_buffs:
            try:
                row.inject()
            except:
                logger.exception("Buff injections failed")

        for custom_death in cls.custom_death_types:
            try:
                custom_death.inject()
            except:
                logger.exception("failed to inject death type: {}".format(custom_death))

        for row in cls.inject_to_loot:
            try:
                row.inject()
            except:
                logger.exception("failed to inject to loot")

        for row in cls.inject_to_club_interaction_group:
            try:
                row.inject()
            except:
                logger.exception("failed to inject to club interaction group")

        for row in cls.inject_to_postures:
            try:
                row.inject()
            except:
                logger.exception("failed to inject to postures")

        for row in cls.inject_to_service_picker:
            try:
                row.inject()
            except:
                logger.exception("Service npc picker injections failed")

        for row in cls.inject_to_mixer_list:
            try:
                row.inject()
            except:
                logger.exception("social mixer injections failed")

        for row in cls.inject_to_affordances:
            try:
                row.inject()
            except:
                logger.exception("Failed to inject to affordance")

        for row in cls.inject_by_utility_info:
            try:
                row.inject()
            except:
                logger.exception("failed injecting by utility")

        if cls.social_bunny is not None:
            try:
                cls.social_bunny.inject()
            except:
                logger.exception("failed injecting to social bunny")

        if cls.inject_to_drama_scheduler is not None:
            try:
                cls.inject_to_drama_scheduler.inject()
            except:
                logger.exception("failed injecting to drama scheduler")


@on_load_complete(Types.TDESC_DEBUG)
def _do_injections(manager: InstanceManager):
    snippet_manager: InstanceManager = get_instance_manager(Types.SNIPPET)
    snippets = snippet_manager.get_ordered_types(only_subclasses_of=TuningInjector)
    for snippet in snippets:
        try:
            snippet.perform_injections()
        except:
            logger.exception("failed injecting to snippet: {}".format(snippet))

