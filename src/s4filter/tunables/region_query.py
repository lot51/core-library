import services
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableReference, TunableList


class BaseRegionQuery(HasTunableSingletonFactory, AutoFactoryInit):
    def get_regions_gen(self):
        raise NotImplementedError


class SpecificRegionQuery(BaseRegionQuery):
    FACTORY_TUNABLES = {
        'regions': TunableList(tunable=TunableReference(manager=services.get_instance_manager(Types.REGION))),
    }

    def get_regions_gen(self):
        yield from self.regions


class AllRegionsQuery(BaseRegionQuery):
    FACTORY_TUNABLES = {
        'ignore_list': TunableList(tunable=TunableReference(manager=services.get_instance_manager(Types.REGION))),
    }
    def get_regions_gen(self):
        for region in services.get_instance_manager(Types.REGION).get_ordered_types():
            if region not in self.ignore_list:
                yield region
