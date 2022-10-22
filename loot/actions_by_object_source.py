from event_testing.resolver import SingleObjectResolver
from interactions.utils.loot import LootActionVariant
from interactions.utils.loot_basic_op import BaseLootOperation
from lot51_core import logger
from lot51_core.tunables.object_query import ObjectSearchMethodVariant
from sims4.tuning.tunable import TunableList


class DoActionsByObjectSource(BaseLootOperation):
    FACTORY_TUNABLES = {
        'loot_actions': TunableList(tunable=LootActionVariant()),
        'object_source': ObjectSearchMethodVariant(),
    }

    def __init__(self, loot_actions=(), object_source=None, **kwargs):
        self._loot_actions = loot_actions
        self._object_source = object_source
        super().__init__(**kwargs)

    def _apply_to_subject_and_target(self, subject, target, resolver):
        for obj in self._object_source.get_objects_gen(resolver):
            resolver = SingleObjectResolver(obj)
            for action in self._loot_actions:
                success = action.apply_to_resolver(resolver)
                logger.debug("doing action: {} on obj: {} success: {}".format(action, obj, success))
