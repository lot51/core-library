from lot51_core import logger
from lot51_core.utils.collections import AttributeDict
from lot51_core.utils.injection import merge_dict, merge_list
from services import get_instance_manager
from sims4.resources import Types
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableList, TunableReference, OptionalTunable, TunableTuple, TunableVariant, Tunable
from snippets import TunableVenueListReference


class TunableMapViewPickerInteractionInjection(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'additional_venue_inclusion': OptionalTunable(
            description="This injection does not change the inclusion type.",
            tunable=TunableTuple(
                exclude_venues=TunableList(
                    tunable=TunableReference(manager=get_instance_manager(Types.VENUE), pack_safe=True),
                ),
                exclude_lists=TunableList(
                    tunable=TunableVenueListReference(),
                ),
                include_venues=TunableList(
                    tunable=TunableReference(manager=get_instance_manager(Types.VENUE), pack_safe=True),
                ),
                include_lists=TunableList(
                    tunable=TunableVenueListReference(pack_safe=True),
                ),
            )
        ),
    }

    __slots__ = ('additional_venue_inclusion',)

    def inject_to_affordance(self, affordance):
        if affordance is None:
            logger.error("Failed to inject to map view picker interaction, affordance not found")
            return

        if self.additional_venue_inclusion is not None:
            custom_inclusion = self.additional_venue_inclusion
            default_inclusion = getattr(affordance, 'default_inclusion', None)
            if default_inclusion is None:
                logger.warn("Affordance ({}) is not a valid map view picker interaction.".format(affordance))
            else:
                overrides = AttributeDict()
                if hasattr(default_inclusion, 'exclude_venues'):
                    overrides.exclude_venues = merge_list(default_inclusion.exclude_venues, custom_inclusion.exclude_venues)
                if hasattr(default_inclusion, 'exclude_lists'):
                    overrides.exclude_lists = merge_list(default_inclusion.exclude_lists, custom_inclusion.exclude_lists)
                if hasattr(default_inclusion, 'include_venues'):
                    overrides.include_venues = merge_list(default_inclusion.include_venues, custom_inclusion.include_venues)
                if hasattr(default_inclusion, 'include_lists'):
                    overrides.include_lists = merge_list(default_inclusion.include_lists, custom_inclusion.include_lists)
                # logger.info("Overrides: {}".format(overrides))
                if overrides is not None:
                    new_default_inclusion = merge_dict(default_inclusion, new_items=overrides)
                    setattr(affordance, 'default_inclusion', new_default_inclusion)
