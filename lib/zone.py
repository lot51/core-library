import services


def in_world_edit_mode():
    """
    Returns True if the current zone is running and in "Edit Mode"

    Many game services are unavailable, and Sims are not instanced.
    """
    zone = services.current_zone()
    if zone and zone.venue_service.build_buy_edit_mode:
        return True
    return False


def add_zone_modifier(zone_modifier, apply_immediately=True):
    if zone_modifier is None:
        return False
    zone_id = services.current_zone_id()
    persistence_service = services.get_persistence_service()
    zone_data = persistence_service.get_zone_proto_buff(services.current_zone_id())
    if zone_data is None:
        return False
    zone_modifier_id = zone_modifier.guid64
    if zone_modifier_id in zone_data.lot_traits:
        return True
    zone_data.lot_traits.append(zone_modifier_id)
    if apply_immediately:
        services.get_zone_modifier_service().check_for_and_apply_new_zone_modifiers(zone_id)
    return True


def remove_zone_modifier(zone_modifier, apply_immediately=True):
    if zone_modifier is None:
        return False
    zone_id = services.current_zone_id()
    persistence_service = services.get_persistence_service()
    zone_data = persistence_service.get_zone_proto_buff(services.current_zone_id())
    if zone_data is None:
        return False
    zone_modifier_id = zone_modifier.guid64
    if zone_modifier_id not in zone_data.lot_traits:
        return True
    zone_data.lot_traits.remove(zone_modifier_id)
    if apply_immediately:
        services.get_zone_modifier_service().check_for_and_apply_new_zone_modifiers(zone_id)
    return True