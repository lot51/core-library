import services
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import inject_list
from sims4.resources import Types
from sims4.tuning.tunable import Tunable, TunableReference, TunableList, OptionalTunable, TunableTuple


class TunablePostureListInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'posture_type_lists': TunableList(
            tunable=TunableReference(manager=services.get_instance_manager(Types.SNIPPET), pack_safe=True, class_restrictions=('PostureTypeList',))
        ),
        'posture_types': TunableList(
            tunable=TunableTuple(
                posture_type=TunableReference(manager=services.get_instance_manager(Types.POSTURE), pack_safe=True),
                required_clearance=OptionalTunable(tunable=Tunable(tunable_type=float, default=1))
            )
        )
    }

    __slots__ = ('posture_type_lists', 'posture_types',)

    def inject(self):
        for snippet in self.posture_type_lists:
            inject_list(snippet, 'value', new_items=self.posture_types)