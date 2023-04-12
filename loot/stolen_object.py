from interactions.utils.loot_basic_op import BaseLootOperation
from lot51_core import logger
from lot51_core.tunables.object_query import ObjectSearchMethodVariant
from objects.components.types import STOLEN_COMPONENT
from sims4.tuning.tunable import OptionalTunable, TunableTuple, Tunable


class ReturnStolenObjectLoot(BaseLootOperation):
    FACTORY_TUNABLES = {
        'object_source': ObjectSearchMethodVariant(),
        'fade_in': OptionalTunable(
            tunable=TunableTuple(
                duration=Tunable(tunable_type=float, default=1.5),
            )
        )
    }

    def __init__(self, object_source=None, fade_in=None, **kwargs):
        self._object_source = object_source
        self._fade_in = fade_in
        super().__init__(**kwargs)

    def _apply_to_subject_and_target(self, subject, target, resolver):
        for obj in self._object_source.get_objects_gen(resolver=resolver):
            try:
                if obj.has_component(STOLEN_COMPONENT):
                    obj.remove_component(STOLEN_COMPONENT)
                    if self._fade_in is not None:
                        obj.fade_in(fade_duration=self._fade_in.duration)
            except:
                logger.exception("Failed to return stolen object: {}".format(obj))
