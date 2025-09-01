from lot51_core.utils.flags import Flag
from sims4.tuning.tunable import TunableFactory, TunableEnumSet


class TunableFlags(TunableFactory):

    @staticmethod
    def factory(enum_set):
        flags = 0
        for enum_value in enum_set:
            flags |= 1 << enum_value
        return Flag(flags)

    FACTORY_TYPE = factory

    def __init__(self, enum_type, enum_default=None, default_enum_list=frozenset(), **kwargs):
        super().__init__(
            enum_set=TunableEnumSet(enum_type=enum_type, enum_default=enum_default, default_enum_list=default_enum_list,),
            **kwargs
        )
