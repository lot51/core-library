import services
from event_testing.tests import TunableGlobalTestSet
from interactions.utils.tunable_icon import TunableIconAllPacks
from lot51_core import logger
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import inject_list
from sims4.localization import TunableLocalizedStringFactory
from sims4.resources import Types
from sims4.tuning.tunable import Tunable, TunableReference, TunableVariant, TunableList, TunableEnumEntry
from situations.service_npcs.service_npc_tuning import ServiceNpcHireable
from tag import Tag


class TunableServicePickerInjection(BaseTunableInjection):
    PICKER_TUNING_ID = 9838
    FACTORY_TUNABLES = {
        'picker_tuning': Tunable(tunable_type=int, default=0),
        'icon': TunableIconAllPacks(description="The icon to be displayed in 'Hire a Service' UI"),
        'name': TunableLocalizedStringFactory(description="The name to be displayed for this NPC in the 'Hire a Service' UI."),
        'cost_string': TunableVariant(
            description='When enabled, the tuned string will be shown as the cost of hiring this NPC.',
            cost_amount=Tunable(description='', tunable_type=int, default=0),
            no_cost_string=TunableLocalizedStringFactory(description="The description to be used for this NPC in the if there isn't a cost associated with it"),
            locked_args={'disabled': None},
            default='disabled'
        ),
        'hire_interaction': TunableReference(
            description='The affordance to push the sim making the call when hiring this service npc from a picker dialog from the phone.',
            manager=services.get_instance_manager(Types.INTERACTION),
            pack_safe=True
        ),
        'tag_list': TunableList(description='Tags to be filtered by.', tunable=TunableEnumEntry(tunable_type=Tag, default=Tag.INVALID), unique_entries=True),
        'tests': TunableGlobalTestSet(description='A set of global tests that are always run before other tests. All tests must pass in order for the interaction to run.'),
        'free_service_traits': TunableList(
            description='If any Sim in the household has one of these traits, the non service npc will be free.',
            tunable=TunableReference(manager=services.get_instance_manager(Types.TRAIT), pack_safe=True),
            unique_entries=True
        )
    }

    __slots__ = ('description', 'icon', 'name', 'cost_string', 'hire_interaction', 'tag_list', 'tests', 'free_service_traits',)

    @classmethod
    def get_picker_tuning(cls):
        return services.get_instance_manager(Types.INTERACTION).get(cls.picker_tuning)

    def inject(self):
        picker_tuning = self.get_picker_tuning()
        if picker_tuning is not None:
            inject_list(picker_tuning, 'non_service_npcs', (self,))
        else:
            logger.warn("Could not find service npc picker tuning to inject with id {}".format(self.picker_tuning))


class TunableHireableServicePickerInjection(BaseTunableInjection):
    PICKER_TUNING_ID = 9838
    FACTORY_TUNABLES = {
        'picker_tuning': Tunable(tunable_type=int, default=0),
        'service_npc': TunableReference(manager=services.get_instance_manager(Types.SERVICE_NPC), class_restrictions=(ServiceNpcHireable,), pack_safe=True),
        'tag_list': TunableList(description='Tags to be filtered by.', tunable=TunableEnumEntry(tunable_type=Tag, default=Tag.INVALID), unique_entries=True),
        'already_hired_tooltip': TunableLocalizedStringFactory(description='Tooltip that displays if the service has already been hired.'),
        'tests': TunableGlobalTestSet(),
    }

    __slots__ = ('service_npc', 'tag_list', 'already_hired_tooltip', 'tests',)

    @classmethod
    def get_picker_tuning(cls):
        return services.get_instance_manager(Types.INTERACTION).get(cls.picker_tuning)

    def inject(self):
        picker_tuning = self.get_picker_tuning()
        if picker_tuning is not None:
            inject_list(picker_tuning, 'service_npcs', (self,))
        else:
            logger.warn("Could not find hireable service npc picker tuning to inject with id {}".format(self.picker_tuning))