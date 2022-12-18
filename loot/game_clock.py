import services
from clock import ClockSpeedMode
from interactions.utils.loot_basic_op import BaseLootOperation
from sims4.tuning.tunable import TunableEnumEntry


class GameClockSpeedLoot(BaseLootOperation):
    FACTORY_TUNABLES = {
        'clock_speed': TunableEnumEntry(tunable_type=ClockSpeedMode, default=ClockSpeedMode.NORMAL, invalid_enums=(ClockSpeedMode.INTERACTION_STARTUP_SPEED, ClockSpeedMode.SUPER_SPEED3,)),
    }

    def __init__(self, clock_speed=False, **kwargs):
        self._clock_speed = clock_speed
        super().__init__(**kwargs)

    def _apply_to_subject_and_target(self, subject, target, resolver):
        services.game_clock_service().set_clock_speed(self._clock_speed)