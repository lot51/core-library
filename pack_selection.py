import sims4.reload
from lot51_core.lib.game_version import is_game_version
from lot51_core.utils.injection import inject_to
from services import InstanceTuningManagers


with sims4.reload.protected(globals()):
    _pack_hot_load_triggered = False


def is_pack_hot_load_triggered():
    """
    Check if the Player changed their Pack Selection settings and triggered a Tuning reload
    """
    global _pack_hot_load_triggered
    return _pack_hot_load_triggered


if is_game_version(">=1.117.0"):
    @inject_to(InstanceTuningManagers, '_pack_hot_load_callback')
    def _lot51_pack_hot_load_callback(original, *args, **kwargs):
        global _pack_hot_load_triggered
        _pack_hot_load_triggered = True
        return original(*args, **kwargs)
