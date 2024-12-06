import services
from business.business_tuning import BusinessTuning
from lot51_core import logger
from lot51_core.tunables.base_injection import BaseTunableInjection
from lot51_core.utils.injection import inject_dict
from sims4.resources import Types
from sims4.tuning.tunable import TunableReference, TunableMapping, Tunable


class TunableBusinessTuningInjection(BaseTunableInjection):
    FACTORY_TUNABLES = {
        'business_data': TunableMapping(
            key_name='business_type',
            key_type=Tunable(tunable_type=int, default=-1),
            value_name='business',
            value_type=TunableReference(manager=services.get_instance_manager(Types.BUSINESS), pack_safe=True),
        ),
    }

    __slots__ = ('business_data',)

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
