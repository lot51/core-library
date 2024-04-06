import build_buy
import enum
import services
from lot51_core import logger
from interactions import ParticipantType
from lot51_core.tunables.object_query import ObjectSearchMethodVariant
from lot51_core.utils.placement import get_location_near_location, get_location_near_object
from objects.terrain import TerrainPoint
from sims.sim_info import SimInfo
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableEnumEntry, TunableList, Tunable, OptionalTunable, TunableInterval


class InventoryDeliveryFallback(enum.Int):
    NONE = 0
    ACTIVE_HOUSEHOLD = 1
    ZONE_HOUSEHOLD = 2


def attempt_fallback_delivery(resolver, obj, fallback_inventory):
    if fallback_inventory == InventoryDeliveryFallback.ACTIVE_HOUSEHOLD:
        active_household_id = services.active_household_id()
        if build_buy.is_household_inventory_available(active_household_id):
            if build_buy.move_object_to_household_inventory(obj):
                return True
    elif fallback_inventory == InventoryDeliveryFallback.ZONE_HOUSEHOLD:
        current_zone = services.current_zone()
        zone_household = current_zone.get_active_lot_owner_household()
        if zone_household and build_buy.is_household_inventory_available(zone_household.id):
            if build_buy.move_object_to_household_inventory(obj):
                return True
    return False


class FglDeliveryMethod(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {
        'participant_type': TunableEnumEntry(tunable_type=ParticipantType, default=ParticipantType.Object),
        'optimal_distance': Tunable(tunable_type=float, default=0),
        'radius_width': Tunable(tunable_type=float, default=8),
        'max_distance': Tunable(tunable_type=float, default=8),
        'x_random_offset': OptionalTunable(tunable=TunableInterval(tunable_type=float, default_lower=0, default_upper=0)),
        'z_random_offset': OptionalTunable(tunable=TunableInterval(tunable_type=float, default_lower=0, default_upper=0)),
    }

    __slots__ = ('participant_type', 'optimal_distance', 'radius_width', 'max_distance', 'x_random_offset', 'z_random_offset')

    def __call__(self, resolver, obj, **kwargs):
        participant = resolver.get_participant(self.participant_type)
        if isinstance(participant, TerrainPoint):
            translation, orientation, routing_surface = get_location_near_location(obj, participant.location, optimal_distance=self.optimal_distance, radius_width=self.radius_width, max_distance=self.max_distance, x_range=self.x_random_offset, z_range=self.z_random_offset)
        elif isinstance(participant, SimInfo):
            sim = participant.get_sim_instance()
            translation, orientation, routing_surface = get_location_near_object(obj, sim, optimal_distance=self.optimal_distance, radius_width=self.radius_width, max_distance=self.max_distance, x_range=self.x_random_offset, z_range=self.z_random_offset)
        else:
            translation, orientation, routing_surface = get_location_near_object(obj, participant, optimal_distance=self.optimal_distance, radius_width=self.radius_width, max_distance=self.max_distance, x_range=self.x_random_offset, z_range=self.z_random_offset)

        obj.opacity = 0
        obj.move_to(translation=translation, orientation=orientation, routing_surface=routing_surface)
        obj.fade_in()
        logger.debug("delivering obj to participant {} {}".format(obj, participant))
        return True


class MailboxDeliveryMethod(HasTunableSingletonFactory, AutoFactoryInit):

    FACTORY_TUNABLES = {
        'fallback_inventory': TunableEnumEntry(tunable_type=InventoryDeliveryFallback, default=InventoryDeliveryFallback.NONE),
    }

    __slots__ = ('fallback_inventory',)

    def __call__(self, resolver, obj, participant=ParticipantType.Actor):
        # attempt to find a valid inventory
        sim_info = resolver.get_participant(participant)
        zone = services.get_zone(sim_info.household.home_zone_id)
        if zone is not None:
            lot_hidden_inventory = zone.lot.get_hidden_inventory()
            if lot_hidden_inventory is not None and lot_hidden_inventory.player_try_add_object(obj):
                return True
        # otherwise attempt to use fallback inventory
        if attempt_fallback_delivery(resolver, obj, self.fallback_inventory):
            return True
        # delivery failed
        return False


class InventoryDeliveryMethod(HasTunableSingletonFactory, AutoFactoryInit):

    FACTORY_TUNABLES = {
        'inventory_source': ObjectSearchMethodVariant(),
        'fallback_inventory': TunableEnumEntry(tunable_type=InventoryDeliveryFallback, default=InventoryDeliveryFallback.NONE),
    }

    __slots__ = ('inventory_source', 'fallback_inventory',)

    def __call__(self, resolver, obj, **kwargs):
        # attempt to find a valid inventory
        for inventory_owner in self.inventory_source.get_objects_gen(resolver=resolver):
            if inventory_owner.inventory_component is not None:
                if inventory_owner.inventory_component.player_try_add_object(obj):
                    return True
        # otherwise attempt to use fallback inventory
        if attempt_fallback_delivery(resolver, obj, self.fallback_inventory):
            return True
        # delivery failed
        return False


class MultipleInventoriesDeliveryMethod(HasTunableSingletonFactory, AutoFactoryInit):

    class InventoryDeliveryFallback(enum.Int):
        NONE = 0
        ACTIVE_HOUSEHOLD = 1
        ZONE_HOUSEHOLD = 2

    FACTORY_TUNABLES = {
        'inventory_sources': TunableList(tunable=ObjectSearchMethodVariant()),
        'fallback_inventory': TunableEnumEntry(tunable_type=InventoryDeliveryFallback, default=InventoryDeliveryFallback.NONE),
    }

    __slots__ = ('inventory_sources', 'fallback_inventory',)

    def __call__(self, resolver, obj, **kwargs):
        # attempt to find a valid inventory
        for inventory_source in self.inventory_sources:
            for inventory_owner in inventory_source.get_objects_gen(resolver=resolver):
                if inventory_owner.inventory_component is not None:
                    if inventory_owner.inventory_component.player_try_add_object(obj):
                        return True
        # attempt to find a valid alternate inventory
        # otherwise attempt to use fallback inventory
        if attempt_fallback_delivery(resolver, obj, self.fallback_inventory):
            return True
        # delivery failed
        return False
