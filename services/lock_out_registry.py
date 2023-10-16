import alarms
import services
from event_testing.test_events import TestEvent
from lot51_core.services.events import event_handler, CoreEvent
from lot51_core.snippets.lock_out import AffordanceLockOutSnippet, LockCompatibilityType
from sims4.commands import Command, CommandType
from lot51_core import logger
from date_and_time import create_time_span
from event_testing.register_test_event_mixin import RegisterTestEventMixin


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


lock_out_registry = AffordanceLockOutRegistry()


@event_handler(CoreEvent.LOADING_SCREEN_LIFTED)
def _lockout_on_zone_load(*args, **kwargs):
    lock_out_registry.start()


@event_handler(CoreEvent.ZONE_UNLOAD)
def _lockout_on_zone_unload(*args, **kwargs):
    lock_out_registry.stop()


@Command('lock_out.print_keys', command_type=CommandType.Live)
def _print_lock_out_keys(_connection=None):
    logger.info('#### LOCKOUT KEYS ####')
    logger.info('Current Time: {}'.format(services.time_service().sim_now))
    for key, value in lock_out_registry._registry.items():
        logger.info("Key: {}".format(key))
        logger.info("Value: {}".format(value))
