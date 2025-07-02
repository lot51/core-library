import build_buy
import services
from distributor.system import Distributor
from lot51_core.lib.game_version import is_game_version
from plex.plex_enums import PlexBuildingType, INVALID_PLEX_ID
from protocolbuffers import InteractionOps_pb2, Consts_pb2, Business_pb2
from protocolbuffers.FileSerialization_pb2 import HouseholdAccountPair
from sims4.geometry import Polygon
from sims4.resources import Types
from world.travel_service import travel_sim_to_zone


def current_zone_is_apartment(consider_penthouse_an_apartment=False, consider_multi_unit_an_apartment=False):
    zone_id = services.current_zone_id()
    plex_service = services.get_plex_service()
    return plex_service.is_zone_an_apartment(zone_id, consider_penthouse_an_apartment=consider_penthouse_an_apartment, consider_multi_unit_an_apartment=consider_multi_unit_an_apartment)


def current_zone_is_penthouse():
    plex_service = services.get_plex_service()
    plex_type = plex_service.get_plex_building_type(services.current_zone_id())
    if is_game_version("<1.108.0"):
        return plex_type in (PlexBuildingType.PENTHOUSE_PLEX,)
    return plex_type in (PlexBuildingType.PENTHOUSE_PLEX, PlexBuildingType.BT_PENTHOUSE_RENTAL,)


def current_zone_is_multi_unit():
    if is_game_version("<1.108.0"):
        return False
    current_zone_id = services.current_zone_id()
    persistence_service = services.get_persistence_service()
    if persistence_service is None:
        return False
    zone_data = persistence_service.get_zone_proto_buff(current_zone_id)
    if zone_data is None:
        return False
    lot_data = persistence_service.get_lot_data_from_zone_data(zone_data)
    if lot_data is None:
        return False
    venue_tuning = services.get_instance_manager(Types.VENUE).get(lot_data.venue_key)
    return venue_tuning.is_multi_unit


def in_world_edit_mode():
    """
    Returns True if the current zone is running and in "Edit Mode"

    Many game services are unavailable, and Sims are not instanced.
    """
    zone = services.current_zone()
    if zone and zone.venue_service.build_buy_edit_mode:
        return True
    return False


def get_zone_data_gen():
   yield from services.get_persistence_service().zone_proto_buffs_gen()


def get_zone_data(zone_id):
   return services.get_persistence_service().get_zone_proto_buff(zone_id)


def get_lot_description_id_from_zone_data(zone_data):
    zone_world_description_id = services.get_world_description_id(zone_data.world_id)
    zone_lot_description_id = services.get_lot_description_id(zone_data.lot_id, zone_world_description_id)
    return zone_lot_description_id


def get_lot_description_id_from_zone_id(zone_id):
    zone_data = get_zone_data(zone_id)
    return get_lot_description_id_from_zone_data(zone_data)


def get_current_lot_description_id():
    return get_lot_description_id_from_zone_id(services.current_zone_id())


def get_zone_data_from_lot_description_id(lot_desc_id):
    for zone_proto in get_zone_data_gen():
        if zone_proto.lot_description_id == lot_desc_id:
            return zone_proto


def get_zone_id_from_lot_description_id(lot_desc_id):
    zone_data = get_zone_data_from_lot_description_id(lot_desc_id)
    if zone_data is not None:
        return zone_data.zone_id


def get_neighborhood_data_from_zone_data(zone_data):
    return services.get_persistence_service().get_neighborhood_proto_buff(zone_data.neighborhood_id)


def get_neighborhood_data_from_zone_id(zone_id):
    zone_data = get_zone_data(zone_id)
    return services.get_persistence_service().get_neighborhood_proto_buff(zone_data.neighborhood_id)


def add_zone_modifier(zone_modifier, zone_id=None, apply_immediately=True):
    if zone_modifier is None:
        return False
    if zone_id is None:
        zone_id = services.current_zone_id()
    zone_data = get_zone_data(zone_id)
    if zone_data is None:
        return False
    zone_modifier_id = zone_modifier.guid64
    if zone_modifier_id in zone_data.lot_traits:
        return True
    zone_data.lot_traits.append(zone_modifier_id)
    if apply_immediately:
        services.get_zone_modifier_service().check_for_and_apply_new_zone_modifiers(zone_id)
    return True


def remove_zone_modifier(zone_modifier, zone_id=None, apply_immediately=True):
    if zone_modifier is None:
        return False
    if zone_id is None:
        zone_id = services.current_zone_id()
    zone_data = get_zone_data(zone_id)
    if zone_data is None:
        return False
    zone_modifier_id = zone_modifier.guid64
    if zone_modifier_id not in zone_data.lot_traits:
        return True
    zone_data.lot_traits.remove(zone_modifier_id)
    if apply_immediately:
        services.get_zone_modifier_service().check_for_and_apply_new_zone_modifiers(zone_id)
    return True


def get_lot_owner_household_account_pair_from_zone_data(zone_data, neighborhood_data=None):
    if neighborhood_data is None:
        neighborhood_data = get_neighborhood_data_from_zone_data(zone_data)
    for lot_owner_info in neighborhood_data.lots:
        if lot_owner_info.zone_instance_id == zone_data.zone_id:
            if lot_owner_info.lot_owner:
                return lot_owner_info.lot_owner[0]
            else:
                break


def get_lot_owner_household_account_pair(zone_id):
    zone_data = get_zone_data(zone_id)
    return get_lot_owner_household_account_pair_from_zone_data(zone_data)


def get_lot_owner_household_id(zone_id):
    household_account_pair = get_lot_owner_household_account_pair(zone_id)
    if household_account_pair is not None:
        return household_account_pair.household_id


def clear_zone_owner(zone_id, sim_info=None, sell_business=True, include_lot_value_on_sell=False, success_callback=None):
    if sim_info is None:
        sim_info = services.active_sim_info()
    business_manager = None
    current_zone_id = services.current_zone_id()
    zone_manager = services.get_zone_manager()
    if sell_business:
        business_service = services.business_service()
        business_manager = business_service.get_business_manager_for_zone(zone_id)
        if business_manager is not None:
            if include_lot_value_on_sell:
                lot_value = build_buy.get_lot_value(zone_id, is_furnished=business_manager.include_furniture_price_on_sell)[0]
            else:
                lot_value = 0
            # Transfer business funds
            business_manager.sell_business_finalize_funds(lot_value)
            # Remove business owner
            unowned_business_type = business_manager.add_unowned_business_on_sell()
            business_service.remove_owner(zone_id, household_id=business_manager.owner_household_id, unowned_business_type=unowned_business_type)
    if not business_manager or business_manager.clear_lot_ownership_on_sell:
        zone_manager.clear_lot_ownership(zone_id)
    if business_manager and business_manager.disown_household_objects_on_sell:
        zone = zone_manager.get(zone_id)
        if zone is not None:
            zone.disown_household_objects()

    if success_callback is not None:
        success_callback()

    build_buy.set_venue_owner_id(zone_id, 0)
    # Reload zone
    travel_sim_to_zone(sim_info.sim_id, current_zone_id)
    # elif business_manager is not None:
    #     # Forces player to world map if selling active zone
    #     msg = InteractionOps_pb2.SellRetailLot()
    #     msg.retail_zone_id = zone_id
    #     Distributor.instance().add_event(Consts_pb2.MSG_SELL_RETAIL_LOT, msg)

    return True


def set_zone_owner(zone_id, sim_info, force_ownership=False, set_residential_ownership=False, travel_to_zone=True, business_type=None, success_callback=None):
    """

    :param zone_id: The zone to purchase
    :param sim_info: The sim who is purchasing
    :param set_residential_ownership: This will set zone_proto.household_id which triggers other services to kick in
    :param travel_to_zone: Whether to travel to zone on purchase or not, you should
    :param business_type: Type of business to create on purchase
    :param success_callback: Run final actions before traveling like charging the sim
    :return: True if successfully take ownership
    """
    household_id = sim_info.household_id
    household = services.household_manager().get(household_id)

    # Get existing HouseholdAccountPair of home zone to clone
    home_zone_owner_msg = get_lot_owner_household_account_pair(household.home_zone_id)

    travel_group_manager = services.travel_group_manager()

    zone_data = get_zone_data(zone_id)
    if zone_data is not None:
        if set_residential_ownership:
            if not force_ownership and zone_data.household_id != 0:
                return False
            # Update zone proto with new household id
            # See notes below about travel groups
            zone_data.household_id = household_id

        lot_decoration_service = services.lot_decoration_service()
        neighborhood_data = get_neighborhood_data_from_zone_data(zone_data)
        for lot_owner_info in neighborhood_data.lots:
            if lot_owner_info.zone_instance_id != zone_id:
                continue

            # Clear existing lot owners
            if force_ownership:
                lot_owner_info.ClearField('lot_owner')
            elif len(lot_owner_info.lot_owner):
                return False

            # Clone HouseholdAccountPair and append
            new_lot_owner = HouseholdAccountPair()
            new_lot_owner.CopyFrom(home_zone_owner_msg)
            lot_owner_info.lot_owner.append(new_lot_owner)

            if lot_decoration_service is not None:
                lot_decoration_service.handle_lot_owner_changed(zone_id, household)

            # Create business and set as owner if business type provided
            if business_type is not None:
                business_data = Business_pb2.SetBusinessData()
                business_data.sim_id = sim_info.id

                business_service = services.business_service()
                business_service.make_owner(sim_info.household_id, business_type, zone_id, business_data=business_data)

            if set_residential_ownership:
                # If there are any travel groups on the lot that are not StayOverTravelGroup
                # when the zone_data.household_id is set they will cause an exception
                # from the RoommateService on zone tick! So we should destroy all travel groups
                for travel_group in tuple(travel_group_manager.values()):
                    if travel_group.zone_id == zone_id:
                        travel_group_manager.destroy_travel_group_and_release_zone(travel_group)
            else:
                # New lot owner household should not have a travel group
                # in this case, others should be okay
                travel_group = travel_group_manager.get_travel_group_by_sim_info(sim_info)
                if travel_group and travel_group.zone_id == zone_id:
                    travel_group_manager.destroy_travel_group_and_release_zone(travel_group)

            # Run success callback before traveling
            if success_callback is not None:
                success_callback()

            if travel_to_zone:
                # Traveling allows the zone proto to be saved
                # and the Lot object to have an updated zone_owner_household_id
                travel_sim_to_zone(sim_info.sim_id, zone_id)

            return True
    return False


def get_level_area(level_index):
    plex_service = services.get_plex_service()
    plex_id = plex_service.get_active_zone_plex_id() or INVALID_PLEX_ID
    plex_type = plex_service.get_plex_building_type(services.current_zone_id())
    is_penthouse = plex_type in (PlexBuildingType.PENTHOUSE_PLEX, PlexBuildingType.BT_PENTHOUSE_RENTAL,)

    def get_area(block_polys):
        area = 0
        for (poly_data, block_level_index) in block_polys:
            if block_level_index != level_index:
                pass
            else:
                for p in poly_data:
                    polygon = Polygon(list(reversed(p)))
                    polygon.normalize()
                    area += polygon.area()
        return area

    area = get_area(build_buy.get_all_block_polygons(plex_id).values())

    # Updated Jun 2, 2024
    # Residential rental common area polys are stored in plex id of 0,
    # so perform additional query. This does not apply to CL apartments.
    # Updated Aug 3, 2024 - Penthouse apartments also have this same "issue"
    if plex_id != INVALID_PLEX_ID and is_penthouse:
        area += get_area(build_buy.get_all_block_polygons(INVALID_PLEX_ID).values())
    return area


def get_total_building_area():
    lot = services.active_lot()
    total_area = 0
    if lot is None:
        return total_area
    for level_index, lot_level in lot.lot_levels.items():
        area = get_level_area(level_index)
        total_area += area
    return int(total_area)


def get_lot_size():
    lot = services.active_lot()
    if lot is None:
        return 0, 0
    return int(lot.size_x), int(lot.size_z)


def get_total_lot_area():
    x, z = get_lot_size()
    return int(x * z)