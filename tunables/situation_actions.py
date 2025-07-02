import services
from event_testing.resolver import SingleSimResolver
from event_testing.tests import TunableTestSet
from interactions.aop import AffordanceObjectPair
from interactions.priority import Priority
from lot51_core.tunables.coordinates import TunableCoordinates
from sims4.resources import Types
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import TunableList, HasTunableSingletonFactory, AutoFactoryInit, TunableReference, \
    OptionalTunable, TunableVariant, TunableEnumEntry


class SituationAction(HasTunableSingletonFactory, AutoFactoryInit):

    FACTORY_TUNABLES = {
        'jobs': TunableList(
            description="Situation Jobs in this Situation that should be valid for this action.",
            tunable=TunableReference(manager=services.get_instance_manager(Types.SITUATION_JOB)),
            needs_tuning=True,
        ),
        'tests': TunableTestSet(),
    }

    __slots__ = ('jobs', 'tests',)

    def get_resolver(self, sim):
        return SingleSimResolver(sim)

    def is_valid(self, sim, job):
        if job not in self.jobs:
            return False
        resolver = self.get_resolver(sim)
        return self.tests.run_tests(resolver)

    def apply_to_sim(self, situation, sim, job):
        raise NotImplementedError


class MoveSimSpawnAction(SituationAction):
    FACTORY_TUNABLES = {
        'street': TunableReference(
            description="The Street these coordinates are valid on",
            manager=services.get_instance_manager(Types.STREET)
        ),
        'coordinates': TunableCoordinates.TunableFactory(),
        'facing_coordinates': OptionalTunable(
            description="If enabled, the Sim will face this position, otherwise a random orientation will be chosen.",
            tunable=TunableCoordinates.TunableFactory(),
        )
    }

    __slots__ = ('coordinates', 'facing_coordinates', 'street',)

    def is_valid(self, sim, job):
        current_street = services.current_street()
        if self.street is None or current_street != self.street:
            return False
        return super().is_valid(sim, job)

    def apply_to_sim(self, situation, sim, job):
        self.coordinates.move_sim_to(sim, facing_coordinates=self.facing_coordinates)


class PushRoleInteractionAction(SituationAction):

    FACTORY_TUNABLES = {
        'priority': TunableEnumEntry(tunable_type=Priority, default=Priority.Low)
    }

    __slots__ = ('priority',)

    def apply_to_sim(self, situation, sim, job):
        interaction = situation._choose_role_interaction(sim, run_priority=self.priority)
        if interaction is not None:
            execute_result = AffordanceObjectPair.execute_interaction(interaction)


class ApplyLootAction(SituationAction):
    FACTORY_TUNABLES = {
        'loot_list': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.ACTION))
        )
    }

    __slots__ = ('loot_list',)

    def apply_to_sim(self, situation, sim, job):
        resolver = self.get_resolver(sim)
        for action in self.loot_list:
            action.apply_to_resolver(resolver)


class ApplyReferenceActions(SituationAction):
    FACTORY_TUNABLES = {
        'reference': TunableReference(manager=services.get_instance_manager(Types.SNIPPET))
    }

    __slots__ = ('reference',)

    def apply_to_sim(self, situation, sim, job):
        for spawn_action in self.reference:
            if spawn_action.is_valid(sim, job):
                spawn_action.apply_to_sim(situation, sim, job)


class SituationActionVariant(TunableVariant):

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            loot=ApplyLootAction.TunableFactory(),
            move_sim=MoveSimSpawnAction.TunableFactory(),
            push_role_interaction=PushRoleInteractionAction.TunableFactory(),
            reference=ApplyReferenceActions.TunableFactory(),
            **kwargs
            )


class SituationSpawnActionsSnippet(metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(Types.SNIPPET)):
    _snippet_instances = set()

    INSTANCE_TUNABLES = {
        'spawn_actions': TunableList(
            tunable=SituationActionVariant(),
        ),
    }

    __slots__ = ('spawn_actions',)

    def __iter__(self):
        yield from self.spawn_actions
