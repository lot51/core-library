import services
import enum
from event_testing.test_events import TestEvent
from lot51_core.services.events import event_handler
from sims4.resources import Types
from lot51_core import logger
from date_and_time import create_time_span
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import TunableTuple, TunableList, TunableReference, TunableSimMinute, TunableInterval, TunableEnumEntry, HasTunableReference
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
                interval=TunableInterval(description='Time in sim minutes in which this affordance will not be valid for.', tunable_type=TunableSimMinute, default_lower=1, default_upper=1, minimum=0)
            )
        )
    }

    @classmethod
    def all_snippets_gen(cls):
        yield from services.get_instance_manager(Types.SNIPPET).get_ordered_types(only_subclasses_of=cls)

    @classmethod
    def on_load(cls, *args, **kwargs):
        if cls.LOCK_OUT_TEST_SET is None:
            logger.warn("Lock out test set not found.")
            return

        for snippet in cls.all_snippets_gen():
            for row in snippet.lock_out:
                for affordance in row.affordances:
                    affordance.add_additional_test(cls.LOCK_OUT_TEST_SET)


class AffordanceLockOutRegistry(RegisterTestEventMixin):
    _registry = {}

    @classmethod
    def get_key(cls, actor, affordance, target=None):
        return actor, affordance, target

    @classmethod
    def is_locked_out(cls, actor, affordance, target=None):
        key = cls.get_key(actor, affordance, target=target)
        if key in cls._registry:
            return cls._registry[key] >= services.time_service().sim_now
        return False

    @classmethod
    def get_lock_out_time(cls, affordance, is_user_directed=False, default=0):
        for snippet in AffordanceLockOutSnippet.all_snippets_gen():
            for row in snippet.lock_out:
                if affordance in row.affordances:
                    if (is_user_directed and row.compatibility_type is LockCompatibilityType.AUTONOMOUS_ONLY) or (not is_user_directed and row.compatibility_type is LockCompatibilityType.USER_DIRECTED_ONLY):
                        return 0
                    return row.interval.random_float()
        return default

    @classmethod
    def on_interaction_start(cls, interaction):
        now = services.time_service().sim_now
        if interaction.is_super:
            duration = cls.get_lock_out_time(interaction.affordance, is_user_directed=interaction.is_user_directed)
            if duration > 0:
                lock_out_time = now + create_time_span(minutes=duration)
                actor = interaction.sim.sim_info
                key = cls.get_key(actor, interaction.affordance, target=interaction.target)
                cls._registry[key] = lock_out_time
                logger.debug("interaction is now locked: {} for {} minutes".format(key, duration))

    def start(self):
        self._register_test_event(TestEvent.InteractionStart)

    def stop(self):
        AffordanceLockOutRegistry._registry = {}
        self._unregister_test_event(TestEvent.InteractionStart)

    def handle_event(self, sim_info, event, resolver):
        if event == TestEvent.InteractionStart:
            interaction = resolver.event_kwargs['interaction']
            AffordanceLockOutRegistry.on_interaction_start(interaction)


lock_out_service = AffordanceLockOutRegistry()


@event_handler("instance_managers.loaded")
def _inject_lock_out(*args, **kwargs):
    AffordanceLockOutSnippet.on_load()


@event_handler('zone.loading_screen_lifted')
def _lockout_on_zone_load(*args, **kwargs):
    lock_out_service.start()


@event_handler('zone.unload')
def _lockout_on_zone_unload(*args, **kwargs):
    lock_out_service.stop()
