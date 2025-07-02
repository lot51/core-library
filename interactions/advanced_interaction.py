from interactions import ParticipantTypeSingleSim, ParticipantType
from interactions.base.basic import TunableBasicContentSet
from interactions.base.super_interaction import SuperInteraction
from interactions.constraint_variants import TunableConstraintVariant
from lot51_core.interactions.door_constraint import TunableDoorConstraint
from lot51_core.interactions.elements.xevt_callback import CallbackXevtElement
from sims4.tuning.tunable import TunableList, TunableTuple, TunableEnumEntry, Tunable


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
        '_xevt_callback_id': Tunable(tunable_type=int, default=100),
        'basic_content': TunableBasicContentSet(
            description='The main animation and periodic stat changes for the interaction. (Same as SuperInteract but uses one_shot as the default instead)',
            one_shot=True,
            flexible_length=True,
            default='one_shot',
        ),
    }

    def __init__(self, *args, xevt_callback=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._xevt_callback = xevt_callback

    def build_basic_elements(self, **kwargs):
        sequence = super().build_basic_elements(**kwargs)
        if self._xevt_callback is None:
            return sequence

        def handle_callback():
            self._xevt_callback(self)

        change_element = CallbackXevtElement(self, sequence, self._xevt_callback_id, callback=handle_callback)
        return change_element
