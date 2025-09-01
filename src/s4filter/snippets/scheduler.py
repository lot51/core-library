import services
from event_testing.resolver import SingleObjectResolver, GlobalResolver, SingleSimResolver
from event_testing.tests import TunableTestSet
from interactions.utils.loot import LootActionVariant
from interactions.utils.success_chance import SuccessChance
from lot51_core import logger
from lot51_core.services.events import event_handler, CoreEvent
from lot51_core.tunables.object_query import ObjectSearchMethodVariant
from lot51_core.tunables.scheduling import TunableAlarmVariant
from lot51_core.utils.math import chance_succeeded
from sims.sim_info import SimInfo
from sims4.resources import Types
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import Tunable, TunableList, TunableTuple, OptionalTunable, TunableReference


class TunableSchedulerSnippet(metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(Types.SNIPPET)):
    _snippet_instances = set()

    INSTANCE_TUNABLES = {
        'mod_manifest': TunableReference(manager=services.get_instance_manager(Types.SNIPPET)),
        'actions': TunableList(
            tunable=TunableTuple(
                loot_actions=TunableList(tunable=LootActionVariant()),
                object_source=ObjectSearchMethodVariant(description="Objects to apply loot actions to"),
                chance=SuccessChance.TunableFactory(description="Chance this specific action occurs on alarm"),
                tests=TunableTestSet(description="Tests to run before running this row of loot_actions"),
            ),
        ),
        'global_chance': SuccessChance.TunableFactory(description="Global chance to run actions on alarm, will reschedule otherwise if repeating is enabled."),
        'repeating': OptionalTunable(
            description="Enable to repeat the alarm by the schedule_type interval tuned below.",
            tunable=TunableTuple(
                cancel_on_test_failure=Tunable(tunable_type=bool, default=False),
            )
        ),
        'schedule_type': TunableAlarmVariant(description="Type of scheduling"),
        'tests': TunableTestSet(description="Tests to run before the actions are executed each trigger."),
        'zone_tests': TunableTestSet(description="Tests to run before scheduling on each zone load."),
    }

    @classmethod
    def _tuning_loaded_callback(cls):
        cls._snippet_instances.add(cls())

    @classmethod
    def all_schedulers_gen(cls):
        yield from cls._snippet_instances

    @classmethod
    def all_snippets_gen(cls):
        yield from services.get_instance_manager(Types.SNIPPET).get_ordered_types(only_subclasses_of=(TunableSchedulerSnippet,))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.schedule_type = self.schedule_type(self, callback=self._scheduler_callback)
        logger.debug("[init] {}".format(self))

    def __str__(self):
        return "<TunableScheduler {} scheduled: {}>".format(type(self).__name__, self.scheduled)

    @property
    def scheduled(self):
        return self.schedule_type and self.schedule_type.scheduled

    def start(self):
        if not self.run_zone_tests():
            logger.debug("[{}] Global tests have failed, not starting in this zone.".format(self))
            return
        time_span = self.schedule_type.start()
        logger.debug("[{}] Started scheduler: {}".format(self, time_span))

    def reschedule(self):
        time_span = self.schedule_type.reschedule()
        logger.debug("[{}] Rescheduled scheduler: {}".format(self, time_span))

    def stop(self):
        self.schedule_type.stop()
        logger.debug("[{}] Stopped scheduler".format(self))

    def get_resolver(self, resolver=None):
        if resolver is None:
            resolver = GlobalResolver()
        return resolver

    def test_chance(self, chance, resolver):
        value = chance.get_chance(resolver)
        logger.debug("Chance Value: {}".format(value))
        return chance_succeeded(value)

    def run_tests(self, resolver=None):
        resolver = self.get_resolver(resolver)
        return self.tests.run_tests(resolver)

    def run_zone_tests(self, resolver=None):
        resolver = self.get_resolver(resolver)
        return self.zone_tests.run_tests(resolver)

    def run_actions(self):
        for action_type in self.actions:
            for obj in action_type.object_source.get_objects_gen(resolver=None):
                if isinstance(obj, SimInfo) or obj.is_sim:
                    resolver = SingleSimResolver(obj)
                else:
                    resolver = SingleObjectResolver(obj)

                if action_type.tests.run_tests(resolver):
                    if self.test_chance(action_type.chance, resolver):
                        for action in action_type.loot_actions:
                            action.apply_to_resolver(resolver)
                    else:
                        logger.debug("Action chance failed")
                else:
                    logger.debug("Action tests failed")

    def _scheduler_callback(self):
        try:
            logger.debug("[{}] Running callback".format(self))
            test_result = self.run_tests()
            if test_result:
                logger.debug("[{}] run_tests passed".format(self))
                self.run_actions()
            else:
                logger.debug("[{}] run_tests failed".format(self))

            if self.repeating is not None:
                if (test_result or (not test_result and not self.repeating.cancel_on_test_failure)):
                    logger.debug("[{}] Rescheduling on callback".format(self))
                    self.reschedule()
                else:
                    logger.debug("[{}] Rescheduling not permitted due to test failure".format(self))
        except:
            logger.exception("[{}] Failed running callback".format(self))


@event_handler(CoreEvent.ZONE_CLEANUP_OBJECTS)
def _setup_schedulers_on_zone_load(service, **kwargs):
    for scheduler in TunableSchedulerSnippet.all_schedulers_gen():
        try:
            scheduler.start()
        except:
            logger.exception("Failed to start scheduler {}".format(scheduler))


@event_handler(CoreEvent.ZONE_UNLOAD)
def _shutdown_schedulers_on_zone_unload(service, **kwargs):
    for scheduler in TunableSchedulerSnippet.all_schedulers_gen():
        try:
            scheduler.stop()
        except:
            logger.exception("Failed to stop scheduler {}".format(scheduler))
