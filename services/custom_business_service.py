from business.business_enums import BusinessType
from business.business_tracker import BusinessTracker
from lot51_core import logger
from lot51_core.utils.injection import inject_to, inject_to_enum


class CustomBusinessService:
    CUSTOM_BUSINESS_MANAGERS = dict()

    @classmethod
    def register_business_type(cls, business_type_key: str, business_type: int, business_manager_type):
        """
        Injects business type to BusinessType enum, and registers BusinessManager class factory
        to be used when `make_owner` is called on the business service.

        :param business_type_key: string that represents the business type enum key
        :param business_type: int that represents the business type enum value
        :param business_manager_type: business manager factory
        :return: None
        """
        inject_to_enum({business_type_key: business_type}, BusinessType)
        cls.CUSTOM_BUSINESS_MANAGERS[business_type] = business_manager_type
        logger.info("[CustomBusinessService] Registered type {}:{} with manager {}".format(business_type_key, business_type, business_manager_type))

    @classmethod
    def get_business_manager_factory(cls, business_type: int):
        return cls.CUSTOM_BUSINESS_MANAGERS.get(business_type, None)


@inject_to(BusinessTracker, 'make_owner')
def _business_tracker_make_owner(original, self, owner_household_id, business_zone_id, *args, **kwargs):
    custom_business_manager_factory = CustomBusinessService.get_business_manager_factory(self.business_type)

    if custom_business_manager_factory is not None:
        logger.info("Using custom business type {} for Household ID: {}, Zone ID: {}".format(self.business_type, owner_household_id, business_zone_id))
        business_manager = custom_business_manager_factory(**kwargs)
        self._business_managers[business_zone_id] = business_manager
        business_manager.set_owner_household_id(owner_household_id)
        business_manager.set_zone_id(business_zone_id)
        return business_manager
    else:
        return original(self, owner_household_id, business_zone_id, *args, **kwargs)
