import enum
import services
from interactions import ParticipantTypeSingle
from interactions.utils.loot_basic_op import BaseLootOperation
from lot51_core.utils.flags import Flag
from sims4.math import MAX_INT32
from sims4.resources import Types
from sims4.tuning.tunable import TunableEnumEntry, TunableReference, Tunable, TunableRange


class FlagStatLoot(BaseLootOperation):
    class FlagAction(enum.Int):
        INVALID = 0
        ADD = 1
        REMOVE = 2
        RESET = 3

    FACTORY_TUNABLES = {
        'add_stat': Tunable(tunable_type=bool, default=True),
        'stat_type': TunableReference(manager=services.get_instance_manager(Types.STATISTIC)),
        'participant': TunableEnumEntry(tunable_type=ParticipantTypeSingle, default=ParticipantTypeSingle.Object),
        'flag_value': TunableRange(tunable_type=int, default=1, minimum=0, maximum=MAX_INT32),
        'flag_action': TunableEnumEntry(tunable_type=FlagAction, default=FlagAction.INVALID),
    }

    def __init__(self, add_stat=False, participant=None, stat_type=None, flag_value=0, flag_action=FlagAction.INVALID, **kwargs):
        self._add_stat = add_stat
        self._participant = participant
        self._stat_type = stat_type
        self._flag_value = flag_value
        self._flag_action = flag_action
        super().__init__(**kwargs)

    def _apply_to_subject_and_target(self, subject, target, resolver):
        obj = resolver.get_participant(self._participant)
        if obj is None or self._stat_type is None or self._flag_action == FlagStatLoot.FlagAction.INVALID:
            return

        stat = obj.get_tracker(self._stat_type).get_statistic(self._stat_type, add=self._add_stat)
        if stat is None:
            return

        if self._flag_action == FlagStatLoot.FlagAction.RESET:
            stat.set_value(0)
        else:
            flag = Flag(stat.get_value())
            if self._flag_action == FlagStatLoot.FlagAction.ADD:
                flag.add(1 << self._flag_value)
            elif self._flag_action == FlagStatLoot.FlagAction.REMOVE:
                flag.remove(1 << self._flag_value)

            stat.set_value(flag.get())
