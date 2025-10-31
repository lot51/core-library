import services
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import inject_list
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableSet

try:
    # Introduced 1.117
    from custom_schedules.custom_schedule_tuning import CustomScheduleTuning
except:
    CustomScheduleTuning = None

class TunableCustomScheduleTuningInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'premade_custom_assignments': TunableSet(
            description='A set of affordance lists associated with this interaction group.',
            tunable=TunableReference(
                manager=services.get_instance_manager(Types.SNIPPET),
                class_restrictions=('CustomScheduleAssignment',),
                pack_safe=True
            )
        ),
        'premade_custom_schedules': TunableSet(
            description='A set of affordance lists associated with this interaction group.',
            tunable=TunableReference(
                manager=services.get_instance_manager(Types.SNIPPET),
                class_restrictions=('CustomSchedulePreset',),
                pack_safe=True
            )
        ),
    }

    __slots__ = ('premade_custom_assignments', 'premade_custom_schedules',)

    def inject(self):
        if CustomScheduleTuning is None:
            return
        if self.premade_custom_assignments is not None:
            inject_list(CustomScheduleTuning, 'PREMADE_CUSTOM_ASSIGNMENTS', new_items=self.premade_custom_assignments)
        if self.premade_custom_schedules is not None:
            inject_list(CustomScheduleTuning, 'PREMADE_CUSTOM_SCHEDULES', new_items=self.premade_custom_schedules)
