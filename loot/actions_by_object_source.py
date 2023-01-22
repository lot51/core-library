from event_testing.resolver import DoubleObjectResolver
from interactions import ParticipantTypeSingle
from interactions.utils.loot import LootActionVariant
from interactions.utils.loot_basic_op import BaseLootOperation
from lot51_core.tunables.object_query import ObjectSearchMethodVariant
from sims4.tuning.tunable import TunableList, TunableEnumEntry


class DoActionsByObjectSource(BaseLootOperation):
    FACTORY_TUNABLES = {
        'actor_participant': TunableEnumEntry(tunable_type=ParticipantTypeSingle, default=ParticipantTypeSingle.Object),
        'loot_actions': TunableList(tunable=LootActionVariant()),
        'object_source': ObjectSearchMethodVariant(),
    }

    def __init__(self, loot_actions=(), object_source=None, actor_participant=None, **kwargs):
        self._actor_participant = actor_participant
        self._loot_actions = loot_actions
        self._object_source = object_source
        super().__init__(**kwargs)

    def _apply_to_subject_and_target(self, subject, target, resolver):
        actor = resolver.get_participant(self._actor_participant)
        for obj in self._object_source.get_objects_gen(resolver):
            resolver = DoubleObjectResolver(actor, obj)
            for action in self._loot_actions:
                # logger.debug("apply loot to obj: {} -> actor: {} target: {}".format(action, actor, obj))
                action.apply_to_resolver(resolver)
