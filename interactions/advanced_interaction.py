from interactions import ParticipantTypeSingleSim
from interactions.base.basic import TunableBasicContentSet
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
                            door_target=TunableDoorConstraint(description="An alternative to the front_door constraint that allows you to target a specific door.")
                        )
                    )
                )
            )
        ),
        'basic_content': TunableBasicContentSet(
            description='The main animation and periodic stat changes for the interaction. (Same as SuperInteract but uses one_shot as the default instead)',
            one_shot=True,
            flexible_length=True,
            default='one_shot',
        ),
    }
