from balloon.balloon_enums import BALLOON_TYPE_LOOKUP
from balloon.balloon_request import BalloonRequest
from balloon.balloon_variant import BalloonVariant
from interactions import ParticipantType
from interactions.utils.loot_basic_op import BaseLootOperation
from lot51_core import logger
from sims.sim_info import SimInfo
from sims4.tuning.geometric import TunableVector3
from sims4.tuning.tunable import TunableList, TunableEnumEntry, Tunable, OptionalTunable
from sims4.random import weighted_random_item


class BalloonLoot(BaseLootOperation):
    FACTORY_TUNABLES = {
        'balloon_subject': TunableEnumEntry(tunable_type=ParticipantType, default=ParticipantType.Actor),
        'balloon_choices': TunableList(tunable=BalloonVariant.TunableFactory()),
        'delay': Tunable(tunable_type=float, default=0),
        'delay_random_offset': Tunable(tunable_type=float, default=0),
        'duration': Tunable(description='The duration, in seconds, that a balloon should last.', tunable_type=float, default=3.0),
        'offset': OptionalTunable(
            description='If enabled, the Vector3 offset from the balloon bone to the thought balloon.',
            tunable=TunableVector3(default=TunableVector3.DEFAULT_ZERO)
        )
    }

    def __init__(self, balloon_subject=None, balloon_choices=(), delay=0, delay_random_offset=0, duration=3, offset=None, **kwargs):
        self._balloon_subject = balloon_subject
        self._balloon_choices = balloon_choices
        self._delay = delay
        self._delay_random_offset = delay_random_offset
        self._duration = duration
        self._offset = offset
        super().__init__(**kwargs)

    def get_balloons(self, resolver):
        possible_balloons = []
        for balloon in self._balloon_choices:
            balloons = balloon.get_balloon_icons(resolver)
            possible_balloons.extend(balloons)
        return possible_balloons

    def send_balloon(self, balloon, target, resolver):
        icon_info = balloon.icon(resolver, balloon_target_override=None)

        category_icon = None
        if balloon.category_icon is not None:
            category_icon = balloon.category_icon(resolver, balloon_target_override=None)
            if icon_info[0] is None or icon_info[1] is None:
                logger.debug("Icon info is none: {}".format(icon_info))
                # return

        balloon_type, priority = BALLOON_TYPE_LOOKUP[balloon.balloon_type]
        balloon_overlay = balloon.overlay
        request = BalloonRequest(target, icon_info[0], icon_info[1], balloon_overlay, balloon_type, priority, self._duration, self._delay, self._delay_random_offset, category_icon, self._offset)
        request.distribute()
        logger.debug("Sent balloon {} to target: {}".format(balloon, target))
        return True


    def _apply_to_subject_and_target(self, subject, target, resolver):
        balloon_targets = resolver.get_participants(self._balloon_subject)
        possible_balloons = self.get_balloons(resolver)

        for obj in balloon_targets:
            if isinstance(obj, SimInfo):
                obj = obj.get_sim_instance()
                if obj is None:
                    continue
            chosen_balloon = weighted_random_item(possible_balloons)
            logger.debug("Applying balloon {} to target: {} and resolver: {}".format(chosen_balloon, obj, resolver))
            self.send_balloon(chosen_balloon, obj, resolver)
