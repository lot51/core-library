import services
from event_testing.resolver import SingleObjectResolver
from event_testing.tests import TunableTestSet
from interactions.base.picker_interaction import PickerSuperInteraction
from interactions.utils.tunable_icon import TunableIconVariant
from lot51_core import logger
from lot51_core.utils.flags import Flag
from sims4.localization import TunableLocalizedStringFactory
from sims4.math import MAX_INT32
from sims4.resources import Types
from sims4.tuning.tunable import OptionalTunable, TunableMapping, TunableTuple, TunableRange, TunableReference
from sims4.utils import flexmethod
from ui.ui_dialog_picker import ObjectPickerRow


class FlagStatPickerSuperInteraction(PickerSuperInteraction):

    INSTANCE_TUNABLES = {
        '_active_icon': OptionalTunable(tunable=TunableIconVariant()),
        '_inactive_icon': OptionalTunable(tunable=TunableIconVariant()),
        'stat_type': TunableReference(manager=services.get_instance_manager(Types.STATISTIC)),
        'flag_values': TunableMapping(
            key_type=TunableRange(tunable_type=int, default=1, minimum=0, maximum=MAX_INT32),
            value_type=TunableTuple(
                flag_name=TunableLocalizedStringFactory(),
                display_description=TunableLocalizedStringFactory(),
                tests=TunableTestSet(),
                tooltip=OptionalTunable(tunable=TunableLocalizedStringFactory()),
            )
        )
    }

    def on_choice_selected(self, raw_flag_value, **kwargs):
        stat = self.target.get_tracker(self.stat_type).get_statistic(self.stat_type, add=True)
        flag = Flag(stat.get_value() if stat is not None else 0)
        flag_value = 1 << raw_flag_value
        if flag.has(flag_value):
            flag.remove(flag_value)
            logger.debug("Removing flag! {} {}".format(flag_value, flag.get()))
        else:
            flag.add(flag_value)
            logger.debug("Adding to flag! {} {}".format(flag_value, flag.get()))
        stat.set_value(flag.get())

    @flexmethod
    def picker_rows_gen(cls, inst, target, context, **kwargs):
        inst_or_cls = inst if inst is not None else cls
        for flag_value, flag_data in inst_or_cls.flag_values.items():
            yield ObjectPickerRow(name=flag_data.flag_name(), row_description=flag_data.display_description(), tag=flag_value)

    def _run_interaction_gen(self, timeline):
        self._show_picker_dialog(self.sim)
        yield from ()

    @classmethod
    def potential_interactions(cls, target, context, **kwargs):
        if cls.use_pie_menu():
            resolver = SingleObjectResolver(target)
            stat = target.get_tracker(cls.stat_type).get_statistic(cls.stat_type)
            flag = Flag(stat.get_value() if stat is not None else 0)
            for aop in super().potential_interactions(target, context, **kwargs):
                picker_row_data = aop.affordance.picker_row_data
                flag_value = 1 << picker_row_data.tag
                flag_data = cls.flag_values.get(picker_row_data.tag, None)
                test_result = flag_data.tests.run_tests(resolver)
                if not test_result:
                    tooltip = test_result.tooltip
                    picker_row_data.is_enable = False
                    if flag_data.tooltip is not None:
                         tooltip = flag_data.tooltip
                    picker_row_data.row_tooltip = tooltip

                if flag.has(flag_value):
                    if cls._active_icon is not None:
                        aop.affordance.pie_menu_icon = cls._active_icon
                else:
                    if cls._inactive_icon is not None:
                        aop.affordance.pie_menu_icon = cls._inactive_icon

                yield aop
        else:
            yield from super().potential_interactions(target, context, **kwargs)
