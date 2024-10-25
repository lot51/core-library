import logging
import os
import lot51_core
from lot51_core.lib.game_version import get_game_version
from lot51_core.lib.time import get_wallclock_now


def Logger(name, root, filename, prefix='', version='N/A', mode='development', is_first_party=False, **kwargs):
    path = os.path.join(root, filename)
    handler = logging.FileHandler(path, mode='w')
    log_mode = logging.DEBUG if mode == 'development' else logging.INFO

    formatter = logging.Formatter('[%(levelname)s] %(message)s')

    logger = logging.getLogger(name)
    logger.setLevel(log_mode)
    logger.addHandler(handler)
    handler.setFormatter(formatter)

    if is_first_party and not prefix:
        prefix = '[Lot 51]'

    now = get_wallclock_now()
    timestamp = int(now.timestamp())

    logger.info('{prefix}[{name}] Version: {version}; Mode: {mode}; Core Library Version: {lib}; Game Version: {game_version}; Generated: {timestamp} UTC'.format(
        prefix=prefix, name=name, version=version, mode=mode, lib=lot51_core.__version__, game_version=get_game_version(), timestamp=timestamp))
    if is_first_party:
        logger.info('If you are experiencing any issues with this mod, please join my Discord at https://lot51.cc/discord and report your error in #mod-support with this log.')
    return logger


def stringify_sim_info(sim_info):
    """
    DEPRECATED. Use lot51_core.lib.sim.get_sim_name instead.
    """
    from lot51_core.lib.sims import get_sim_name
    return get_sim_name(sim_info)


def stringify_sim(sim):
    """
    DEPRECATED. Use lot51_core.lib.sim.get_sim_name instead.
    """
    from lot51_core.lib.sims import get_sim_name
    return get_sim_name(sim)
