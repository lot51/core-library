import services
from filters.tunable import FilterTermVariant, TunableSimFilter
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import inject_list
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableList, OptionalTunable, TunableVariant, TunableTuple
from singletons import DEFAULT


class TunableSimFilterInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'sim_filters': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.SIM_FILTER), pack_safe=True),
        ),
        'additional_conform_terms': TunableList(
            tunable=FilterTermVariant(),
        ),
        'filter_terms': TunableList(
            tunable=FilterTermVariant(),
        ),
        'repurpose_terms_override': OptionalTunable(
            tunable=TunableTuple(
                repurpose_terms=TunableVariant(
                    use_specific_sims=TunableReference(manager=services.get_instance_manager(Types.SIM_FILTER)),
                    locked_args={'use_constrained_sims': TunableSimFilter.USE_CONSTRAINED_SIMS, 'use_unimportant_sims': DEFAULT, 'dont_repurpose': None},
                    default='dont_repurpose',
                ),
            )
        ),
    }

    __slots__ = ('sim_filters', 'additional_conform_terms', 'filter_terms', 'repurpose_terms_override',)

    def inject(self):
        for sim_filter in self.sim_filters:
            inject_list(sim_filter, 'additional_conform_terms', self.additional_conform_terms)
            inject_list(sim_filter, '_filter_terms', self.filter_terms)

            if self.repurpose_terms_override is not None:
                sim_filter.repurpose_terms = self.repurpose_terms_override.repurpose_terms