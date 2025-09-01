from event_testing.resolver import SingleObjectResolver
from event_testing.tests import TunableTestSet
from interactions.base.state_picker_interaction import StatePickerSuperInteraction
from interactions.utils.tunable_icon import TunableIconVariant
from services import get_instance_manager
from sims4.localization import TunableLocalizedStringFactory
from sims4.resources import Types
from sims4.tuning.tunable import OptionalTunable, TunableMapping, TunableReference, TunableTuple


class AdvancedStatePickerSuperInteraction(StatePickerSuperInteraction):

    INSTANCE_TUNABLES = {
        '_active_icon': OptionalTunable(tunable=TunableIconVariant()),
        '_inactive_icon': OptionalTunable(tunable=TunableIconVariant()),
        'state_value_tests': TunableMapping(
            key_type=TunableReference(manager=get_instance_manager(Types.OBJECT_STATE)),
            value_type=TunableTuple(
                tests=TunableTestSet(),
                tooltip=OptionalTunable(tunable=TunableLocalizedStringFactory()),
            )
        )
    }

    @classmethod
    def potential_interactions(cls, target, context, **kwargs):
        if cls.use_pie_menu():
            resolver = SingleObjectResolver(target)
            for aop in super().potential_interactions(target, context, **kwargs):
                picker_row_data = aop.affordance.picker_row_data
                state_value = picker_row_data.tag

                if picker_row_data.is_enable:
                    if state_value in cls.state_value_tests:
                        sv_tuple = cls.state_value_tests[state_value]
                        if not sv_tuple.tests.run_tests(resolver):
                            picker_row_data.is_enable = False
                            if sv_tuple.tooltip is not None:
                                picker_row_data.row_tooltip = sv_tuple.tooltip

                if target.state_value_active(state_value):
                    if cls._active_icon is not None:
                        aop.affordance.pie_menu_icon = cls._active_icon
                else:
                    if cls._inactive_icon is not None:
                        aop.affordance.pie_menu_icon = cls._inactive_icon

                yield aop
        else:
            yield from super().potential_interactions(target, context, **kwargs)
