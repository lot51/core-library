from interactions.base.state_picker_interaction import StatePickerSuperInteraction
from interactions.utils.tunable_icon import TunableIconVariant
from sims4.tuning.tunable import OptionalTunable


class AdvancedStatePickerSuperInteraction(StatePickerSuperInteraction):

    INSTANCE_TUNABLES = {
        '_active_icon': OptionalTunable(tunable=TunableIconVariant()),
        '_inactive_icon': OptionalTunable(tunable=TunableIconVariant()),
    }

    @classmethod
    def potential_interactions(cls, target, context, **kwargs):
        if cls.use_pie_menu():
            for aop in super().potential_interactions(target, context, **kwargs):
                picker_row_data = aop.affordance.picker_row_data
                state_value = picker_row_data.tag
                if target.get_state(state_value.state) == state_value:
                    if cls._active_icon is not None:
                        aop.affordance.pie_menu_icon = cls._active_icon
                else:
                    if cls._inactive_icon is not None:
                        aop.affordance.pie_menu_icon = cls._inactive_icon

                yield aop
        else:
            yield from super().potential_interactions(target, context, **kwargs)
