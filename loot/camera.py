import camera
from interactions.utils.loot_basic_op import BaseLootOperation
from lot51_core.tunables.object_query import ObjectSearchMethodVariant
from sims4.tuning.tunable import Tunable


class CameraFocusLoot(BaseLootOperation):
    FACTORY_TUNABLES = {
        'follow': Tunable(tunable_type=bool, default=False),
        'object_source': ObjectSearchMethodVariant(),
    }

    def __init__(self, follow=False, object_source=None, **kwargs):
        self._follow = follow
        self._object_source = object_source
        super().__init__(**kwargs)

    def _apply_to_subject_and_target(self, subject, target, resolver):
        for obj in self._object_source.get_objects_gen(resolver):
            camera.focus_on_object(obj, follow=self._follow)
            return
