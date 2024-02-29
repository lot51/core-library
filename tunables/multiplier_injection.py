from lot51_core import logger
from _sims4_collections import frozendict
from sims4.localization import TunableLocalizedStringFactory
from sims4.tuning.tunable import Tunable, OptionalTunable, HasTunableSingletonFactory, AutoFactoryInit, TunableFactory
from tunable_multiplier import _get_tunable_multiplier_list_entry, TunableMultiplier


class TunableMultiplierInjection(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'base_value_override': OptionalTunable(
            tunable=Tunable(tunable_type=float, default=1),
        ),
        'additional_multipliers': _get_tunable_multiplier_list_entry(),
    }

    __slots__ = ('base_value_override', 'additional_multipliers',)

    @TunableFactory.factory_option
    def multiplier_options(use_tooltip=False):
        tuple_elements = {}
        if use_tooltip:
            tuple_elements['tooltip'] = OptionalTunable(
                description='If enabled, provides a tooltip for this entry if it is the first entry to pass its tests. Future: Offer ways to combine tooltips in separated lists, etc.',
                tunable=TunableLocalizedStringFactory()
            )
        else:
            tuple_elements['locked_args'] = {'tooltip': frozendict()}
        return {'additional_multipliers': _get_tunable_multiplier_list_entry(**tuple_elements)}

    def inject(self, target, key):
        tunable = getattr(target, key, None)
        if tunable is not None:
            base_value = tunable.base_value if self.base_value_override is None else self.base_value_override
            multipliers = tuple(tunable.multipliers) + self.additional_multipliers
            new_tunable = TunableMultiplier(base_value=base_value, multipliers=multipliers)
            # logger.debug("replacing multiplier {} with {}".format(getattr(target, key, None), new_tunable))
            setattr(target, key, new_tunable)
