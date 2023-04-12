import alarms
import services
import enum
from event_testing.test_events import TestEvent
from lot51_core.services.events import event_handler, CoreEvent
from sims4.commands import Command, CommandType
from sims4.resources import Types
from lot51_core import logger
from date_and_time import create_time_span
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import TunableTuple, TunableList, TunableReference, TunableSimMinute, TunableInterval, \
    TunableEnumEntry, HasTunableReference, Tunable
from event_testing.register_test_event_mixin import RegisterTestEventMixin


class LockCompatibilityType(enum.Int):
    ANY = 0
    AUTONOMOUS_ONLY = 1
    USER_DIRECTED_ONLY = 2


class AffordanceLockOutSnippet(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(Types.SNIPPET)):
    LOCK_OUT_TEST_SET = TunableReference(manager=services.get_instance_manager(Types.SNIPPET))

    INSTANCE_TUNABLES = {
        'lock_out': TunableList(
            tunable=TunableTuple(
                affordances=TunableList(tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION))),
                compatibility_type=TunableEnumEntry(tunable_type=LockCompatibilityType, default=LockCompatibilityType.ANY),
                interval=TunableInterval(description='Time in sim minutes in which this affordance will not be valid for.', tunable_type=TunableSimMinute, default_lower=1, default_upper=1, minimum=0),
                lock_by_target=Tunable(tunable_type=bool, default=False)
            )
        ),
        'test_set': TunableReference(manager=services.get_instance_manager(Types.SNIPPET)),
    }

    @classmethod
    def all_snippets_gen(cls):
        yield from services.get_instance_manager(Types.SNIPPET).get_ordered_types(only_subclasses_of=cls)

    @classmethod
    def get_test_set(cls):
        return cls.test_set if cls.test_set is not None else cls.LOCK_OUT_TEST_SET

    @classmethod
    def on_load(cls, *args, **kwargs):
        for snippet in cls.all_snippets_gen():
            test_set = snippet.get_test_set()
            if test_set is None:
                logger.warn("[AffordanceLockOutSnippet] Lock out test set not found for snippet: {}".format(snippet))
                continue
            for row in snippet.lock_out:
                for affordance in row.affordances:
                    if affordance is not None:
                        affordance.add_additional_test(test_set)
                        logger.warn("[AffordanceLockOutSnippet] added test to affordance {} in snippet: {}".format(affordance, snippet))
                    else:
                        logger.warn("[AffordanceLockOutSnippet] an affordance was None in snippet: {}".format(snippet))


class AffordanceLockOutRegistry(RegisterTestEventMixin):

    def __init__(self):
        super().__init__()
        self._registry = dict()
        self._cleanup_alarm = None

    def get_key(self, actor, affordance, target=None):
        return actor, affordance

    def is_locked_out(self, actor, affordance, target=None):
        key = self.get_key(actor, affordance, target=target)
        if key in self._registry:
            return self._registry[key] >= services.time_service().sim_now
        return False

    def get_lock_out_time(self, affordance, is_user_directed=False, default=0):
        for snippet in AffordanceLockOutSnippet.all_snippets_gen():
            for row in snippet.lock_out:
                if affordance in row.affordances:
                    if (is_user_directed and row.compatibility_type is LockCompatibilityType.AUTONOMOUS_ONLY) or (not is_user_directed and row.compatibility_type is LockCompatibilityType.USER_DIRECTED_ONLY):
                        return 0
                    return row.interval.random_float()
        return default

    def on_interaction_start(self, interaction):
        now = services.time_service().sim_now
        if interaction.is_super:
            duration = self.get_lock_out_time(interaction.get_interaction_type(), is_user_directed=interaction.is_user_directed)
            if duration > 0:
                lock_out_time = now + create_time_span(minutes=duration)
                actor = interaction.sim.sim_info
                key = self.get_key(actor, interaction.get_interaction_type(), target=interaction.target)
                self._registry[key] = lock_out_time
                logger.debug("[AffordanceLockOutRegistry] interaction is now locked: {} for {} minutes".format(key, duration))

    def _setup_cleanup_alarm(self):
        if self._cleanup_alarm is None:
            time_span = create_time_span(hours=3)
            self._cleanup_alarm = alarms.add_alarm(self, time_span, self._handle_cleanup_alarm)

    def _handle_cleanup_alarm(self, _):
        try:
            now = int(services.time_service().sim_now)
            for key, value in self._registry.items():
                if value <= now:
                    del self._registry[key]
        except:
            logger.exception("[AffordanceLockOutRegistry] Failed during cleanup")

    def _stop_cleanup_alarm(self):
        if self._cleanup_alarm is not None:
            self._cleanup_alarm.cancel()
            self._cleanup_alarm = None

    def start(self):
        self._setup_cleanup_alarm()
        self._register_test_event(TestEvent.InteractionStart)

    def stop(self):
        self._stop_cleanup_alarm()
        self._registry.clear()
        self._unregister_test_event(TestEvent.InteractionStart)

    def handle_event(self, sim_info, event, resolver):
        if event == TestEvent.InteractionStart:
            interaction = resolver.event_kwargs['interaction']
            self.on_interaction_start(interaction)


lock_out_service = AffordanceLockOutRegistry()


@event_handler(CoreEvent.TUNING_LOADED)
def _inject_lock_out(*args, **kwargs):
    AffordanceLockOutSnippet.on_load()


@event_handler(CoreEvent.LOADING_SCREEN_LIFTED)
def _lockout_on_zone_load(*args, **kwargs):
    lock_out_service.start()


@event_handler(CoreEvent.ZONE_UNLOAD)
def _lockout_on_zone_unload(*args, **kwargs):
    lock_out_service.stop()


@Command('lock_out.print_keys', command_type=CommandType.Live)
def _print_lock_out_keys(_connection=None):
    logger.info('#### LOCKOUT KEYS ####')
    logger.info('Current Time: {}'.format(services.time_service().sim_now))
    for key, value in lock_out_service._registry.items():
        logger.info("Key: {}".format(key))
        logger.info("Value: {}".format(value))
