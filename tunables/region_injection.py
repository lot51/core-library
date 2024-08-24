from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.tunables.region_query import AllRegionsQuery, SpecificRegionQuery
from lot51_core.utils.injection import inject_list
from services import get_instance_manager
from sims4.resources import Types
from sims4.tuning.tunable import OptionalTunable, Tunable, TunableVariant, TunableList, TunableReference


class TunableRegionInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'region_source': TunableVariant(
            all_regions=AllRegionsQuery.TunableFactory(),
            specific_regions=SpecificRegionQuery.TunableFactory(),
            default='specific_regions'
        ),
        'is_persistable': OptionalTunable(
            description="Allows regions to save their statistic component",
            tunable=Tunable(tunable_type=bool, default=True)
        ),
        'compatible_venues': TunableList(tunable=TunableReference(manager=get_instance_manager(Types.VENUE), pack_safe=True))
    }

    __slots__ = ('region_source', 'is_persistable', 'compatible_venues',)

    def inject(self):
        for region in self.region_source.get_regions_gen():
            if region is not None:
                if self.is_persistable is not None:
                    region.is_persistable = self.is_persistable

                inject_list(region, 'compatible_venues', new_items=self.compatible_venues)