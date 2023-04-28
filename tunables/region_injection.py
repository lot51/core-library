from lot51_core.tunables.region_query import AllRegionsQuery, SpecificRegionQuery
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, OptionalTunable, Tunable, TunableVariant



class TunableRegionInjection(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'region_source': TunableVariant(
            all_regions=AllRegionsQuery.TunableFactory(),
            specific_regions=SpecificRegionQuery.TunableFactory(),
            default='specific_regions'
        ),
        'is_persistable': OptionalTunable(tunable=Tunable(tunable_type=bool, default=True)),
    }

    __slots__ = ('region_source', 'is_persistable',)

    def inject(self):
        for region in self.region_source.get_regions_gen():
            if region is not None:
                if self.is_persistable is not None:
                    region.is_persistable = self.is_persistable
