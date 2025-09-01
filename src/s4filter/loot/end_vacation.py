import services
from interactions import ParticipantType
from interactions.utils.loot_basic_op import BaseLootOperation
from lot51_core import logger
from sims4.tuning.tunable import TunableEnumEntry


class EndVacationLoot(BaseLootOperation):
    FACTORY_TUNABLES = {
        'participant': TunableEnumEntry(tunable_type=ParticipantType, default=ParticipantType.Actor, invalid_enums=(ParticipantType.Invalid,)),
    }

    def __init__(self, participant=None, **kwargs):
        self._participant = participant
        super().__init__(**kwargs)

    def _apply_to_subject_and_target(self, subject, target, resolver):
        sim_info = resolver.get_participant(self._participant)
        logger.debug("ending vacation for participant {}".format(sim_info))
        travel_group_manager = services.travel_group_manager()
        travel_group = travel_group_manager.get_travel_group_by_sim_info(sim_info)
        if travel_group is not None:
            travel_group.end_vacation()
