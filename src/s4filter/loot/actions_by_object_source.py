from event_testing.resolver import DoubleObjectResolver, SingleSimResolver
from interactions import ParticipantTypeSingle
from interactions.utils.loot import LootActionVariant
from interactions.utils.loot_basic_op import BaseLootOperation
from lot51_core import logger
from lot51_core.tunables.object_query import ObjectSearchMethodVariant
from sims4.tuning.tunable import TunableList, TunableEnumEntry


class DoActionsByObjectSource(BaseLootOperation):
    FACTORY_TUNABLES = {
        'actor_participant': TunableEnumEntry(tunable_type=ParticipantTypeSingle, default=ParticipantTypeSingle.Object),
        'loot_actions': TunableList(tunable=LootActionVariant()),
        'object_source': ObjectSearchMethodVariant(),
        'actions_on_success': TunableList(tunable=LootActionVariant()),
        'actions_on_failure': TunableList(tunable=LootActionVariant()),
    }

    def __init__(self, loot_actions=(), object_source=None, actor_participant=None, actions_on_success=(), actions_on_failure=(), **kwargs):
        self._actor_participant = actor_participant
        self._loot_actions = loot_actions
        self._object_source = object_source
        self._actions_on_success = actions_on_success
        self._actions_on_failure = actions_on_failure
        super().__init__(**kwargs)

    def _apply_to_subject_and_target(self, subject, target, resolver):
        try:
            logger.debug("doing actions by object source: {}".format(self))
            if isinstance(resolver, SingleSimResolver) and self._actor_participant == ParticipantTypeSingle.Object:
                participant = ParticipantTypeSingle.Actor
            else:
                participant = self._actor_participant
            did_apply_action = False
            # Apply actions to object query
            actor = resolver.get_participant(participant)
            for obj in self._object_source.get_objects_gen(resolver):
                resolver = DoubleObjectResolver(actor, obj)
                for action in self._loot_actions:
                    logger.debug("apply loot to obj: {} -> actor: {} target: {}".format(action, actor, obj))
                    action.apply_to_resolver(resolver)
                    did_apply_action = True
            # Apply additional actions based on object query success
            actor_resolver = SingleSimResolver(actor)
            if did_apply_action:
                for loot in self._actions_on_success:
                    loot.apply_to_resolver(actor_resolver)
            else:
                for loot in self._actions_on_failure:
                    loot.apply_to_resolver(actor_resolver)
        except:
            logger.exception("failed applying actions to object source")
