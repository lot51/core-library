from interactions import ParticipantTypeSingleSim
from interactions.base.super_interaction import SuperInteraction
from interactions.constraint_variants import TunableConstraintVariant
from lot51_core.interactions.door_constraint import TunableDoorConstraint
from sims4.tuning.tunable import TunableList, TunableTuple, TunableEnumEntry


class AdvancedSuperInteraction(SuperInteraction):

    INSTANCE_TUNABLES = {
        '_constraints': TunableList(
            tunable=TunableTuple(
                constrained_participant=TunableEnumEntry(
                    tunable_type=ParticipantTypeSingleSim,
                    default=ParticipantTypeSingleSim.Actor
                ),
                constraints=TunableList(
                    tunable=TunableTuple(
                        value=TunableConstraintVariant(
                            door_target=TunableDoorConstraint()
                        )
                    )
                )
            )
        )
    }