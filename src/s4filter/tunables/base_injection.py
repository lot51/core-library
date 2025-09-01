import enum
import sims4.common
from sims4.common import Pack
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit


class InjectionTiming(enum.Int):
    TUNING_LOADED = 1
    POST_TUNING_LOADED = 32
    ZONE_LOAD = 64


class BaseTunableInjection(HasTunableSingletonFactory, AutoFactoryInit):

    @property
    def injection_timing(self):
        return InjectionTiming.TUNING_LOADED

    @property
    def required_packs(self):
        return (Pack.BASE_GAME,)

    def is_available(self):
        return sims4.common.are_packs_available(self.required_packs)

    def inject(self):
        raise NotImplementedError