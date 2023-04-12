import services
from autonomy.settings import AutonomyState


def get_autonomy_setting():
    """
    Returns the global autonomy setting (represented as off or full in the Gameplay Settings)
    """
    autonomy_service = services.autonomy_service()
    return autonomy_service._cached_autonomy_state_setting


def autonomy_for_active_sim_is_enabled():
    """
    Returns true if the active sim in general is permitted to use autonomy (represented by a checkbox in Gameplay Settings)
    """
    autonomy_service = services.autonomy_service()
    return autonomy_service._selected_sim_autonomy_enabled


def autonomy_for_sim_is_enabled(sim_info):
    """
    Returns true if a specific sim can be controlled by autonomy depending on the global autonomy setting and the
    autonomy for active sim setting.
    """
    if get_autonomy_setting() <= AutonomyState.DISABLED:
        return False
    active_sim = services.active_sim_info()
    if not autonomy_for_active_sim_is_enabled() and active_sim == sim_info:
        return False
    return True

