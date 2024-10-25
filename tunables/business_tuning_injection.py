import services
from business.business_enums import BusinessType
from business.business_tuning import BusinessTuning
from game_effect_modifier.game_effect_modifiers import TunableGameEffectVariant, GameEffectModifiers
from interactions import ParticipantType
from interactions.base.mixer_interaction import MixerInteraction
from interactions.utils.tunable import TunableAffordanceLinkList
from interactions.utils.tunable_provided_affordances import TunableProvidedAffordances
from lot51_core import logger
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.tunables.test_injection import TestInjectionVariant
from lot51_core.utils.injection import inject_mapping_lists, inject_list, merge_list, inject_dict, get_tuned_value
from lot51_core.utils.tunables import create_factory_wrapper
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableList, TunableMapping, TunableSet, OptionalTunable, Tunable
from sims4.collections import make_immutable_slots_class


class TunableBusinessTuningInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'business_data': TunableMapping(
            key_name='business_type',
            key_type=Tunable(tunable_type=int, default=-1),
            value_name='business',
            value_type=TunableReference(manager=services.get_instance_manager(Types.BUSINESS), pack_safe=True),
        ),
    }

    __slots__ = ('business_type', 'business',)

    def inject(self):

        for business_type, business_data in self.business_data.items():
            try:
                if business_type in BusinessTuning.BUSINESS_TYPE_TO_BUSINESS_DATA_MAP:
                    logger.warn("Business data for business type {} already exists.".format(business_type))
                    continue
                logger.debug("Adding business data to business type {} {}".format(business_type, business_data))
                inject_dict(BusinessTuning, 'BUSINESS_TYPE_TO_BUSINESS_DATA_MAP', new_items={business_type: business_data})
            except:
                logger.exception("Failed adding business data for enum value {}".format(business_type))
