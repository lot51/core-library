import services
import enum
from sims4.resources import Types
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import TunableTuple, TunableList, TunableReference, TunableSimMinute, TunableInterval, TunableEnumEntry, HasTunableReference, Tunable


class LockCompatibilityType(enum.Int):
    ANY = 0
    AUTONOMOUS_ONLY = 1
    USER_DIRECTED_ONLY = 2


class AffordanceLockOutSnippet(HasTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(Types.SNIPPET)):

    INSTANCE_TUNABLES = {
        "version": Tunable(tunable_type=str, allow_empty=True, default='1', description="The schema version of AffordanceLockOutSnippet"),
        "creator_name": Tunable(tunable_type=str, allow_empty=True, default='N/A'),
        "mod_name": Tunable(tunable_type=str, allow_empty=True, default='N/A'),
        'lock_out': TunableList(
            tunable=TunableTuple(
                _disabled=Tunable(tunable_type=bool, default=False),
                affordances=TunableList(tunable=TunableReference(manager=services.get_instance_manager(Types.INTERACTION))),
                compatibility_type=TunableEnumEntry(tunable_type=LockCompatibilityType, default=LockCompatibilityType.ANY),
                interval=TunableInterval(description='Time in sim minutes in which this affordance will not be valid for.', tunable_type=TunableSimMinute, default_lower=1, default_upper=1, minimum=0),
                lock_by_target=Tunable(tunable_type=bool, default=False)
            )
        ),
    }

    @classmethod
    def all_snippets_gen(cls):
        yield from services.get_instance_manager(Types.SNIPPET).get_ordered_types(only_subclasses_of=cls)
