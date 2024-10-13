import services
from lot51_core.lib.game_version import is_game_version
from plex.plex_enums import PlexBuildingType
from sims4.resources import Types


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
    for zone_proto in get_zone_data_gen():
        if zone_proto.lot_description_id == lot_desc_id:
            return zone_proto.zone_id


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

