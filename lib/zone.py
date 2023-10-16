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