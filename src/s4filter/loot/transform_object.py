import random
import sims4.math
from interactions.utils.loot_basic_op import BaseLootOperation
from lot51_core import logger
from lot51_core.tunables.object_query import ObjectSearchMethodVariant
from sims4.tuning.tunable import OptionalTunable, TunableInterval


class TransformObjectLoot(BaseLootOperation):
    FACTORY_TUNABLES = {
        'object_source': ObjectSearchMethodVariant(),
        'orientation': OptionalTunable(
            description="A 360 degree angle value to add to the current object orientation",
            tunable=TunableInterval(tunable_type=int, default_lower=0, default_upper=360, minimum=-360, maximum=360)
        ),
    }

    def __init__(self, object_source=None, orientation=None, **kwargs):
        self._object_source = object_source
        self._orientation = orientation
        super().__init__(**kwargs)

    @classmethod
    def _apply_orientation(cls, obj, angle=0):
        current_angle = sims4.math.yaw_quaternion_to_angle(obj.orientation)
        new_angle = current_angle + angle
        orientation = sims4.math.angle_to_yaw_quaternion(new_angle)
        obj.move_to(orientation=orientation)

    def _apply_to_subject_and_target(self, subject, target, resolver):
        for obj in self._object_source.get_objects_gen(resolver=resolver):
            try:
                if self._orientation is not None:
                    chosen_angle = random.randint(self._orientation.lower_bound, self._orientation.upper_bound)
                    self._apply_orientation(obj, angle=chosen_angle)
            except:
                logger.exception("Failed to transform object: {}".format(obj))
